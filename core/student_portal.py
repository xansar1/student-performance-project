def get_student_record(df, username):
    username = username.strip().lower()

    student_row = df[
        df["STUDENT_NAME"].str.lower() == username
    ]

    if student_row.empty:
        return None

    return student_row.iloc[0]
