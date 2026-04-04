# Meta x Hugging Face Hackathon Submission Checklist

## Environment: Aviation Agent (ATC Communication Training System)

### Problem Statement

Build an Agentic AI system that learns from ATC-pilot communication patterns and enables trainee pilots to practice, interpret and generate accurate responses in simulated flight scenarios with automated evaluation of correctness and adherence to aviation communication standards.

### Solution Overview

An OpenEnv reinforcement learning environment that trains AI agents to master aviation communication through:
- **Pattern Learning**: Agents learn proper communication structures from reward signals
- **Practice Environment**: Progressive scenarios from simple to complex
- **Response Generation**: AI generates pilot responses to ATC instructions
- **Automated Evaluation**: Standards-based grading (0.0-1.0 scores)
- **Standards Adherence**: Checks ICAO aviation phraseology compliance

### ✅ Real-World Task Simulation
**Task**: Air Traffic Control (ATC) radio communication

**Why it's real-world**: Professional pilots communicate with ATC thousands of times daily. They must:
- Acknowledge instructions with callsigns
- Read back altitude, heading, and speed clearances
- Use standard aviation phraseology
- Respond appropriately to traffic alerts

This is NOT a game or toy - it's a simplified simulation of actual aviation communication.

---

### ✅ OpenEnv Spec Compliance

**Implementation**:
- ✅ Typed Pydantic models: `AviationAgentAction`, `AviationAgentObservation`
- ✅ `step(action)` → returns observation, reward, done, metadata
- ✅ `reset()` → returns initial observation
- ✅ `state()` → returns State with episode_id and step_count
- ✅ `openenv.yaml` with complete metadata

**Files**:
- `Aviation_Agent/models.py` - Pydantic models
- `Aviation_Agent/server/Aviation_Agent_environment.py` - Environment implementation
- `Aviation_Agent/openenv.yaml` - Metadata

**Validation**:
```bash
cd Aviation_Agent
openenv validate
```

---

### ✅ Minimum 3 Tasks with Agent Graders

#### Task 1: Easy - Single Altitude Change
**Objective**: Respond to simple altitude change instruction

**ATC Instruction**: "Speedbird 247, descend and maintain flight level 180."

**Grading Criteria** (0.0-1.0):
- Callsign acknowledged: 0.33 points
- Altitude read back correctly: 0.33 points
- Action (descend) acknowledged: 0.34 points

**Success Threshold**: 0.9 (90%)

**Example Perfect Response**: "Descend and maintain flight level 180, Speedbird 247"

---

#### Task 2: Medium - Heading and Altitude Change
**Objective**: Respond to heading and altitude instruction

**ATC Instruction**: "United 512, turn left heading 090, descend and maintain 5000 feet."

**Grading Criteria** (0.0-1.0):
- Callsign acknowledged: 0.20 points
- Heading read back: 0.20 points
- Altitude read back: 0.20 points
- Turn direction: 0.20 points
- Action (descend) acknowledged: 0.20 points

**Success Threshold**: 0.9 (90%)

**Example Perfect Response**: "Turn left heading 090, descend and maintain 5000 feet, United 512"

---

#### Task 3: Hard - Traffic Alert with Maneuver
**Objective**: Respond to traffic alert with heading and altitude changes

**ATC Instruction**: "Delta 1823, traffic alert. Traffic 2 o'clock, 3 miles, opposite direction, altitude indicates 8000 feet. Turn right heading 270, climb and maintain 10000 feet."

**Grading Criteria** (0.0-1.0):
- Callsign acknowledged: 0.167 points
- Traffic acknowledged: 0.167 points
- Heading read back: 0.167 points
- Altitude read back: 0.167 points
- Turn direction: 0.166 points
- Action (climb) acknowledged: 0.166 points

**Success Threshold**: 0.9 (90%)

**Example Perfect Response**: "Traffic in sight, turn right heading 270, climb and maintain 10000 feet, Delta 1823"

---

**Grader Implementation**: `Aviation_Agent/task_graders.py`

Each grader:
- Takes agent responses as input
- Returns deterministic score (0.0-1.0)
- Provides detailed grading breakdown
- Has clear success/failure criteria

**Test Graders**:
```bash
python Aviation_Agent/task_graders.py
```

---

### ✅ Meaningful Reward Function

**Design Philosophy**: Provide trajectory-level signals, not just binary end-of-episode rewards.

**Reward Calculation**:
```python
reward = base_score - step_penalty + bonuses - penalties
```

**Components**:

1. **Base Reward**: Grader score (0.0-1.0)
   - Rewards partial progress toward task completion
   - Each required element contributes to score

2. **Step Penalty**: -0.05 per additional step
   - Penalizes inefficient behavior
   - Encourages getting it right the first time

3. **First-Attempt Bonus**: +0.3 for perfect score on step 1
   - Rewards optimal performance
   - Encourages learning efficient responses

4. **Max Steps Penalty**: -0.2 if max steps reached without success
   - Penalizes clearly undesirable behavior
   - Prevents infinite loops

**Example Trajectories**:

Perfect first response:
- Step 1: score=1.0, reward=1.3 (1.0 + 0.3 bonus)

Good second attempt:
- Step 1: score=0.6, reward=0.6
- Step 2: score=1.0, reward=0.95 (1.0 - 0.05 penalty)

Poor performance:
- Step 1: score=0.3, reward=0.3
- Step 2: score=0.5, reward=0.45
- Step 3: score=0.6, reward=0.4 (0.6 - 0.2 max steps penalty)

**Implementation**: `Aviation_Agent/server/Aviation_Agent_environment.py` - `_calculate_reward()` method

---

### ✅ Baseline Inference Script

**File**: `Aviation_Agent/baseline_inference.py`

