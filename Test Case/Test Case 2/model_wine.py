import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

df = pd.read_csv("wine.csv")
X = df.drop(columns=["Wine"])
y = df["Wine"]

X = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = SVC(kernel='rbf', C=1.0, probability=True)
model.fit(X_train, y_train)
joblib.dump(model, "model.h5")

test_df = pd.DataFrame(X_test, columns=[f"feature_{i}" for i in range(X.shape[1])])
test_df["label"] = y_test.values
test_df.to_csv("test_dataset.csv", index=False)

with open("hyperparameters.json", "w") as f:
    json.dump({"kernel": "rbf", "C": 1.0}, f, indent=2)

print("✅ Wine model, test dataset, and hyperparameters saved.")
