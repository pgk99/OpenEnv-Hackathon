---
title: Aviation Agent Environment Server
emoji: ✈️
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - aviation
  - atc
  - reinforcement-learning
  - real-world-task
---

# Aviation Agent Environment

An OpenEnv reinforcement learning environment that trains AI agents to master Air Traffic Control (ATC) radio communication. The system enables agents to learn from communication patterns, practice in simulated flight scenarios, and receive automated evaluation based on aviation communication standards.

## Real-World Task Simulation

This environment simulates a critical real-world task: pilot-ATC radio communication. Professional pilots must:
- Acknowledge instructions with their callsign
- Read back altitude, heading, and speed clearances
- Use standard aviation phraseology (ICAO standards)
- Respond to traffic alerts appropriately

This is not a game or toy - it's a training environment based on actual aviation communication that happens thousands of times daily worldwide.

## Training Philosophy

### Learning from Communication Patterns

The environment teaches AI agents proper communication through:

1. **Pattern Recognition**: Agents learn to identify required elements in ATC instructions
2. **Response Generation**: Agents practice generating standards-compliant responses
3. **Feedback Loop**: Immediate rewards signal correctness and adherence to standards
4. **Progressive Difficulty**: Agents master simple scenarios before advancing to complex ones

### Automated Evaluation

Every response is evaluated against aviation communication standards:
- **Callsign usage**: Required for all communications
- **Read-back accuracy**: Critical for safety (altitude, heading, speed)
- **Phraseology compliance**: Standard terminology (e.g., "flight level", "descend and maintain")
- **Completeness**: All instruction elements must be acknowledged

Scores range from 0.0 (incorrect) to 1.0 (perfect), providing clear learning signals for RL algorithms.

## Quick Start

The simplest way to use the Aviation Agent environment is through the `AviationAgentEnv` class:

```python
from Aviation_Agent import AviationAgentAction, AviationAgentEnv

try:
    # Create environment from Docker image
    env = AviationAgentEnv.from_docker_image("Aviation_Agent-env:latest")

    # Reset to get initial ATC instruction
    result = env.reset()
    print(f"ATC: {result.observation.atc_instruction}")
    print(f"Task: {result.observation.task_description}")

    # Respond as pilot
    pilot_response = "Descend and maintain flight level 180, Speedbird 247"
    result = env.step(AviationAgentAction(message=pilot_response))
    
    print(f"Pilot: {pilot_response}")
    print(f"Score: {result.observation.metadata['score']:.2f}")
    print(f"Reward: {result.reward:.2f}")
    print(f"Done: {result.done}")

finally:
    # Always clean up
    env.close()
```

## Three Tasks: Easy → Medium → Hard

The environment provides progressive training scenarios that build communication skills:

### Task 1 (Easy): Single Altitude Change
**Training Focus**: Basic read-back and acknowledgment

**ATC Instruction**: "Speedbird 247, descend and maintain flight level 180."

**Learning Objectives**:
- Recognize callsign
- Identify altitude instruction
- Acknowledge action (descend)

**Required Elements**:
- Callsign acknowledgment
- Altitude read back
- Action acknowledgment

**Example Perfect Response**: "Descend and maintain flight level 180, Speedbird 247"

**Success Rate**: High (agents typically master this quickly)

---

### Task 2 (Medium): Heading and Altitude Change
**Training Focus**: Multi-element instruction handling

**ATC Instruction**: "United 512, turn left heading 090, descend and maintain 5000 feet."

**Learning Objectives**:
- Process multiple instructions simultaneously
- Maintain proper sequence
- Use correct directional terminology

**Required Elements**:
- Callsign acknowledgment
- Heading read back
- Turn direction
- Altitude read back
- Action acknowledgment

**Example Perfect Response**: "Turn left heading 090, descend and maintain 5000 feet, United 512"

**Success Rate**: Medium (requires understanding of compound instructions)

---

### Task 3 (Hard): Traffic Alert with Maneuver
**Training Focus**: Safety-critical communication under pressure

**ATC Instruction**: "Delta 1823, traffic alert. Traffic 2 o'clock, 3 miles, opposite direction, altitude indicates 8000 feet. Turn right heading 270, climb and maintain 10000 feet."

**Learning Objectives**:
- Acknowledge safety-critical information (traffic)
- Process complex multi-part instructions
- Respond with appropriate urgency
- Maintain communication standards under stress

