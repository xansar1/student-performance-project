def get_student_record(df, admission_no):
    if df is None or df.empty:
        return None

    # normalize columns
    df.columns = df.columns.str.strip().str.upper()

    if "ADMISSION_NO" not in df.columns:
        return None

    student_row = df[
        df["ADMISSION_NO"].astype(str).str.strip().str.upper()
        == str(admission_no).strip().upper()
    ]

    if student_row.empty:
        return None

    return student_row.iloc[0]
