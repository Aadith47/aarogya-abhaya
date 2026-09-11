import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pyttsx3
import os
import threading

# -----------------------------
# LOAD MODEL
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "training", "posture_lstm_model.h5")

model = tf.keras.models.load_model(MODEL_PATH)

# -----------------------------
# MEDIAPIPE SETUP
# -----------------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=0, smooth_landmarks=True)
mp_draw = mp.solutions.drawing_utils

# -----------------------------
# VOICE
# -----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 160)

last_label = ""

def speak_async(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

# -----------------------------
# PARAMETERS
# -----------------------------
SEQUENCE_LENGTH = 30
sequence = []

labels = [
    "Correct Squat",
    "Shallow Squat",
    "Forward Lean",
    "Knees Caving"
]

frame_counter = 0
last_label_display = "Starting..."

# -----------------------------
# REP COUNTERS
# -----------------------------
total_reps = 0
correct_reps = 0
incorrect_reps = 0
squat_phase = "up"

rep_label = "Unknown"

squat_down_hold = 0
squat_up_hold = 0

MIN_DOWN_HOLD = 3
MIN_UP_HOLD = 3

# -----------------------------
# ADJUSTED THRESHOLDS
# -----------------------------
SQUAT_DOWN_KNEE_ANGLE = 135
SQUAT_UP_KNEE_ANGLE = 160

SQUAT_DOWN_HIP_ANGLE = 125
SQUAT_UP_HIP_ANGLE = 155

# -----------------------------
# ANGLE FUNCTION
# -----------------------------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.degrees(np.arccos(cosine))

    return angle

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def run_squat_detection():

    global sequence, frame_counter, last_label_display
    global total_reps, correct_reps, incorrect_reps
    global squat_phase, squat_down_hold, squat_up_hold
    global last_label, rep_label

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():
        print("Camera not detected")
        return

    print("Press 'q' to exit")

    while True:

        ret, frame = cap.read()
        if not ret:
            continue

        frame_counter += 1

        knee_angle = 0
        hip_angle = 0

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:

            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            landmarks = results.pose_landmarks.landmark

            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]

            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)

            # FEATURES
            features = [
                knee_angle, hip_angle,
                shoulder[0], shoulder[1],
                hip[0], hip[1],
                knee[0], knee[1],
                ankle[0], ankle[1],
                frame.shape[0], frame.shape[1]
            ]

            sequence.append(features)

            if len(sequence) > SEQUENCE_LENGTH:
                sequence.pop(0)

            # -----------------------------
            # SQUAT STATE
            # -----------------------------
            squat_down = (knee_angle < SQUAT_DOWN_KNEE_ANGLE and hip_angle < SQUAT_DOWN_HIP_ANGLE)
            squat_up = (knee_angle > SQUAT_UP_KNEE_ANGLE and hip_angle > SQUAT_UP_HIP_ANGLE)

            squat_down_hold = squat_down_hold + 1 if squat_down else 0
            squat_up_hold = squat_up_hold + 1 if squat_up else 0

            # -----------------------------
            # MODEL + OVERRIDE
            # -----------------------------
            if len(sequence) == SEQUENCE_LENGTH and frame_counter % 5 == 0:

                try:
                    input_data = np.expand_dims(sequence, axis=0)
                    prediction = model.predict(input_data, verbose=0)
                    predicted_class = int(np.argmax(prediction))

                    if predicted_class < len(labels):
                        label = labels[predicted_class]
                    else:
                        label = "Unknown"

                    # 🔥 OVERRIDE (important)
                    if knee_angle < 140 and hip_angle < 135:
                        label = "Correct Squat"

                    last_label_display = label

                    # -----------------------------
                    # REP COUNT FIXED
                    # -----------------------------
                    if squat_phase == "up" and squat_down_hold >= MIN_DOWN_HOLD:
                        squat_phase = "down"
                        rep_label = label   # store label at bottom

                    if squat_phase == "down" and squat_up_hold >= MIN_UP_HOLD:
                        squat_phase = "up"
                        total_reps += 1

                        if rep_label == "Correct Squat":
                            correct_reps += 1
                            speak_async("Good rep")
                        else:
                            incorrect_reps += 1
                            speak_async("Fix posture")

                    # -----------------------------
                    # VOICE
                    # -----------------------------
                    if label != last_label:
                        if label == "Correct Squat":
                            speak_async("Good squat")
                        else:
                            speak_async("Adjust posture")

                        last_label = label

                except Exception as e:
                    print("Prediction error:", e)
                    sequence.clear()

        else:
            last_label_display = "No pose"

        # -----------------------------
        # DISPLAY
        # -----------------------------
        cv2.putText(frame, last_label_display, (20,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)

        cv2.putText(frame, f"Knee: {int(knee_angle)}", (20,80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

        cv2.putText(frame, f"Hip: {int(hip_angle)}", (20,105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

        cv2.putText(frame, f"Reps: {total_reps}", (20,130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.putText(frame, f"Correct: {correct_reps}", (20,155),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.putText(frame, f"Incorrect: {incorrect_reps}", (20,180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        cv2.imshow("Squat Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    run_squat_detection()