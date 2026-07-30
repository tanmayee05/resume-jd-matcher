"""
scorer.py
Combines all pipeline pieces into a single, realistic ATS-style score.

Weights loosely follow how real ATS systems score (per industry write-ups):
- Keyword/semantic match : 50%
- Job title alignment    : 30%
- Formatting/parseability: 20%
"""



from src.file_reader import extract_text
from src.preprocessor import preprocess
from src.tfidf_matcher import calculate_tfidf_similarity, get_missing_keywords
from src.embedding_matcher import calculate_embedding_similarity
from src.title_matcher import check_title_match
from src.format_checker import check_formatting
from src.skill_matcher import load_skills, compare_skills
# for 7.1
from src.skill_matcher import load_skills, compare_skills



def score_resume_against_jd(resume_path, jd_text_raw, job_title=""):
    """
    Full simplified pipeline:
    1. Read resume file
    2. Preprocess text for TF-IDF
    3. Keyword/semantic score (embeddings -- single score, no blending)
    4. Job title alignment score
    5. Formatting/section-header score
    6. Combine into one final weighted score
    7. List missing keywords (TF-IDF based, still useful as a simple list)
    """

    # 1. Raw text
    resume_raw = extract_text(resume_path)
    jd_raw = jd_text_raw

    # 2. Preprocess for TF-IDF (used only for missing keyword list)
    resume_clean = preprocess(resume_raw)
    jd_clean = preprocess(jd_raw)

    # 3. Keyword/semantic score -- embeddings only (captures meaning + exact words reasonably well)
    keyword_score = calculate_embedding_similarity(resume_raw, jd_raw)

    # 4. Job title alignment
    title_score = check_title_match(resume_raw, job_title) if job_title else 0.5
    # default 0.5 (neutral) if no title provided, so it doesn't unfairly tank the score

    # 5. Formatting check
    format_result = check_formatting(resume_raw)
    format_score = format_result["formatting_score"]

    # 6. Final weighted score
    final_score = (
        (keyword_score * 0.50)
        + (title_score * 0.30)
        + (format_score * 0.20)
    )

    # 7. Missing keywords (simple list, still from TF-IDF and pos tagging) still some scrap is coming so using 7.1
    #missing_keywords = get_missing_keywords(resume_clean, jd_clean)

    # 7.1 it is from skill_matcher.py, by uploading the .csv and finding missing and matching onces.
    _skills_db = load_skills("data/tech_skills.csv")
    skill_result = compare_skills(resume_raw, jd_raw, _skills_db)

    return {
        "match_score_percent": round(final_score * 100, 2),
        "keyword_score_percent": round(keyword_score * 100, 2),
        "title_score_percent": round(title_score * 100, 2),
        "format_score_percent": round(format_score * 100, 2),
        #"missing_keywords": missing_keywords,                  // is this 7
        "matched_skills": skill_result["matched_skills"],       # is for 7.1
        "missing_skills": skill_result["missing_skills"],       # is for 7.1
        "missing_sections": format_result["missing_sections"],
        "resume_raw_preview": resume_raw[:300],
    }


# Quick manual test
if __name__ == "__main__":
    result = score_resume_against_jd(
        resume_path="data/Tanmayee_Valluru_Resume.pdf",
        jd_text_raw="We are looking for a Backend Engineer with experience in Spring Boot, Kafka, Docker, and AWS.",
        job_title="Backend Engineer",
    )

    print("Final ATS-Style Score:", result["match_score_percent"], "%")
    print("  -> Keyword score:   ", result["keyword_score_percent"], "%")
    print("  -> Title score:     ", result["title_score_percent"], "%")
    print("  -> Format score:    ", result["format_score_percent"], "%")
    print("Missing Keywords:", result["missing_keywords"])
    print("Missing Sections:", result["missing_sections"])


    