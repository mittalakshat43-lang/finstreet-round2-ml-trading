# model/predict.py

import pandas as pd
import joblib

def load_model(model_path="model/artifacts/logistic_model.pkl"):
    return joblib.load(model_path)

def predict_signals():
    # Load model
    model = load_model()

    # Load feature data
    df = pd.read_csv("data/processed/rites_features.csv")

    X = df.drop(columns=["date", "target"])

    # Predictions
    df["prediction"] = model.predict(X)
    df["buy_probability"] = model.predict_proba(X)[:, 1]

    # Save predictions
    df.to_csv("data/processed/rites_predictions.csv", index=False)

    print("✅ Predictions generated")
    print("Saved to data/processed/rites_predictions.csv")
    print("\nPreview:\n", df[["date", "prediction", "buy_probability"]].tail())

if __name__ == "__main__":
    predict_signals()
