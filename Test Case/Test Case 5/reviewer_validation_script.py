import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
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

def load_test_data(path):
    df = pd.read_csv(path)

    # Drop rows where label is NaN
    df = df.dropna(subset=["label"])

    X_test = df.drop("label", axis=1).values
    y_test = df["label"].values
    return X_test, y_test


def evaluate_model(model_path, X_test, y_test):
    model = joblib.load(model_path)
    y_pred = model.predict(X_test)
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

    claimed = extract_metrics_from_trig(trig_file)
    if not claimed:
        print("No metrics found in nanopub.")
        exit(1)

    X_test, y_test = load_test_data(test_file)
    reproduced = evaluate_model(model_file, X_test, y_test)
    comparison = compare_metrics(claimed, reproduced)

    print("Comparison:")
    for k, v in comparison.items():
        print(f"{k.capitalize()}:")
        print(f"  Claimed     : {v['claimed']:.4f}")
        print(f"  Reproduced  : {v['reproduced']:.4f}")
        print(f"  Difference  : {v['difference']:.4f}")
        print(f"  % Difference: {v['percent_difference']:.2f}%")
        print(f"  Validated" if v["valid"] else f"  Discrepancy found")
        print("")
