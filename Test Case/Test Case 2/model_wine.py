print("🚀 Starting model_wine.py...")

import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import re

import re

def write_metrics_to_trig(metrics, template_path="nanopub_example.trig", output_path="nanopub_example.trig"):
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            trig = f.read()

        trig = trig.replace(
            re.search(r'ex:hasAccuracy\s+"[\d.]+"', trig).group(0),
            f'ex:hasAccuracy "{metrics["accuracy"]:.4f}"'
        )
        trig = trig.replace(
            re.search(r'ex:hasPrecision\s+"[\d.]+"', trig).group(0),
            f'ex:hasPrecision "{metrics["precision"]:.4f}"'
        )
        trig = trig.replace(
            re.search(r'ex:hasRecall\s+"[\d.]+"', trig).group(0),
            f'ex:hasRecall "{metrics["recall"]:.4f}"'
        )
        trig = trig.replace(
            re.search(r'ex:hasF1Score\s+"[\d.]+"', trig).group(0),
            f'ex:hasF1Score "{metrics["f1"]:.4f}"'
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(trig)

        print(f"✅ Updated trig written to {output_path}")
    except Exception as e:
        print("❌ Failed to write updated trig:", e)


df = pd.read_csv("wine.csv")
X = df.drop(columns=["Wine"])
y = df["Wine"].values

X = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = SVC(kernel='rbf', C=1.0, probability=True)
model.fit(X_train, y_train)
joblib.dump(model, "model.h5")

test_df = pd.DataFrame(X_test, columns=[f"feature_{i}" for i in range(X.shape[1])])
test_df["label"] = y_test
test_df.to_csv("test_dataset.csv", index=False)

with open("hyperparameters.json", "w") as f:
    json.dump({"kernel": "rbf", "C": 1.0}, f, indent=2)

y_pred = model.predict(X_test)
metrics = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
    "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
    "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0)
}

write_metrics_to_trig(metrics)
print("🎉 All steps completed successfully.")
