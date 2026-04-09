import pandas as pd
import numpy as np


REQUIRED_COLS = [
    "STUDENT_NAME",
    "UNIVERSITY",
    "PROGRAM",
    "GENERAL_SCORE",
    "DOMAIN_SCORE",
    "TOTAL_SCORE"
]


RENAME_MAP = {
    "NAME_OF_THE_STUDENT": "STUDENT_NAME",
    "PROGRAM_NAME": "PROGRAM",
    "GENERAL_MANAGEMENT_SCORE_(OUT_OF_50)": "GENERAL_SCORE",
    "DOMAIN_SPECIFIC_SCORE_(OUT_50)": "DOMAIN_SCORE",
    "TOTAL_SCORE_(OUT_OF_100)": "TOTAL_SCORE"
}


def load_and_clean_data(uploaded_file):
    """
    Load CSV, normalize columns, validate schema,
    fill optional defaults, and return cleaned dataframe.
    """
    df = pd.read_csv(uploaded_file)

    # normalize column names
    df.columns = [
        col.strip().replace(" ", "_").upper()
        for col in df.columns
    ]

    # rename known alternative columns
    df.rename(columns=RENAME_MAP, inplace=True)

    # validate required columns
    missing = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # fill optional fields
    optional_defaults = {
        "EMAIL": "N/A",
        "GENDER": "N/A",
        "SPECIALISATION": "N/A"
    }

    for col, default_value in optional_defaults.items():
        if col not in df.columns:
            df[col] = default_value

    # semester fallback
    if "SEMESTER" not in df.columns:
        df["SEMESTER"] = np.random.choice(
            ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
            size=len(df)
        )

    return df
