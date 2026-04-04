#!/usr/bin/env python3
"""
Inference script for Aviation Agent Environment - Hackathon Submission.

This script follows the required format with structured stdout logs:
[START], [STEP], and [END] format for evaluation scoring.

Required environment variables:
- API_BASE_URL: The API endpoint for the LLM
- MODEL_NAME: The model identifier to use for inference
- HF_TOKEN: Your Hugging Face / API key (or OPENAI_API_KEY)
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List
from openai import OpenAI

# Import environment components
try:
    from Aviation_Agent.client import AviationAgentEnv
    from Aviation_Agent.models import AviationAgentAction
except ImportError:
    # If running from different location, adjust path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Aviation_Agent'))
    from client import AviationAgentEnv  # type: ignore
    from models import AviationAgentAction  # type: ignore


def get_llm_client() -> OpenAI:
    """
    Initialize OpenAI client using environment variables.
    
    Required environment variables:
    - API_BASE_URL: API endpoint (optional, defaults to OpenAI)
    - MODEL_NAME: Model identifier
    - HF_TOKEN or OPENAI_API_KEY: API key
    """
    api_base = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("HF_TOKEN or OPENAI_API_KEY environment variable must be set")
    
    return OpenAI(
        api_key=api_key,
        base_url=api_base if api_base != "https://api.openai.com/v1" else None
    )


def get_model_name() -> str:
    """Get model name from environment variable."""
    model = os.getenv("MODEL_NAME", "gpt-4o-mini")
    return model


async def run_task_async(
    client: OpenAI,
    env: AviationAgentEnv,
    task_id: str,
    model: str,
    max_steps: int = 4
) -> Dict[str, Any]:
    """
    Run a single task with the LLM (async version).
    
    Args:
        client: OpenAI client
        env: Aviation environment
        task_id: Task identifier
        model: Model name
        max_steps: Maximum steps per episode
        
    Returns:
        Dictionary with task results
    """
    # Reset environment
    result = await env.reset()
    obs = result.observation
    
    # System prompt for aviation communication
    system_prompt = """You are a professional airline pilot communicating with Air Traffic Control (ATC).
You must respond to ATC instructions using proper aviation phraseology.

Key rules:
1. Always acknowledge with your callsign
2. Read back all altitude, heading, and speed instructions
3. Use standard aviation terminology (e.g., "flight level", "descend and maintain")
4. Be concise and clear
5. For traffic alerts, acknowledge with "traffic in sight" or "looking for traffic"

Example responses:
ATC: "Speedbird 247, descend and maintain flight level 180."
Pilot: "Descend and maintain flight level 180, Speedbird 247."

ATC: "United 512, turn left heading 090, descend and maintain 5000 feet."
Pilot: "Turn left heading 090, descend and maintain 5000 feet, United 512."

ATC: "Delta 1823, traffic alert. Traffic 2 o'clock, 3 miles. Turn right heading 270, climb and maintain 10000 feet."
Pilot: "Traffic in sight, turn right heading 270, climb and maintain 10000 feet, Delta 1823."
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"ATC Instruction: {obs.atc_instruction}\n\nRespond as the pilot:"}
    ]
    
    total_reward = 0.0
    step_count = 0
    done = False
    final_score = 0.0
    steps_data = []
    
    while not done and step_count < max_steps:
        # Get model response
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,  # Deterministic for reproducibility
                max_tokens=150
            )
            
            pilot_response = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] LLM API call failed: {e}", file=sys.stderr)
            pilot_response = "Unable to respond"
        
        # Take step in environment
        action = AviationAgentAction(message=pilot_response)
        result = await env.step(action)
        obs = result.observation
        
        step_count += 1
        total_reward += result.reward
        done = result.done
        
        # Try to get score from metadata, otherwise estimate from reward
        if obs.metadata and 'score' in obs.metadata:
            final_score = obs.metadata.get("score", 0.0)
        else:
            # Fallback: estimate score from reward
            # Reward of ~1.3 = perfect (score 1.0 + 0.3 bonus)
            # Reward of ~1.0 = good (score 1.0)
            # Reward < 1.0 = partial
            if result.reward >= 1.2:
                final_score = 1.0
            elif result.reward >= 0.9:
                final_score = min(1.0, result.reward)
            else:
                final_score = max(0.0, result.reward)
        
        # Log step in required format
        step_data = {
            "step": step_count,
            "action": pilot_response,
            "reward": float(result.reward),
            "score": float(final_score),
            "done": done
        }
        steps_data.append(step_data)
        
        # Print structured log
        print(json.dumps({
            "type": "STEP",
            "task_id": task_id,
            "step": step_count,
            "action": pilot_response,
            "reward": float(result.reward),
            "score": float(final_score),
            "done": done
        }))
        
        # Add to conversation history for potential multi-turn
        messages.append({"role": "assistant", "content": pilot_response})
        if not done and step_count < max_steps:
            messages.append({
                "role": "user",
                "content": "Try again with a more complete response that includes all required elements:"
            })
    
    return {
        "task_id": task_id,
        "final_score": float(final_score),
        "total_reward": float(total_reward),
        "steps_taken": step_count,
        "success": final_score >= 0.9,
        "steps": steps_data
    }


