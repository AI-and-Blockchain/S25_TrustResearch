import json
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from rdflib import ConjunctiveGraph

# ------------------------
# Extract metrics from .trig
# ------------------------
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
    metrics = {}
    for row in results:
        metrics = {
            "accuracy": float(row.accuracy),
            "precision": float(row.precision),
            "recall": float(row.recall),
            "f1": float(row.f1)
        }
    return metrics

# ------------------------
# Load and prepare test dataset
# ------------------------
def load_test_data(path):
    df = pd.read_csv(path)
    X_test = df.drop("species", axis=1).values
    y_test = LabelEncoder().fit_transform(df["species"])
    return X_test, y_test

# ------------------------
# Run model prediction
# ------------------------
def evaluate_model(model_path, X_test, y_test):
    model = tf.keras.models.load_model(model_path)
    predictions = model.predict(X_test)
    y_pred = np.argmax(predictions, axis=1)

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
        "f1": f1_score(y_test, y_pred, average='weighted', zero_division=0)
    }

# ------------------------
# Compare claimed and reproduced metrics
# ------------------------
def compare_metrics(claimed, reproduced, tolerance=5.0):
    comparison_results = {}
    for metric in claimed:
        diff = abs(claimed[metric] - reproduced[metric])
        percent_diff = (diff / claimed[metric]) * 100 if claimed[metric] != 0 else 0
        comparison_results[metric] = {
            "claimed": claimed[metric],
            "reproduced": reproduced[metric],
            "difference": diff,
            "percent_difference": percent_diff,
            "valid": percent_diff <= tolerance
        }
    return comparison_results

# ------------------------
# Main Execution
# ------------------------
if __name__ == "__main__":
    trig_file = "nanopub_example.trig"
    model_file = "model.h5"
    test_file = "test_dataset.csv"

    claimed_metrics = extract_metrics_from_trig(trig_file)
    if not claimed_metrics:
        print("No claimed metrics found in the .trig file.")
        exit(1)

    X_test, y_test = load_test_data(test_file)
    reproduced_metrics = evaluate_model(model_file, X_test, y_test)
    comparison = compare_metrics(claimed_metrics, reproduced_metrics)

    print("\nClaimed vs Reproduced Metrics:\n")
    for metric, data in comparison.items():
        print(f"{metric.capitalize()}:")
        print(f"  Claimed     : {data['claimed']:.4f}")
        print(f"  Reproduced  : {data['reproduced']:.4f}")
        print(f"  Difference  : {data['difference']:.4f}")
        print(f"  % Difference: {data['percent_difference']:.2f}%")
        print(f"  Validated" if data["valid"] else f"  Discrepancy found")
        print("")

    if all(data["valid"] for data in comparison.values()):
        print("All metrics validated successfully.")
    else:
        print("Some metrics did not match the claim.")
