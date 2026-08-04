"""
app.py
Streamlit UI for the Resume <-> Job Description Matcher.
Run with: streamlit run app.py
"""

import streamlit as st
import tempfile
import os

from src.scorer import score_resume_against_jd

st.set_page_config(page_title="Resume Matcher", page_icon="📄", layout="centered")

st.title("📄 Resume ↔ Job Description Matcher")
st.write(
    "Upload your resume, add the job title, and paste the job description "
    "to get an ATS-style match score."
)

resume_file = st.file_uploader("Upload your Resume", type=["pdf", "docx", "txt"])
job_title = st.text_input("Job Title (as listed in the posting)")
jd_text = st.text_area("Paste the Job Description", height=200)

if st.button("Calculate Match Score"):
    if resume_file is None:
        st.warning("Please upload a resume.")
    elif not jd_text.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Analyzing..."):
            suffix = os.path.splitext(resume_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(resume_file.read())
                tmp_path = tmp.name

            result = score_resume_against_jd(
                resume_path=tmp_path,
                jd_text_raw=jd_text,
                job_title=job_title,
            )

            os.remove(tmp_path)

        st.subheader("Match Score")
        st.metric(label="ATS Match Score", value=f"{result['match_score_percent']}%")
        st.progress(min(int(result['match_score_percent']), 100))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Keyword Match: {result['keyword_score_percent']}%")
        with col2:
            st.caption(f"Title Match: {result['title_score_percent']}%")
        with col3:
            st.caption(f"Formatting: {result['format_score_percent']}%")

        col4, col5 = st.columns(2)
        with col4:
            edu = result["education_details"]
            st.caption(f"Education Match: {result['education_score_percent']}% "
                       f"(status: {edu['status']})")
        with col5:
            exp = result["experience_details"]
            st.caption(f"Experience Match: {result['experience_score_percent']}% "
                       f"(status: {exp['status']}, resume years: {exp['resume_years']})")

        st.subheader("✅ Matched Skills")
        if result["matched_skills"]:
            st.write(", ".join(result["matched_skills"]))
        else:
            st.write("No matched skills found.")

        st.subheader("⚠️ Missing Skills")
        if result["missing_skills"]:
            st.write(", ".join(result["missing_skills"]))
        else:
            st.write("No major missing skills found — good match!")

        st.subheader("📋 Missing Resume Sections")
        if result["missing_sections"]:
            st.write(", ".join(result["missing_sections"]))
        else:
            st.write("All standard sections present!")