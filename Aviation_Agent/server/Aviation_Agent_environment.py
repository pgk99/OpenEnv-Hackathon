# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from uuid import uuid4
import random
import re
from typing import Dict, Any

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import AviationAgentAction, AviationAgentObservation
except ImportError:
    from models import AviationAgentAction, AviationAgentObservation


class AviationAgentEnvironment(Environment):
    """
    Aviation ATC Communication Environment.
    
    Simulates Air Traffic Control radio communication where an agent (pilot)
    must respond correctly to ATC instructions using proper aviation phraseology.
    
    Tasks range from simple (single instruction) to complex (multiple instructions
    with conditional logic).
    """
    
    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    
    # Define 3 tasks: Easy → Medium → Hard
    TASKS = [
        {
            "id": "task_1_easy",
            "difficulty": "easy",
            "instruction": "Speedbird 247, descend and maintain flight level 180.",
            "description": "Acknowledge and read back altitude change",
            "required_elements": {
                "callsign": ["Speedbird 247", "Speedbird two four seven"],
                "altitude": ["FL180", "flight level 180", "flight level one eight zero"],
                "action": ["descend", "descending"]
            },
            "max_steps": 2
        },
        {
            "id": "task_2_medium",
            "difficulty": "medium",
            "instruction": "United 512, turn left heading 090, descend and maintain 5000 feet.",
            "description": "Acknowledge and read back heading and altitude changes",
            "required_elements": {
                "callsign": ["United 512", "United five one two"],
                "heading": ["090", "heading 090", "zero nine zero"],
                "altitude": ["5000", "five thousand"],
                "action_turn": ["left", "turn left"],
                "action_descend": ["descend", "descending"]
            },
            "max_steps": 3
        },
        {
            "id": "task_3_hard",
            "difficulty": "hard",
            "instruction": "Delta 1823, traffic alert. Traffic 2 o'clock, 3 miles, opposite direction, altitude indicates 8000 feet. Turn right heading 270, climb and maintain 10000 feet.",
            "description": "Acknowledge traffic, read back heading and altitude, confirm visual or looking",
            "required_elements": {
                "callsign": ["Delta 1823", "Delta one eight two three"],
                "traffic_ack": ["traffic", "looking", "visual", "in sight"],
                "heading": ["270", "heading 270", "two seven zero"],
                "altitude": ["10000", "ten thousand", "flight level 100"],
                "action_turn": ["right", "turn right"],
                "action_climb": ["climb", "climbing"]
            },
            "max_steps": 4
        }
    ]

    def __init__(self, task_id: str = None):
        """
        Initialize environment.
        
        Args:
            task_id: Optional specific task ID to use. If None, random task is selected.
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_id = task_id
        self._current_task = None
        self._response_history = []
        self._max_steps_reached = False

    def reset(self) -> AviationAgentObservation:
        """Reset environment and select a task."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._response_history = []
        self._max_steps_reached = False
        
        # Select task
        if self._task_id:
            self._current_task = next(t for t in self.TASKS if t["id"] == self._task_id)
        else:
            self._current_task = random.choice(self.TASKS)
        
        return AviationAgentObservation(
            atc_instruction=self._current_task["instruction"],
            task_description=self._current_task["description"],
            step_count=0,
            done=False,
            reward=0.0,
        )

    def step(self, action: AviationAgentAction) -> AviationAgentObservation:
        """Execute one step in the environment."""
        self._state.step_count += 1
        response = action.message.strip()
        self._response_history.append(response)
        
        # Grade the response
        score = self._grade_response(response)
        
        # Calculate reward with trajectory signals
        reward = self._calculate_reward(score, self._state.step_count)
        
        # Check if done
        done = score >= 0.9 or self._state.step_count >= self._current_task["max_steps"]
        if self._state.step_count >= self._current_task["max_steps"]:
            self._max_steps_reached = True
        
        # Build metadata
        metadata = {
            "task_id": self._current_task["id"],
            "difficulty": self._current_task["difficulty"],
            "response": response,
            "score": score,
            "max_steps_reached": self._max_steps_reached,
            "grading_details": self._get_grading_details(response)
        }
        
        return AviationAgentObservation(
            atc_instruction=self._current_task["instruction"],
            task_description=self._current_task["description"],
            step_count=self._state.step_count,
            done=done,
            reward=reward,
            metadata=metadata
        )

    def _grade_response(self, response: str) -> float:
        """
        Grade the pilot's response (0.0 to 1.0).
        
        Checks for required elements in the response using aviation phraseology.
        """
        response_lower = response.lower()
        required = self._current_task["required_elements"]
        
        scores = {}
        
        # Check each required element category
        for category, acceptable_phrases in required.items():
            found = any(phrase.lower() in response_lower for phrase in acceptable_phrases)
            scores[category] = 1.0 if found else 0.0
        
        # Calculate overall score
        total_score = sum(scores.values()) / len(scores) if scores else 0.0
        
        return total_score

    def _get_grading_details(self, response: str) -> Dict[str, Any]:
        """Get detailed grading breakdown."""
        response_lower = response.lower()
        required = self._current_task["required_elements"]
        
        details = {}
        for category, acceptable_phrases in required.items():
            found = any(phrase.lower() in response_lower for phrase in acceptable_phrases)
            details[category] = {
                "found": found,
                "expected_phrases": acceptable_phrases
            }
        
        return details

    def _calculate_reward(self, score: float, step_count: int) -> float:
        """
        Calculate reward with trajectory signals.
        
        - Rewards partial progress (not just binary end-of-episode)
        - Penalizes taking too many steps
        - Bonus for completing in fewer steps
        """
        # Base reward from score
        reward = score
        
        # Penalty for each step taken (encourages efficiency)
        step_penalty = 0.05 * (step_count - 1)
        reward -= step_penalty
        
        # Bonus for high score on first attempt
        if step_count == 1 and score >= 0.9:
            reward += 0.3
        
        # Penalty for max steps reached without success
        if self._max_steps_reached and score < 0.9:
            reward -= 0.2
        
        # Ensure reward is in reasonable range
        return max(-1.0, min(1.0, reward))

    @property
    def state(self) -> State:
        return self._state
