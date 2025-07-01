#!/bin/bash

# Get the port from environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting uvicorn on port $PORT"
echo "Current directory: $(pwd)"
echo "Available files: $(ls -la)"
echo "Python version: $(python --version)"

# Check if the app module can be imported
echo "Testing app import..."
python -c "from app.main import app; print('App imported successfully')" || {
    echo "ERROR: Failed to import app"
    python -c "from app.main import app" 2>&1
    exit 1
}

echo "Starting uvicorn with verbose logging..."
# Start the FastAPI application with more verbose output
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug 