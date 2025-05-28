# Exercise Analyzer Backend

This is a FastAPI backend for analyzing exercise videos using pose detection (mediapipe).

## Local Setup

1. Clone the repo:
   git clone https://github.com/yourusername/exercise-analyzer-backend.git

2. Navigate to the folder:
   cd exercise-analyzer-backend

3. Create virtual environment:
   python3 -m venv venv
   source venv/bin/activate

4. Install packages:
   pip install -r requirements.txt

5. Run the server:
   uvicorn exercise_api_backend:app --host 0.0.0.0 --port 8000 --reload

## Cloud Deployment (Railway)

1. Create a Railway account: https://railway.app
2. Click 'New Project' > 'Deploy from GitHub'
3. Select this repo
4. Set start command:
   uvicorn exercise_api_backend:app --host 0.0.0.0 --port $PORT
5. Deploy and test the public URL!
