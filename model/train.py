# model/train.py

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def train_model():
    # 1. Load the processed feature dataset
    file_path = "data/processed/rites_features.csv"
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found. Run build_features.py first!")
        return

    df = pd.read_csv(file_path)
    print(f"✅ Loaded {len(df)} rows of feature data.")

    # 2. Separate Features (X) and Target (y)
    # We drop 'date' because the model can't process date strings
    X = df.drop(columns=["date", "target"])
    y = df["target"]

    # 3. Time-Series Split (NO SHUFFLING)
    # Critical for Finance: We train on the past to predict the future.
    # We'll use 80% for training and the last 20% for validation.
    split_index = int(len(X) * 0.8)
    
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    print(f"📅 Training on first {len(X_train)} days, validating on last {len(X_test)} days.")

    # 4. Build the Pipeline
    # Scaling is important for many models, and a Pipeline keeps everything clean.
    model_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=100, 
            max_depth=5,       # Prevent overfitting on small datasets
            random_state=42,
            class_weight="balanced" # Handles cases where 'Up' days > 'Down' days
        ))
    ])

    # 5. Train the Model
    print("🧠 Training Random Forest model...")
    model_pipeline.fit(X_train, y_train)

    # 6. Evaluation
    y_pred = model_pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n--- MODEL PERFORMANCE ---")
    print(f"Accuracy: {acc:.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # 7. Save the Model Artifacts
    os.makedirs("model/artifacts", exist_ok=True)
    model_save_path = "model/artifacts/trading_model.pkl"
    joblib.dump(model_pipeline, model_save_path)
    
    print(f"\n💾 SUCCESS! Model saved to: {model_save_path}")

if __name__ == "__main__":
    train_model()
