import pandas as pd


def load_and_clean_data(
    uploaded_file,
    institution_type,
    academic_level=None,
    department=None
):
    df = pd.read_csv(uploaded_file)

    # normalize column names
    df.columns = [col.strip().upper() for col in df.columns]

    metadata_cols = {
        "STUDENT_NAME",
        "CLASS",
        "SECTION",
        "MEDIUM",
        "STREAM",
        "BATCH",
        "INSTITUTION",
        "DEPARTMENT",
        "SEMESTER",
        "COACHING_CENTRE"
    }

    # detect all score columns dynamically
    subject_cols = [
        col for col in df.columns
        if col not in metadata_cols
        and col != "STUDENT_NAME"
    ]

    if not subject_cols:
        raise ValueError("No valid subject score columns found.")

    # total score
    df["TOTAL_SCORE"] = df[subject_cols].sum(axis=1)

    # first 2 subjects for existing analytics compatibility
    df["GENERAL_SCORE"] = df[subject_cols[0]]

    if len(subject_cols) > 1:
        df["DOMAIN_SCORE"] = df[subject_cols[1]]
    else:
        df["DOMAIN_SCORE"] = df[subject_cols[0]]

    # universal filter columns
    if institution_type == "School":
        df["UNIVERSITY"] = df.get("CLASS", "School")
        df["PROGRAM"] = df.get("SECTION", "General")

    elif institution_type == "Higher Secondary":
        df["UNIVERSITY"] = df.get("STREAM", "Higher Secondary")
        df["PROGRAM"] = df.get("BATCH", "General")

    elif institution_type == "College":
        df["UNIVERSITY"] = df.get("INSTITUTION", "College")
        df["PROGRAM"] = df.get("DEPARTMENT", "General")

    else:
        df["UNIVERSITY"] = df.get("COACHING_CENTRE", "Coaching")
        df["PROGRAM"] = df.get("BATCH", "General")

    return df