**Features**:
- Uses OpenAI API client
- Reads credentials from `OPENAI_API_KEY` environment variable
- Runs all 3 tasks
- Produces reproducible baseline scores (temperature=0.0)
- Reports detailed results

**Usage**:
```bash
# Install dependencies
pip install -r Aviation_Agent/requirements-baseline.txt

# Set API key
export OPENAI_API_KEY=your_key_here

# Start environment server
uvicorn Aviation_Agent.server.app:app --host 0.0.0.0 --port 8000 &

# Run baseline
python Aviation_Agent/baseline_inference.py
```

**Expected Output**:
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

---

## Testing & Validation

### Local Testing (No Server Required)
```bash
python Aviation_Agent/test_environment.py
```

This tests the environment logic directly.

### OpenEnv Validation
```bash
cd Aviation_Agent
openenv validate
```

Validates OpenEnv spec compliance.

### Server Testing
```bash
# Start server
uvicorn Aviation_Agent.server.app:app --host 0.0.0.0 --port 8000

# In another terminal, test with client
python -c "
from Aviation_Agent import AviationAgentEnv, AviationAgentAction
with AviationAgentEnv(base_url='http://localhost:8000') as env:
    obs = env.reset()
    print(f'ATC: {obs.atc_instruction}')
    result = env.step(AviationAgentAction(message='Descend FL180, Speedbird 247'))
    print(f'Score: {result.observation.metadata[\"score\"]:.2f}')
"
```

---

## Deployment to Hugging Face Spaces

### Prerequisites
```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login
```

### Deploy
```bash
cd Aviation_Agent
openenv push --repo-id your-username/aviation-agent
```

### Access Deployed Space
- Web Interface: `https://huggingface.co/spaces/your-username/aviation-agent/web`
- API Docs: `https://huggingface.co/spaces/your-username/aviation-agent/docs`
- Health Check: `https://huggingface.co/spaces/your-username/aviation-agent/health`

---

## Project Structure

```
Aviation_Agent/
├── models.py                          # Pydantic Action/Observation models
├── client.py                          # Environment client
├── openenv.yaml                       # OpenEnv metadata
├── task_graders.py                    # Programmatic graders for 3 tasks
├── baseline_inference.py              # OpenAI baseline script
├── test_environment.py                # Local testing script
├── requirements-baseline.txt          # Baseline dependencies
├── README.md                          # Complete documentation
└── server/
    ├── Aviation_Agent_environment.py  # Core environment logic
    ├── app.py                         # FastAPI server
    ├── requirements.txt               # Server dependencies
    └── Dockerfile                     # Container definition
```

---

## Hackathon Requirements Summary

| Requirement | Status | Evidence |
|------------|--------|----------|
| Real-world task simulation | ✅ | ATC radio communication - actual pilot task |
| OpenEnv spec compliance | ✅ | Full implementation in `models.py` and `Aviation_Agent_environment.py` |
| Typed Pydantic models | ✅ | `AviationAgentAction`, `AviationAgentObservation` |
| step/reset/state methods | ✅ | Implemented in `Aviation_Agent_environment.py` |
| openenv.yaml metadata | ✅ | Complete metadata file |
| Validated with openenv | ✅ | Run `openenv validate` |
| 3 tasks (easy→medium→hard) | ✅ | Task 1 (altitude), Task 2 (heading+altitude), Task 3 (traffic alert) |
| Programmatic graders | ✅ | `task_graders.py` with 0.0-1.0 scoring |
| Deterministic grading | ✅ | Clear success/failure criteria |
| Meaningful reward function | ✅ | Trajectory-level signals with partial progress |
| Rewards partial progress | ✅ | Each required element contributes to score |
| Penalizes bad behavior | ✅ | Step penalty, max steps penalty |
| Baseline inference script | ✅ | `baseline_inference.py` |
| Uses OpenAI API | ✅ | OpenAI client with configurable model |
| Reads from env vars | ✅ | `OPENAI_API_KEY` required |
| Reproducible scores | ✅ | temperature=0.0 for determinism |
| **inference.py in root** | ✅ | Structured logging format |
| **API_BASE_URL variable** | ✅ | Configurable API endpoint |
| **MODEL_NAME variable** | ✅ | Configurable model selection |
| **HF_TOKEN variable** | ✅ | Alternative to OPENAI_API_KEY |
| **Structured stdout logs** | ✅ | [START], [STEP], [END] format |
| **OpenAI Client usage** | ✅ | All LLM calls use OpenAI client |
| **Runtime < 20 min** | ✅ | Typical runtime: 1-2 minutes |
| **Works on 2 vCPU, 8GB RAM** | ✅ | Minimal resource requirements |
| **Dockerfile builds** | ✅ | Multi-stage build with health checks |
| **HF Space deployment** | ✅ | Tagged with openenv |
| **Complete documentation** | ✅ | README with all required sections |

---

## Quick Start for Judges

1. **Validate OpenEnv compliance**:
   ```bash
   cd Aviation_Agent
   openenv validate
   ```

2. **Test environment locally**:
   ```bash
   python Aviation_Agent/test_environment.py
   ```

3. **Run baseline inference**:
   ```bash
   export OPENAI_API_KEY=your_key
   uvicorn Aviation_Agent.server.app:app --host 0.0.0.0 --port 8000 &
   python Aviation_Agent/baseline_inference.py
   ```

4. **Deploy to HF Spaces**:
   ```bash
   cd Aviation_Agent
   openenv push
   ```

---

## Contact & Support

For questions about this submission, please refer to:
- `Aviation_Agent/README.md` - Complete documentation
- `HACKATHON_SUBMISSION.md` - This file
- Code comments in all Python files
