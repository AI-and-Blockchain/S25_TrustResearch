print("🚀 Starting model_digits.py with CNN...")

import os
import json
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model

# === Config ===
IMG_SIZE = (28, 28)
IMG_SHAPE = (28, 28, 1)
DATA_DIR = "digits_updated"
MODEL_FILE = "model.h5"
TEST_FILE = "test_dataset.csv"
HYPERPARAM_FILE = "hyperparameters.json"

# === Load images ===
X = []
y = []

print("📂 Loading digit images...")
for label in sorted(os.listdir(DATA_DIR)):
    folder = os.path.join(DATA_DIR, label)
    if not os.path.isdir(folder):
        continue
    for filename in os.listdir(folder):
        if filename.endswith(".png"):
            path = os.path.join(folder, filename)
            try:
                img = Image.open(path).convert("L").resize(IMG_SIZE)
                img_arr = np.array(img).astype("float32") / 255.0
                X.append(img_arr.reshape(28, 28, 1))
                y.append(int(label))
            except Exception as e:
                print(f"⚠️ Error loading {path}: {e}")

X = np.array(X)
y = np.array(y)
print(f"✅ Loaded {X.shape[0]} images of shape {X.shape[1:]}")

# === Encode labels ===
y_cat = to_categorical(y, num_classes=10)

# === Split ===
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)
print("✅ Dataset split into train/test sets.")

# === Build CNN model ===
print("⚙️ Building CNN model...")
model = Sequential([
    Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=IMG_SHAPE),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(10, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
print("✅ Model compiled.")

# === Train model ===
print("⏳ Training CNN...")
model.fit(X_train, y_train, epochs=10, batch_size=32,
          validation_split=0.1, callbacks=[EarlyStopping(patience=3)])
print("✅ Model trained.")

# === Save model ===
model.save(MODEL_FILE)
print(f"✅ CNN model saved as {MODEL_FILE}")

# === Save test dataset ===
X_test_flat = X_test.reshape(X_test.shape[0], -1)
test_labels = np.argmax(y_test, axis=1)
test_df = pd.DataFrame(X_test_flat, columns=[f"pixel_{i}" for i in range(X_test_flat.shape[1])])
test_df["label"] = test_labels
test_df.to_csv(TEST_FILE, index=False)
print(f"✅ Test dataset saved as {TEST_FILE}")

# === Save hyperparameters ===
with open(HYPERPARAM_FILE, "w") as f:
    json.dump({
        "model": "CNN",
        "input_shape": IMG_SHAPE,
        "image_size": IMG_SIZE,
        "epochs": 10,
        "batch_size": 32
    }, f, indent=2)
print(f"✅ Hyperparameters saved as {HYPERPARAM_FILE}")

print("🎉 All steps completed successfully.")
