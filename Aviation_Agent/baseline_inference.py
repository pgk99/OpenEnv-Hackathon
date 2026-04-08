#!/usr/bin/env python3
"""
Baseline inference script for Aviation Agent Environment.

Uses OpenAI API to run a model against the environment and produce
reproducible baseline scores on all 3 tasks.

Usage:
    export OPENAI_API_KEY=your_key_here
    python baseline_inference.py
"""

import os
import sys
from typing import List, Dict, Any
from openai import OpenAI

try:
    from Aviation_Agent.client import AviationAgentEnv
    from Aviation_Agent.models import AviationAgentAction
except ImportError:
    from client import AviationAgentEnv
    from models import AviationAgentAction


def run_task(client: OpenAI, env: AviationAgentEnv, task_id: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Run a single task with the OpenAI model.
    
    Args:
        client: OpenAI client
        env: Aviation environment
        task_id: Task identifier
        model: OpenAI model to use
        
    Returns:
        Dictionary with task results
    """
    # Reset environment for this task
    obs = env.reset()
    
    system_prompt = """You are a professional airline pilot communicating with Air Traffic Control (ATC).
You must respond to ATC instructions using proper aviation phraseology.

Key rules:
1. Always acknowledge with your callsign
2. Read back all altitude, heading, and speed instructions
3. Use standard aviation terminology
4. Be concise and clear

Example:
ATC: "Speedbird 247, descend and maintain flight level 180."
Pilot: "Descend and maintain flight level 180, Speedbird 247."
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"ATC Instruction: {obs.atc_instruction}\n\nRespond as the pilot:"}
    ]
    
    total_reward = 0.0
    step_count = 0
    done = False
    final_score = 0.0
    
    while not done:
        # Get model response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,  # Deterministic for reproducibility
            max_tokens=150
        )
        
        pilot_response = response.choices[0].message.content.strip()
        
        # Take step in environment
        action = AviationAgentAction(message=pilot_response)
        obs = env.step(action)
        
        total_reward += obs.reward
        step_count += 1
        done = obs.done
        
        if obs.metadata:
            final_score = obs.metadata.get("score", 0.0)
        
        # Add to conversation history for potential multi-turn
        messages.append({"role": "assistant", "content": pilot_response})
        if not done:
            messages.append({"role": "user", "content": "Try again with a more complete response:"})
    
    return {
        "task_id": task_id,
        "final_score": final_score,
        "total_reward": total_reward,
        "steps_taken": step_count,
        "success": final_score >= 0.9
    }


def main():
    """Run baseline inference on all tasks."""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Model to use
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    print(f"Running baseline inference with model: {model}")
    print("=" * 60)
    
    # Task IDs to test
    task_ids = ["task_1_easy", "task_2_medium", "task_3_hard"]
    
    results = []
    
    # Run each task
    for task_id in task_ids:
        print(f"\nRunning {task_id}...")
        
        # Connect to environment (assumes server is running)
        base_url = os.getenv("AVIATION_ENV_URL", "http://localhost:8000")
        
        try:
            with AviationAgentEnv(base_url=base_url) as env:
                # Override task selection
                env._task_id = task_id
                
                result = run_task(client, env, task_id, model)
                results.append(result)
                
                print(f"  Score: {result['final_score']:.2f}")
                print(f"  Reward: {result['total_reward']:.2f}")
                print(f"  Steps: {result['steps_taken']}")
                print(f"  Success: {'✓' if result['success'] else '✗'}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
            print(f"  Make sure the server is running at {base_url}")
            results.append({
                "task_id": task_id,
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("BASELINE RESULTS SUMMARY")
    print("=" * 60)
    
    successful_tasks = [r for r in results if r.get("success", False)]
    avg_score = sum(r.get("final_score", 0) for r in results) / len(results) if results else 0
    avg_reward = sum(r.get("total_reward", 0) for r in results) / len(results) if results else 0
    
    print(f"Tasks completed: {len(successful_tasks)}/{len(task_ids)}")
    print(f"Average score: {avg_score:.2f}")
    print(f"Average reward: {avg_reward:.2f}")
    print()
    
    for result in results:
        if "error" not in result:
            print(f"{result['task_id']}: {result['final_score']:.2f} ({'✓' if result['success'] else '✗'})")
        else:
            print(f"{result['task_id']}: ERROR - {result['error']}")


if __name__ == "__main__":
    main()
