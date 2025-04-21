print("🚀 Starting model_digits.py...")

import os
import zipfile
import json
import numpy as np
import pandas as pd
from PIL import Image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import re

# === TRIG UPDATE ===
def write_metrics_to_trig(metrics, template_path="nanopub_example.trig", output_path="nanopub_example.trig"):
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            trig = f.read()

        trig = re.sub(r'ex:hasAccuracy\s+"[\d.]+"', f'ex:hasAccuracy "{metrics["accuracy"]:.4f}"', trig)
        trig = re.sub(r'ex:hasPrecision\s+"[\d.]+"', f'ex:hasPrecision "{metrics["precision"]:.4f}"', trig)
        trig = re.sub(r'ex:hasRecall\s+"[\d.]+"', f'ex:hasRecall "{metrics["recall"]:.4f}"', trig)
        trig = re.sub(r'ex:hasF1Score\s+"[\d.]+"', f'ex:hasF1Score "{metrics["f1"]:.4f}"', trig)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(trig)

        print(f"✅ Updated trig written to {output_path}")
    except Exception as e:
        print("❌ Failed to update trig file:", e)

# === CONFIG ===
ZIP_FILE = "digits_updated.zip"
UNZIPPED_FOLDER = "digits_updated"
IMG_SIZE = (28, 28)
IMG_SHAPE = (28, 28, 1)

# === UNZIP DATASET ===
if not os.path.exists(UNZIPPED_FOLDER):
    print(f"📦 Unzipping {ZIP_FILE}...")
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(".")
    print("✅ Unzipping complete.")
else:
    print("📁 Dataset folder already exists.")

# === Load images ===
X, y = [], []
for label in sorted(os.listdir(UNZIPPED_FOLDER)):
    label_path = os.path.join(UNZIPPED_FOLDER, label)
    if not os.path.isdir(label_path):
        continue
    for img_file in os.listdir(label_path):
        if img_file.endswith(".png"):
            path = os.path.join(label_path, img_file)
            try:
                img = Image.open(path).convert("L").resize(IMG_SIZE)
                img_arr = np.array(img).astype("float32") / 255.0
                X.append(img_arr.reshape(28, 28, 1))
                y.append(int(label))
            except Exception as e:
                print(f"⚠️ Could not load {path}: {e}")

X = np.array(X)
y = np.array(y)
y_cat = to_categorical(y, num_classes=10)

# === Split ===
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# === Build CNN ===
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
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1, callbacks=[EarlyStopping(patience=2)])
model.save("model.h5")
print("✅ CNN model saved.")

# === Save test dataset ===
X_test_flat = X_test.reshape(X_test.shape[0], -1)
y_test_int = np.argmax(y_test, axis=1)
test_df = pd.DataFrame(X_test_flat, columns=[f"pixel_{i}" for i in range(X_test_flat.shape[1])])
test_df["label"] = y_test_int
test_df.to_csv("test_dataset.csv", index=False)
print("✅ Test dataset saved.")

# === Save hyperparameters ===
with open("hyperparameters.json", "w") as f:
    json.dump({
        "model": "CNN",
        "image_shape": IMG_SHAPE,
        "batch_size": 32,
        "epochs": 10
    }, f, indent=2)
print("✅ Hyperparameters saved.")

# === Evaluate and update trig ===
y_pred_prob = model.predict(X_test)
y_pred = np.argmax(y_pred_prob, axis=1)

metrics = {
    "accuracy": accuracy_score(y_test_int, y_pred),
    "precision": precision_score(y_test_int, y_pred, average="weighted", zero_division=0),
    "recall": recall_score(y_test_int, y_pred, average="weighted", zero_division=0),
    "f1": f1_score(y_test_int, y_pred, average="weighted", zero_division=0)
}
write_metrics_to_trig(metrics)
print("🎉 All steps completed successfully.")
