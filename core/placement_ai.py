from sklearn.linear_model import LogisticRegression


FEATURES = [
    "GENERAL_SCORE",
    "DOMAIN_SCORE",
    "TOTAL_SCORE",
    "NEXT_SEM_PREDICTION"
]


def train_placement_model(df):
    """
    MVP employability probability model.
    """
    model_df = df.copy()

    # weak-label placement target
    model_df["PLACEMENT_TARGET"] = (
        (
            model_df["TOTAL_SCORE"] >= 60
        ) &
        (
            model_df["DOMAIN_SCORE"] >= 25
        )
    ).astype(int)

    X = model_df[FEATURES]
    y = model_df["PLACEMENT_TARGET"]

    model = LogisticRegression()
    model.fit(X, y)

    return model


def add_placement_prediction(df):
    """
    Add placement probability + placement label.
    """
    df = df.copy()

    model = train_placement_model(df)

    probs = model.predict_proba(df[FEATURES])[:, 1]
    df["PLACEMENT_PROBABILITY"] = (probs * 100).round(2)

    df["PLACEMENT_AI_STATUS"] = df["PLACEMENT_PROBABILITY"].apply(
        lambda x: "High Chance" if x >= 70 else
        "Moderate Chance" if x >= 40 else
        "Low Chance"
    )

    return df
