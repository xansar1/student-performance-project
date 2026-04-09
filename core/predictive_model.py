from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


FEATURES = [
    "GENERAL_SCORE",
    "DOMAIN_SCORE",
    "TOTAL_SCORE"
]


def train_dropout_model(df):
    """
    Train simple AI dropout risk model.
    """
    model_df = df.copy()

    # create weak-label target for MVP
    model_df["DROPOUT_TARGET"] = (
        model_df["TOTAL_SCORE"] < 50
    ).astype(int)

    X = model_df[FEATURES]
    y = model_df["DROPOUT_TARGET"]

    model = LogisticRegression()
    model.fit(X, y)

    return model


def add_ai_dropout_prediction(df):
    """
    Add AI-based dropout probability.
    """
    df = df.copy()

    model = train_dropout_model(df)

    probs = model.predict_proba(df[FEATURES])[:, 1]
    df["AI_DROPOUT_RISK"] = (probs * 100).round(2)

    return df
