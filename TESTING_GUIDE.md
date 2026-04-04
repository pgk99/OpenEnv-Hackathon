# Testing Guide - Serial Testing Steps

Complete step-by-step guide to test the Aviation Agent environment before submission.

## Prerequisites

Install required dependencies:

```bash
# Core dependencies
pip install openenv[core] fastapi uvicorn

# Baseline dependencies
pip install openai

# Or install all at once
pip install -r Aviation_Agent/server/requirements.txt
pip install -r Aviation_Agent/requirements-baseline.txt
```

---

## Step 1: Validate File Structure

```bash
# Run verification script
python verify_submission.py
```

Expected output: All checks should pass with ✓

---

## Step 2: Test Environment Logic (No Server)

Test the core environment logic without starting a server:

```bash
python Aviation_Agent/test_environment.py
```

**Expected Output:**
```
Aviation Agent Environment - Test Suite
============================================================

Testing task_1_easy
============================================================
ATC Instruction: Speedbird 247, descend and maintain flight level 180.
Task: Acknowledge and read back altitude change

Pilot Response: Descend and maintain flight level 180, Speedbird 247

Results:
  Score: 1.00
  Reward: 1.30
  Done: True
  Success: ✓

Grading Details:
  ✓ callsign: ['Speedbird 247', 'Speedbird two four seven']
  ✓ altitude: ['FL180', 'flight level 180', 'flight level one eight zero']
  ✓ action: ['descend', 'descending']

[... similar output for other tasks ...]

============================================================
SUMMARY
============================================================
Task 1 (Easy): 1.00 ✓
Task 2 (Medium): 1.00 ✓
Task 3 (Hard): 1.00 ✓

Average Score: 1.00

✓ All tests passed!
```

**What this tests:**
- ✅ Environment reset() works
- ✅ Environment step() works
- ✅ Grading logic is correct
- ✅ Reward calculation works
- ✅ All 3 tasks are functional

---

## Step 3: Validate OpenEnv Compliance

```bash
cd Aviation_Agent
openenv validate
```

**Expected Output:**
```
✓ openenv.yaml found and valid
✓ Action model defined
✓ Observation model defined
✓ Environment class found
✓ Environment implements reset()
✓ Environment implements step()
✓ Environment implements state property
✓ All checks passed
```

**What this tests:**
- ✅ openenv.yaml is valid
- ✅ Pydantic models are correct
- ✅ Environment implements required interface

---

## Step 4: Test Task Graders

```bash
python Aviation_Agent/task_graders.py
```

**Expected Output:**
```
Good response score: 1.00
Poor response score: 0.33
```

**What this tests:**
- ✅ Graders return scores in [0.0, 1.0] range
- ✅ Graders are deterministic
- ✅ Grading logic differentiates good/poor responses

---

## Step 5: Start the Server

In a terminal, start the FastAPI server:

```bash
cd Aviation_Agent
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal running for the next steps.**

---

## Step 6: Test Health Endpoint

In a new terminal:

```bash
curl http://localhost:8000/health
```

**Expected Output:**
```json
{"status":"healthy"}
```

**What this tests:**
- ✅ Server is running
- ✅ Health check endpoint works

---

## Step 7: Test API Endpoints

### Test Reset Endpoint

```bash
curl -X POST http://localhost:8000/reset
```

**Expected Output:**
```json
{
  "observation": {
    "atc_instruction": "Speedbird 247, descend and maintain flight level 180.",
    "task_description": "Acknowledge and read back altitude change",
    "step_count": 0,
    "done": false,
    "reward": 0.0,
    "metadata": null
  },
  "reward": 0.0,
  "done": false
}
```

### Test Step Endpoint

```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"message": "Descend and maintain flight level 180, Speedbird 247"}'
```

**Expected Output:**
```json
{
  "observation": {
    "atc_instruction": "Speedbird 247, descend and maintain flight level 180.",
    "task_description": "Acknowledge and read back altitude change",
    "step_count": 1,
    "done": true,
    "reward": 1.3,
    "metadata": {
      "task_id": "task_1_easy",
      "difficulty": "easy",
      "response": "Descend and maintain flight level 180, Speedbird 247",
      "score": 1.0,
      ...
    }
  },
  "reward": 1.3,
  "done": true
}
```

**What this tests:**
- ✅ Reset endpoint works
- ✅ Step endpoint works
- ✅ Rewards are calculated
- ✅ Metadata is returned

---

## Step 8: Test with Python Client

```bash
python -c "
from Aviation_Agent import AviationAgentEnv, AviationAgentAction

with AviationAgentEnv(base_url='http://localhost:8000') as env:
    # Reset
    obs = env.reset()
    print(f'ATC: {obs.atc_instruction}')
    print(f'Task: {obs.task_description}')
    
    # Step
    response = 'Descend and maintain flight level 180, Speedbird 247'
    result = env.step(AviationAgentAction(message=response))
    
    print(f'\\nPilot: {response}')
    print(f'Score: {result.observation.metadata[\"score\"]:.2f}')
    print(f'Reward: {result.reward:.2f}')
    print(f'Done: {result.done}')
"
```

**Expected Output:**
```
ATC: Speedbird 247, descend and maintain flight level 180.
Task: Acknowledge and read back altitude change

Pilot: Descend and maintain flight level 180, Speedbird 247
Score: 1.00
Reward: 1.30
Done: True
```

**What this tests:**
- ✅ Client can connect to server
- ✅ WebSocket communication works
- ✅ Full episode works end-to-end

---

## Step 9: Test Inference Script (OpenAI)

Set up environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY=your_openai_key_here
export MODEL_NAME=gpt-4o-mini
export API_BASE_URL=https://api.openai.com/v1

# Or use HF_TOKEN instead
export HF_TOKEN=your_openai_key_here
```

