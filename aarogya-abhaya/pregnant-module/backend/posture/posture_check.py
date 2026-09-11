import cv2
import mediapipe as mp
import numpy as np
import tempfile

mp_pose = mp.solutions.pose

def analyze_posture(file):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(file.file.read())
        video_path = temp.name

    cap = cv2.VideoCapture(video_path)
    posture_ok = True

    with mp_pose.Pose(static_image_mode=False) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]

                angle = calculate_angle(shoulder, hip, knee)

                if angle < 70 or angle > 160:
                    posture_ok = False
                    break

    cap.release()

    if posture_ok:
        return {
            "status": "Correct",
            "message": "Good posture. Keep your back straight."
        }
    else:
        return {
            "status": "Incorrect",
            "message": "Please straighten your back and avoid bending."
        }

def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = abs(radians * 180.0 / np.pi)
    return angle
