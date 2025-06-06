#!/bin/bash

cd ~/stockaffirm-agent || exit 1

# Activate virtual environment
source .venv/bin/activate

# Start Ollama in background if not already running
if ! pgrep -f "ollama serve" > /dev/null; then
  echo "Starting Ollama..."
  ollama serve &
  sleep 3
fi

# Launch the FastAPI agent
echo "Starting StockAffirm API Server..."
uvicorn main:app --host 0.0.0.0 --port 8501
