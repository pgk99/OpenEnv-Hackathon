# Serial Testing Steps - Complete Guide

Follow these steps in order to test your Aviation Agent environment before submission.

## Quick Test (Automated)

On Linux/Mac:
```bash
./quick_test.sh
```

On Windows:
```powershell
# Run each test manually (see below)
```

---

## Manual Testing Steps

### Step 1: Verify File Structure ✅

```bash
python verify_submission.py
```

**Expected:** All checks pass with ✓

**What it tests:**
- All required files exist
- Models import correctly
- Environment has required methods
- Tasks and graders are functional

---

### Step 2: Test Environment Logic (No Server) ✅

```bash
python Aviation_Agent/test_environment.py
```

**Expected:** All 3 tasks pass with score 1.00

**What it tests:**
- Environment reset() works
- Environment step() works
- Grading logic is correct
- Reward calculation works

---

### Step 3: Validate OpenEnv Compliance ✅

```bash
cd Aviation_Agent
openenv validate
cd ..
```

**Expected:** All validation checks pass

**What it tests:**
- openenv.yaml is valid
- Pydantic models are correct
- Environment implements required interface

---

### Step 4: Test Task Graders ✅

```bash
python Aviation_Agent/task_graders.py
```

**Expected:** 
- Good response score: 1.00
- Poor response score: 0.33

**What it tests:**
- Graders return scores in [0.0, 1.0]
- Graders differentiate good/poor responses

---

### Step 5: Start Server ✅

```bash
cd Aviation_Agent
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

**Keep this terminal running!**

**Expected:** Server starts without errors

---

### Step 6: Test Health Endpoint ✅

In a new terminal:

```bash
curl http://localhost:8000/health
```

**Expected:** `{"status":"healthy"}`

---

### Step 7: Test Reset Endpoint ✅

```bash
curl -X POST http://localhost:8000/reset
```

**Expected:** JSON response with `atc_instruction` field

---

### Step 8: Test Step Endpoint ✅

```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"message": "Descend and maintain flight level 180, Speedbird 247"}'
```

**Expected:** JSON response with `reward` and `score` fields

---

### Step 9: Test Python Client ✅

```bash
python -c "
from Aviation_Agent import AviationAgentEnv, AviationAgentAction

with AviationAgentEnv(base_url='http://localhost:8000') as env:
    obs = env.reset()
    print(f'ATC: {obs.atc_instruction}')
    
    result = env.step(AviationAgentAction(
        message='Descend and maintain flight level 180, Speedbird 247'
    ))
    print(f'Score: {result.observation.metadata[\"score\"]:.2f}')
    print(f'Reward: {result.reward:.2f}')
"
```

**Expected:** Score and reward printed

---

### Step 10: Test Inference Script ✅

**Setup:**
```bash
# For OpenAI
export OPENAI_API_KEY=your_key_here
export MODEL_NAME=gpt-4o-mini
export API_BASE_URL=https://api.openai.com/v1

# OR for Hugging Face
export HF_TOKEN=your_hf_token_here
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
export API_BASE_URL=https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2/v1
```

**Run:**
```bash
python inference.py
```

**Expected Output:**
```json
{"type": "START", ...}
{"type": "STEP", "task_id": "task_1_easy", ...}
{"type": "STEP", "task_id": "task_2_medium", ...}
{"type": "STEP", "task_id": "task_3_hard", ...}
{"type": "END", "total_tasks": 3, "successful_tasks": 3, ...}
```

**What it tests:**
- Inference script runs without errors
- Structured logging format is correct
- All 3 tasks complete
- Scores are in [0.0, 1.0] range

---

### Step 11: Stop Server

Go back to the server terminal and press `Ctrl+C`

---

### Step 12: Build Docker Image ✅

```bash
cd Aviation_Agent
docker build -t aviation-agent-env:latest -f server/Dockerfile .
cd ..
```

**Expected:** Build completes successfully

**What it tests:**
- Dockerfile builds without errors
- All dependencies install correctly

---

### Step 13: Test Docker Container ✅

```bash
docker run -p 8000:8000 aviation-agent-env:latest
```

**Keep this running!**

**Expected:** Server starts inside container

---

### Step 14: Test Docker Health ✅

In a new terminal:

```bash
curl http://localhost:8000/health
```

**Expected:** `{"status":"healthy"}`

---

### Step 15: Test Inference Against Docker ✅

```bash
export OPENAI_API_KEY=your_key_here
export MODEL_NAME=gpt-4o-mini
export AVIATION_ENV_URL=http://localhost:8000

python inference.py
```

**Expected:** Same structured output as Step 10

---

### Step 16: Stop Docker Container

Press `Ctrl+C` in the Docker terminal

---

### Step 17: Access Web Interface ✅

Start server again (local or Docker):

```bash
cd Aviation_Agent
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Open browser: http://localhost:8000/web

**Expected:** Interactive web UI loads

---

### Step 18: Check API Documentation ✅

Open browser: http://localhost:8000/docs

**Expected:** Swagger/OpenAPI documentation loads

---

## Pre-Submission Checklist

Before deploying to HF Spaces:

- [ ] All tests above pass
- [ ] `inference.py` is in project root
- [ ] Structured logging format is correct ([START], [STEP], [END])
- [ ] Environment variables work (API_BASE_URL, MODEL_NAME, HF_TOKEN)
- [ ] Docker builds and runs successfully
- [ ] Health endpoint returns 200
- [ ] Reset endpoint works
- [ ] Web interface accessible
- [ ] API docs accessible
- [ ] README.md is complete
- [ ] All documentation files present

---

## Deploy to Hugging Face Spaces

Once all tests pass:

```bash
# Install HF CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Deploy
cd Aviation_Agent
openenv push --repo-id your-username/aviation-agent
```

---

## Troubleshooting

### Server won't start
- Check if port 8000 is in use: `lsof -i :8000` (Linux/Mac)
- Try different port: `uvicorn server.app:app --port 8001`

### Import errors
- Set PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

### Inference script fails
- Verify API key is set: `echo $OPENAI_API_KEY`
- Check server is running: `curl http://localhost:8000/health`
- Verify AVIATION_ENV_URL is correct

### Docker build fails
- Clean cache: `docker system prune -a`
- Rebuild: `docker build --no-cache ...`

---

## Success Criteria

✅ All tests pass  
✅ Inference completes without errors  
✅ Structured logs are correct  
✅ Docker builds and runs  
✅ Ready for HF Spaces deployment  

---

## Next Steps

1. ✅ Complete all tests above
2. ✅ Deploy to HF Spaces
3. ✅ Verify deployed space works
4. ✅ Submit to hackathon

Good luck! 🚀✈️
