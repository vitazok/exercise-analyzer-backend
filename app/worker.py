from celery import Celery
from app.exercise_v2 import ExerciseAnalyzer
import os

celery_app = Celery(
    "worker",
    broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://redis:6379/0")
)

@celery_app.task
def process_video_task(upload_path, processed_folder):
    analyzer = ExerciseAnalyzer()
    filename = os.path.basename(upload_path)
    processed_path = os.path.join(processed_folder, f"processed_{filename}")

    all_feedback, exercise_type = analyzer.process_video(upload_path, processed_path)
    
    return {
        "exercise_type": exercise_type,
        "feedback": all_feedback,
        "processed_file": processed_path
    }
