#!/usr/bin/env python3
"""
Test script for Aviation Agent Environment.

Verifies that the environment works correctly without needing the server.
"""

from Aviation_Agent.server.Aviation_Agent_environment import AviationAgentEnvironment
from Aviation_Agent.models import AviationAgentAction


def test_task(task_id: str, response: str):
    """Test a single task with a given response."""
    print(f"\n{'='*60}")
    print(f"Testing {task_id}")
    print(f"{'='*60}")
    
    env = AviationAgentEnvironment(task_id=task_id)
    obs = env.reset()
    
    print(f"ATC Instruction: {obs.atc_instruction}")
    print(f"Task: {obs.task_description}")
    print(f"\nPilot Response: {response}")
    
    action = AviationAgentAction(message=response)
    obs = env.step(action)
    
    print(f"\nResults:")
    print(f"  Score: {obs.metadata['score']:.2f}")
    print(f"  Reward: {obs.reward:.2f}")
    print(f"  Done: {obs.done}")
    print(f"  Success: {'✓' if obs.metadata['score'] >= 0.9 else '✗'}")
    
    print(f"\nGrading Details:")
    for element, details in obs.metadata['grading_details'].items():
        status = "✓" if details['found'] else "✗"
        print(f"  {status} {element}: {details['expected_phrases']}")
    
    return obs.metadata['score']


def main():
    """Run tests on all tasks."""
    print("Aviation Agent Environment - Test Suite")
    print("="*60)
    
    # Test Task 1 - Good response
    score1 = test_task(
        "task_1_easy",
        "Descend and maintain flight level 180, Speedbird 247"
    )
    
    # Test Task 1 - Poor response
    test_task(
        "task_1_easy",
        "Roger"
    )
    
    # Test Task 2 - Good response
    score2 = test_task(
        "task_2_medium",
        "Turn left heading 090, descend and maintain 5000 feet, United 512"
    )
    
    # Test Task 3 - Good response
    score3 = test_task(
        "task_3_hard",
        "Traffic in sight, turn right heading 270, climb and maintain 10000 feet, Delta 1823"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Task 1 (Easy): {score1:.2f} {'✓' if score1 >= 0.9 else '✗'}")
    print(f"Task 2 (Medium): {score2:.2f} {'✓' if score2 >= 0.9 else '✗'}")
    print(f"Task 3 (Hard): {score3:.2f} {'✓' if score3 >= 0.9 else '✗'}")
    
    avg_score = (score1 + score2 + score3) / 3
    print(f"\nAverage Score: {avg_score:.2f}")
    
    if avg_score >= 0.9:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")


if __name__ == "__main__":
    main()
