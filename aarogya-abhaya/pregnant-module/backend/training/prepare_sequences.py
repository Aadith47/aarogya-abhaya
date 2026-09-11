import numpy as np

SEQUENCE_LENGTH = 30

X = np.load("X_raw.npy")
y = np.load("y_raw.npy")

X_seq, y_seq = [], []

for i in range(len(X) - SEQUENCE_LENGTH):
    X_seq.append(X[i:i+SEQUENCE_LENGTH])
    y_seq.append(y[i+SEQUENCE_LENGTH])

X_seq = np.array(X_seq)
y_seq = np.array(y_seq)

print("X_seq shape:", X_seq.shape)
print("y_seq shape:", y_seq.shape)

np.save("X_seq.npy", X_seq)
np.save("y_seq.npy", y_seq)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X_seq, y_seq, test_size=0.2, random_state=42, stratify=y_seq
)

np.save("X_train.npy", X_train)
np.save("X_test.npy", X_test)
np.save("y_train.npy", y_train)
np.save("y_test.npy", y_test)

print("Train/Test split completed")

sequence_buffer.append(features)

if len(sequence_buffer) == 30:
    X = np.array(sequence_buffer)
    X = np.expand_dims(X, axis=0)  # (1, 30, 12)

    prediction = model.predict(X, verbose=0)
    class_id = np.argmax(prediction)
