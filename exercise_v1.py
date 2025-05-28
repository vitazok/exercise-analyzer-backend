import cv2
import mediapipe as mp
import numpy as np
import math
import json
from datetime import datetime

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

        # Exercise-specific ideal angles and positions
        self.exercise_standards = {
            'pushup': {
                'bottom_elbow_angle': (80, 95),  # degrees
                'top_elbow_angle': (160, 180),
                'back_alignment': 10,  # max deviation from straight line
                'hip_alignment': 15
            },
            'squat': {
                'bottom_knee_angle': (80, 100),
                'bottom_hip_angle': (80, 110),
                'back_angle': (70, 90),  # angle from vertical
                'knee_tracking': 20  # knees shouldn't cave in
            },
            'pullup': {
                'bottom_elbow_angle': (160, 180),
                'top_elbow_angle': (30, 60),
                'shoulder_engagement': True,
                'body_swing': 15  # max degrees
            }
        }

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def detect_exercise_type(self, landmarks):
        """Automatically detect exercise type based on body position"""
        # Get key landmarks
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]

        # Calculate relative positions
        shoulder_height = (left_shoulder.y + right_shoulder.y) / 2
        hip_height = left_hip.y
        knee_height = left_knee.y
        ankle_height = left_ankle.y

        # Detection logic
        if shoulder_height > hip_height and abs(shoulder_height - ankle_height) < 0.3:
            return 'pushup'
        elif knee_height > ankle_height and hip_height > knee_height:
            return 'squat'
        elif shoulder_height < hip_height and abs(left_shoulder.y - right_shoulder.y) < 0.1:
            return 'pullup'
        else:
            return 'general'

    def analyze_pushup_form(self, landmarks, frame_shape):
        """Analyze pushup form and provide feedback"""
        feedback = []

        # Get key landmarks
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]

        # Convert to pixel coordinates
        h, w = frame_shape[:2]
        points = {
            'shoulder': [left_shoulder.x * w, left_shoulder.y * h],
            'elbow': [left_elbow.x * w, left_elbow.y * h],
            'wrist': [left_wrist.x * w, left_wrist.y * h],
            'hip': [left_hip.x * w, left_hip.y * h],
            'knee': [left_knee.x * w, left_knee.y * h],
            'ankle': [left_ankle.x * w, left_ankle.y * h]
        }

        # Calculate elbow angle
        elbow_angle = self.calculate_angle(points['shoulder'], points['elbow'], points['wrist'])

        # Calculate body alignment (should be straight line)
        body_angle = self.calculate_angle(points['shoulder'], points['hip'], points['ankle'])

        # Provide feedback
        if elbow_angle < 80:
            feedback.append("✓ Good depth - elbows at proper angle")
        elif elbow_angle > 120:
            feedback.append("⚠ Too shallow - lower your chest more")

        if abs(body_angle - 180) > 15:
            if points['hip'][1] > points['shoulder'][1] + 20:
                feedback.append("⚠ Hips too high - keep body straight")
            else:
                feedback.append("⚠ Hips sagging - engage your core")
        else:
            feedback.append("✓ Good body alignment")

        return feedback, elbow_angle, body_angle

    def analyze_squat_form(self, landmarks, frame_shape):
        """Analyze squat form and provide feedback"""
        feedback = []

        # Get key landmarks
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]

        # Convert to pixel coordinates
        h, w = frame_shape[:2]
        points = {
            'hip': [left_hip.x * w, left_hip.y * h],
            'knee': [left_knee.x * w, left_knee.y * h],
            'ankle': [left_ankle.x * w, left_ankle.y * h],
            'shoulder': [left_shoulder.x * w, left_shoulder.y * h]
        }

        # Calculate knee angle
        knee_angle = self.calculate_angle(points['hip'], points['knee'], points['ankle'])

        # Calculate hip angle (thigh to torso)
        hip_angle = self.calculate_angle(points['knee'], points['hip'], points['shoulder'])

        # Depth check
        if knee_angle < 90:
            feedback.append("✓ Excellent depth - below parallel")
        elif knee_angle < 110:
            feedback.append("✓ Good depth - at parallel")
        else:
            feedback.append("⚠ Too shallow - squat deeper")

        # Knee tracking
        if points['knee'][0] < points['ankle'][0] - 20:
            feedback.append("⚠ Knees caving in - push knees out")
        else:
            feedback.append("✓ Good knee tracking")

        return feedback, knee_angle, hip_angle

    def create_ideal_ghost(self, exercise_type, frame_shape, phase='bottom'):
        """Create ideal exercise form overlay"""
        h, w = frame_shape[:2]
        ghost_landmarks = {}

        if exercise_type == 'pushup':
            if phase == 'bottom':
                # Ideal pushup bottom position (normalized coordinates)
                ghost_landmarks = {
                    'nose': [0.5, 0.2],
                    'left_shoulder': [0.45, 0.25],
                    'right_shoulder': [0.55, 0.25],
                    'left_elbow': [0.35, 0.35],
                    'right_elbow': [0.65, 0.35],
                    'left_wrist': [0.25, 0.25],
                    'right_wrist': [0.75, 0.25],
                    'left_hip': [0.45, 0.5],
                    'right_hip': [0.55, 0.5],
                    'left_knee': [0.45, 0.75],
                    'right_knee': [0.55, 0.75],
                    'left_ankle': [0.45, 0.9],
                    'right_ankle': [0.55, 0.9]
                }
            else:  # top position
                ghost_landmarks = {
                    'nose': [0.5, 0.15],
                    'left_shoulder': [0.45, 0.2],
                    'right_shoulder': [0.55, 0.2],
                    'left_elbow': [0.4, 0.25],
                    'right_elbow': [0.6, 0.25],
                    'left_wrist': [0.35, 0.2],
                    'right_wrist': [0.65, 0.2],
                    'left_hip': [0.45, 0.45],
                    'right_hip': [0.55, 0.45],
                    'left_knee': [0.45, 0.7],
                    'right_knee': [0.55, 0.7],
                    'left_ankle': [0.45, 0.85],
                    'right_ankle': [0.55, 0.85]
                }

        # Convert normalized coordinates to pixel coordinates
        pixel_landmarks = {}
        for key, coords in ghost_landmarks.items():
            pixel_landmarks[key] = [int(coords[0] * w), int(coords[1] * h)]

        return pixel_landmarks

    def process_video(self, video_path, output_path=None):
        """Process video and analyze exercise form"""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video file")
            return

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Setup video writer if output path provided
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        frame_count = 0
        exercise_detected = None
        all_feedback = []

        print("Processing video...")
        print(f"Total frames: {total_frames}")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 30 == 0:  # Progress update every 30 frames
                print(f"Processed {frame_count}/{total_frames} frames")

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process frame
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                # Auto-detect exercise type on first detection
                if exercise_detected is None:
                    exercise_detected = self.detect_exercise_type(results.pose_landmarks.landmark)
                    print(f"Detected exercise: {exercise_detected}")

                # Analyze form based on exercise type
                feedback = []
                if exercise_detected == 'pushup':
                    feedback, elbow_angle, body_angle = self.analyze_pushup_form(
                        results.pose_landmarks.landmark, frame.shape
                    )
                elif exercise_detected == 'squat':
                    feedback, knee_angle, hip_angle = self.analyze_squat_form(
                        results.pose_landmarks.landmark, frame.shape
                    )

                all_feedback.extend(feedback)

                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

                # Draw ideal ghost overlay (semi-transparent)
                ghost_overlay = frame.copy()
                ideal_landmarks = self.create_ideal_ghost(exercise_detected, frame.shape)

                # Draw ghost connections
                connections = [
                    ('left_shoulder', 'left_elbow'), ('left_elbow', 'left_wrist'),
                    ('right_shoulder', 'right_elbow'), ('right_elbow', 'right_wrist'),
                    ('left_shoulder', 'right_shoulder'),
                    ('left_shoulder', 'left_hip'), ('right_shoulder', 'right_hip'),
                    ('left_hip', 'right_hip'),
                    ('left_hip', 'left_knee'), ('left_knee', 'left_ankle'),
                    ('right_hip', 'right_knee'), ('right_knee', 'right_ankle')
                ]

                for connection in connections:
                    if connection[0] in ideal_landmarks and connection[1] in ideal_landmarks:
                        pt1 = tuple(ideal_landmarks[connection[0]])
                        pt2 = tuple(ideal_landmarks[connection[1]])
                        cv2.line(ghost_overlay, pt1, pt2, (255, 255, 0), 3)  # Yellow ghost

                # Draw ghost points
                for point in ideal_landmarks.values():
                    cv2.circle(ghost_overlay, tuple(point), 5, (255, 255, 0), -1)

                # Blend ghost overlay
                cv2.addWeighted(ghost_overlay, 0.3, frame, 0.7, 0, frame)

                # Add feedback text
                y_offset = 30
                for i, fb in enumerate(feedback[-3:]):  # Show last 3 feedback items
                    cv2.putText(frame, fb, (10, y_offset + i * 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Write frame if output specified
            if output_path:
                out.write(frame)

            # Display frame (optional - comment out if running headless)
            cv2.imshow('Exercise Analysis', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        if output_path:
            out.release()
        cv2.destroyAllWindows()

        # Generate final report
        self.generate_report(exercise_detected, all_feedback, total_frames)

    def generate_report(self, exercise_type, feedback_list, total_frames):
        """Generate comprehensive analysis report"""
        print("\n" + "="*50)
        print("EXERCISE ANALYSIS REPORT")
        print("="*50)
        print(f"Exercise Detected: {exercise_type.upper()}")
        print(f"Total Frames Analyzed: {total_frames}")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Count positive vs negative feedback
        positive_feedback = [f for f in feedback_list if f.startswith('✓')]
        warning_feedback = [f for f in feedback_list if f.startswith('⚠')]

        print(f"\nFeedback Summary:")
        print(f"✓ Positive points: {len(positive_feedback)}")
        print(f"⚠ Areas for improvement: {len(warning_feedback)}")

        # Most common feedback
        from collections import Counter
        feedback_counter = Counter(feedback_list)

        print(f"\nMost Common Feedback:")
        for feedback, count in feedback_counter.most_common(5):
            percentage = (count / len(feedback_list)) * 100
            print(f"  {feedback} ({percentage:.1f}% of time)")

        # Exercise-specific recommendations
        print(f"\nScience-Based Recommendations for {exercise_type.upper()}:")

        if exercise_type == 'pushup':
            print("• Maintain straight line from head to heels")
            print("• Lower chest to within 2-4 inches of ground")
            print("• Keep elbows at 45° angle to body")
            print("• Engage core throughout movement")
            print("• Control both lowering and pressing phases")

        elif exercise_type == 'squat':
            print("• Descend until hip crease below knee cap")
            print("• Keep knees tracking over toes")
            print("• Maintain neutral spine throughout")
            print("• Drive through heels on ascent")
            print("• Keep chest up and core engaged")

        elif exercise_type == 'pullup':
            print("• Achieve full arm extension at bottom")
            print("• Pull chin over bar at top")
            print("• Minimize body swing and momentum")
            print("• Engage lats and rhomboids")
            print("• Control the descent (eccentric phase)")

        print("\nReport saved to console. Video analysis complete!")

# Main execution function
def main():
    print("Exercise Form Analyzer")
    print("=====================")

    # Get video file path from user
    video_path = input("Enter path to your exercise video: ").strip().strip('"')

    # Ask for output video path (optional)
    save_output = input("Save analyzed video? (y/n): ").lower().strip()
    output_path = None
    if save_output == 'y':
        output_path = input("Enter output video path (e.g., analyzed_video.mp4): ").strip()

    # Create analyzer and process video
    analyzer = ExerciseAnalyzer()
    analyzer.process_video(video_path, output_path)

if __name__ == "__main__":
    main()
