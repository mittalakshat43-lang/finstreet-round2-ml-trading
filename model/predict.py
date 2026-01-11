# model/predict.py

def predict(model, X):
    """
    Generates BUY / NO BUY predictions.

    Parameters:
    model: trained model
    X (pd.DataFrame): feature columns only

    Returns:
    array of predictions (0 or 1)
    """
    return model.predict(X)


def predict_proba(model, X):
    """
    Generates BUY probability.

    Returns:
    probability of class 1 (BUY)
    """
    return model.predict_proba(X)[:, 1]