**Required Elements**:
- Callsign acknowledgment
- Traffic acknowledgment
- Heading read back
- Turn direction
- Altitude read back
- Action acknowledgment

**Example Perfect Response**: "Traffic in sight, turn right heading 270, climb and maintain 10000 feet, Delta 1823"

**Success Rate**: Low-Medium (most challenging scenario, tests full competency)

## Grading System

Each task has a programmatic grader that evaluates adherence to aviation communication standards, scoring from 0.0 to 1.0:

### Evaluation Criteria

**Task 1 (Easy)**: 3 required elements, each worth ~0.33 points
- Proper callsign usage
- Accurate altitude read-back
- Action acknowledgment

**Task 2 (Medium)**: 5 required elements, each worth 0.20 points
- Proper callsign usage
- Accurate heading read-back
- Correct turn direction
- Accurate altitude read-back
- Action acknowledgment

**Task 3 (Hard)**: 6 required elements, each worth ~0.167 points
- Proper callsign usage
- Traffic acknowledgment (safety-critical)
- Accurate heading read-back
- Correct turn direction
- Accurate altitude read-back
- Action acknowledgment

### Success Threshold

**0.9 (90%)** - Agents must achieve 90% or higher to pass a task

This threshold ensures:
- High communication accuracy (safety requirement)
- Proper phraseology usage
- Complete information transfer
- Standards compliance

### Grading Process

Graders check for:
1. **Presence of required phraseology** - Standard aviation terms
2. **Correct values** - Accurate altitudes, headings, speeds
3. **Proper acknowledgments** - Callsign and action confirmation
4. **Completeness** - No missing elements

**Deterministic**: Same response always gets same score (reproducible for research)

## Reward Function

The reward function provides trajectory-level learning signals, not just binary end-of-episode rewards. This enables agents to learn from partial progress and understand what makes a good response.

### Design Principles

1. **Reward Partial Progress**: Each correct element contributes to the score
2. **Penalize Inefficiency**: Encourage getting it right the first time
3. **Provide Clear Signals**: Agents understand what they did right/wrong
4. **Encourage Learning**: Reward improvement over episodes

### Reward Components

- **Base reward**: Score from grader (0.0-1.0) - Reflects communication accuracy
- **Step penalty**: -0.05 per additional step - Penalizes inefficiency
- **First-attempt bonus**: +0.3 for perfect score on first try - Rewards mastery
- **Max steps penalty**: -0.2 if max steps reached without success - Prevents poor behavior

### Learning Trajectories

**Perfect First Response** (Optimal):
```
Step 1: score=1.0, reward=1.3 → Agent learns: "This is correct"
```

**Good Second Attempt** (Learning):
```
Step 1: score=0.6, reward=0.6
Step 2: score=1.0, reward=0.95 → Agent learns: "Improved, but first attempt is better"
```

**Poor Performance** (Needs training):
```
Step 1: score=0.3, reward=0.3
Step 2: score=0.5, reward=0.45
Step 3: score=0.6, reward=0.4 → Agent learns: "Need more required elements"
```

This reward structure helps RL algorithms (PPO, SAC, etc.) converge faster by providing rich feedback signals throughout the learning process.

## Baseline Inference Script

The project includes `inference.py` in the root directory that follows the hackathon's required format with structured logging.

### Required Environment Variables

```bash
# Option 1: OpenAI API
export OPENAI_API_KEY=your_key_here
export MODEL_NAME=gpt-4o-mini
export API_BASE_URL=https://api.openai.com/v1

# Option 2: Hugging Face (Mistral-7B-Instruct recommended)
export HF_TOKEN=your_hf_token_here
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
export API_BASE_URL=https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2/v1
```

### Running Inference

```bash
# Start the environment server
uvicorn Aviation_Agent.server.app:app --host 0.0.0.0 --port 8000 &

# Run inference (from project root)
python inference.py
```

### Structured Output Format

The script emits structured JSON logs:

