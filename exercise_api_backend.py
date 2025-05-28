from fastapi import FastAPI, File, UploadFile
import os
import uuid
from exercise_v2 import ExerciseAnalyzer

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
    processed_filename = f"processed_{file.filename}"

    # Save uploaded file
    upload_path = os.path.join(UPLOAD_FOLDER, input_filename)
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    # Define output path
    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)

    # Run the exercise analysis
    all_feedback, exercise_type = analyzer.process_video(upload_path, processed_path)

    # Prepare summary report
    report = {
        "exercise_type": exercise_type,
        "feedback": all_feedback,
        "summary": f"Analysis completed for {exercise_type}"
    }

    return {
        "message": "File received and processed successfully",
        "input_file": upload_path,
        "processed_file": processed_path,
        "report": report
    }
