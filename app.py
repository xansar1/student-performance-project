import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import hashlib

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
from core.student_portal import get_student_record
from core.parent_portal import get_parent_student_record
from core.ml_training import (
    train_dropout_model,
    train_placement_model
)
from core.ml_inference import (
    predict_dropout_probability,
    predict_placement_probability
)

def generate_dynamic_credentials(df):
    student_users = {}
    parent_users = {}

    # Safety check
    if df is None or "ADMISSION_NO" not in df.columns:
        return student_users, parent_users

    for _, row in df.iterrows():
        admission_no = str(row["ADMISSION_NO"]).strip().upper()

        student_password = f"{admission_no}@123"
        parent_username = f"P_{admission_no}"
        parent_password = f"{admission_no}@parent"

        student_users[admission_no] = hashlib.sha256(
            student_password.encode()
        ).hexdigest()

        parent_users[parent_username] = hashlib.sha256(
            parent_password.encode()
        ).hexdigest()

    return student_users, parent_users

def get_subject_mark_cols(df, exclude_cols):
    return [
        col for col in df.columns
        if col not in exclude_cols
        and pd.api.types.is_numeric_dtype(df[col])
        and "RISK" not in col
        and "PROBABILITY" not in col
        and "PREDICTION" not in col
    ]
    
def generate_sample_csv(institution_type, academic_level=None):
    if institution_type == "School":
        if academic_level == "10":
            sample_df = pd.DataFrame({
                "ADMISSION_NO": ["ST101", "ST102"],
                "STUDENT_NAME": ["Ameen", "Fathima"],
                "CLASS": ["10", "10"],
                "SECTION": ["A", "B"],
                "MEDIUM": ["English", "Malayalam"],
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
                "ADMISSION_NO": ["ST103", "ST104"],
                "STUDENT_NAME": ["Ameen", "Fathima"],
                "CLASS": ["8", "9"],
                "SECTION": ["A", "B"],
                "MEDIUM": ["English", "Malayalam"],
                "ENGLISH": [78, 88],
                "MALAYALAM": [80, 90],
                "HINDI": [70, 85],
                "MATHS": [92, 95],
                "BASIC_SCIENCE": [85, 91],
                "SOCIAL_SCIENCE": [79, 87],
                "COMPUTER": [90, 94]
            })

    elif institution_type == "Higher Secondary":
        stream = academic_level if academic_level else "Science"

        if stream == "Science":
            sample_df = pd.DataFrame({
                "ADMISSION_NO": ["HF101", "HF102"],
                "STUDENT_NAME": ["Ameen", "Fathima"],
                "STREAM": ["Science", "Science"],
                "BATCH": ["2025", "2025"],
                "ENGLISH": [78, 88],
                "PHYSICS": [85, 91],
                "CHEMISTRY": [83, 89],
                "MATHS": [92, 95],
                "BIOLOGY": [84, 90],
                "COMPUTER": [90, 94]
            })
        elif stream == "Commerce":
            sample_df = pd.DataFrame({
                "ADMISSION_NO": ["HF103", "HF104"],
                "STUDENT_NAME": ["Ameen", "Fathima"],
                "STREAM": ["Commerce", "Commerce"],
                "BATCH": ["2025", "2025"],
                "ENGLISH": [78, 88],
                "ACCOUNTANCY": [85, 91],
                "BUSINESS_STUDIES": [83, 89],
                "ECONOMICS": [92, 95],
                "COMPUTER_APPLICATION": [84, 90]
            })
        else:
            sample_df = pd.DataFrame({
                "ADMISSION_NO": ["HF105", "HF106"],
                "STUDENT_NAME": ["Ameen", "Fathima"],
                "STREAM": ["Humanities", "Humanities"],
                "BATCH": ["2025", "2025"],
                "ENGLISH": [78, 88],
                "HISTORY": [85, 91],
                "POLITICAL_SCIENCE": [83, 89],
                "SOCIOLOGY": [92, 95],
                "ECONOMICS": [84, 90]
            })

    elif institution_type == "College":
        sample_df = pd.DataFrame({
            "ADMISSION_NO": ["COL101", "COL102"],
            "STUDENT_NAME": ["Ameen", "Fathima"],
            "INSTITUTION": ["ABC College", "ABC College"],
            "DEPARTMENT": ["BSc Computer Science", "BSc Computer Science"],
            "SEMESTER": ["S5", "S5"],
            "PYTHON_PROGRAMMING": [78, 88],
            "DBMS": [85, 91],
            "STATISTICS": [83, 89],
            "MACHINE_LEARNING": [92, 95]
        })

    else:
        sample_df = pd.DataFrame({
            "ADMISSION_NO": ["CO101", "CO102"],
            "STUDENT_NAME": ["Ameen", "Fathima"],
            "COACHING_CENTRE": ["Focus Academy", "Focus Academy"],
            "BATCH": ["NEET Morning", "JEE Evening"],
            "PHYSICS_TEST": [78, 88],
            "CHEMISTRY_TEST": [85, 91],
            "BIOLOGY_TEST": [83, 89]
        })

    return sample_df
# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Academic Performance Analytics",
    page_icon="🎓",
    layout="wide"
)
if "user_info" not in st.session_state:
    st.session_state.user_info = None

if "student_user" not in st.session_state:
    st.session_state.student_user = None

if "parent_user" not in st.session_state:
    st.session_state.parent_user = None

if "main_df" not in st.session_state:
    st.session_state.main_df = None
    
API_URL = "https://fantastic-space-garbanzo-97w9g7wgx77p3pvww-8000.app.github.dev"

# ---------------- SIDEBAR TOGGLES ----------------
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

credential_df = (
    st.session_state.main_df
    if st.session_state.main_df is not None
    else sample_df
)

student_users, parent_users = generate_dynamic_credentials(
    credential_df
)

# ---------------- LOGIN ----------------
if (
    st.session_state.user_info is None
    and st.session_state.student_user is None
    and st.session_state.parent_user is None
):
    st.title("🔐 Multi College SaaS Login")

    login_role = st.selectbox(
        "Login As",
        ["Institution Admin", "Student", "Parent"]
    )

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        if login_role == "Institution Admin":
            user_info = tenant_login(username, password)

            if user_info:
                st.session_state.user_info = user_info
                st.success("Admin login successful")
                st.rerun()
            else:
                st.error("Invalid admin credentials")

        elif login_role == "Student":
            hashed = hashlib.sha256(password.encode()).hexdigest()

            if student_users.get(username.upper()) == hashed:
                st.session_state.student_user = username.upper()
                st.success("Student login successful")
                st.rerun()
            else:
                st.error("Invalid student credentials")

        elif login_role == "Parent":
            hashed = hashlib.sha256(password.encode()).hexdigest()
            
            if parent_users.get(username.upper()) == hashed:
                st.session_state.parent_user = username.upper()
                st.success("Parent login successful")
                st.rerun()
            else:
                st.error("Invalid parent credentials")
                
    st.stop()

# ---------------- WHITE LABEL BRANDING ----------------
institution_brand = st.sidebar.text_input(
    "🏷 Institution Brand Name",
    "Your Institution"
)

logo_url = st.sidebar.text_input(
    "🖼 Logo URL (optional)",
    ""
)

st.title(f"🎓 {institution_brand} Academic Intelligence Dashboard")
st.caption(
    f"Premium AI-powered analytics platform for {institution_brand}"
)

if logo_url:
    st.image(logo_url, width=120)

# ---------------- ROLE BASED HEADER ----------------
if st.session_state.get("student_user"):
    st.success(
        f"👨‍🎓 Student Portal | Welcome "
        f"{st.session_state.student_user}"
    )

elif st.session_state.get("parent_user"):
    st.success(
        f"👨‍👩‍👧 Parent Portal | Welcome "
        f"{st.session_state.parent_user}"
    )

else:
    st.success("🏢 Institution Admin Dashboard")

# ---------------- LOGOUT ----------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.user_info = None
    st.session_state.student_user = None
    st.session_state.parent_user = None
    st.rerun()

st.download_button(
    "📥 Download Sample Format",
    data=sample_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{institution_type.lower()}_sample.csv",
    mime="text/csv"
)
    
# ---------------- FILE UPLOAD + LOAD DATA ----------------
uploaded_file = st.file_uploader("📁 Upload CSV File", type=["csv"])

