import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

# -----------------------------
# Load trained model
# -----------------------------
model = load_model("posture_lstm_model.h5")
print("Model loaded successfully")

# -----------------------------
# Load test data
# -----------------------------
X_test = np.load("X_test.npy")
y_test = np.load("y_test.npy")

print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)

# -----------------------------
# Predict
# -----------------------------
y_pred_prob = model.predict(X_test)
y_pred = np.argmax(y_pred_prob, axis=1)

# -----------------------------
# Accuracy
# -----------------------------
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy * 100:.2f} %")

# -----------------------------
# Confusion Matrix
# -----------------------------
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# -----------------------------
# Classification Report
# -----------------------------
class_names = [
    "Correct Squat",
    "Shallow Squat",
    "Forward Lean",
    "Knees Caving In",
    "Class 4",
    "Class 5"
]

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=class_names))
