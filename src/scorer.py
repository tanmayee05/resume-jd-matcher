"""
scorer.py
Combines all pipeline pieces into a single, realistic ATS-style score.

Weights (rebalanced to include education and experience):
- Keyword/semantic match : 35%
- Job title alignment    : 20%
- Formatting/parseability: 15%
- Education match        : 15%
- Experience match       : 15%
"""

from src.file_reader import extract_text
from src.preprocessor import preprocess
from src.embedding_matcher import calculate_embedding_similarity
from src.title_matcher import check_title_match
from src.format_checker import check_formatting
from src.skill_matcher import load_skills, compare_skills
from src.education_matcher import check_education_match
from src.experience_matcher import check_experience_match

_skills_db = load_skills("data/tech_skills.csv")


def score_resume_against_jd(resume_path, jd_text_raw, job_title=""):
    """
    Full pipeline:
    1. Read resume file
    2. Keyword/semantic score (sentence embeddings)
    3. Job title alignment score
    4. Formatting/section-header score
    5. Education level match (section-aware)
    6. Experience years match (date-range parsing, section-aware)
    7. Skills taxonomy match (matched/missing skills list)
    8. Combine 2-6 into one final weighted score
    """

    resume_raw = extract_text(resume_path)
    jd_raw = jd_text_raw

    # 2. Keyword / semantic score
    keyword_score = calculate_embedding_similarity(resume_raw, jd_raw)

    # 3. Title alignment
    title_score = check_title_match(resume_raw, job_title) if job_title else 0.5

    # 4. Formatting
    format_result = check_formatting(resume_raw)
    format_score = format_result["formatting_score"]

    # 5. Education match
    education_result = check_education_match(resume_raw, jd_raw)
    education_score = education_result["score"]

    # 6. Experience match
    experience_result = check_experience_match(resume_raw, jd_raw)
    experience_score = experience_result["score"]

    # 8. Final weighted score
    final_score = (
        (keyword_score * 0.35)
        + (title_score * 0.20)
        + (format_score * 0.15)
        + (education_score * 0.15)
        + (experience_score * 0.15)
    )



    # 7. Missing keywords (simple list, still from TF-IDF and pos tagging) still some scrap is coming so using 7.1
    #missing_keywords = get_missing_keywords(resume_clean, jd_clean)


    # 7. Skills taxonomy comparison
    skill_result = compare_skills(resume_raw, jd_raw, _skills_db)

    return {
        "match_score_percent": round(final_score * 100, 2),
        "keyword_score_percent": round(keyword_score * 100, 2),
        "title_score_percent": round(title_score * 100, 2),
        "format_score_percent": round(format_score * 100, 2),
        "education_score_percent": round(education_score * 100, 2),
        "experience_score_percent": round(experience_score * 100, 2),
        "education_details": education_result,
        "experience_details": experience_result,
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "missing_sections": format_result["missing_sections"],
        "resume_raw_preview": resume_raw[:300],
    }


if __name__ == "__main__":
    result = score_resume_against_jd(
        resume_path="data/Tanmayee_Valluru_Resume.pdf",
        jd_text_raw="Requires M.Tech and minimum 2 years of experience in DevOps or Cloud Engineering.",
        job_title="DevOps Engineer",
    )

    print("Final Score:", result["match_score_percent"], "%")
    print("  Keyword:   ", result["keyword_score_percent"], "%")
    print("  Title:     ", result["title_score_percent"], "%")
    print("  Format:    ", result["format_score_percent"], "%")
    print("  Education: ", result["education_score_percent"], "%", result["education_details"])
    print("  Experience:", result["experience_score_percent"], "%", result["experience_details"])
    print("Matched Skills:", result["matched_skills"])
    print("Missing Skills:", result["missing_skills"])
    print("Missing Sections:", result["missing_sections"])