#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

echo "Starting Stepwise services..."

# Start FastAPI backend in the background
echo "Starting FastAPI backend on port 8000..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --app-dir . &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Flask frontend in the background
echo "Starting Flask frontend on port 5000..."
cd interface && python app.py &
FRONTEND_PID=$!
cd ..

echo "Services started!"
echo "Backend (FastAPI): http://localhost:8000"
echo "Frontend (Flask): http://localhost:5000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Set up signal handler
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
