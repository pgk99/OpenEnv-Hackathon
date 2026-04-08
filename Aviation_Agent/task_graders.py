"""
Task graders for Aviation Agent Environment.

Each grader evaluates agent performance on a specific task with
deterministic scoring from 0.0 to 1.0.
"""

from typing import Dict, Any, List
from Aviation_Agent.server.Aviation_Agent_environment import AviationAgentEnvironment


class TaskGrader:
    """Base class for task graders."""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.env = AviationAgentEnvironment(task_id=task_id)
    
    def grade(self, agent_responses: List[str]) -> Dict[str, Any]:
        """
        Grade agent performance on the task.
        
        Args:
            agent_responses: List of agent responses (one per step)
            
        Returns:
            Dictionary with grading results including final score (0.0-1.0)
        """
        raise NotImplementedError


class Task1Grader(TaskGrader):
    """
    Grader for Task 1 (Easy): Single altitude change.
    
    Success criteria:
    - Callsign acknowledged: 0.33 points
    - Altitude read back correctly: 0.33 points
    - Action (descend) acknowledged: 0.34 points
    
    Total: 1.0 for perfect response
    """
    
    def __init__(self):
        super().__init__("task_1_easy")
    
    def grade(self, agent_responses: List[str]) -> Dict[str, Any]:
        obs = self.env.reset()
        
        total_reward = 0.0
        final_score = 0.0
        
        for response in agent_responses:
            from Aviation_Agent.models import AviationAgentAction
            action = AviationAgentAction(message=response)
            obs = self.env.step(action)
            total_reward += obs.reward
            
            if obs.metadata:
                final_score = obs.metadata.get("score", 0.0)
            
            if obs.done:
                break
        
        return {
            "task_id": self.task_id,
            "difficulty": "easy",
            "final_score": final_score,
            "total_reward": total_reward,
            "success": final_score >= 0.9,
            "grading_details": obs.metadata.get("grading_details", {}) if obs.metadata else {}
        }


class Task2Grader(TaskGrader):
    """
    Grader for Task 2 (Medium): Heading and altitude change.
    
    Success criteria:
    - Callsign acknowledged: 0.20 points
    - Heading read back correctly: 0.20 points
    - Altitude read back correctly: 0.20 points
    - Turn direction acknowledged: 0.20 points
    - Action (descend) acknowledged: 0.20 points
    
    Total: 1.0 for perfect response
    """
    
    def __init__(self):
        super().__init__("task_2_medium")
    
    def grade(self, agent_responses: List[str]) -> Dict[str, Any]:
        obs = self.env.reset()
        
        total_reward = 0.0
        final_score = 0.0
        
        for response in agent_responses:
            from Aviation_Agent.models import AviationAgentAction
            action = AviationAgentAction(message=response)
            obs = self.env.step(action)
            total_reward += obs.reward
            
            if obs.metadata:
                final_score = obs.metadata.get("score", 0.0)
            
            if obs.done:
                break
        
        return {
            "task_id": self.task_id,
            "difficulty": "medium",
            "final_score": final_score,
            "total_reward": total_reward,
            "success": final_score >= 0.9,
            "grading_details": obs.metadata.get("grading_details", {}) if obs.metadata else {}
        }


class Task3Grader(TaskGrader):
    """
    Grader for Task 3 (Hard): Traffic alert with heading and altitude change.
    
    Success criteria:
    - Callsign acknowledged: 0.167 points
    - Traffic acknowledged: 0.167 points
    - Heading read back correctly: 0.167 points
    - Altitude read back correctly: 0.167 points
    - Turn direction acknowledged: 0.166 points
    - Action (climb) acknowledged: 0.166 points
    
    Total: 1.0 for perfect response
    """
    
    def __init__(self):
        super().__init__("task_3_hard")
    
    def grade(self, agent_responses: List[str]) -> Dict[str, Any]:
        obs = self.env.reset()
        
        total_reward = 0.0
        final_score = 0.0
        
        for response in agent_responses:
            from Aviation_Agent.models import AviationAgentAction
            action = AviationAgentAction(message=response)
            obs = self.env.step(action)
            total_reward += obs.reward
            
            if obs.metadata:
                final_score = obs.metadata.get("score", 0.0)
            
            if obs.done:
                break
        
        return {
            "task_id": self.task_id,
            "difficulty": "hard",
            "final_score": final_score,
            "total_reward": total_reward,
            "success": final_score >= 0.9,
            "grading_details": obs.metadata.get("grading_details", {}) if obs.metadata else {}
        }


def get_grader(task_id: str) -> TaskGrader:
    """Get the appropriate grader for a task ID."""
    graders = {
        "task_1_easy": Task1Grader,
        "task_2_medium": Task2Grader,
        "task_3_hard": Task3Grader,
    }
    
    if task_id not in graders:
        raise ValueError(f"Unknown task_id: {task_id}")
    
    return graders[task_id]()


# Example usage
if __name__ == "__main__":
    # Test grader with sample responses
    grader = Task1Grader()
    
    # Good response
    result = grader.grade(["Descend and maintain flight level 180, Speedbird 247"])
    print(f"Good response score: {result['final_score']:.2f}")
    
    # Poor response
    result = grader.grade(["Roger"])
    print(f"Poor response score: {result['final_score']:.2f}")