if uploaded_file is not None:
    try:
        df = load_and_clean_data(
            uploaded_file,
            institution_type,
            academic_level,
            department=department
        )
        st.session_state.main_df = df

    except ValueError as e:
        st.error(str(e))
        st.stop()

elif st.session_state.main_df is not None:
    df = st.session_state.main_df

else:
    st.info("📁 Upload CSV file to access analytics dashboard")
    st.stop()

student_users, parent_users = generate_dynamic_credentials(df)

# ---------------- TENANT ISOLATION ----------------
if st.session_state.user_info:
    df = apply_role_college_filter(
        df,
        st.session_state.user_info
    )

if df.empty:
    st.warning("No data available for your college access.")
    st.stop()

# ---------------- AI ENRICHMENTS ----------------
df = enrich_student_data(df)
df = add_student_clusters(df)
df = add_ai_dropout_prediction(df)
df = add_intervention_recommendations(df)
df = add_next_semester_forecast(df)
df = add_placement_prediction(df)

# ---------------- ROLE BASED DASHBOARD ROUTING ----------------
if st.session_state.get("student_user"):
    st.subheader("👨‍🎓 Student Self-Service Portal")

    student_data = get_student_record(
        df,
        st.session_state.student_user
    )

    if student_data is not None:
        # Top metrics
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

        # Subject-wise marks
        st.subheader("📚 Subject-wise Marks")

        exclude_cols = {
            "ADMISSION_NO",
            "STUDENT_NAME",
            "CLASS",
            "SECTION",
            "MEDIUM",
            "TOTAL_SCORE",
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "CLUSTER",
            "AI_DROPOUT_RISK",
            "AI_INTERVENTION",
            "NEXT_SEM_PREDICTION",
            "PLACEMENT_PROBABILITY",
            "UNIVERSITY",
            "PROGRAM"
        }

        mark_cols = get_subject_mark_cols(df, exclude_cols)

        marks_df = pd.DataFrame({
            "Subject": mark_cols,
            "Score": [student_data[col] for col in mark_cols]
        })

        st.dataframe(marks_df, use_container_width=True)

        fig_student = px.bar(
            marks_df,
            x="Subject",
            y="Score",
            title=f"{student_data['STUDENT_NAME']} Subject Performance"
        )
        st.plotly_chart(fig_student, use_container_width=True)

        weakest = marks_df.sort_values("Score").iloc[0]
        st.warning(
            f"⚠️ Focus Area: {weakest['Subject']} "
            f"(Score: {weakest['Score']})"
        )

    else:
        st.warning("Student record not found.")

    st.stop()

if st.session_state.get("parent_user"):
    st.subheader("👨‍👩‍👧 Parent Progress Portal")

    student_data = get_parent_student_record(
        df,
        st.session_state.parent_user
    )

    if student_data is not None:
        # Top KPI cards
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

        # Subject-wise marks
        st.subheader("📚 Child Subject-wise Performance")

        exclude_cols = {
            "ADMISSION_NO",
            "STUDENT_NAME",
            "CLASS",
            "SECTION",
            "MEDIUM",
            "TOTAL_SCORE",
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "CLUSTER",
            "AI_DROPOUT_RISK",
            "AI_INTERVENTION",
            "NEXT_SEM_PREDICTION",
            "PLACEMENT_PROBABILITY",
            "UNIVERSITY",
            "PROGRAM"
        }

        mark_cols = get_subject_mark_cols(df, exclude_cols)

        marks_df = pd.DataFrame({
            "Subject": mark_cols,
            "Score": [student_data[col] for col in mark_cols]
        })

        st.dataframe(marks_df, use_container_width=True)

        fig_parent = px.bar(
            marks_df,
            x="Subject",
            y="Score",
            title=f"{student_data['STUDENT_NAME']} Subject Performance"
        )
        st.plotly_chart(fig_parent, use_container_width=True)

        # Weakest subject insight
        weakest = marks_df.sort_values("Score").iloc[0]
        st.error(
            f"⚠️ Parent Attention Needed: {weakest['Subject']} "
            f"(Score: {weakest['Score']})"
        )

        # Parent message preview
        st.subheader("📲 Suggested Parent Action")
        parent_msg = (
            f"Your child needs extra focus in {weakest['Subject']}. "
            f"Current score is {weakest['Score']}. "
            f"Recommended action: {student_data['AI_INTERVENTION']}"
        )
        st.text_area(
            "Parent Guidance",
            value=parent_msg,
            height=120
        )

    else:
        st.warning("Student record not found.")

    st.stop()

