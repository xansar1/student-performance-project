import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os
from xhtml2pdf import pisa

# Page setup
st.set_page_config(page_title="Student Performance Analysis", layout="wide")
st.title("📊 Student Performance Analysis App")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = [col.strip().replace(" ", "_").upper() for col in df.columns]
    df.rename(columns={
        "NAME_OF_THE_STUDENT": "STUDENT_NAME",
        "PROGRAM_NAME": "PROGRAM",
        "GENERAL_MANAGEMENT_SCORE_(OUT_OF_50)": "GENERAL_SCORE",
        "DOMAIN_SPECIFIC_SCORE_(OUT_50)": "DOMAIN_SCORE",
        "TOTAL_SCORE_(OUT_OF_100)": "TOTAL_SCORE"
    }, inplace=True)

    for col in ["EMAIL", "GENDER"]:
        if col not in df.columns:
            df[col] = ""

    # Sidebar – Add Student
    st.sidebar.subheader("➕ Add New Student")
    with st.sidebar.form("add_form"):
        add_name = st.text_input("Student Name")
        add_university = st.text_input("University")
        add_program = st.text_input("Program")
        add_specialisation = st.text_input("Specialisation")
        add_email = st.text_input("Email")
        add_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        add_general = st.number_input("General Score (0–50)", 0, 50)
        add_domain = st.number_input("Domain Score (0–50)", 0, 50)
        submitted = st.form_submit_button("✅ Add Student")

        if submitted:
            new_total = add_general + add_domain
            new_row = pd.DataFrame([{
                "STUDENT_NAME": add_name,
                "UNIVERSITY": add_university,
                "PROGRAM": add_program,
                "SPECIALISATION": add_specialisation,
                "EMAIL": add_email,
                "GENDER": add_gender,
                "GENERAL_SCORE": add_general,
                "DOMAIN_SCORE": add_domain,
                "TOTAL_SCORE": new_total
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            st.success(f"Student '{add_name}' added.")

    # Sidebar – Edit/Delete
    st.sidebar.subheader("✏️ Edit / Delete Student")
    selected_student = st.sidebar.selectbox("Select student to edit/delete", df["STUDENT_NAME"].unique())

    if selected_student:
        selected_row = df[df["STUDENT_NAME"] == selected_student].iloc[0]
        with st.sidebar.form("edit_form"):
            edit_index = int(selected_row.name)
            edit_name = st.text_input("Student Name", value=selected_row["STUDENT_NAME"])
            edit_university = st.text_input("University", value=selected_row["UNIVERSITY"])
            edit_program = st.text_input("Program", value=selected_row["PROGRAM"])
            edit_specialisation = st.text_input("Specialisation", value=selected_row["SPECIALISATION"])
            edit_email = st.text_input("Email", value=selected_row["EMAIL"])
            gender_options = ["Male", "Female", "Other"]
            default_gender_index = gender_options.index(selected_row.get("GENDER", "Male")) if selected_row.get("GENDER") in gender_options else 0
            edit_gender = st.selectbox("Gender", gender_options, index=default_gender_index)
            edit_general = st.number_input("General Score (0–50)", 0, 50, int(selected_row["GENERAL_SCORE"]))
            edit_domain = st.number_input("Domain Score (0–50)", 0, 50, int(selected_row["DOMAIN_SCORE"]))
            updated = st.form_submit_button("💾 Save Changes")
            deleted = st.form_submit_button("🗑️ Delete Student")

            if updated:
                df.loc[edit_index] = [
                    edit_name,
                    edit_university,
                    edit_program,
                    edit_specialisation,
                    edit_email,
                    edit_gender,
                    edit_general,
                    edit_domain,
                    edit_general + edit_domain
                ]
                st.success(f"Updated student: {edit_name}")

            if deleted:
                df = df[df["STUDENT_NAME"] != selected_student]
                st.warning(f"Deleted student: {selected_student}")

    # Preview Data
    st.subheader("📄 Dataset Preview")
    st.dataframe(df)

    # Clustering
    st.subheader("🎯 Performance Clustering")
    features = df[["GENERAL_SCORE", "DOMAIN_SCORE", "TOTAL_SCORE"]]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    kmeans = KMeans(n_clusters=3, random_state=42)
    df["CLUSTER"] = kmeans.fit_predict(scaled)
    st.dataframe(df[["STUDENT_NAME", "PROGRAM", "TOTAL_SCORE", "CLUSTER"]])

    # Chart
    st.subheader("📊 Score Distribution")
    fig = px.scatter(df, x="GENERAL_SCORE", y="DOMAIN_SCORE", color="CLUSTER",
                     hover_data=["STUDENT_NAME", "TOTAL_SCORE"])
    st.plotly_chart(fig, key="score_chart")

    # Optional: Save chart image
    chart_path = os.path.join(os.getcwd(), "chart.png")
    try:
        fig.write_image(chart_path)  # Requires kaleido
    except:
        chart_path = None

    # PDF Export
    st.subheader("📥 Download Report")

    def convert_html_to_pdf(source_html, output_path):
        with open(output_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(source_html, dest=pdf_file)
        return not pisa_status.err

    if st.button("Generate & Download PDF"):
        html_content = f"""
        <html>
        <head>
        <style>
        body {{ font-family: Arial; padding: 20px; }}
        h1 {{ color: navy; }}
        table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 6px; }}
        </style>
        </head>
        <body>
        <h1>Student Performance Report</h1>
        <h3>Clustering Summary</h3>
        {df.to_html(index=False)}
        """

        if chart_path:
            html_content += f'<h3>Visualization</h3><img src="{chart_path}" width="600">'
        html_content += "</body></html>"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            if convert_html_to_pdf(html_content, tmp_pdf.name):
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name="student_report.pdf")
            else:
                st.error("❌ Failed to generate PDF.")

else:
    st.info("📁 Please upload a CSV file to begin.")
