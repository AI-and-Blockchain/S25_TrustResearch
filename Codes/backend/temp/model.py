import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json

# Load dataset
df = pd.read_csv("iris_dataset.csv")
X = df.drop("species", axis=1).values
y = LabelEncoder().fit_transform(df["species"])

# Split the dataset
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Load hyperparameters
with open("hyperparameters.json", "r") as f:
    hyperparams = json.load(f)

# Create model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(len(set(y)), activation='softmax')
])

# Compile and train
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(X_train, y_train,
          epochs=hyperparams["epochs"],
          batch_size=hyperparams["batch_size"])

# ✅ Save the full model
model.save("model.h5")
print("✅ model.h5 saved successfully.")
