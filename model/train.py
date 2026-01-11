# model/train.py

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


def train_model(df):
    """
    Trains a logistic regression model.

    Parameters:
    df (pd.DataFrame): feature columns + 'target'

    Returns:
    trained sklearn pipeline
    """

    # Separate features and target
    X = df.drop(columns=["target", "date"], errors="ignore")
    y = df["target"]

    # Pipeline = scale data + model
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression())
    ])

    model.fit(X, y)
    return model

