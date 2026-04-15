import pandas as pd


def get_grade(score):
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 50:
        return "C"
    return "D"


def placement_readiness(score):
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Placement Ready"
    elif score >= 50:
        return "Needs Upskilling"
    return "High Risk"


def dropout_risk(score):
    if score < 40:
        return 90
    elif score < 60:
        return 60
    return 10


def enrich_student_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all derived intelligence columns.
    """
    df = df.copy()

    df["GRADE"] = df["TOTAL_SCORE"].apply(get_grade)
    df["PLACEMENT_STATUS"] = df["TOTAL_SCORE"].apply(
        placement_readiness
    )
    df["DROPOUT_RISK"] = df["TOTAL_SCORE"].apply(
        dropout_risk
    )

    return df


def get_kpis(df):
    subject_cols = [
        col for col in df.select_dtypes(include="number").columns
        if col not in [
            "PARENT_PHONE",
            "AI_DROPOUT_RISK",
            "PLACEMENT_PROBABILITY",
            "NEXT_SEM_PREDICTION",
            "CLUSTER"
        ]
    ]

    if len(subject_cols) == 0:
        return {
            "total_students": len(df),
            "avg_score": 0,
            "top_score": 0,
            "at_risk": 0
        }

    df["TOTAL_SCORE"] = df[subject_cols].sum(axis=1)

    return {
        "total_students": len(df),
        "avg_score": round(df["TOTAL_SCORE"].mean(), 2),
        "top_score": round(df["TOTAL_SCORE"].max(), 2),
        "at_risk": len(df[df["AI_DROPOUT_RISK"] > 0.7])
    }

def get_topper(df: pd.DataFrame):
    return df.loc[df["TOTAL_SCORE"].idxmax()]
