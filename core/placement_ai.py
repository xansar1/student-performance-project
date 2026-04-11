from sklearn.linear_model import LogisticRegression

def add_placement_prediction(df):
    feature_cols = [
        col for col in [
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "TOTAL_SCORE"
        ]
        if col in df.columns
    ]

    # not enough features
    if len(feature_cols) < 2:
        df["PLACEMENT_PROBABILITY"] = 0.5
        return df

    # synthetic placement label
    y = (
        df["TOTAL_SCORE"] > df["TOTAL_SCORE"].mean()
    ).astype(int)

    # one-class protection
    if y.nunique() < 2:
        df["PLACEMENT_PROBABILITY"] = 0.5
        return df

    # too few rows protection
    if len(df) < 5:
        df["PLACEMENT_PROBABILITY"] = 0.5
        return df

    X = df[feature_cols]

    model = LogisticRegression()
    model.fit(X, y)

    df["PLACEMENT_PROBABILITY"] = model.predict_proba(X)[:, 1]

    return df
