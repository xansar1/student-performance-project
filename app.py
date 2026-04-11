import streamlit as st
import pandas as pd
import requests
import plotly.express as px

from core.data_loader import load_and_clean_data
from core.analytics import (
    enrich_student_data,
    get_kpis,
    get_topper
)
from core.reporting import (
    generate_pdf_report,
    send_email_report,
    generate_parent_pdf
)
from core.notifications import generate_parent_alert
from core.clustering import add_student_clusters
from core.filters import (
    apply_academic_filters,
    validate_filtered_data
)
from core.predictive_model import add_ai_dropout_prediction
from core.intervention_engine import add_intervention_recommendations
from core.forecasting import add_next_semester_forecast
from core.placement_ai import add_placement_prediction
from core.model_evaluation import build_evaluation_dataframe
from core.genai_advisor import generate_student_advisor_report
from core.tenant_auth import tenant_login
from core.role_access import apply_role_college_filter
from core.student_auth import student_login
from core.student_portal import get_student_record
from core.parent_auth import parent_login
from core.parent_portal import get_parent_student_record
from core.ml_training import (
    train_dropout_model,
    train_placement_model
)
from core.ml_inference import (
    predict_dropout_probability,
    predict_placement_probability
)

def generate_sample_csv(institution_type, academic_level=None):
    if institution_type == "School":
        if academic_level == "10":
            sample_df = pd.DataFrame({
                "STUDENT_NAME": ["Ameen", "Fathima"],
                "ENGLISH": [78, 88],
                "MALAYALAM": [80, 90],
                "HINDI": [70, 85],
                "MATHS": [92, 95],
                "PHYSICS": [85, 91],
                "CHEMISTRY": [83, 89],
                "BIOLOGY": [84, 90],
                "SOCIAL_SCIENCE": [79, 87],
                "COMPUTER": [90, 94]
            })
        else:
            sample_df = pd.DataFrame({
                "STUDENT_NAME": ["Ameen", "Fathima"],
                "ENGLISH": [78, 88],
                "MALAYALAM": [80, 90],
                "HINDI": [70, 85],
                "MATHS": [92, 95],
                "BASIC_SCIENCE": [85, 91],
                "SOCIAL_SCIENCE": [79, 87],
                "COMPUTER": [90, 94]
            })

    elif institution_type == "Higher Secondary":
        sample_df = pd.DataFrame({
            "STUDENT_NAME": ["Ameen", "Fathima"],
            "ENGLISH": [78, 88],
            "PHYSICS": [85, 91],
            "CHEMISTRY": [83, 89],
            "MATHS": [92, 95],
            "BIOLOGY": [84, 90],
            "COMPUTER": [90, 94]
        })

    elif institution_type == "College":
        sample_df = pd.DataFrame({
            "STUDENT_NAME": ["Ameen", "Fathima"],
            "SUBJECT_1": [78, 88],
            "SUBJECT_2": [85, 91],
            "SUBJECT_3": [83, 89],
            "SUBJECT_4": [92, 95]
        })

    else:
        sample_df = pd.DataFrame({
            "STUDENT_NAME": ["Ameen", "Fathima"],
            "TEST_1": [78, 88],
            "TEST_2": [85, 91],
            "TEST_3": [83, 89]
        })

    return sample_df

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Academic Performance Analytics",
    page_icon="🎓",
    layout="wide"
)
API_URL = "https://fantastic-space-garbanzo-97w9g7wgx77p3pvww-8000.app.github.dev"

# ---------------- LOGIN ----------------
if "user_info" not in st.session_state:
    st.session_state.user_info = None

if st.session_state.user_info is None:
    st.title("🔐 Multi College SaaS Login")

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        user_info = tenant_login(username, password)

        if user_info:
            st.session_state.user_info = user_info
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- LOGOUT ----------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.user_info = None
    st.rerun()

