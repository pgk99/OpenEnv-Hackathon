# Deployment Guide - Hugging Face Spaces

Quick guide for deploying the Aviation Agent environment to Hugging Face Spaces for the hackathon submission.

## Prerequisites

✅ Hugging Face account  
✅ Docker installed locally  
✅ OpenEnv CLI installed  
✅ Environment tested locally  

## Step-by-Step Deployment

### 1. Verify Environment Works Locally

```bash
# Test environment logic
cd Aviation_Agent
python test_environment.py

# Validate OpenEnv compliance
openenv validate

# Build Docker image
docker build -t aviation-agent-env:latest -f server/Dockerfile .

# Test Docker container
docker run -p 8000:8000 aviation-agent-env:latest

# In another terminal, verify health
curl http://localhost:8000/health
```

### 2. Authenticate with Hugging Face

```bash
# Install HF CLI if not already installed
pip install huggingface_hub

# Login (will open browser for authentication)
huggingface-cli login

# Verify login
huggingface-cli whoami
```

### 3. Deploy to Hugging Face Spaces

```bash
# From Aviation_Agent directory
cd Aviation_Agent

# Deploy (will create space if it doesn't exist)
openenv push --repo-id your-username/aviation-agent

# Or deploy as private space
openenv push --repo-id your-username/aviation-agent --private
```

The `openenv push` command will:
1. ✅ Validate the environment
2. ✅ Prepare Docker configuration for HF Spaces
3. ✅ Upload files to Hugging Face
4. ✅ Trigger space build
5. ✅ Provide URL to your deployed space

### 4. Verify Deployment

Once deployed, your space will be available at:
```
https://huggingface.co/spaces/your-username/aviation-agent
```

Check these endpoints:
- **Web Interface**: `/web` - Interactive UI
- **API Docs**: `/docs` - Swagger/OpenAPI docs
- **Health Check**: `/health` - Container health
- **WebSocket**: `/ws` - Persistent connections

### 5. Test Deployed Environment

```bash
# Set your space URL
export AVIATION_ENV_URL=https://your-username-aviation-agent.hf.space

# Test with client
python -c "
from Aviation_Agent import AviationAgentEnv, AviationAgentAction

with AviationAgentEnv(base_url='$AVIATION_ENV_URL') as env:
    obs = env.reset()
    print(f'ATC: {obs.atc_instruction}')
    
    result = env.step(AviationAgentAction(
        message='Descend and maintain flight level 180, Speedbird 247'
    ))
    print(f'Score: {result.observation.metadata[\"score\"]:.2f}')
"
```

### 6. Run Baseline Against Deployed Space

```bash
# Set environment variables
export OPENAI_API_KEY=your_key_here
export AVIATION_ENV_URL=https://your-username-aviation-agent.hf.space

# Run baseline
python Aviation_Agent/baseline_inference.py
```

## Space Configuration

The deployed space includes:

### README.md Header (Auto-generated)
```yaml
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
---
```

### Dockerfile
- Multi-stage build for efficiency
- Health checks enabled
- Port 8000 exposed
- All dependencies installed

### Environment Variables (Optional)
You can set these in Space settings if needed:
- `OPENAI_API_KEY` - For testing with OpenAI models
- `LOG_LEVEL` - Logging verbosity (default: INFO)

## Updating Your Space

To update after making changes:

```bash
# Make your changes locally
# Test them
python Aviation_Agent/test_environment.py

# Rebuild Docker image
docker build -t aviation-agent-env:latest -f server/Dockerfile .

# Test Docker image
docker run -p 8000:8000 aviation-agent-env:latest

# Push update to HF Spaces
cd Aviation_Agent
openenv push --repo-id your-username/aviation-agent
```

## Troubleshooting Deployment

### Space Build Fails

Check the build logs in HF Spaces interface:
1. Go to your space
2. Click "Logs" tab
3. Look for error messages

Common issues:
- Missing dependencies → Check `server/requirements.txt`
- Port conflicts → Verify `app_port: 8000` in README header
- Import errors → Check PYTHONPATH in Dockerfile

### Space Runs But Endpoints Don't Work

```bash
# Check health endpoint
curl https://your-username-aviation-agent.hf.space/health

# Check API docs
# Visit: https://your-username-aviation-agent.hf.space/docs

# Check logs in HF Spaces interface
```

### Slow Response Times

HF Spaces may have cold starts. First request might be slow:
- Space sleeps after inactivity
- First request wakes it up (can take 30-60 seconds)
- Subsequent requests are fast

### Authentication Issues

```bash
# Re-login to HF
huggingface-cli logout
huggingface-cli login

# Verify token has write permissions
# Go to: https://huggingface.co/settings/tokens
```

## Space Settings

After deployment, configure in HF Spaces UI:

1. **Visibility**: Public or Private
2. **Hardware**: Default (CPU) is sufficient
3. **Secrets**: Add `OPENAI_API_KEY` if needed
4. **Sleep time**: Configure auto-sleep settings

## Hackathon Submission Checklist

Before submitting:

- [ ] Space is deployed and accessible
- [ ] Web interface works at `/web`
- [ ] API docs accessible at `/docs`
- [ ] Health check returns 200 at `/health`
- [ ] Space is tagged with `openenv`
- [ ] README.md is complete with all sections
- [ ] Baseline inference works against deployed space
- [ ] All 3 tasks are functional
- [ ] Graders return scores 0.0-1.0
- [ ] Docker container runs cleanly

## Submission Information

Include in your hackathon submission:

**Space URL**: `https://huggingface.co/spaces/your-username/aviation-agent`

**Key Features**:
- ✅ Real-world task: ATC radio communication
- ✅ 3 tasks: Easy → Medium → Hard
- ✅ Programmatic graders with deterministic scoring
- ✅ Meaningful reward function with trajectory signals
- ✅ Baseline inference script with OpenAI API
- ✅ Full OpenEnv spec compliance
- ✅ Containerized with Docker
- ✅ Complete documentation

**Endpoints**:
- Web UI: `https://your-username-aviation-agent.hf.space/web`
- API: `https://your-username-aviation-agent.hf.space/docs`
- Health: `https://your-username-aviation-agent.hf.space/health`

## Quick Commands Reference

```bash
# Validate
openenv validate

# Test locally
python test_environment.py

# Build Docker
docker build -t aviation-agent-env:latest -f server/Dockerfile .

# Test Docker
docker run -p 8000:8000 aviation-agent-env:latest

# Deploy to HF
openenv push --repo-id your-username/aviation-agent

# Test deployed
export AVIATION_ENV_URL=https://your-username-aviation-agent.hf.space
python baseline_inference.py
```

## Support

For deployment issues:
- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- OpenEnv Docs: Check openenv documentation
- Docker Docs: https://docs.docker.com/

Good luck with your hackathon submission! 🚀✈️
