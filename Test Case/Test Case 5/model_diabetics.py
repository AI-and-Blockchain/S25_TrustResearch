print("🚀 Starting model_diabetes.py...")

import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# === File paths ===
DATA_FILE = "diabetes.csv"
MODEL_FILE = "model.h5"
TEST_FILE = "test_dataset.csv"
HYPERPARAM_FILE = "hyperparameters.json"

# === Load dataset ===
try:
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded {DATA_FILE} successfully.")
except Exception as e:
    print(f"❌ Failed to read {DATA_FILE}:", e)
    exit(1)

# === Prepare features and labels ===
try:
    X = df.drop(columns=["Outcome"])
    y = df["Outcome"]
    print("✅ Feature matrix and labels prepared.")
except Exception as e:
    print(f"❌ Error processing columns:", e)
    exit(1)

# === Preprocess ===
X = StandardScaler().fit_transform(X)

# === Split dataset ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("✅ Dataset split into train/test sets.")

# === Train model ===
print("⏳ Training model...")
try:
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    print("✅ Model trained.")
except Exception as e:
    print("❌ Model training failed:", e)
    exit(1)

# === Save model ===
try:
    joblib.dump(model, MODEL_FILE)
    print(f"✅ Model saved as {MODEL_FILE}")
except Exception as e:
    print("❌ Failed to save model:", e)

# === Save test dataset ===
try:
    test_df = pd.DataFrame(X_test, columns=[f"feature_{i}" for i in range(X.shape[1])])
    test_df["label"] = y_test
    test_df.to_csv(TEST_FILE, index=False)
    print(f"✅ Test dataset saved as {TEST_FILE}")
except Exception as e:
    print("❌ Failed to save test dataset:", e)

# === Save hyperparameters ===
try:
    with open(HYPERPARAM_FILE, "w") as f:
        json.dump({
            "model": "RandomForestClassifier",
            "n_estimators": 100
        }, f, indent=2)
    print(f"✅ Hyperparameters saved as {HYPERPARAM_FILE}")
except Exception as e:
    print("❌ Failed to save hyperparameters:", e)

print("🎉 All steps completed successfully.")
