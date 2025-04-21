import json
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from rdflib import ConjunctiveGraph

def extract_metrics_from_trig(trig_file_path):
    g = ConjunctiveGraph()
    g.parse(trig_file_path, format="trig")
    query = """
    PREFIX ex: <http://example.org/>
    SELECT ?accuracy ?precision ?recall ?f1
    WHERE {
      GRAPH ?g {
        ?model ex:hasAccuracy ?accuracy ;
               ex:hasPrecision ?precision ;
               ex:hasRecall ?recall ;
               ex:hasF1Score ?f1 .
      }
    }
    """
    results = g.query(query)
    for row in results:
        return {
            "accuracy": float(row.accuracy),
            "precision": float(row.precision),
            "recall": float(row.recall),
            "f1": float(row.f1)
        }
    return {}

def load_test_data(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["label"])
    X_test = df.drop("label", axis=1).values.astype("float32") / 255.0
    y_test = df["label"].values.astype(int)
    return X_test, y_test

def evaluate_model(model_path, X_test, y_test):
    model = load_model(model_path)
    X_test = X_test.reshape((-1, 28, 28, 1)).astype("float32")
    y_pred_prob = model.predict(X_test)
    y_pred = np.argmax(y_pred_prob, axis=1)
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
        "f1": f1_score(y_test, y_pred, average='weighted', zero_division=0)
    }

def compare_metrics(claimed, reproduced, tolerance=5.0):
    comparison = {}
    for metric in claimed:
        diff = abs(claimed[metric] - reproduced[metric])
        percent_diff = (diff / claimed[metric]) * 100 if claimed[metric] != 0 else 0
        comparison[metric] = {
            "claimed": claimed[metric],
            "reproduced": reproduced[metric],
            "difference": diff,
            "percent_difference": percent_diff,
            "valid": percent_diff <= tolerance
        }
    return comparison

if __name__ == "__main__":
    trig_file = "nanopub_example.trig"
    model_file = "model.h5"
    test_file = "test_dataset.csv"

    print(" Extracting claimed metrics from:", trig_file)
    claimed = extract_metrics_from_trig(trig_file)
    if not claimed:
        print(" No metrics found in RDF nanopub.")
        exit(1)

    print(" Loading test dataset:", test_file)
    X_test, y_test = load_test_data(test_file)
    print(f" Loaded {len(X_test)} test samples")

    print(" Evaluating model:", model_file)
    reproduced = evaluate_model(model_file, X_test, y_test)

    print(" Comparing reproduced metrics to claimed ones...")
    comparison = compare_metrics(claimed, reproduced)

    print("\n Metric Comparison Report:")
    for k, v in comparison.items():
        print(f"{k.upper()}:")
        print(f"  Claimed     : {v['claimed']:.4f}")
        print(f"  Reproduced  : {v['reproduced']:.4f}")
        print(f"  Difference  : {v['difference']:.4f}")
        print(f"  % Difference: {v['percent_difference']:.2f}%")
        print("   Validated" if v["valid"] else "   Discrepancy")
        print("")

    print(" Validation complete.")
