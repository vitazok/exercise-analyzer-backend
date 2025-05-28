import cv2
import mediapipe as mp
import numpy as np
import os

class ExerciseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_video(self, video_path, output_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video: {video_path}")
            return [], "unknown"

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        frame_count = 0
        all_feedback = []
        exercise_detected = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                # Detect exercise type on first valid frame
                if exercise_detected is None:
                    exercise_detected = "general"  # default (or use detection logic here)

                feedback = [f"✓ Frame {frame_count}: Good posture (mock feedback)"]
                all_feedback.extend(feedback)

                # Draw landmarks on frame
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

            out.write(frame)

        cap.release()
        out.release()

        # Remove duplicates from feedback
        unique_feedback = list(set(all_feedback))

        if exercise_detected is None:
            exercise_detected = "unknown"

        return unique_feedback, exercise_detected
