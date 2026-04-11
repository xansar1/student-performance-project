import pandas as pd


def get_required_subjects(
    institution_type,
    academic_level=None,
    medium=None,
    department=None
):
    if institution_type == "School":
        if academic_level == "10":
            return [
                "ENGLISH",
                "MALAYALAM",
                "HINDI",
                "MATHS",
                "PHYSICS",
                "CHEMISTRY",
                "BIOLOGY",
                "SOCIAL_SCIENCE",
                "COMPUTER"
            ]
        else:
            return [
                "ENGLISH",
                "MALAYALAM",
                "HINDI",
                "MATHS",
                "BASIC_SCIENCE",
                "SOCIAL_SCIENCE",
                "COMPUTER"
            ]

    elif institution_type == "Higher Secondary":
        if academic_level == "Science":
            return [
                "ENGLISH",
                "PHYSICS",
                "CHEMISTRY",
                "MATHS",
                "BIOLOGY",
                "COMPUTER"
            ]
        elif academic_level == "Commerce":
            return [
                "ENGLISH",
                "ACCOUNTANCY",
                "BUSINESS_STUDIES",
                "ECONOMICS",
                "COMPUTER"
            ]
        else:
            return [
                "ENGLISH",
                "HISTORY",
                "POLITICS",
                "ECONOMICS",
                "SOCIOLOGY"
            ]

    elif institution_type == "College":
        return [
            "SUBJECT_1",
            "SUBJECT_2",
            "SUBJECT_3",
            "SUBJECT_4"
        ]

    elif institution_type == "Coaching Centre":
        return [
            "TEST_1",
            "TEST_2",
            "TEST_3"
        ]

    return []


def load_and_clean_data(
    uploaded_file,
    institution_type,
    academic_level=None,
    medium=None,
    department=None
):
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().upper() for col in df.columns]

    required_subjects = get_required_subjects(
        institution_type,
        academic_level,
        medium,
        department
    )

    required_cols = ["STUDENT_NAME"] + required_subjects

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["TOTAL_SCORE"] = df[required_subjects].sum(axis=1)

    df["GENERAL_SCORE"] = df[required_subjects[0]]
    df["DOMAIN_SCORE"] = df[required_subjects[1]]

    # universal labels for existing app
    df["UNIVERSITY"] = institution_type
    df["PROGRAM"] = academic_level or department or "GENERAL"

    return df
