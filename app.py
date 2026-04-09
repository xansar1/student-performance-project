import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from core.auth import check_login
from core.data_loader import load_and_clean_data
from core.analytics import (
    get_grade,
    placement_readiness,
    dropout_risk
)
from core.pdf_report import generate_pdf
from core.mailer import send_email_report


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Academic Performance Analytics",
    page_icon="🎓",
    layout="wide"
)

# ---------------- LOGIN SYSTEM ----------------
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

    df = df[
        (df["UNIVERSITY"].isin(selected_university)) &
        (df["PROGRAM"].isin(selected_program))
    ]

    if df.empty:
        st.warning("No students match selected filters.")
        st.stop()

    # ---------------- ANALYTICS COLUMNS ----------------
    df["GRADE"] = df["TOTAL_SCORE"].apply(get_grade)
    df["PLACEMENT_STATUS"] = df["TOTAL_SCORE"].apply(
        placement_readiness
    )
    df["DROPOUT_RISK"] = df["TOTAL_SCORE"].apply(dropout_risk)

    # ---------------- KPI ----------------
    total_students = len(df)
    avg_score = round(df["TOTAL_SCORE"].mean(), 2)
    top_score = int(df["TOTAL_SCORE"].max())
    at_risk = len(df[df["TOTAL_SCORE"] < 50])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👨‍🎓 Total Students", total_students)
    c2.metric("📈 Average Score", avg_score)
    c3.metric("🏆 Top Score", top_score)
    c4.metric("⚠️ At Risk", at_risk)

    topper = df.loc[df["TOTAL_SCORE"].idxmax()]

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

    # ---------------- CLUSTERING ----------------
    features = df[["GENERAL_SCORE", "DOMAIN_SCORE", "TOTAL_SCORE"]]
    scaled = StandardScaler().fit_transform(features)

    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["CLUSTER"] = model.fit_predict(scaled)

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

    # ---------------- PDF ----------------
    pdf_buffer = generate_pdf(
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
            send_email_report(email, pdf_buffer)
            st.success("PDF sent successfully")
        else:
            st.warning("Please enter recipient email")
