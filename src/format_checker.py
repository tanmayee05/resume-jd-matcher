"""
format_checker.py
Checks if standard resume section headers are present -- a real ATS
needs these to correctly parse a resume. Missing headers = lost points.
"""

STANDARD_SECTIONS = [
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
]


def check_formatting(resume_text):
    """
    Returns a score (0 to 1) based on how many standard section
    headers are present in the resume, plus the list of found/missing ones.
    """
    resume_lower = resume_text.lower()

    found = [s for s in STANDARD_SECTIONS if s in resume_lower]
    missing = [s for s in STANDARD_SECTIONS if s not in resume_lower]

    score = len(found) / len(STANDARD_SECTIONS)

    return {
        "formatting_score": score,
        "found_sections": found,
        "missing_sections": missing,
    }


# Quick manual test
if __name__ == "__main__":
    sample_resume = """
    EDUCATION
    B.Tech Computer Science

    EXPERIENCE
    Backend Intern at XYZ

    TECHNICAL SKILLS
    Python, Java, Spring Boot
    """

    result = check_formatting(sample_resume)
    print(result)