```json
{"type": "START", "environment": "Aviation_Agent", "model": "gpt-4o-mini", ...}
{"type": "STEP", "task_id": "task_1_easy", "step": 1, "action": "...", "reward": 1.3, "score": 1.0, "done": true}
{"type": "STEP", "task_id": "task_2_medium", "step": 1, "action": "...", "reward": 1.25, "score": 1.0, "done": true}
{"type": "STEP", "task_id": "task_3_hard", "step": 1, "action": "...", "reward": 1.25, "score": 1.0, "done": true}
{"type": "END", "total_tasks": 3, "successful_tasks": 3, "average_score": 1.0, "average_reward": 1.27, ...}
```

### Alternative: Legacy Baseline Script

For detailed output, use the legacy baseline:

```bash
# Install dependencies
pip install -r Aviation_Agent/requirements-baseline.txt

# Set API key
export OPENAI_API_KEY=your_key_here

# Start environment server
uvicorn Aviation_Agent.server.app:app --host 0.0.0.0 --port 8000 &

# Run baseline inference
python Aviation_Agent/baseline_inference.py
```

Expected output:
```
Running baseline inference with model: gpt-4o-mini
============================================================

Running task_1_easy...
  Score: 1.00
  Reward: 1.25
  Steps: 1
  Success: ✓

Running task_2_medium...
  Score: 1.00
  Reward: 1.25
  Steps: 1
  Success: ✓

Running task_3_hard...
  Score: 0.83
  Reward: 0.73
  Steps: 2
  Success: ✗

============================================================
BASELINE RESULTS SUMMARY
============================================================
Tasks completed: 2/3
Average score: 0.94
Average reward: 1.08
```

## Baseline Scores

Performance of different models on the Aviation Agent environment:

| Model | Task 1 (Easy) | Task 2 (Medium) | Task 3 (Hard) | Avg Score | Success Rate |
|-------|---------------|-----------------|---------------|-----------|--------------|
| gpt-4o-mini | 1.00 | 1.00 | 0.83 | 0.94 | 67% (2/3) |
| gpt-4o | 1.00 | 1.00 | 1.00 | 1.00 | 100% (3/3) |
| gpt-3.5-turbo | 1.00 | 0.80 | 0.67 | 0.82 | 33% (1/3) |

Notes:
- Scores are deterministic (temperature=0.0)
- Task 3 is significantly harder due to traffic alert complexity
- Success threshold: 0.9 (90%)
- Models tested with standard aviation phraseology prompt

## Building the Docker Image

Before deploying, build the Docker image:

```bash
# From Aviation_Agent directory
docker build -t Aviation_Agent-env:latest -f server/Dockerfile .

# Test the container locally
docker run -p 8000:8000 Aviation_Agent-env:latest

# Verify it's running
curl http://localhost:8000/health
```

The container:
- Exposes port 8000
- Includes health check endpoint
- Uses multi-stage build for smaller image size
- Installs all dependencies via uv

## Deploying to Hugging Face Spaces

You can easily deploy your OpenEnv environment to Hugging Face Spaces using the `openenv push` command:

```bash
# From the environment directory (where openenv.yaml is located)
openenv push

# Or specify options
openenv push --namespace my-org --private
```

