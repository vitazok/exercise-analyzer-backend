from fastapi import FastAPI, UploadFile, File
import os
import uuid
from app.worker import process_video_task, celery_app
from celery.result import AsyncResult

app = FastAPI()

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Exercise API Backend is running"}

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_filename = f"{file_id}_{file.filename}"
    upload_path = os.path.join(UPLOAD_FOLDER, input_filename)

    with open(upload_path, "wb") as f:
        f.write(await file.read())

    task = process_video_task.delay(upload_path, PROCESSED_FOLDER)
    return {"message": "Job submitted", "job_id": task.id}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    res = AsyncResult(job_id, app=celery_app)
    if res.state == "PENDING":
        return {"status": "pending"}
    elif res.state == "SUCCESS":
        return {"status": "completed", "result": res.result}
    elif res.state == "FAILURE":
        return {"status": "failed", "error": str(res.info)}
    else:
        return {"status": res.state}