Run inference script:

```bash
python inference.py
```

**Expected Output:**
```json
{"type": "START", "environment": "Aviation_Agent", "model": "gpt-4o-mini", "timestamp": "..."}
{"type": "STEP", "task_id": "task_1_easy", "step": 1, "action": "Descend and maintain flight level 180, Speedbird 247", "reward": 1.3, "score": 1.0, "done": true}
{"type": "STEP", "task_id": "task_2_medium", "step": 1, "action": "Turn left heading 090, descend and maintain 5000 feet, United 512", "reward": 1.25, "score": 1.0, "done": true}
{"type": "STEP", "task_id": "task_3_hard", "step": 1, "action": "Traffic in sight, turn right heading 270, climb and maintain 10000 feet, Delta 1823", "reward": 1.25, "score": 1.0, "done": true}
{"type": "END", "total_tasks": 3, "successful_tasks": 3, "average_score": 1.0, "average_reward": 1.27, "results": [...], "timestamp": "..."}
```

**What this tests:**
- ✅ Inference script runs without errors
- ✅ Structured logging format is correct
- ✅ All 3 tasks complete
- ✅ Scores are in [0.0, 1.0] range
- ✅ OpenAI client works

---

## Step 10: Test Inference Script (Hugging Face)

For using Hugging Face models (e.g., Mistral-7B-Instruct):

```bash
# Set up for HF Inference API
export HF_TOKEN=your_huggingface_token_here
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
export API_BASE_URL=https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2/v1

# Run inference
python inference.py
```

**Note:** HF Inference API uses OpenAI-compatible format, so the same client works.

**What this tests:**
- ✅ Works with alternative LLM providers
- ✅ Flexible model selection

---

## Step 11: Build Docker Image

Stop the server (Ctrl+C in the server terminal), then:

```bash
cd Aviation_Agent
docker build -t aviation-agent-env:latest -f server/Dockerfile .
```

**Expected Output:**
```
[+] Building 45.2s (18/18) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 2.34kB
 ...
 => exporting to image
 => => exporting layers
 => => writing image sha256:...
 => => naming to docker.io/library/aviation-agent-env:latest
```

**What this tests:**
- ✅ Dockerfile builds successfully
- ✅ All dependencies install correctly
- ✅ Multi-stage build works

---

## Step 12: Test Docker Container

```bash
# Run container
docker run -p 8000:8000 aviation-agent-env:latest
```

**Expected Output:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

In another terminal:

```bash
# Test health
curl http://localhost:8000/health

# Test reset
curl -X POST http://localhost:8000/reset
```

**What this tests:**
- ✅ Container runs successfully
- ✅ Server starts inside container
- ✅ Endpoints are accessible

---

## Step 13: Test Inference Against Docker Container

With Docker container running:

```bash
export OPENAI_API_KEY=your_key_here
export MODEL_NAME=gpt-4o-mini
export AVIATION_ENV_URL=http://localhost:8000

python inference.py
```

**Expected:** Same structured output as Step 9.

**What this tests:**
- ✅ Inference works against containerized environment
- ✅ End-to-end integration works

---

## Step 14: Access Web Interface

With server running (local or Docker):

Open browser to: http://localhost:8000/web

**Expected:**
- Interactive web UI loads
- Can reset environment
- Can send actions
- Can see observations and rewards

**What this tests:**
- ✅ Web interface works
- ✅ Frontend integration works

---

## Step 15: Check API Documentation

Open browser to: http://localhost:8000/docs

**Expected:**
- Swagger/OpenAPI documentation loads
- All endpoints are documented
- Can test endpoints interactively

**What this tests:**
- ✅ API documentation is generated
- ✅ OpenAPI spec is valid

---

## Pre-Submission Checklist

Before deploying to HF Spaces, verify:

- [ ] `python verify_submission.py` passes all checks
- [ ] `python Aviation_Agent/test_environment.py` succeeds
- [ ] `openenv validate` passes
- [ ] Server starts: `uvicorn server.app:app --host 0.0.0.0 --port 8000`
- [ ] Health endpoint returns 200: `curl http://localhost:8000/health`
- [ ] Reset endpoint works: `curl -X POST http://localhost:8000/reset`
- [ ] `python inference.py` completes without errors
- [ ] Docker builds: `docker build -t aviation-agent-env:latest -f server/Dockerfile .`
- [ ] Docker runs: `docker run -p 8000:8000 aviation-agent-env:latest`
- [ ] Inference works against Docker container
- [ ] Web interface accessible at `/web`
- [ ] API docs accessible at `/docs`
- [ ] README.md has all required sections
- [ ] `inference.py` is in project root
- [ ] Structured logging format is correct

---

## Common Issues and Solutions

### Issue: Import errors

**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port
lsof -i :8000
# Kill it or use different port
uvicorn server.app:app --host 0.0.0.0 --port 8001
```

### Issue: OpenAI API rate limits

**Solution:**
- Wait a few seconds between runs
- Use gpt-4o-mini (cheaper, faster)
- Check your API quota

### Issue: Docker build fails

**Solution:**
```bash
# Clean Docker cache
docker system prune -a
# Rebuild
docker build --no-cache -t aviation-agent-env:latest -f server/Dockerfile .
```

### Issue: Inference script hangs

**Solution:**
- Check server is running
- Verify AVIATION_ENV_URL is correct
- Check API_BASE_URL and credentials

---

## Summary

If all steps pass, you're ready to deploy to Hugging Face Spaces!

Next: Follow `DEPLOYMENT_GUIDE.md` for HF Spaces deployment.
