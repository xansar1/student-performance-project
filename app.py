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

        # student login
        student_username = admission_no
        student_password = f"{admission_no}@123"

        # parent login
        parent_username = f"P_{admission_no}"
        parent_password = f"{admission_no}@parent"

        student_users[student_username] = hashlib.sha256(
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


def generate_sample_csv():
    return pd.DataFrame({
        "ADMISSION_NO": ["NEET101", "NEET102"],
        "STUDENT_NAME": ["Ameen", "Fathima"],
        "COACHING_CENTRE": ["Focus Academy", "Focus Academy"],
        "BATCH": ["NEET Morning", "JEE Evening"],
        "PHYSICS_TEST": [78, 88],
        "CHEMISTRY_TEST": [85, 91],
        "BIOLOGY_TEST": [83, 89],
        "PARENT_PHONE": ["9876543210", "9876543211"]
    })

def render_login(student_users, parent_users):
    st.title("🔐 Coaching centre SaaS Login")

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


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Coaching Centre Analytics",
    page_icon="🎯",
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

# ---------------- SIDEBAR ----------------
institution_type = "Coaching Centre"
academic_level = None
department = None

st.sidebar.success("🏢 Coaching Centre SaaS Mode")

institution_brand = st.sidebar.text_input(
    "🏷 Coaching Centre Brand",
    "Focus Academy"
)

logo_url = st.sidebar.text_input(
    "🖼 Logo URL (optional)",
    ""
)

product_mode = st.sidebar.radio(
    "🚀 Analytics Mode",
    ["Standard Dashboard", "Advanced Analytics"]
)

# sample dataset
sample_df = generate_sample_csv()

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
    render_login(student_users, parent_users)
    st.stop()

# ---------------- WHITE LABEL BRANDING ----------------
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
    
# ---------------- DATA INPUT CENTER ----------------
st.subheader("📥 Smart Data Input Center")

input_mode = st.radio(
    "Choose Data Input Method",
    ["CSV Upload", "Quick Table Entry"]
)

df = None

if input_mode == "CSV Upload":
    uploaded_file = st.file_uploader(
        "📁 Upload CSV File",
        type=["csv"]
    )

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

elif input_mode == "Quick Table Entry":
    st.info("✍️ Enter marks directly like Excel")

    row_count = st.number_input(
        "Number of Students",
        min_value=1,
        max_value=1000,
        value=40
    )

    # dynamic subject count
    subject_count = st.number_input(
        "Number of Subjects",
        min_value=1,
        max_value=20,
        value=5
    )

    subject_names = []
    for i in range(subject_count):
        subject = st.text_input(
            f"Subject {i+1} Name",
            value=f"SUBJECT_{i+1}",
            key=f"sub_{i}"
        )
        subject_names.append(subject)

    # create empty editable dataframe
    editable_df = pd.DataFrame({
        "ADMISSION_NO": [f"ST{i+1:03}" for i in range(row_count)],
        "STUDENT_NAME": ["" for _ in range(row_count)],
        "PARENT_PHONE": ["" for _ in range(row_count)],
        **{sub: [0 for _ in range(row_count)] for sub in subject_names}
    })

    edited_df = st.data_editor(
        editable_df,
        use_container_width=True,
        num_rows="fixed"
    )

    if st.button("✅ Use Entered Data"):
        df = edited_df.copy()
        st.session_state.main_df = df
        st.success("✅ Table data loaded successfully")

# fallback from session
if df is None:
    if st.session_state.main_df is not None:
        df = st.session_state.main_df
    else:
        st.info("📁 Upload CSV or use Quick Table Entry")
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
@st.cache_data
def run_ai_pipeline(df):
    df = enrich_student_data(df)
    df = add_student_clusters(df)
    df = add_ai_dropout_prediction(df)

    if "AI_DROPOUT_RISK" not in df.columns:
        df["AI_DROPOUT_RISK"] = 0.0
        
    df = add_intervention_recommendations(df)
    df = add_next_semester_forecast(df)
    df = add_placement_prediction(df)
    return df
df = run_ai_pipeline(df)

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

primary_label = "Coaching Centre"
secondary_label = "Batch"

filter_col_1 = "COACHING_CENTRE"
filter_col_2 = "BATCH"

selected_centres = st.sidebar.multiselect(
    "Select Coaching Centre",
    options=df[filter_col_1].unique(),
    default=df[filter_col_1].unique()
)

selected_batches = st.sidebar.multiselect(
    "Select Batch",
    options=df[filter_col_2].unique(),
    default=df[filter_col_2].unique()
)

try:
    df = apply_academic_filters(
        df,
        selected_centres,
        selected_batches
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

topper_org = topper["COACHING_CENTRE"]
   
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
student_row = None
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

subject_cols = get_subject_mark_cols(
    df,
    {
        "TOTAL_SCORE",
        "GENERAL_SCORE",
        "DOMAIN_SCORE",
        "AI_DROPOUT_RISK",
        "DROPOUT_RISK",
        "PLACEMENT_PROBABILITY",
        "NEXT_SEM_PREDICTION",
        "CLUSTER",
        "REAL_ML_DROPOUT_PROB",
        "REAL_ML_PLACEMENT_PROB",
        "PARENT_PHONE"
    }
)

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

mark_cols = get_subject_mark_cols(
    df,
    {
        "ADMISSION_NO",
        "STUDENT_NAME",
        "TOTAL_SCORE",
        "GENERAL_SCORE",
        "DOMAIN_SCORE",
        "CLUSTER",
        "AI_DROPOUT_RISK",
        "PLACEMENT_PROBABILITY",
        "NEXT_SEM_PREDICTION"
    }
)

if len(mark_cols) >= 3:
    trend_subjects = mark_cols[:3]

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

phone = str(student_row.get("PARENT_PHONE", "")).strip()

alert_message = (
    f"Dear Parent, {student_row['STUDENT_NAME']} currently scored "
    f"{student_row['TOTAL_SCORE']}. "
    f"Dropout risk: {round(student_row['AI_DROPOUT_RISK'], 2)}. "
    f"Recommended support: {student_row['AI_INTERVENTION']}"
)

st.text_area(
    "WhatsApp Message Preview",
    value=alert_message,
    height=120
)

if phone and phone != "nan":
    whatsapp_url = (
        f"https://wa.me/91{phone}"
        f"?text={alert_message.replace(' ', '%20')}"
    )

    st.markdown(
        f"[📩 Send WhatsApp Alert to Parent]({whatsapp_url})"
    )
else:
    st.warning("⚠️ Parent phone number not available.")

# ---------------- BULK PARENT COMMUNICATION ----------------
st.subheader("👨‍👩‍👧 Bulk Parent Communication")

message_type = st.selectbox(
    "📨 Communication Type",
    [
        "Weak Student Alert",
        "Topper Appreciation",
        "Exam Reminder",
        "Homework Reminder"
    ]
)

selected_students = st.multiselect(
    "Select Students",
    df["STUDENT_NAME"].tolist(),
    default=df["STUDENT_NAME"].tolist()[:5]
)

bulk_df = df[df["STUDENT_NAME"].isin(selected_students)]

bulk_mark_cols = get_subject_mark_cols(
    df,
    {
        "ADMISSION_NO",
        "STUDENT_NAME",
        "TOTAL_SCORE",
        "GENERAL_SCORE",
        "DOMAIN_SCORE",
        "CLUSTER",
        "AI_DROPOUT_RISK",
        "PLACEMENT_PROBABILITY",
        "NEXT_SEM_PREDICTION",
        "PARENT_PHONE"
    }
)

for _, row in bulk_df.iterrows():
    phone = str(row.get("PARENT_PHONE", "")).strip()

    if not phone or phone == "nan":
        continue

    weakest_subject = min(bulk_mark_cols, key=lambda x: row[x])
    lowest_mark = row[weakest_subject]

    # dynamic weakest subject
    mark_cols = get_subject_mark_cols(
        df,
        {
            "ADMISSION_NO",
            "STUDENT_NAME",
            "TOTAL_SCORE",
            "GENERAL_SCORE",
            "DOMAIN_SCORE",
            "CLUSTER",
            "AI_DROPOUT_RISK",
            "PLACEMENT_PROBABILITY",
            "NEXT_SEM_PREDICTION"
        }
    )

    weakest_subject = min(mark_cols, key=lambda x: row[x])
    lowest_mark = row[weakest_subject]

    if message_type == "Weak Student Alert":
        msg = (
            f"Dear Parent, {row['STUDENT_NAME']} needs support in "
            f"{weakest_subject}. Current mark: {lowest_mark}."
        )

    elif message_type == "Topper Appreciation":
        msg = (
            f"Congratulations! {row['STUDENT_NAME']} scored "
            f"{row['TOTAL_SCORE']} marks. Great performance!"
        )

    elif message_type == "Exam Reminder":
        msg = (
            f"Reminder: Upcoming exam for {row['STUDENT_NAME']}. "
            f"Please ensure revision."
        )

    else:
        msg = (
            f"Homework reminder for {row['STUDENT_NAME']}. "
            f"Please complete today's revision."
        )

    whatsapp_url = (
        f"https://wa.me/91{phone}"
        f"?text={msg.replace(' ', '%20')}"
    )

    st.markdown(
        f"📲 {row['STUDENT_NAME']} → [Send Message]({whatsapp_url})"
    )

# ---------------- ADVANCED ANALYTICS ----------------
if product_mode == "Advanced Analytics":
    st.subheader("🎯 Advanced Academic Intelligence")

    # AI Cluster
    cluster_fig = px.scatter(
        df,
        x="TOTAL_SCORE",
        y="NEXT_SEM_PREDICTION",
        color="CLUSTER",
        hover_data=["STUDENT_NAME"]
    )
    st.plotly_chart(cluster_fig, use_container_width=True)

    # Dropout
    st.subheader("🤖 Dropout Risk Distribution")
    risk_fig = px.histogram(df, x="AI_DROPOUT_RISK")
    st.plotly_chart(risk_fig, use_container_width=True)

    # Placement
    st.subheader("🎓 Placement Probability")
    placement_fig = px.histogram(
        df,
        x="PLACEMENT_PROBABILITY"
    )
    st.plotly_chart(placement_fig, use_container_width=True)

    # Forecast
    st.subheader("📈 Next Semester Forecast")
    forecast_fig = px.scatter(
        df,
        x="TOTAL_SCORE",
        y="NEXT_SEM_PREDICTION",
        hover_data=["STUDENT_NAME"]
    )
    st.plotly_chart(forecast_fig, use_container_width=True)
    
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