The `openenv push` command will:
1. Validate that the directory is an OpenEnv environment (checks for `openenv.yaml`)
2. Prepare a custom build for Hugging Face Docker space (enables web interface)
3. Upload to Hugging Face (ensuring you're logged in)

### Prerequisites

- Authenticate with Hugging Face: The command will prompt for login if not already authenticated

### Options

- `--directory`, `-d`: Directory containing the OpenEnv environment (defaults to current directory)
- `--repo-id`, `-r`: Repository ID in format 'username/repo-name' (defaults to 'username/env-name' from openenv.yaml)
- `--base-image`, `-b`: Base Docker image to use (overrides Dockerfile FROM)
- `--private`: Deploy the space as private (default: public)

### Examples

```bash
# Push to your personal namespace (defaults to username/env-name from openenv.yaml)
openenv push

# Push to a specific repository
openenv push --repo-id my-org/my-env

# Push with a custom base image
openenv push --base-image ghcr.io/meta-pytorch/openenv-base:latest

# Push as a private space
openenv push --private

# Combine options
openenv push --repo-id my-org/my-env --base-image custom-base:latest --private
```

After deployment, your space will be available at:
`https://huggingface.co/spaces/<repo-id>`

The deployed space includes:
- **Web Interface** at `/web` - Interactive UI for exploring the environment
- **API Documentation** at `/docs` - Full OpenAPI/Swagger interface
- **Health Check** at `/health` - Container health monitoring
- **WebSocket** at `/ws` - Persistent session endpoint for low-latency interactions

## Environment Details

### Action
**AviationAgentAction**: Pilot's radio response
- `message` (str) - The pilot's response to ATC instruction

### Observation
**AviationAgentObservation**: ATC instruction and feedback
- `atc_instruction` (str) - The ATC instruction given to pilot
- `task_description` (str) - Description of what pilot should do
- `step_count` (int) - Number of steps taken in episode
- `reward` (float) - Reward for this step
- `done` (bool) - Whether episode is complete
- `metadata` (dict) - Grading details, score, task info

### Reward
Calculated with trajectory signals:
- Base: grader score (0.0-1.0)
- Step penalty: -0.05 per additional step
- First-attempt bonus: +0.3 for perfect first response
- Max steps penalty: -0.2 if limit reached

### State
- `episode_id` (str) - Unique episode identifier
- `step_count` (int) - Steps taken in current episode

## OpenEnv Spec Compliance

This environment fully implements the OpenEnv interface:

✅ Typed Pydantic models for Observation, Action, and Reward  
✅ `step(action)` → returns observation, reward, done, info  
✅ `reset()` → returns initial observation  
✅ `state()` → returns current state  
✅ `openenv.yaml` with metadata  
✅ Validated via `openenv validate`

Run validation:
```bash
cd Aviation_Agent
openenv validate
```

## Advanced Usage

### Connecting to an Existing Server

If you already have a Aviation Agent environment server running, you can connect directly:

```python
from Aviation_Agent import AviationAgentEnv

# Connect to existing server
Aviation_Agentenv = AviationAgentEnv(base_url="<ENV_HTTP_URL_HERE>")

# Use as normal
result = Aviation_Agentenv.reset()
result = Aviation_Agentenv.step(AviationAgentAction(message="Hello!"))
```

Note: When connecting to an existing server, `Aviation_Agentenv.close()` will NOT stop the server.

### Using the Context Manager

The client supports context manager usage for automatic connection management:

```python
from Aviation_Agent import AviationAgentAction, AviationAgentEnv

# Connect with context manager (auto-connects and closes)
with AviationAgentEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    print(f"Reset: {result.observation.echoed_message}")
    # Multiple steps with low latency
    for msg in ["Hello", "World", "!"]:
        result = env.step(AviationAgentAction(message=msg))
        print(f"Echoed: {result.observation.echoed_message}")
```

The client uses WebSocket connections for:
- **Lower latency**: No HTTP connection overhead per request
- **Persistent session**: Server maintains your environment state
- **Efficient for episodes**: Better for many sequential steps

### Concurrent WebSocket Sessions

The server supports multiple concurrent WebSocket connections. To enable this,
modify `server/app.py` to use factory mode:

```python
# In server/app.py - use factory mode for concurrent sessions
app = create_app(
    AviationAgentEnvironment,  # Pass class, not instance
    AviationAgentAction,
    AviationAgentObservation,
    max_concurrent_envs=4,  # Allow 4 concurrent sessions
)
```

Then multiple clients can connect simultaneously:

```python
from Aviation_Agent import AviationAgentAction, AviationAgentEnv
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with AviationAgentEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        for i in range(10):
            result = env.step(AviationAgentAction(message=f"Client {client_id}, step {i}"))
        return client_id, result.observation.message_length

# Run 4 episodes concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_episode, range(4)))
```

## Development & Testing

### Direct Environment Testing

Test the environment logic directly without starting the HTTP server:

```bash
# From the server directory
python3 server/Aviation_Agent_environment.py
```

This verifies that:
- Environment resets correctly
- Step executes actions properly
- State tracking works
- Rewards are calculated correctly

### Running Locally

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```

## Project Structure

```
Aviation_Agent/
├── .dockerignore         # Docker build exclusions
├── __init__.py            # Module exports
├── README.md              # This file
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependencies (generated)
├── client.py              # AviationAgentEnv client
├── models.py              # Action and Observation models
└── server/
    ├── __init__.py        # Server module exports
    ├── Aviation_Agent_environment.py  # Core environment logic
    ├── app.py             # FastAPI application (HTTP + WebSocket endpoints)
    └── Dockerfile         # Container image definition
```
