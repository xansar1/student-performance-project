def generate_intervention(row):
    """
    Personalized academic intervention recommendation.
    """
    actions = []

    if row["GENERAL_SCORE"] < 20:
        actions.append("Soft skills + aptitude foundation program")

    if row["DOMAIN_SCORE"] < 20:
        actions.append("Domain-specific tutoring and faculty support")

    if row["AI_DROPOUT_RISK"] >= 70:
        actions.append("Immediate mentor counseling + parent escalation")

    if 50 <= row["TOTAL_SCORE"] < 70:
        actions.append("Placement readiness bootcamp")

    if row["TOTAL_SCORE"] >= 85:
        actions.append("Scholarship + leadership acceleration track")

    if not actions:
        actions.append("Maintain current academic progress")

    return " | ".join(actions)


def add_intervention_recommendations(df):
    """
    Add intervention recommendations for all students.
    """
    df = df.copy()
    df["AI_INTERVENTION"] = df.apply(
        generate_intervention,
        axis=1
    )
    return df
