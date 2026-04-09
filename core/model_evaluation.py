import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


def evaluate_binary_model(
    y_true,
    y_pred
):
    return {
        "Accuracy": round(accuracy_score(y_true, y_pred), 2),
        "Precision": round(
            precision_score(y_true, y_pred, zero_division=0), 2
        ),
        "Recall": round(
            recall_score(y_true, y_pred, zero_division=0), 2
        ),
        "F1 Score": round(
            f1_score(y_true, y_pred, zero_division=0), 2
        )
    }


def evaluate_dropout_model(df):
    y_true = (df["TOTAL_SCORE"] < 50).astype(int)
    y_pred = (df["AI_DROPOUT_RISK"] > 0.5).astype(int)

    return evaluate_binary_model(y_true, y_pred)


def evaluate_placement_model(df):
    y_true = (df["TOTAL_SCORE"] >= 60).astype(int)
    y_pred = (df["PLACEMENT_PROBABILITY"] > 0.5).astype(int)

    return evaluate_binary_model(y_true, y_pred)


def build_evaluation_dataframe(df):
    dropout_metrics = evaluate_dropout_model(df)
    placement_metrics = evaluate_placement_model(df)

    rows = []

    for metric, value in dropout_metrics.items():
        rows.append({
            "MODEL": "Dropout AI",
            "METRIC": metric,
            "VALUE": value
        })

    for metric, value in placement_metrics.items():
        rows.append({
            "MODEL": "Placement AI",
            "METRIC": metric,
            "VALUE": value
        })

    return pd.DataFrame(rows)