# ---------------- PAGE HEADER ----------------
st.title("🎓 AI Academic Performance Analytics Dashboard")
st.caption("Premium SaaS-style student performance intelligence system")

# ---------------- CSV GUIDE ----------------
st.subheader("📘 CSV Format Guide")

sample_df = pd.DataFrame({
    "STUDENT_NAME": ["Aarav", "Meera"],
    "UNIVERSITY": ["MG University", "KTU"],
    "PROGRAM": ["BTech AI", "MBA"],
    "SPECIALISATION": ["Machine Learning", "Finance"],
    "EMAIL": ["aarav@example.com", "meera@example.com"],
    "GENDER": ["Male", "Female"],
    "GENERAL_SCORE": [45, 38],
    "DOMAIN_SCORE": [42, 40],
    "TOTAL_SCORE": [87, 78]
})

st.download_button(
    "📥 Download Sample CSV Format",
    data=sample_df.to_csv(index=False).encode("utf-8"),
    file_name="sample_format.csv",
    mime="text/csv"
)

# ---------------- SIDEBAR TOGGLES ----------------
st.sidebar.markdown("## 👨‍🎓 Student Portal")
student_mode = st.sidebar.toggle("Enable Student Login")

st.sidebar.markdown("## 👨‍👩‍👧 Parent Portal")
parent_mode = st.sidebar.toggle("Enable Parent Login")

institution_type = st.sidebar.selectbox(
    "🏢 Institution Type",
    ["School", "Higher Secondary", "College", "Coaching Centre"]
)

academic_level = None
department = None

if institution_type == "School":
    academic_level = st.sidebar.selectbox(
        "📚 Class",
        ["1-9", "10"]
    )

elif institution_type == "Higher Secondary":
    academic_level = st.sidebar.selectbox(
        "🎓 Stream",
        ["Science", "Commerce", "Humanities"]
    )

elif institution_type == "College":
    department = st.sidebar.text_input("🏛 Department")

sample_df = generate_sample_csv(
    institution_type,
    academic_level
)

st.download_button(
    "📥 Download Sample Format",
    data=sample_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{institution_type.lower()}_sample.csv",
    mime="text/csv"
)
    
# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📁 Upload CSV File", type=["csv"])

if not uploaded_file:
    st.info("📁 Upload CSV file to access analytics dashboard")
    st.stop()

# ---------------- LOAD DATA ----------------
try:
    df = load_and_clean_data(
        uploaded_file,
        institution_type
    )
except ValueError as e:
    st.error(str(e))
    st.stop()

# ---------------- TENANT ISOLATION ----------------
df = apply_role_college_filter(
    df,
    st.session_state.user_info
)

if df.empty:
    st.warning("No data available for your college access.")
    st.stop()

# ---------------- FILTERS ----------------
st.sidebar.header("🎛 Filters")

selected_university = st.sidebar.multiselect(
    "Select University",
    options=df["UNIVERSITY"].unique(),
    default=df["UNIVERSITY"].unique()
)

selected_program = st.sidebar.multiselect(
    "Select Program",
    options=df["PROGRAM"].unique(),
    default=df["PROGRAM"].unique()
)

try:
    df = apply_academic_filters(
        df,
        selected_university,
        selected_program
    )
    validate_filtered_data(df)
except ValueError as e:
    st.warning(str(e))
    st.stop()

# ---------------- AI ENRICHMENTS ----------------
df = enrich_student_data(df)
df = add_student_clusters(df)
df = add_ai_dropout_prediction(df)
df = add_intervention_recommendations(df)
df = add_next_semester_forecast(df)
df = add_placement_prediction(df)

# ---------------- KPI ----------------
kpis = get_kpis(df)

try:
    api_kpis = requests.get(f"{API_URL}/analytics/kpis", timeout=5).json()
except Exception:
    api_kpis = {
        "total_students": "N/A",
        "avg_score": "N/A"
    }

