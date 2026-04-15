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
    df = df.copy()

    subject_cols = [
        col for col in df.select_dtypes(include="number").columns
        if col not in ["PARENT_PHONE"]
    ]

    if len(subject_cols) == 0:
        df["AI_DROPOUT_RISK"] = 0.0
        return df

    avg_marks = df[subject_cols].mean(axis=1)

    df["AI_DROPOUT_RISK"] = (
        1 - (avg_marks / 100)
    ).clip(0, 1)

    return df
