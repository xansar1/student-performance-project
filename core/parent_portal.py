def get_parent_student_record(df, parent_username):
    admission_no = parent_username.replace("P_", "").upper()

    row = df[
        df["ADMISSION_NO"].astype(str).str.upper()
        == admission_no
    ]

    if row.empty:
        return None

    return row.iloc[0]
