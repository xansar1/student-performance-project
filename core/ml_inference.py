import joblib


def predict_dropout_probability(df):
    model = joblib.load("dropout_model.pkl")

    X = df[
        [
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "TOTAL_SCORE"
        ]
    ]

    probs = model.predict_proba(X)[:, 1]

    df["REAL_ML_DROPOUT_PROB"] = probs
    return df


def predict_placement_probability(df):
    model = joblib.load("placement_model.pkl")

    X = df[
        [
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "TOTAL_SCORE"
        ]
    ]

    probs = model.predict_proba(X)[:, 1]

    df["REAL_ML_PLACEMENT_PROB"] = probs
    return df
