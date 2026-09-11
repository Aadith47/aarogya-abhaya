import pandas as pd
from pathlib import Path

# backend/training
BASE_DIR = Path(__file__).resolve().parent

# Go to project root → dataset
DATASET_DIR = (BASE_DIR / ".." / ".." / "dataset").resolve()

print("Dataset directory:", DATASET_DIR)
print("Exists:", DATASET_DIR.exists())

# List files
print("Files found:", list(DATASET_DIR.iterdir()))

# Pick CSV automatically
csv_files = list(DATASET_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV file found in dataset folder")

DATASET_PATH = csv_files[0]

print("Using dataset:", DATASET_PATH)

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully")
print("Shape:", df.shape)
print("Columns:", df.columns)

import numpy as np

# Separate features and labels
X = df.drop(columns=["label", "video_file", "frame"], errors="ignore").values
y = df["label"].values

print("X shape:", X.shape)
print("y shape:", y.shape)

# Save for next step
np.save("X_raw.npy", X)
np.save("y_raw.npy", y)
