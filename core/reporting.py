from io import BytesIO
import yagmail

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def generate_pdf_report(
    df,
    total_students,
    avg_score,
    top_score,
    at_risk
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]

    story = []

    story.append(
        Paragraph("🎓 Student Performance Executive Report", title_style)
    )
    story.append(Spacer(1, 0.25 * inch))

    topper_name = df.loc[df["TOTAL_SCORE"].idxmax(), "STUDENT_NAME"]

    summary_data = [
        ["Total Students", str(total_students)],
        ["Average Score", str(avg_score)],
        ["Top Score", str(top_score)],
        ["At Risk Students", str(at_risk)],
        ["Top Performer", topper_name]
    ]

    summary_table = Table(summary_data, colWidths=[180, 120])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, "black"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.35 * inch))

    story.append(Paragraph("Detailed Student Data", heading_style))
    story.append(Spacer(1, 0.15 * inch))

    display_cols = [
        "STUDENT_NAME",
        "UNIVERSITY",
        "PROGRAM",
        "TOTAL_SCORE",
        "GRADE"
    ]

    table_df = df[display_cols].copy()
    table_data = [table_df.columns.tolist()] + table_df.astype(str).values.tolist()

    report_table = Table(
        table_data,
        colWidths=[120, 120, 120, 80, 60],
        repeatRows=1
    )

    report_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#dbeafe"),
        ("GRID", (0, 0), (-1, -1), 0.4, "grey"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (3, 1), (4, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(report_table)

    doc.build(story)
    buffer.seek(0)
    return buffer


def send_email_report(
    receiver_email,
    pdf_buffer,
    sender_email,
    app_password
):
    yag = yagmail.SMTP(
        sender_email,
        app_password
    )

    yag.send(
        to=receiver_email,
        subject="Student Performance Executive Report",
        contents="Attached is the executive performance report.",
        attachments={
            "executive_student_report.pdf": pdf_buffer.getvalue()
        }
    )
