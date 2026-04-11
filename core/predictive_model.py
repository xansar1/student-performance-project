from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


FEATURES = [
    "GENERAL_SCORE",
    "DOMAIN_SCORE",
    "TOTAL_SCORE"
]


from sklearn.linear_model import LogisticRegression

def train_dropout_model(df):
    feature_cols = [
        "GENERAL_SCORE",
        "DOMAIN_SCORE",
        "TOTAL_SCORE"
    ]

    available_cols = [
        col for col in feature_cols
        if col in df.columns
    ]

    # fallback when not enough features
    if len(available_cols) < 2:
        return None

    X = df[available_cols]

    # create synthetic safe target
    y = (df["TOTAL_SCORE"] < df["TOTAL_SCORE"].mean()).astype(int)

    # 🚨 critical fix: at least 2 classes required
    if y.nunique() < 2:
        return None

    # 🚨 critical fix: enough rows
    if len(df) < 5:
        return None

    model = LogisticRegression()
    model.fit(X, y)

    return model


def add_ai_dropout_prediction(df):
    model = train_dropout_model(df)

    if model is None:
        df["AI_DROPOUT_RISK"] = 0.2
        return df

    feature_cols = [
        col for col in [
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "TOTAL_SCORE"
        ]
        if col in df.columns
    ]

    probs = model.predict_proba(df[feature_cols])[:, 1]
    df["AI_DROPOUT_RISK"] = probs

    return df