total_students = kpis["total_students"]
avg_score = kpis["avg_score"]
top_score = kpis["top_score"]
at_risk = kpis["at_risk"]

topper = get_topper(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("👨‍🎓 Total Students", total_students)
c2.metric("📈 Average Score", avg_score)
c3.metric("🏆 Top Score", top_score)
c4.metric("⚠️ At Risk", at_risk)

st.subheader("🚨 Students Needing Immediate Attention")

attention_df = df[
    df["AI_DROPOUT_RISK"] > 0.7
][
    [
        "STUDENT_NAME",
        "PROGRAM",
        "TOTAL_SCORE",
        "AI_DROPOUT_RISK"
    ]
]

st.dataframe(attention_df, use_container_width=True)

st.info(
    f"🌐 Live Backend API Connected | "
    f"Students: {api_kpis['total_students']} | "
    f"Avg: {api_kpis['avg_score']}"
)

st.success(
    f"🏆 Top Performer: {topper['STUDENT_NAME']} | "
    f"{topper['UNIVERSITY']} | Score: {topper['TOTAL_SCORE']}"
)

# ---------------- STUDENT SEARCH ----------------
student_name = st.selectbox(
    "🔍 Select Student",
    df["STUDENT_NAME"].sort_values().unique()
)

student_row = df[df["STUDENT_NAME"] == student_name].iloc[0]

parent_pdf = generate_parent_pdf(student_row)

st.download_button(
    "📄 Download Parent Progress Report",
    data=parent_pdf,
    file_name=f"{student_name}_progress_report.pdf",
    mime="application/pdf"
)

st.subheader("📲 Parent Alert Preview")
st.warning(generate_parent_alert(student_row))

university_avg = round(
    df[df["UNIVERSITY"] == student_row["UNIVERSITY"]]["TOTAL_SCORE"].mean(),
    2
)

compare_df = pd.DataFrame({
    "Category": ["Student Score", "University Avg"],
    "Score": [student_row["TOTAL_SCORE"], university_avg]
})

fig_compare = px.bar(
    compare_df,
    x="Category",
    y="Score",
    title=f"{student_row['STUDENT_NAME']} Benchmark Comparison"
)
st.plotly_chart(fig_compare, use_container_width=True)

# ---------------- DATASET ----------------
st.subheader("📄 Student Dataset")
st.dataframe(df, use_container_width=True)

# ---------------- CLUSTER ----------------
cluster_fig = px.scatter(
    df,
    x="GENERAL_SCORE",
    y="DOMAIN_SCORE",
    color="CLUSTER",
    size="TOTAL_SCORE",
    hover_data=["STUDENT_NAME", "GRADE"],
    title="AI Cluster Segmentation"
)
st.plotly_chart(cluster_fig, use_container_width=True)

# ---------------- DROPOUT ----------------
st.subheader("🤖 AI Dropout Prediction")

risk_fig = px.histogram(
    df,
    x="AI_DROPOUT_RISK",
    nbins=20,
    title="AI Dropout Risk Probability Distribution"
)
st.plotly_chart(risk_fig, use_container_width=True)

# ---------------- INTERVENTION ----------------
st.subheader("🎯 Personalized AI Intervention Engine")
st.dataframe(
    df[
        [
            "STUDENT_NAME",
            "TOTAL_SCORE",
            "AI_DROPOUT_RISK",
            "AI_INTERVENTION"
        ]
    ],
    use_container_width=True
)

# ---------------- FORECAST ----------------
st.subheader("📈 Next Semester Forecasting AI")

forecast_fig = px.scatter(
    df,
    x="TOTAL_SCORE",
    y="NEXT_SEM_PREDICTION",
    hover_data=["STUDENT_NAME"],
    title="Current Score vs Next Semester Forecast"
)
st.plotly_chart(forecast_fig, use_container_width=True)

# ---------------- PLACEMENT ----------------
st.subheader("🎓 Placement Prediction AI")

placement_fig = px.histogram(
    df,
    x="PLACEMENT_PROBABILITY",
    nbins=20,
    title="Placement Probability Distribution"
)
st.plotly_chart(placement_fig, use_container_width=True)

# ---------------- MODEL EVAL ----------------
st.subheader("📊 AI Model Evaluation Dashboard")
eval_df = build_evaluation_dataframe(df)
st.dataframe(eval_df, use_container_width=True)

# ---------------- GENAI ADVISOR ----------------
st.subheader("🧠 GenAI Academic Advisor")
advisor_report = generate_student_advisor_report(student_row)
st.markdown(advisor_report)

# ---------------- STUDENT PORTAL ----------------
if student_mode:
    st.subheader("👨‍🎓 Student Self-Service Portal")

    student_user = st.text_input("Student Username")
    student_pass = st.text_input("Student Password", type="password")

    if st.button("Student Login"):
        if student_login(student_user, student_pass):
            student_data = get_student_record(df, student_user)

            if student_data is not None:
                s1, s2, s3 = st.columns(3)
                s1.metric("📈 Current Score", student_data["TOTAL_SCORE"])
                s2.metric(
                    "🎯 Placement Probability",
                    round(student_data["PLACEMENT_PROBABILITY"], 2)
                )
                s3.metric(
                    "📈 Next Semester Forecast",
                    round(student_data["NEXT_SEM_PREDICTION"], 2)
                )
                st.info(student_data["AI_INTERVENTION"])
            else:
                st.warning("Student record not found.")
        else:
            st.error("Invalid student login")

# ---------------- PARENT PORTAL ----------------
if parent_mode:
    st.subheader("👨‍👩‍👧 Parent Progress Portal")

    parent_user = st.text_input("Parent Username")
    parent_pass = st.text_input("Parent Password", type="password")

    if st.button("Parent Login"):
        if parent_login(parent_user, parent_pass):
            student_data = get_parent_student_record(df, parent_user)

            if student_data is not None:
                p1, p2, p3 = st.columns(3)
                p1.metric("📈 Current Score", student_data["TOTAL_SCORE"])
                p2.metric(
                    "🚨 Dropout Risk",
                    round(student_data["AI_DROPOUT_RISK"], 2)
                )
                p3.metric(
                    "🎯 Placement Probability",
                    round(student_data["PLACEMENT_PROBABILITY"], 2)
                )
                st.warning(student_data["AI_INTERVENTION"])
            else:
                st.warning("Student record not found.")
        else:
            st.error("Invalid parent login")

# ---------------- REAL ML ----------------
st.subheader("🌲 Real ML Training Pipeline")

if st.button("🚀 Train Real ML Models"):
    dropout_acc = train_dropout_model(df)
    placement_acc = train_placement_model(df)

    st.success(
        f"Dropout Model Accuracy: {dropout_acc} | "
        f"Placement Model Accuracy: {placement_acc}"
    )

    df = predict_dropout_probability(df)
    df = predict_placement_probability(df)

    st.dataframe(
        df[
            [
                "STUDENT_NAME",
                "REAL_ML_DROPOUT_PROB",
                "REAL_ML_PLACEMENT_PROB"
            ]
        ],
        use_container_width=True
    )

# ---------------- REPORTING ----------------
pdf_buffer = generate_pdf_report(
    df,
    total_students,
    avg_score,
    top_score,
    at_risk
)

st.download_button(
    label="📄 Download Executive PDF",
    data=pdf_buffer,
    file_name="executive_student_report.pdf",
    mime="application/pdf"
)

st.markdown("### 📧 Email Executive Report")
email = st.text_input("Enter recipient email")

if st.button("📤 Send PDF Report"):
    if email:
        send_email_report(
            email,
            pdf_buffer,
            st.secrets["EMAIL"],
            st.secrets["APP_PASSWORD"]
        )
        st.success("PDF sent successfully")
    else:
        st.warning("Please enter recipient email")