async def main_async():
    """Main inference script following required format (async version)."""
    
    # Print START log
    print(json.dumps({
        "type": "START",
        "environment": "Aviation_Agent",
        "model": get_model_name(),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }))
    
    try:
        # Initialize LLM client
        client = get_llm_client()
        model = get_model_name()
        
        print(f"[INFO] Using model: {model}", file=sys.stderr)
        print(f"[INFO] API base: {os.getenv('API_BASE_URL', 'default')}", file=sys.stderr)
        
        # Environment URL
        base_url = os.getenv("AVIATION_ENV_URL", "http://localhost:8000")
        print(f"[INFO] Environment URL: {base_url}", file=sys.stderr)
        
        # Task IDs to test
        task_ids = ["task_1_easy", "task_2_medium", "task_3_hard"]
        
        results = []
        
        # Run each task
        for i, task_id in enumerate(task_ids):
            print(f"[INFO] Running task {i+1}/3...", file=sys.stderr)
            
            try:
                # Connect to environment (async)
                # Note: Server will randomly select a task since we can't specify task_id through client
                async with AviationAgentEnv(base_url=base_url) as env:
                    result = await run_task_async(client, env, f"task_{i+1}", model)
                    results.append(result)
                    
                    print(f"[INFO] Task {i+1} completed: score={result['final_score']:.2f}, reward={result['total_reward']:.2f}", file=sys.stderr)
            
            except Exception as e:
                print(f"[ERROR] Task {task_id} failed: {e}", file=sys.stderr)
                results.append({
                    "task_id": task_id,
                    "error": str(e),
                    "final_score": 0.0,
                    "total_reward": 0.0,
                    "steps_taken": 0,
                    "success": False
                })
        
        # Calculate summary statistics
        successful_tasks = [r for r in results if r.get("success", False)]
        avg_score = sum(r.get("final_score", 0) for r in results) / len(results) if results else 0
        avg_reward = sum(r.get("total_reward", 0) for r in results) / len(results) if results else 0
        
        # Print END log with summary
        print(json.dumps({
            "type": "END",
            "total_tasks": len(task_ids),
            "successful_tasks": len(successful_tasks),
            "average_score": float(avg_score),
            "average_reward": float(avg_reward),
            "results": results,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }))
        
        print(f"\n[INFO] Inference completed successfully", file=sys.stderr)
        print(f"[INFO] Tasks completed: {len(successful_tasks)}/{len(task_ids)}", file=sys.stderr)
        print(f"[INFO] Average score: {avg_score:.2f}", file=sys.stderr)
        print(f"[INFO] Average reward: {avg_reward:.2f}", file=sys.stderr)
        
        # Exit with success if at least one task succeeded
        sys.exit(0 if len(successful_tasks) > 0 else 1)
    
    except Exception as e:
        # Print error in END log
        print(json.dumps({
            "type": "END",
            "error": str(e),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }))
        print(f"[ERROR] Inference failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Entry point that runs async main."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
