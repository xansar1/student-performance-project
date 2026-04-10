def generate_parent_alert(student_row):
    if student_row["AI_DROPOUT_RISK"] > 0.7:
        return (
            f"Alert: {student_row['STUDENT_NAME']} "
            f"needs academic attention."
        )
    return "Student is performing well."
