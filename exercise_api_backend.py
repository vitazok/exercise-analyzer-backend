from fastapi import FastAPI, File, UploadFile
import os
import uuid
from app.exercise_v2 import ExerciseAnalyzer

app = FastAPI()

# Create folders if they don't exist
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Initialize the analyzer
analyzer = ExerciseAnalyzer()

@app.get("/")
async def root():
    return {"message": "Exercise API Backend is running"}

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    # Generate unique filenames
    file_id = str(uuid.uuid4())
    input_filename = f"{file_id}_{file.filename}"

    # Save uploaded file
    upload_path = os.path.join(UPLOAD_FOLDER, input_filename)
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    # Submit the task to Celery worker
    from app.worker import process_video_task  # import here or at top
    task = process_video_task.delay(upload_path, PROCESSED_FOLDER)

    return {
        "message": "Job submitted",
        "job_id": task.id
    }
