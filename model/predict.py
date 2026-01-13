# model/predict.py

import pandas as pd
import joblib


def predict_signals(
    features_csv="data/processed/rites_features.csv",
    model_path="model/artifacts/logistic_model.pkl",
    threshold=0.4
):
    """
    Generate predictions for price movement using a trained ML model.
    Uses probability-based thresholding instead of hard 0.5 cutoff.
    """

    # Load processed feature data
    df = pd.read_csv(features_csv)

    # Separate features
    X = df.drop(columns=["date", "target"])

    # Load trained model
    model = joblib.load(model_path)

    # Predict probability of UP move (class = 1)
    df["buy_probability"] = model.predict_proba(X)[:, 1]

    # Apply threshold to generate signal
    df["signal"] = (df["buy_probability"] > threshold).astype(int)

    # Map signal to readable action
    df["action"] = df["signal"].map({
        1: "BUY",
        0: "HOLD / NO TRADE"
    })

    # Save predictions
    output_path = "data/processed/rites_predictions.csv"
    df.to_csv(output_path, index=False)

    print("✅ Predictions generated successfully")
    print(f"Saved to: {output_path}")
    print("\nLatest predictions:\n")
    print(df[["date", "buy_probability", "signal", "action"]].tail(5))

    return df


if __name__ == "__main__":
    predict_signals()
