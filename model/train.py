# model/train.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_model():
    # Load processed feature data
    df = pd.read_csv("data/processed/rites_features.csv")

    # Separate features and target
    X = df.drop(columns=["date", "target"])
    y = df["target"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )

    # ML pipeline
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(class_weight="balanced"))
    ])

    # Train model
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("✅ Model trained successfully")
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # Save model
    os.makedirs("model/artifacts", exist_ok=True)
    joblib.dump(model, "model/artifacts/logistic_model.pkl")

    print("\n💾 Model saved to model/artifacts/logistic_model.pkl")

if __name__ == "__main__":
    train_model()
