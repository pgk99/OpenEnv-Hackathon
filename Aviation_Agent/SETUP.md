# Aviation Agent Environment - Setup Guide

Complete setup instructions for the Aviation Agent OpenEnv environment.

## Prerequisites

- Python 3.10 or higher
- Docker (for containerized deployment)
- Git
- OpenAI API key (for baseline inference)

## Installation Methods

### Method 1: Local Development (Recommended for Testing)

1. **Clone or navigate to the project**:
   ```bash
   cd Aviation_Agent
   ```

2. **Install dependencies using uv** (recommended):
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync
   ```

3. **Or install using pip**:
   ```bash
   pip install -r server/requirements.txt
   ```

4. **Test the environment locally** (no server needed):
   ```bash
   python test_environment.py
   ```

5. **Start the server**:
   ```bash
   uvicorn server.app:app --host 0.0.0.0 --port 8000
   ```

6. **Access the environment**:
   - Web Interface: http://localhost:8000/web
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Method 2: Docker (Recommended for Deployment)

1. **Build the Docker image**:
   ```bash
   docker build -t aviation-agent-env:latest -f server/Dockerfile .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 aviation-agent-env:latest
   ```

3. **Verify it's running**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Access the environment**:
   - Web Interface: http://localhost:8000/web
   - API Docs: http://localhost:8000/docs

### Method 3: Hugging Face Spaces (Production Deployment)

1. **Install Hugging Face CLI**:
   ```bash
   pip install huggingface_hub
   ```

2. **Login to Hugging Face**:
   ```bash
   huggingface-cli login
   ```

3. **Deploy using openenv**:
   ```bash
   openenv push --repo-id your-username/aviation-agent
   ```

4. **Or deploy as private space**:
   ```bash
   openenv push --repo-id your-username/aviation-agent --private
   ```

5. **Access your deployed space**:
   - https://huggingface.co/spaces/your-username/aviation-agent

## Validation

### Validate OpenEnv Compliance

```bash
cd Aviation_Agent
openenv validate
```

Expected output:
```
✓ openenv.yaml found and valid
✓ Action model defined
✓ Observation model defined
✓ Environment implements required methods
✓ All checks passed
```

### Test Environment Logic

```bash
python test_environment.py
```

Expected output:
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
...
```

### Test with Client

```bash
python -c "
from Aviation_Agent import AviationAgentEnv, AviationAgentAction

with AviationAgentEnv(base_url='http://localhost:8000') as env:
    obs = env.reset()
    print(f'ATC: {obs.atc_instruction}')
    
    response = 'Descend and maintain flight level 180, Speedbird 247'
    result = env.step(AviationAgentAction(message=response))
    
    print(f'Pilot: {response}')
    print(f'Score: {result.observation.metadata[\"score\"]:.2f}')
    print(f'Reward: {result.reward:.2f}')
"
```

## Running Baseline Inference

1. **Install baseline dependencies**:
   ```bash
   pip install -r requirements-baseline.txt
   ```

2. **Set OpenAI API key**:
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

3. **Start the environment server** (if not already running):
   ```bash
   uvicorn server.app:app --host 0.0.0.0 --port 8000 &
   ```

4. **Run baseline inference**:
   ```bash
   python baseline_inference.py
   ```

5. **Optional: Use different model**:
   ```bash
   export OPENAI_MODEL=gpt-4o
   python baseline_inference.py
   ```

6. **Optional: Use different server URL**:
   ```bash
   export AVIATION_ENV_URL=http://your-server:8000
   python baseline_inference.py
   ```

## Testing Task Graders

```bash
python task_graders.py
```

This will test the grading logic with sample responses.

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uvicorn server.app:app --host 0.0.0.0 --port 8001

# Update client connection
export AVIATION_ENV_URL=http://localhost:8001
```

### Docker Build Issues

If Docker build fails:

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t aviation-agent-env:latest -f server/Dockerfile .
```

### Import Errors

If you get import errors:

```bash
# Make sure you're in the right directory
cd Aviation_Agent

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in editable mode
pip install -e .
```

### OpenAI API Errors

If baseline inference fails:

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key
python -c "from openai import OpenAI; client = OpenAI(); print('API key valid')"

# Check rate limits
# Wait a few seconds between runs if you hit rate limits
```

### Server Not Starting

If the server doesn't start:

```bash
# Check if port is available
lsof -i :8000

# Check logs
uvicorn server.app:app --host 0.0.0.0 --port 8000 --log-level debug

# Verify dependencies
pip list | grep openenv
pip list | grep fastapi
```

## Development Workflow

1. **Make changes to environment logic**:
   - Edit `server/Aviation_Agent_environment.py`

2. **Test locally without server**:
   ```bash
   python test_environment.py
   ```

3. **Start server with auto-reload**:
   ```bash
   uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Test with client**:
   ```bash
   python -c "from Aviation_Agent import AviationAgentEnv, AviationAgentAction; ..."
   ```

5. **Validate OpenEnv compliance**:
   ```bash
   openenv validate
   ```

6. **Build and test Docker image**:
   ```bash
   docker build -t aviation-agent-env:latest -f server/Dockerfile .
   docker run -p 8000:8000 aviation-agent-env:latest
   ```

7. **Deploy to Hugging Face**:
   ```bash
   openenv push
   ```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for baseline | - | Yes (for baseline) |
| `OPENAI_MODEL` | Model to use for baseline | `gpt-4o-mini` | No |
| `AVIATION_ENV_URL` | Environment server URL | `http://localhost:8000` | No |

## File Structure

```
Aviation_Agent/
├── models.py                    # Pydantic models
├── client.py                    # Environment client
├── openenv.yaml                 # OpenEnv metadata
├── pyproject.toml               # Project config
├── uv.lock                      # Locked dependencies
├── task_graders.py              # Task graders
├── baseline_inference.py        # Baseline script
├── test_environment.py          # Test script
├── requirements-baseline.txt    # Baseline deps
├── SETUP.md                     # This file
├── README.md                    # Main documentation
└── server/
    ├── Aviation_Agent_environment.py  # Environment logic
    ├── app.py                         # FastAPI server
    ├── requirements.txt               # Server deps
    └── Dockerfile                     # Container definition
```

## Next Steps

After setup:

1. ✅ Validate OpenEnv compliance: `openenv validate`
2. ✅ Test environment locally: `python test_environment.py`
3. ✅ Start server: `uvicorn server.app:app --host 0.0.0.0 --port 8000`
4. ✅ Run baseline: `python baseline_inference.py`
5. ✅ Build Docker image: `docker build -t aviation-agent-env:latest -f server/Dockerfile .`
6. ✅ Deploy to HF Spaces: `openenv push`

## Support

For issues or questions:
- Check the main README.md
- Review HACKATHON_SUBMISSION.md
- Check code comments in Python files
