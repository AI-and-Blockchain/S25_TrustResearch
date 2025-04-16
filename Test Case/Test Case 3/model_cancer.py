import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv("cancer_dataset.csv")
X = df.drop(columns=["id", "diagnosis"])
y = LabelEncoder().fit_transform(df["diagnosis"])  # M/B → 0/1

X = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=5)
model.fit(X_train, y_train)
joblib.dump(model, "model.h5")

test_df = pd.DataFrame(X_test, columns=[f"feature_{i}" for i in range(X.shape[1])])
test_df["label"] = y_test
test_df.to_csv("test_dataset.csv", index=False)

with open("hyperparameters.json", "w") as f:
    json.dump({"max_depth": 5}, f, indent=2)

print("✅ Cancer model, test dataset, and hyperparameters saved.")
