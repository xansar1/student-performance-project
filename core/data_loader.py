import pandas as pd


def load_and_clean_data(uploaded_file, institution_type="College"):
    df = pd.read_csv(uploaded_file)

    df.columns = [col.strip().upper() for col in df.columns]

    if institution_type == "College":
        required = [
            "STUDENT_NAME",
            "UNIVERSITY",
            "PROGRAM",
            "TOTAL_SCORE"
        ]

        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # universal score mapping
        if "GENERAL_SCORE" not in df.columns:
            df["GENERAL_SCORE"] = df["TOTAL_SCORE"] * 0.5
        if "DOMAIN_SCORE" not in df.columns:
            df["DOMAIN_SCORE"] = df["TOTAL_SCORE"] * 0.5

    elif institution_type == "School":
        required = [
            "STUDENT_NAME",
            "CLASS",
            "SECTION",
            "ENGLISH",
            "MATHS",
            "SCIENCE"
        ]

        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df["TOTAL_SCORE"] = (
            df["ENGLISH"] +
            df["MATHS"] +
            df["SCIENCE"]
        )

        df["GENERAL_SCORE"] = df["ENGLISH"]
        df["DOMAIN_SCORE"] = df["MATHS"]

        df["UNIVERSITY"] = "School"
        df["PROGRAM"] = df["CLASS"].astype(str)

    elif institution_type == "Coaching Centre":
        required = [
            "STUDENT_NAME",
            "BATCH",
            "TEST_NAME",
            "PHYSICS",
            "CHEMISTRY",
            "MATHS_BIO"
        ]

        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df["TOTAL_SCORE"] = (
            df["PHYSICS"] +
            df["CHEMISTRY"] +
            df["MATHS_BIO"]
        )

        df["GENERAL_SCORE"] = df["PHYSICS"]
        df["DOMAIN_SCORE"] = df["CHEMISTRY"]

        df["UNIVERSITY"] = "Coaching Centre"
        df["PROGRAM"] = df["BATCH"]

    return df
