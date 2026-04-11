def generate_student_advisor_report(student_row):
    name = student_row.get("STUDENT_NAME", "Student")
    score = student_row.get("TOTAL_SCORE", 0)
    grade = student_row.get("GRADE", "N/A")
    placement = student_row.get(
        "PLACEMENT_AI_STATUS",
        "Placement prediction unavailable"
    )
    dropout = student_row.get("AI_DROPOUT_RISK", 0)
    intervention = student_row.get(
        "AI_INTERVENTION",
        "General mentoring recommended"
    )
    next_sem = student_row.get("NEXT_SEM_PREDICTION", 0)

    if score >= 85:
        academic_comment = (
            f"{name} is performing at an excellent academic level "
            f"with grade {grade}. The student demonstrates strong "
            f"subject mastery and leadership potential."
        )
    elif score >= 60:
        academic_comment = (
            f"{name} shows stable academic performance with grade "
            f"{grade}. Focused mentoring can improve consistency "
            f"and raise next semester outcomes."
        )
    else:
        academic_comment = (
            f"{name} is currently academically vulnerable with "
            f"grade {grade}. Immediate faculty mentoring and "
            f"targeted intervention are strongly recommended."
        )

    placement_comment = (
        f"Placement outlook is currently marked as {placement}. "
        f"Recommended focus areas include aptitude, communication, "
        f"projects, and mock interviews."
    )

    dropout_comment = (
        f"Predicted dropout risk stands at {round(dropout, 2)}. "
        f"Suggested action: {intervention}."
    )

    future_comment = (
        f"Next semester forecasted score is {round(next_sem, 2)}. "
        f"This should be used for proactive academic planning."
    )

    final_report = (
        f"## 🎓 GenAI Advisor Report for {name}\n\n"
        f"### 📘 Academic Insight\n{academic_comment}\n\n"
        f"### 🎯 Placement Insight\n{placement_comment}\n\n"
        f"### 🚨 Risk Insight\n{dropout_comment}\n\n"
        f"### 📈 Future Semester Forecast\n{future_comment}\n\n"
        f"### 🏫 Advisor Recommendation\n"
        f"Continuous monitoring, faculty review, parent communication, "
        f"and personalized mentoring should be scheduled."
    )

    return final_report
