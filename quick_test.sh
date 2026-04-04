#!/bin/bash
# Quick test script for Aviation Agent environment

set -e  # Exit on error

echo "=========================================="
echo "Aviation Agent - Quick Test Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify submission
echo -e "${YELLOW}Step 1: Verifying submission...${NC}"
python verify_submission.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Verification passed${NC}"
else
    echo -e "${RED}✗ Verification failed${NC}"
    exit 1
fi
echo ""

# Step 2: Test environment logic
echo -e "${YELLOW}Step 2: Testing environment logic...${NC}"
python Aviation_Agent/test_environment.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Environment tests passed${NC}"
else
    echo -e "${RED}✗ Environment tests failed${NC}"
    exit 1
fi
echo ""

# Step 3: Validate OpenEnv compliance
echo -e "${YELLOW}Step 3: Validating OpenEnv compliance...${NC}"
cd Aviation_Agent
openenv validate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ OpenEnv validation passed${NC}"
else
    echo -e "${RED}✗ OpenEnv validation failed${NC}"
    exit 1
fi
cd ..
echo ""

# Step 4: Test graders
echo -e "${YELLOW}Step 4: Testing task graders...${NC}"
python Aviation_Agent/task_graders.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Grader tests passed${NC}"
else
    echo -e "${RED}✗ Grader tests failed${NC}"
    exit 1
fi
echo ""

# Step 5: Start server in background
echo -e "${YELLOW}Step 5: Starting server...${NC}"
cd Aviation_Agent
uvicorn server.app:app --host 0.0.0.0 --port 8000 > /tmp/aviation_server.log 2>&1 &
SERVER_PID=$!
cd ..

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}✗ Server failed to start${NC}"
    cat /tmp/aviation_server.log
    exit 1
fi
echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
echo ""

# Step 6: Test health endpoint
echo -e "${YELLOW}Step 6: Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    kill $SERVER_PID
    exit 1
fi
echo ""

# Step 7: Test reset endpoint
echo -e "${YELLOW}Step 7: Testing reset endpoint...${NC}"
RESET_RESPONSE=$(curl -s -X POST http://localhost:8000/reset)
if echo "$RESET_RESPONSE" | grep -q "atc_instruction"; then
    echo -e "${GREEN}✓ Reset endpoint works${NC}"
else
    echo -e "${RED}✗ Reset endpoint failed${NC}"
    kill $SERVER_PID
    exit 1
fi
echo ""

# Step 8: Test with Python client
echo -e "${YELLOW}Step 8: Testing with Python client...${NC}"
python -c "
from Aviation_Agent import AviationAgentEnv, AviationAgentAction
with AviationAgentEnv(base_url='http://localhost:8000') as env:
    obs = env.reset()
    result = env.step(AviationAgentAction(message='Descend FL180, Speedbird 247'))
    assert result.observation.metadata['score'] > 0, 'Score should be > 0'
    print('✓ Client test passed')
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python client test passed${NC}"
else
    echo -e "${RED}✗ Python client test failed${NC}"
    kill $SERVER_PID
    exit 1
fi
echo ""

# Step 9: Test inference script (if API key is set)
if [ -n "$OPENAI_API_KEY" ] || [ -n "$HF_TOKEN" ]; then
    echo -e "${YELLOW}Step 9: Testing inference script...${NC}"
    python inference.py > /tmp/inference_output.log 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Inference script passed${NC}"
        # Check for structured logs
        if grep -q '"type": "START"' /tmp/inference_output.log && \
           grep -q '"type": "STEP"' /tmp/inference_output.log && \
           grep -q '"type": "END"' /tmp/inference_output.log; then
            echo -e "${GREEN}✓ Structured logging format correct${NC}"
        else
            echo -e "${YELLOW}⚠ Warning: Structured logging format may be incorrect${NC}"
        fi
    else
        echo -e "${RED}✗ Inference script failed${NC}"
        cat /tmp/inference_output.log
        kill $SERVER_PID
        exit 1
    fi
else
    echo -e "${YELLOW}Step 9: Skipping inference test (no API key set)${NC}"
    echo "Set OPENAI_API_KEY or HF_TOKEN to test inference"
fi
echo ""

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
kill $SERVER_PID
echo -e "${GREEN}✓ Server stopped${NC}"
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Build Docker: docker build -t aviation-agent-env:latest -f Aviation_Agent/server/Dockerfile Aviation_Agent"
echo "2. Test Docker: docker run -p 8000:8000 aviation-agent-env:latest"
echo "3. Deploy to HF: cd Aviation_Agent && openenv push --repo-id your-username/aviation-agent"
echo ""
