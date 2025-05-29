
Exercise Analyzer Backend
=========================

A FastAPI + Celery + Redis backend to analyze exercise videos and generate posture feedback, with Railway deployment.

-------------------------------------------------------------

🚀 Features
-----------
✅ Upload exercise videos
✅ Analyze posture + technique
✅ Return processed videos + feedback report
✅ Background job processing with Celery
✅ REST API endpoints (upload, status check)
✅ Docker + Railway deploy ready

-------------------------------------------------------------

📂 Project Structure
---------------------
/app
    main.py            → FastAPI app
    worker.py          → Celery worker
    exercise_v2.py     → Exercise analyzer logic
Dockerfile
docker-compose.yml
requirements.txt
README.md

-------------------------------------------------------------

💻 Local Development
---------------------

1️⃣ Install Docker
- Docker Desktop → https://www.docker.com/products/docker-desktop
- Check Docker Compose → docker compose --version

2️⃣ Build + Run
docker compose up --build

- FastAPI → http://localhost:8000
- Redis runs in container
- Celery worker in background

3️⃣ API Endpoints
- POST /analyze → upload video
- GET /status/{job_id} → check status

Swagger docs:
http://localhost:8000/docs

-------------------------------------------------------------

☁ Railway Deployment
----------------------

Prerequisites:
- Railway account → https://railway.app
- Connected GitHub repo
- Env var: REDIS_URL=redis://redis:6379/0

Steps:
1️⃣ Link GitHub to Railway
2️⃣ Use Dockerfile deploy
3️⃣ Start command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT

4️⃣ Set up Redis (plugin/container)
5️⃣ Get public domain (e.g., https://exercise-analyzer-backend.up.railway.app)
6️⃣ Visit /docs to test API

-------------------------------------------------------------

⚙ Common Commands
------------------

- View logs:
docker compose logs -f

- Prune Docker:
docker system prune -a

- Restart containers:
docker compose down && docker compose up --build

-------------------------------------------------------------

❗ Troubleshooting
------------------

✅ Builds hang → restart Docker Desktop
✅ Railway build fails → check failing package
✅ Large .venv → use .dockerignore to exclude

-------------------------------------------------------------

🌟 Next Features
-----------------

- ✅ Celery background worker
- ⏳ Flutter frontend app
- ⏳ Video progress tracking
- ⏳ User sessions + storage

Maintained by: https://github.com/vitazok
