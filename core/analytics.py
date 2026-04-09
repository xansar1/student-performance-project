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


def get_kpis(df: pd.DataFrame):
    total_students = len(df)
    avg_score = round(df["TOTAL_SCORE"].mean(), 2)
    top_score = int(df["TOTAL_SCORE"].max())
    at_risk = len(df[df["TOTAL_SCORE"] < 50])

    return {
        "total_students": total_students,
        "avg_score": avg_score,
        "top_score": top_score,
        "at_risk": at_risk
    }


def get_topper(df: pd.DataFrame):
    return df.loc[df["TOTAL_SCORE"].idxmax()]
