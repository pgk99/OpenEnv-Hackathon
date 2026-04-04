# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from uuid import uuid4
import random

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import AviationAgentAction, AviationAgentObservation
except ImportError:
    from models import AviationAgentAction, AviationAgentObservation


class AviationAgentEnvironment(Environment):
    # Enable concurrent WebSocket sessions.
    # Set to True if your environment isolates state between instances.
    # When True, multiple WebSocket clients can connect simultaneously, each
    # getting their own environment instance (when using factory mode in app.py).
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0

    def reset(self) -> AviationAgentObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1

        self.tasks = [{"instruction": "Indigo 302, descend to FL180"},
                      {"instruction": "Climb to FL300 and maintain heading 270"},
                      {"instruction": "Indigo 101, maintain heading 180 and descend to FL200"}]

        self.current_task = random.choice(self.tasks)

        return AviationAgentObservation(
            echoed_message=self.current_task["instruction"],
            message_length=0,
            done=False,
            reward=0.0,
        )

    def step(self, action: AviationAgentAction) -> AviationAgentObservation:  # type: ignore[override]
        self._state.step_count += 1

        response = action.message
        instruction = self.current_task["instruction"]

        altitude_correct = any(x in response for x in ["FL180", "FL200", "FL300"] and "FL" in instruction)
        heading_correct = any(x in response for x in ["180","270"])
        callsign_present = "Indigo" in response

        done = True

        return AviationAgentObservation(
            echoed_message=instruction,
            message_length=len(response),
            done=done,
            reward=score,
            metadata={"instruction": instruction,
            "response": response,
            "altitude_correct": altitude_correct,
            "heading_correct": heading_correct,
            "callsign_present": callsign_present,
            "score": score,},
        )

    @property
    def state(self) -> State:
        return self._state
