"""
title_matcher.py
Checks if the job title from the JD appears (or closely appears) in the resume.
Real ATS systems weight this heavily (~20-30% of score).
"""

import re


def extract_probable_title(jd_text, max_words=6):
    """
    Naive but effective: most JDs state the title in the first line
    or right after words like 'looking for a', 'hiring a', 'role:'.
    We just grab the first short line as a fallback.
    """
    first_line = jd_text.strip().split("\n")[0]
    words = first_line.split()
    return " ".join(words[:max_words]).lower()


def check_title_match(resume_text, jd_title):
    """
    Returns 1.0 if the JD title (or its individual key words) appears
    in the resume, 0.0 if not, partial credit for partial word overlap.
    """
    resume_lower = resume_text.lower()
    jd_title_lower = jd_title.lower()

    # Direct full-phrase match
    if jd_title_lower in resume_lower:
        return 1.0

    # Partial match: how many of the title's words appear in resume
    title_words = [w for w in re.findall(r"\w+", jd_title_lower) if len(w) > 2]
    if not title_words:
        return 0.0

    matched = sum(1 for w in title_words if w in resume_lower)
    return matched / len(title_words)


# Quick manual test
if __name__ == "__main__":
    resume = "Experienced Backend Engineer skilled in Java and Spring Boot"
    jd_title = "Senior Backend Engineer"

    score = check_title_match(resume, jd_title)
    print(f"Title match score: {score * 100:.0f}%")