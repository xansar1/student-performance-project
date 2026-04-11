def get_student_record(df, admission_no):
    row = df[
        df["ADMISSION_NO"].astype(str).str.upper()
        == str(admission_no).upper()
    ]

    if row.empty:
        return None

    return row.iloc[0]
