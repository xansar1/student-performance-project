import streamlit as st
import pandas as pd
import plotly.express as px

from core.auth import check_login
from core.data_loader import load_and_clean_data
from core.analytics import (
    enrich_student_data,
    get_kpis,
    get_topper
)
from core.reporting import (
    generate_pdf_report,
    send_email_report
)
from core.clustering import add_student_clusters
from core.filters import (
    apply_academic_filters,
    validate_filtered_data
)
from core.predictive_model import add_ai_dropout_prediction
from core.intervention_engine import add_intervention_recommendations
from core.forecasting import add_next_semester_forecast

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Academic Performance Analytics",
    page_icon="🎓",
    layout="wide"
)

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 AI Academic Login Portal")

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()

# ---------------- LOGOUT ----------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
</style>
""", unsafe_allow_html=True)

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

csv_sample = sample_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Sample CSV Format",
    data=csv_sample,
    file_name="sample_format.csv",
    mime="text/csv"
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📁 Upload CSV File", type=["csv"])

if uploaded_file:
    try:
        df = load_and_clean_data(uploaded_file)
    except ValueError as e:
        st.error(str(e))
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

    # ---------------- ANALYTICS ----------------
    df = enrich_student_data(df)
    df = add_student_clusters(df)
    df = add_ai_dropout_prediction(df)
    df = add_intervention_recommendations(df)
    df = add_next_semester_forecast(df)

    kpis = get_kpis(df)

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

    st.success(
        f"🏆 Top Performer: {topper['STUDENT_NAME']} | "
        f"{topper['UNIVERSITY']} | Score: {topper['TOTAL_SCORE']}"
    )

    # ---------------- SEARCH ----------------
    student_name = st.selectbox(
        "🔍 Select Student",
        df["STUDENT_NAME"].sort_values().unique()
    )

    student_row = df[df["STUDENT_NAME"] == student_name].iloc[0]

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

    # ---------------- CLUSTER CHART ----------------
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
    
    # ---------------- DROPOUT CHART --------------
    st.subheader("🤖 AI Dropout Prediction")

    risk_fig = px.histogram(
        df,
        x="AI_DROPOUT_RISK",
        nbins=20,
        title="AI Dropout Risk Probability Distribution"
    )
    st.plotly_chart(risk_fig, use_container_width=True)

    # ------------ INTERVENTION ENGINE ------------
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

    # --------------- SEMESTER FORECASTING --------------
    st.subheader("📈 Next Semester Forecasting AI")

    forecast_fig = px.scatter(
        df,
        x="TOTAL_SCORE",
        y="NEXT_SEM_PREDICTION",
        hover_data=["STUDENT_NAME"],
        title="Current Score vs Next Semester Forecast"
    )
    st.plotly_chart(forecast_fig, use_container_width=True)

    # -------------- FORECAST TABLE ------------
    st.dataframe(
        df[
            [ 
                "STUDENT_NAME",
                "TOTAL_SCORE",
                "NEXT_SEM_PREDICTION"
            ]
        ],
        use_container_width=True
    )

    # ---------------- PDF ----------------
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

    # ---------------- EMAIL ----------------
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
