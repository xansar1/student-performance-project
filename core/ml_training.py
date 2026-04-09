import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def train_dropout_model(df):
    model_df = df.copy()

    model_df["TARGET"] = (
        model_df["TOTAL_SCORE"] < 50
    ).astype(int)

    X = model_df[
        [
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "TOTAL_SCORE"
        ]
    ]

    y = model_df["TARGET"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    joblib.dump(model, "dropout_model.pkl")

    return round(acc, 2)


def train_placement_model(df):
    model_df = df.copy()

    model_df["TARGET"] = (
        model_df["TOTAL_SCORE"] >= 60
    ).astype(int)

    X = model_df[
        [
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "TOTAL_SCORE"
        ]
    ]

    y = model_df["TARGET"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    joblib.dump(model, "placement_model.pkl")

    return round(acc, 2)
