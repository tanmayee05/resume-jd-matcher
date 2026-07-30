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
    "Upload your resume and paste a job description to get an ATS-style "
    "match score and see which important keywords might be missing."
)

resume_file = st.file_uploader("Upload your Resume", type=["pdf", "docx", "txt"])
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
                jd_is_file=False,
            )

            os.remove(tmp_path)

        st.subheader("Match Score")
        st.metric(label="ATS Match Score", value=f"{result['match_score_percent']}%")
        st.progress(min(int(result['match_score_percent']), 100))

        # Show both scoring methods
        col1, col2 = st.columns(2)

        with col1:
            st.caption(f"TF-IDF (keyword) score: {result['tfidf_score_percent']}%")

        with col2:
            st.caption(f"Embedding (semantic) score: {result['embedding_score_percent']}%")

        st.subheader("⚠️ Keywords Missing or Weak in Your Resume")
        if result["missing_keywords"]:
            st.write(", ".join(result["missing_keywords"]))
        else:
            st.write("No major missing keywords found — good match!")

        with st.expander("🔍 See extracted entities from your resume"):
            st.json(result["resume_entities"])

        with st.expander("🔍 See extracted skills/noun phrases from your resume"):
            st.write(result["resume_skills_noun_chunks"])