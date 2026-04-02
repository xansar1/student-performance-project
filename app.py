import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from xhtml2pdf import pisa

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Academic Performance Analytics",
    page_icon="🎓",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.metric-card {
    background: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 AI Academic Performance Analytics Dashboard")
st.caption("Premium SaaS-style student performance intelligence system")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📁 Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ---------------- CLEANING ----------------
    df.columns = [col.strip().replace(" ", "_").upper() for col in df.columns]

    rename_map = {
        "NAME_OF_THE_STUDENT": "STUDENT_NAME",
        "PROGRAM_NAME": "PROGRAM",
        "GENERAL_MANAGEMENT_SCORE_(OUT_OF_50)": "GENERAL_SCORE",
        "DOMAIN_SPECIFIC_SCORE_(OUT_50)": "DOMAIN_SCORE",
        "TOTAL_SCORE_(OUT_OF_100)": "TOTAL_SCORE"
    }

    df.rename(columns=rename_map, inplace=True)

    # fallback optional columns
    for col in ["EMAIL", "GENDER", "UNIVERSITY", "SPECIALISATION"]:
        if col not in df.columns:
            df[col] = "N/A"

    # ---------------- ADD GRADE ----------------
    def get_grade(score):
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 50:
            return "C"
        return "D"

    df["GRADE"] = df["TOTAL_SCORE"].apply(get_grade)

    # ---------------- KPI SECTION ----------------
    total_students = len(df)
    avg_score = round(df["TOTAL_SCORE"].mean(), 2)
    top_score = int(df["TOTAL_SCORE"].max())
    at_risk = len(df[df["TOTAL_SCORE"] < 50])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👨‍🎓 Total Students", total_students)
    c2.metric("📈 Average Score", avg_score)
    c3.metric("🏆 Top Score", top_score)
    c4.metric("⚠️ At Risk", at_risk)

    st.divider()

    # ---------------- DATA PREVIEW ----------------
    st.subheader("📄 Student Dataset")
    st.dataframe(
        df.style.highlight_max(subset=["TOTAL_SCORE"], color="lightgreen")
                .highlight_min(subset=["TOTAL_SCORE"], color="salmon"),
        use_container_width=True
    )

    # ---------------- CLUSTERING ----------------
    st.subheader("🎯 AI Performance Clustering")

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

    # ---------------- CHARTS ----------------
    col1, col2 = st.columns(2)

    with col1:
        top10 = df.sort_values("TOTAL_SCORE", ascending=False).head(10)
        fig_bar = px.bar(
            top10,
            x="STUDENT_NAME",
            y="TOTAL_SCORE",
            title="🏆 Top 10 Students"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_pie = px.pie(
            df,
            names="GRADE",
            title="📊 Grade Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------- UNIVERSITY INSIGHTS ----------------
    st.subheader("🏫 University-wise Performance")
    uni_avg = df.groupby("UNIVERSITY")["TOTAL_SCORE"].mean().reset_index()
    fig_uni = px.bar(
        uni_avg,
        x="UNIVERSITY",
        y="TOTAL_SCORE",
        title="Average Score by University"
    )
    st.plotly_chart(fig_uni, use_container_width=True)

    # ---------------- AI RECOMMENDATIONS ----------------
    st.subheader("🤖 AI Recommendations")
    weak_students = df[df["TOTAL_SCORE"] < 50]

    if len(weak_students) > 0:
        for _, row in weak_students.iterrows():
            st.warning(
                f"{row['STUDENT_NAME']} needs academic support in {row['PROGRAM']} "
                f"(Score: {row['TOTAL_SCORE']})"
            )
    else:
        st.success("🎉 No at-risk students detected.")

    # ---------------- PDF EXPORT ----------------
    st.subheader("📥 Executive PDF Report")

    def convert_html_to_pdf(source_html, output_path):
        with open(output_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(source_html, dest=pdf_file)
        return not pisa_status.err

    if st.button("Generate Executive PDF"):
        html = f"""
        <html>
        <body style="font-family: Arial;">
            <h1 style="color:navy;">🎓 Student Performance Executive Report</h1>
            <p>Total Students: {total_students}</p>
            <p>Average Score: {avg_score}</p>
            <p>Top Score: {top_score}</p>
            <p>At Risk Students: {at_risk}</p>
            <h3>Detailed Data</h3>
            {df.to_html(index=False)}
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            if convert_html_to_pdf(html, tmp_pdf.name):
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button(
                        "📄 Download PDF",
                        f,
                        file_name="executive_student_report.pdf"
                    )
            else:
                st.error("❌ PDF generation failed.")

else:
    st.info("📁 Upload a CSV file to start analytics.")
