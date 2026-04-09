def get_parent_student_record(df, parent_username):
    student_name = parent_username.replace("_parent", "")
    student_name = student_name.strip().lower()

    row = df[
        df["STUDENT_NAME"].str.lower() == student_name
    ]

    if row.empty:
        return None

    return row.iloc[0]
