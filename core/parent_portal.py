def get_parent_student_record(df, parent_username):
    if df is None or df.empty:
        return None

    df.columns = df.columns.str.strip().str.upper()

    if "ADMISSION_NO" not in df.columns:
        return None

    admission_no = parent_username.replace("P_", "").strip().upper()

    student_row = df[
        df["ADMISSION_NO"].astype(str).str.strip().str.upper()
        == admission_no
    ]

    if student_row.empty:
        return None

    return student_row.iloc[0]
