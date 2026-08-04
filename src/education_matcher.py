"""
education_matcher.py
Checks whether the resume's education level meets the JD's stated requirement.
Now checks only within the resume's EDUCATION section (falls back to the
full document if no Education header is detected), avoiding false positives
like "Master's" appearing in a Projects bullet about a teammate.
"""

import re
from src.section_extractor import get_section

DEGREE_LEVELS = {
    "phd": 4, "ph.d": 4, "doctorate": 4,
    "m.tech": 3, "mtech": 3, "m.s": 3, "ms": 3, "master": 3, "masters": 3, "mca": 3, "mba": 3,
    "b.tech": 2, "btech": 2, "b.e": 2, "be": 2, "bachelor": 2, "bachelors": 2, "bca": 2, "bsc": 2,
    "diploma": 1,
}


def _find_degree_level(text):
    text_lower = text.lower()
    found_levels = []
    for degree, level in DEGREE_LEVELS.items():
        if re.search(r"\b" + re.escape(degree) + r"\b", text_lower):
            found_levels.append(level)
    return max(found_levels) if found_levels else None


def check_education_match(resume_text, jd_text):
    resume_education_section = get_section(resume_text, "education")

    jd_level = _find_degree_level(jd_text)
    resume_level = _find_degree_level(resume_education_section)

    if jd_level is None:
        return {"score": 1.0, "jd_requirement": None, "resume_level": resume_level, "status": "no_requirement_stated"}

    if resume_level is None:
        return {"score": 0.5, "jd_requirement": jd_level, "resume_level": None, "status": "resume_degree_not_detected"}

    if resume_level >= jd_level:
        return {"score": 1.0, "jd_requirement": jd_level, "resume_level": resume_level, "status": "match_or_higher"}
    else:
        return {"score": 0.0, "jd_requirement": jd_level, "resume_level": resume_level, "status": "below_requirement"}


if __name__ == "__main__":
    resume = """
    EDUCATION
    B.Tech in Computer Science, KL University

    PROJECTS
    Collaborated with a teammate holding a Master's degree.
    """
    jd = "Required Qualifications: M.Tech or PhD in Computer Science preferred."

    result = check_education_match(resume, jd)
    print(result)