from fastapi import FastAPI, File, UploadFile
import os
import uuid
from app.exercise_v2 import ExerciseAnalyzer
from app.worker import process_video_task, celery_app

app = FastAPI()

# Create folders if they don't exist
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Initialize the analyzer (if used locally, not by Celery)
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
    task = process_video_task.delay(upload_path, PROCESSED_FOLDER)

    return {
        "message": "Job submitted",
        "job_id": task.id
    }

@app.get("/status/{job_id}")
def get_task_status(job_id: str):
    task_result = celery_app.AsyncResult(job_id)
    if task_result.state == "PENDING":
        return {"status": "pending"}
    elif task_result.state == "SUCCESS":
        return {
            "status": "completed",
            "result": task_result.result
        }
    elif task_result.state == "FAILURE":
        return {
            "status": "failed",
            "error": str(task_result.info)
        }
    else:
        return {"status": task_result.state}
