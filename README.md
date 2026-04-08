# Aviation Agent - ATC Communication Training Environment

An Agentic AI system that learns from ATC-pilot communication patterns and enables AI agents (and trainee pilots) to practice, interpret, and generate accurate responses in simulated flight scenarios with automated evaluation of correctness and adherence to aviation communication standards.

We model ATC communication as a sequential decision-making problem using OpenEnv, where an agent learns optimal aviation phraseology through interaction and graded feedback.

**Meta x Hugging Face OpenEnv Hackathon Submission**

## Quick Start

```bash
# 1. Test the environment
python Aviation_Agent/test_environment.py

# 2. Start the server
cd Aviation_Agent
uvicorn server.app:app --host 0.0.0.0 --port 8000

# 3. Run inference (in another terminal)
export OPENAI_API_KEY=your_key_here
python inference.py
```

## Project Structure

- **`inference.py`** - Main inference script (hackathon submission)
- **`Aviation_Agent/`** - OpenEnv environment package
  - `README.md` - Complete documentation
  - `server/` - FastAPI server and environment logic
  - `models.py` - Pydantic models
  - `task_graders.py` - Task grading logic
- **Documentation**:
  - `SERIAL_TESTING_STEPS.md` - Step-by-step testing guide
  - `DEPLOYMENT_GUIDE.md` - HF Spaces deployment
  - `HACKATHON_SUBMISSION.md` - Submission checklist

## Documentation

📖 **Start here**: [Aviation_Agent/README.md](Aviation_Agent/README.md)

📋 **Testing**: [SERIAL_TESTING_STEPS.md](SERIAL_TESTING_STEPS.md)

🚀 **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

✅ **Submission**: [HACKATHON_SUBMISSION.md](HACKATHON_SUBMISSION.md)

## Environment Description

A reinforcement learning environment that simulates Air Traffic Control (ATC) radio communication, designed to train AI agents to master aviation communication standards.

## Architecture workflow

ATC → Environment → Agent → Response → Grader → Reward → Learning

### Training Objectives

**Primary Goal**: Train AI agents to learn proper ATC-pilot communication patterns through:
- **Pattern Recognition**: Understanding aviation phraseology requirements
- **Response Generation**: Producing accurate, standards-compliant responses
- **Progressive Learning**: Mastering increasingly complex scenarios
- **Automated Feedback**: Receiving immediate evaluation on correctness

### Use Cases

1. **AI Agent Training** (Primary): 
   - Train reinforcement learning agents to communicate like professional pilots
   - Learn from reward signals based on communication accuracy
   - Progress from simple to complex scenarios

2. **Human Pilot Training** (Secondary):
   - Trainee pilots can practice via web interface (`/web`)
   - Receive instant feedback on response quality
   - Learn proper aviation phraseology

### Simulated Flight Scenarios

**3 Progressive Training Tasks**:
- **Task 1 (Easy)**: Single altitude change - Learn basic read-back procedures
- **Task 2 (Medium)**: Heading + altitude change - Master multi-element instructions
- **Task 3 (Hard)**: Traffic alert with maneuver - Handle complex, safety-critical communications

### Automated Evaluation System

**Standards-Based Grading**:
- ✅ Callsign acknowledgment (aviation standard)
- ✅ Accurate read-back of clearances (safety requirement)
- ✅ Proper phraseology (ICAO standards)
- ✅ Complete response elements (no missing information)

**Learning Signals**:
- Scores: 0.0-1.0 (deterministic, reproducible)
- Rewards: Trajectory-level feedback for RL training
- Metadata: Detailed breakdown of what was correct/incorrect

## Requirements Met

✅ **Agentic AI system** - RL environment for training AI agents  
✅ **Learns from communication patterns** - Reward-based learning signals  
✅ **Practice environment** - Multiple scenarios with progressive difficulty  
✅ **Interpret & generate responses** - AI generates pilot responses, system interprets correctness  
✅ **Simulated flight scenarios** - 3 realistic ATC situations  
✅ **Automated evaluation** - Programmatic graders with deterministic scoring  
✅ **Aviation standards adherence** - Checks proper phraseology and ICAO compliance  
✅ **OpenEnv spec compliance** - Full implementation with typed models  
✅ **Docker containerization** - Production-ready deployment  
✅ **Complete documentation** - Comprehensive guides and examples  

## Future Enhancements

Future work includes integrating real ATC datasets and fine-tuning domain-specific LLMs for aviation communication

## Testing

```bash
# Quick verification
python verify_submission.py

# Full test suite
./quick_test.sh  # Linux/Mac
```

## Deployment

```bash
cd Aviation_Agent
openenv push --repo-id your-username/aviation-agent
```

## License

See individual files for license information.