# ---------------- FILTERS ----------------
st.sidebar.header("🎛 Filters")

if institution_type == "School":
    primary_label = "Class"
    secondary_label = "Section / Stream"
elif institution_type == "Higher Secondary":
    primary_label = "Stream"
    secondary_label = "Subject Group"
elif institution_type == "College":
    primary_label = "Institution"
    secondary_label = "Department"
else:
    primary_label = "Coaching Centre"
    secondary_label = "Batch"

if institution_type == "School":
    filter_col_1 = "CLASS"
    filter_col_2 = "SECTION"

elif institution_type == "Higher Secondary":
    filter_col_1 = "STREAM"
    filter_col_2 = "BATCH"

elif institution_type == "College":
    filter_col_1 = "INSTITUTION"
    filter_col_2 = "DEPARTMENT"

else:
    filter_col_1 = "COACHING_CENTRE"
    filter_col_2 = "BATCH"

selected_university = st.sidebar.multiselect(
    f"Select {primary_label}",
    options=df[filter_col_1].unique(),
    default=df[filter_col_1].unique()
)

selected_program = st.sidebar.multiselect(
    f"Select {secondary_label}",
    options=df[filter_col_2].unique(),
    default=df[filter_col_2].unique()
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

topper_org = (
    topper["UNIVERSITY"]
    if "UNIVERSITY" in topper.index
    else topper[filter_col_1]
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("👨‍🎓 Total Students", total_students)
c2.metric("📈 Average Score", avg_score)
c3.metric("🏆 Top Score", top_score)
c4.metric("⚠️ At Risk", at_risk)

st.subheader("🚨 Students Needing Immediate Attention")

program_col = "PROGRAM" if "PROGRAM" in df.columns else filter_col_2

attention_df = df[
    df["AI_DROPOUT_RISK"] > 0.7
][
    [
        "STUDENT_NAME",
        program_col,
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
    f"{topper_org} | Score: {topper['TOTAL_SCORE']}"
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

benchmark_col = filter_col_1

university_avg = round(
    df[df[benchmark_col] == student_row[benchmark_col]]["TOTAL_SCORE"].mean(),
    2
)

benchmark_label = f"{primary_label} Avg"

compare_df = pd.DataFrame({
    "Category": ["Student Score", benchmark_label],
    "Score": [student_row["TOTAL_SCORE"], university_avg]
})

fig_compare = px.bar(
    compare_df,
    x="Category",
    y="Score",
    title=f"{student_row['STUDENT_NAME']} vs {benchmark_label}"
)
st.plotly_chart(fig_compare, use_container_width=True)

# ---------------- DATASET ----------------
st.subheader("📄 Student Dataset")
st.dataframe(df, use_container_width=True)

st.subheader("📚 Subject-wise Performance Insights")

metadata_cols = {
    "STUDENT_NAME",
    "CLASS",
    "SECTION",
    "MEDIUM",
    "STREAM",
    "BATCH",
    "INSTITUTION",
    "DEPARTMENT",
    "SEMESTER",
    "COACHING_CENTRE",
    "UNIVERSITY",
    "PROGRAM",
    "TOTAL_SCORE",
    "GENERAL_SCORE",
    "DOMAIN_SCORE",
    "CLUSTER",
    "AI_DROPOUT_RISK",
    "AI_INTERVENTION",
    "NEXT_SEM_PREDICTION",
    "PLACEMENT_PROBABILITY"
}

subject_cols = [
    col for col in df.select_dtypes(include="number").columns
    if col not in {
        "TOTAL_SCORE",
        "GENERAL_SCORE",
        "DOMAIN_SCORE",
        "AI_DROPOUT_RISK",
        "DROPOUT_RISK",
        "PLACEMENT_PROBABILITY",
        "NEXT_SEM_PREDICTION",
        "CLUSTER",
        "REAL_ML_DROPOUT_PROB",
        "REAL_ML_PLACEMENT_PROB"
    }
]

if len(subject_cols) > 0:
    subject_avg = (
        df[subject_cols]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    subject_avg.columns = ["Subject", "Average Score"]

    st.dataframe(subject_avg, use_container_width=True)

    fig_subjects = px.bar(
        subject_avg,
        x="Subject",
        y="Average Score",
        title="Subject-wise Average Performance"
    )
    st.plotly_chart(fig_subjects, use_container_width=True)

else:
    st.warning("No numeric subject columns found.")
    subject_avg = pd.DataFrame(
        columns=["Subject", "Average Score"]
    )

# ---------------- WEAKEST SUBJECT AI ----------------
st.subheader("🚨 Weakest Subject Intelligence")

if not subject_avg.empty:
    weakest_subject = subject_avg.sort_values(
        by="Average Score"
    ).iloc[0]

    st.error(
        f"⚠️ Weakest Subject: {weakest_subject['Subject']} "
        f"(Avg Score: {round(weakest_subject['Average Score'], 2)})"
    )
else:
    st.info("Weakest subject analysis unavailable.")

# ---------------- BATCH / DEPARTMENT COMPARISON ----------------
st.subheader("🏫 Batch / Department Comparison")

batch_comparison = (
    df.groupby(filter_col_2)["TOTAL_SCORE"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

batch_comparison.columns = [secondary_label, "Average Score"]

st.dataframe(batch_comparison, use_container_width=True)

fig_batch = px.bar(
    batch_comparison,
    x=secondary_label,
    y="Average Score",
    title=f"{secondary_label} Performance Comparison"
)
st.plotly_chart(fig_batch, use_container_width=True)

# ---------------- STUDENT GROWTH TREND ----------------
st.subheader("📈 Student Growth Trend")

if len(subject_cols) >= 3:
    trend_subjects = subject_cols[:3]

    trend_df = pd.DataFrame({
        "Assessment": trend_subjects,
        "Score": [student_row[col] for col in trend_subjects]
    })

    fig_trend = px.line(
        trend_df,
        x="Assessment",
        y="Score",
        markers=True,
        title=f"{student_row['STUDENT_NAME']} Progress Trend"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("Not enough test/subject columns for growth trend.")

# ---------------- PARENT WHATSAPP ALERT TEMPLATE ----------------
st.subheader("📲 Parent WhatsApp Alert")

alert_message = (
    f"Dear Parent, {student_row['STUDENT_NAME']} currently has "
    f"a score of {student_row['TOTAL_SCORE']} with dropout risk "
    f"probability {round(student_row['AI_DROPOUT_RISK'], 2)}. "
    f"Recommended support: {student_row['AI_INTERVENTION']}"
)

st.text_area(
    "WhatsApp Message Preview",
    value=alert_message,
    height=120
)

# ---------------- REVENUE RISK INTELLIGENCE ----------------
st.subheader("💸 Revenue Retention Risk")

revenue_risk_students = df[
    df["AI_DROPOUT_RISK"] > 0.6
][
    [
        "STUDENT_NAME",
        "TOTAL_SCORE",
        "AI_DROPOUT_RISK"
    ]
].copy()

if not revenue_risk_students.empty:
    revenue_risk_students["Retention Risk"] = (
        revenue_risk_students["AI_DROPOUT_RISK"]
        .apply(lambda x: "High" if x > 0.8 else "Medium")
    )

    st.dataframe(
        revenue_risk_students,
        use_container_width=True
    )

    high_risk_count = len(
        revenue_risk_students[
            revenue_risk_students["Retention Risk"] == "High"
        ]
    )

    st.error(
        f"⚠️ Estimated High Revenue Risk Students: "
        f"{high_risk_count}"
    )
else:
    st.success("✅ No revenue retention risk students detected.")

# ---------------- PREMIUM UPSELL INTELLIGENCE ----------------
st.subheader("🎯 Premium Upsell Opportunities")

upsell_students = df[
    (df["TOTAL_SCORE"] > df["TOTAL_SCORE"].mean()) &
    (df["PLACEMENT_PROBABILITY"] > 0.7)
][
    [
        "STUDENT_NAME",
        "TOTAL_SCORE",
        "PLACEMENT_PROBABILITY"
    ]
]

st.dataframe(upsell_students, use_container_width=True)

st.success(
    f"💰 Premium Program Upsell Candidates: {len(upsell_students)}"
)

# ---------------- AI SALES RECOMMENDATION ENGINE ----------------
st.subheader("🤖 AI Course Sales Recommendations")

def recommend_course(row):
    if row["AI_DROPOUT_RISK"] > 0.7:
        return "Remedial Support Program"
    elif row["PLACEMENT_PROBABILITY"] > 0.8:
        return "Placement Bootcamp"
    elif row["TOTAL_SCORE"] > df["TOTAL_SCORE"].mean():
        return "Advanced Excellence Batch"
    else:
        return "Standard Progress Program"

sales_df = df[
    [
        "STUDENT_NAME",
        "TOTAL_SCORE",
        "AI_DROPOUT_RISK",
        "PLACEMENT_PROBABILITY"
    ]
].copy()

sales_df["Recommended Program"] = sales_df.apply(
    recommend_course,
    axis=1
)

st.dataframe(sales_df, use_container_width=True)

# ---------------- AI COUNSELOR FOLLOW-UP DASHBOARD ----------------
st.subheader("📞 Counselor Follow-up Priority")

followup_df = sales_df.copy()

def get_followup_priority(row):
    if row["AI_DROPOUT_RISK"] > 0.8:
        return "Urgent Parent Call"
    elif row["Recommended Program"] in [
        "Placement Bootcamp",
        "Advanced Excellence Batch"
    ]:
        return "Upsell Counseling"
    else:
        return "Routine Academic Follow-up"

followup_df["Counselor Action"] = followup_df.apply(
    get_followup_priority,
    axis=1
)

st.dataframe(
    followup_df[
        [
            "STUDENT_NAME",
            "Recommended Program",
            "Counselor Action"
        ]
    ],
    use_container_width=True
)

# ---------------- REVENUE FORECAST DASHBOARD ----------------
st.subheader("📊 Revenue Forecast Intelligence")

base_fee = 3000
premium_fee = 8000

expected_renewals = len(
    df[df["AI_DROPOUT_RISK"] <= 0.6]
)

expected_premium = len(
    sales_df[
        sales_df["Recommended Program"].isin([
            "Placement Bootcamp",
            "Advanced Excellence Batch"
        ])
    ]
)

forecast_revenue = (
    expected_renewals * base_fee
) + (
    expected_premium * premium_fee
)

st.metric("💰 Expected Next Month Revenue", f"₹{forecast_revenue:,}")
st.metric("📈 Expected Renewals", expected_renewals)
st.metric("🎯 Premium Upsells", expected_premium)

# ---------------- ROI PROPOSAL GENERATOR ----------------
st.subheader("🧾 ROI Proposal Summary")

monthly_subscription = 5000
roi_gain = forecast_revenue - monthly_subscription

proposal_text = f"""
Institution Revenue Forecast: ₹{forecast_revenue:,}
Expected Premium Upsells: {expected_premium}
Expected Renewals: {expected_renewals}

Suggested SaaS Subscription: ₹{monthly_subscription:,}/month

Estimated ROI Gain After Subscription:
₹{roi_gain:,} per month
"""

st.text_area(
    "Institution ROI Proposal",
    value=proposal_text,
    height=220
)

# ---------------- CLUSTER ----------------
st.subheader("🧩 AI Cluster Segmentation")

numeric_cols = df.select_dtypes(include="number").columns.tolist()

preferred_x = "GENERAL_SCORE"
preferred_y = "DOMAIN_SCORE"

if len(numeric_cols) >= 2:
    x_col = preferred_x if preferred_x in numeric_cols else numeric_cols[0]
    y_col = preferred_y if preferred_y in numeric_cols else numeric_cols[1]

    cluster_fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="CLUSTER",
        size="TOTAL_SCORE" if "TOTAL_SCORE" in df.columns else None,
        hover_data=["STUDENT_NAME"],
        title=f"AI Cluster Segmentation ({x_col} vs {y_col})"
    )
    st.plotly_chart(cluster_fig, use_container_width=True)
else:
    st.warning("Not enough numeric columns for clustering chart.")

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
