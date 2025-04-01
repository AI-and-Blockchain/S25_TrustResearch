import json
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from model import create_model  # Author-provided model code

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
# Data utilities
# ------------------------
def load_dataset(path):
    return pd.read_csv(path)

def load_hyperparameters(path):
    with open(path, 'r') as f:
        return json.load(f)

def prepare_data(dataset):
    X = dataset.drop('species', axis=1).values
    y = LabelEncoder().fit_transform(dataset['species'].values)
    return train_test_split(X, y, test_size=0.2, random_state=42)

# ------------------------
# Model training & evaluation
# ------------------------
def train_and_evaluate(X_train, X_test, y_train, y_test, hyperparameters):
    input_shape = X_train.shape[1:]
    num_classes = len(np.unique(y_train))
    model = create_model(input_shape, num_classes)

    model.fit(X_train, y_train, batch_size=hyperparameters['batch_size'], epochs=hyperparameters['epochs'])

    predictions = model.predict(X_test)
    predicted_classes = np.argmax(predictions, axis=1)

    return {
        "accuracy": accuracy_score(y_test, predicted_classes),
        "precision": precision_score(y_test, predicted_classes, average='weighted', zero_division=0),
        "recall": recall_score(y_test, predicted_classes, average='weighted', zero_division=0),
        "f1": f1_score(y_test, predicted_classes, average='weighted', zero_division=0)
    }

# ------------------------
# Comparison
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
# Main
# ------------------------
if __name__ == "__main__":
    dataset_path = 'iris_dataset.csv'
    hyperparams_path = 'hyperparameters.json'
    trig_file_path = 'nanopub_example.trig'

    dataset = load_dataset(dataset_path)
    hyperparams = load_hyperparameters(hyperparams_path)
    X_train, X_test, y_train, y_test = prepare_data(dataset)

    reproduced_metrics = train_and_evaluate(X_train, X_test, y_train, y_test, hyperparams)
    claimed_metrics = extract_metrics_from_trig(trig_file_path)

    if not claimed_metrics:
        print("No metrics found in the .trig file.")
    else:
        print("\n📊 Claimed vs Reproduced Metrics:\n")
        comparison = compare_metrics(claimed_metrics, reproduced_metrics)

        for metric, data in comparison.items():
            print(f"{metric.capitalize()}:")
            print(f"  Claimed     : {data['claimed']:.4f}")
            print(f"  Reproduced  : {data['reproduced']:.4f}")
            print(f"  Difference  : {data['difference']:.4f}")
            print(f"  % Difference: {data['percent_difference']:.2f}%")
            print(f"  ✅ Validated" if data["valid"] else f"  ❌ Discrepancy found")
            print("")

        if all(data['valid'] for data in comparison.values()):
            print("✅ All metrics validated successfully.")
        else:
            print("⚠️ Some metrics did not match the claim.")

