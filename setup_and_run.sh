#!/bin/bash

# Navigate to project directory
cd /Users/vitazok/Desktop/Rabotenka/Exercise || { echo "❌ Directory not found!"; exit 1; }
echo "✅ Moved to project directory: $(pwd)"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python 3.13 virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated."

# Install required packages
echo "📦 Installing required Python packages..."
pip install --upgrade pip
pip install fastapi uvicorn python-multipart opencv-python mediapipe numpy

# Start the backend server
echo "🚀 Starting FastAPI server with Uvicorn..."
uvicorn exercise_api_backend:app --host 0.0.0.0 --port 8000 --reload
