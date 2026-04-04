#!/usr/bin/env python3
"""
Verification script for hackathon submission.

Checks all requirements are met before submission.
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check(condition, message):
    """Print check result."""
    if condition:
        print(f"{GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"{RED}✗{RESET} {message}")
        return False

def warning(message):
    """Print warning."""
    print(f"{YELLOW}⚠{RESET} {message}")

def section(title):
    """Print section header."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{title}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

def main():
    """Run all verification checks."""
    print(f"{BOLD}Aviation Agent Environment - Submission Verification{RESET}")
    
    all_passed = True
    
    # Check 1: File Structure
    section("1. File Structure")
    
    required_files = [
        "Aviation_Agent/models.py",
        "Aviation_Agent/client.py",
        "Aviation_Agent/openenv.yaml",
        "Aviation_Agent/server/Aviation_Agent_environment.py",
        "Aviation_Agent/server/app.py",
        "Aviation_Agent/server/Dockerfile",
        "Aviation_Agent/server/requirements.txt",
        "Aviation_Agent/task_graders.py",
        "Aviation_Agent/baseline_inference.py",
        "Aviation_Agent/test_environment.py",
        "Aviation_Agent/README.md",
        "HACKATHON_SUBMISSION.md",
    ]
    
    for file in required_files:
        exists = Path(file).exists()
        all_passed &= check(exists, f"File exists: {file}")
    
    # Check 2: OpenEnv Compliance
    section("2. OpenEnv Compliance")
    
    try:
        # Check models
        from Aviation_Agent.models import AviationAgentAction, AviationAgentObservation
        all_passed &= check(True, "Action model imports successfully")
        all_passed &= check(True, "Observation model imports successfully")
        
        # Check action has required field
        all_passed &= check(
            hasattr(AviationAgentAction, 'message'),
            "Action has 'message' field"
        )
        
        # Check observation has required fields
        obs_fields = ['atc_instruction', 'task_description', 'step_count']
        for field in obs_fields:
            all_passed &= check(
                hasattr(AviationAgentObservation, field),
                f"Observation has '{field}' field"
            )
        
    except Exception as e:
        all_passed &= check(False, f"Model import failed: {e}")
    
    try:
        # Check environment
        from Aviation_Agent.server.Aviation_Agent_environment import AviationAgentEnvironment
        all_passed &= check(True, "Environment imports successfully")
        
        # Check environment has required methods
        env = AviationAgentEnvironment()
        all_passed &= check(hasattr(env, 'reset'), "Environment has reset() method")
        all_passed &= check(hasattr(env, 'step'), "Environment has step() method")
        all_passed &= check(hasattr(env, 'state'), "Environment has state property")
        
    except Exception as e:
        all_passed &= check(False, f"Environment import failed: {e}")
    
    # Check 3: Tasks and Graders
    section("3. Tasks and Graders")
    
    try:
        from Aviation_Agent.server.Aviation_Agent_environment import AviationAgentEnvironment
        
        env = AviationAgentEnvironment()
        all_passed &= check(
            len(env.TASKS) >= 3,
            f"Environment has 3+ tasks (found {len(env.TASKS)})"
        )
        
        # Check task difficulties
        difficulties = [task['difficulty'] for task in env.TASKS]
        all_passed &= check(
            'easy' in difficulties,
            "Has easy task"
        )
        all_passed &= check(
            'medium' in difficulties,
            "Has medium task"
        )
        all_passed &= check(
            'hard' in difficulties,
            "Has hard task"
        )
        
    except Exception as e:
        all_passed &= check(False, f"Task check failed: {e}")
    
    try:
        from Aviation_Agent.task_graders import Task1Grader, Task2Grader, Task3Grader
        all_passed &= check(True, "Task graders import successfully")
        
        # Test a grader
        grader = Task1Grader()
        result = grader.grade(["Descend and maintain flight level 180, Speedbird 247"])
        all_passed &= check(
            0.0 <= result['final_score'] <= 1.0,
            f"Grader returns score in range [0.0, 1.0] (got {result['final_score']:.2f})"
        )
        
    except Exception as e:
        all_passed &= check(False, f"Grader check failed: {e}")
    
    # Check 4: Reward Function
    section("4. Reward Function")
    
    try:
        from Aviation_Agent.server.Aviation_Agent_environment import AviationAgentEnvironment
        from Aviation_Agent.models import AviationAgentAction
        
        env = AviationAgentEnvironment(task_id="task_1_easy")
        obs = env.reset()
        
        # Test step
        action = AviationAgentAction(message="Descend FL180, Speedbird 247")
        obs = env.step(action)
        
        all_passed &= check(
            hasattr(obs, 'reward'),
            "Observation has reward"
        )
        all_passed &= check(
            isinstance(obs.reward, (int, float)),
            f"Reward is numeric (type: {type(obs.reward).__name__})"
        )
        
        # Check reward function exists
        all_passed &= check(
            hasattr(env, '_calculate_reward'),
            "Environment has _calculate_reward() method"
        )
        
    except Exception as e:
        all_passed &= check(False, f"Reward function check failed: {e}")
    
    # Check 5: Baseline Script
    section("5. Baseline Inference Script")
    
    baseline_path = Path("Aviation_Agent/baseline_inference.py")
    if baseline_path.exists():
        content = baseline_path.read_text()
        all_passed &= check(
            "OpenAI" in content or "openai" in content,
            "Baseline uses OpenAI API"
        )
        all_passed &= check(
            "OPENAI_API_KEY" in content,
            "Baseline reads OPENAI_API_KEY from environment"
        )
        all_passed &= check(
            "task_1_easy" in content and "task_2_medium" in content and "task_3_hard" in content,
            "Baseline runs all 3 tasks"
        )
    else:
        all_passed &= check(False, "Baseline script not found")
    
    # Check 6: Docker
    section("6. Docker Configuration")
    
    dockerfile_path = Path("Aviation_Agent/server/Dockerfile")
    all_passed &= check(dockerfile_path.exists(), "Dockerfile exists")
    
    if dockerfile_path.exists():
        content = dockerfile_path.read_text()
        all_passed &= check(
            "FROM" in content,
            "Dockerfile has FROM instruction"
        )
        all_passed &= check(
            "8000" in content,
            "Dockerfile exposes port 8000"
        )
        all_passed &= check(
            "HEALTHCHECK" in content,
            "Dockerfile has health check"
        )
    
    dockerignore_path = Path("Aviation_Agent/.dockerignore")
    all_passed &= check(dockerignore_path.exists(), ".dockerignore exists")
    
    # Check 7: Documentation
    section("7. Documentation")
    
    readme_path = Path("Aviation_Agent/README.md")
    if readme_path.exists():
        content = readme_path.read_text()
        
        required_sections = [
            ("environment description", any(x in content.lower() for x in ["air traffic control", "atc", "aviation"])),
            ("action space", "AviationAgentAction" in content),
            ("observation space", "AviationAgentObservation" in content),
            ("task descriptions", "Task 1" in content or "task_1" in content),
            ("difficulty levels", "easy" in content.lower() and "medium" in content.lower() and "hard" in content.lower()),
            ("setup instructions", "install" in content.lower() or "setup" in content.lower()),
            ("usage instructions", "usage" in content.lower() or "quick start" in content.lower()),
            ("baseline scores", "baseline" in content.lower()),
        ]
        
        for section_name, condition in required_sections:
            all_passed &= check(condition, f"README has {section_name}")
    else:
        all_passed &= check(False, "README.md not found")
    
    # Check 8: HF Spaces Configuration
    section("8. Hugging Face Spaces Configuration")
    
    openenv_yaml = Path("Aviation_Agent/openenv.yaml")
    if openenv_yaml.exists():
        content = openenv_yaml.read_text()
        all_passed &= check(
            "type: space" in content,
            "openenv.yaml has type: space"
        )
        all_passed &= check(
            "sdk: docker" in content or "runtime: fastapi" in content,
            "openenv.yaml has runtime configuration"
        )
        all_passed &= check(
            "port: 8000" in content,
            "openenv.yaml specifies port 8000"
        )
    else:
        all_passed &= check(False, "openenv.yaml not found")
    
    if readme_path.exists():
        content = readme_path.read_text()
        all_passed &= check(
            content.startswith("---"),
            "README has YAML frontmatter for HF Spaces"
        )
        all_passed &= check(
            "sdk: docker" in content,
            "README frontmatter specifies Docker SDK"
        )
        all_passed &= check(
            "openenv" in content.lower(),
            "README is tagged with 'openenv'"
        )
    
    # Final Summary
    section("Summary")
    
    if all_passed:
        print(f"\n{GREEN}{BOLD}✓ All checks passed! Ready for submission.{RESET}\n")
        print("Next steps:")
        print("1. Test locally: python Aviation_Agent/test_environment.py")
        print("2. Build Docker: docker build -t aviation-agent-env:latest -f Aviation_Agent/server/Dockerfile Aviation_Agent")
        print("3. Test Docker: docker run -p 8000:8000 aviation-agent-env:latest")
        print("4. Deploy to HF: cd Aviation_Agent && openenv push --repo-id your-username/aviation-agent")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ Some checks failed. Please fix the issues above.{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
