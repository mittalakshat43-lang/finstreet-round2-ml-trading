#train.py 

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# =========================
# 🔹 CONFIGURATION
# =========================
FEATURE_COLS = [
    "return_1d", "return_3d", "return_5d", 
    "clv", "up_streak", "down_streak", "accel"
]

# 🛑 STRICT RULE: Training must end here.
TRAINING_CUTOFF_DATE = "2025-12-31"

def train_model():
    # 1. SETUP PATHS
    base_dir = os.getcwd()
    input_path = os.path.join(base_dir, "data", "processed", "rites_features.csv")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    model_save_path = os.path.join(artifacts_dir, "trading_model.pkl")

    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found.")
        return

    print(f"📖 Loading data from: {input_path}")
    df = pd.read_csv(input_path)
    
    # 2. 🛡️ COMPLIANCE FILTER (The Critical Fix)
    # We explicitly convert to datetime and throw away any January data
    df["date"] = pd.to_datetime(df["date"])
    
    # Filter: Keep ONLY rows on or before Dec 31, 2025
    train_df = df[df["date"] <= pd.Timestamp(TRAINING_CUTOFF_DATE)].copy()
    
    print(f"📉 Filtering Data: {len(df)} total rows -> {len(train_df)} rows (Max Date: {train_df['date'].max().date()})")
    
    # 3. PREPARE FEATURES
    try:
        X = train_df[FEATURE_COLS] 
        y = train_df["target"]
    except KeyError as e:
        print(f"❌ DATA ERROR: Missing columns: {e}")
        return

    # 4. SPLIT (Chronological Split on the valid Nov-Dec data)
    split = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    print(f"🧠 Training on {len(X_train)} days, Validating on {len(X_test)} days...")

    # 5. TRAIN PIPELINE
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)

    # 6. EVALUATE & SAVE
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*30)
    print(f"🎯 VALIDATION ACCURACY: {acc:.2%} (Nov-Dec Only)")
    print("="*30)
    
    # Optional: Retrain on FULL Nov-Dec data for the final model
    pipeline.fit(X, y)
    print("✅ Final Model retrained on all Nov-Dec data.")

    os.makedirs(artifacts_dir, exist_ok=True)
    joblib.dump(pipeline, model_save_path)
    print(f"💾 Model saved to: {model_save_path}")

if __name__ == "__main__":
    train_model()
