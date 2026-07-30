"""
skill_matcher.py
Matches resume/JD text against a KNOWN list of real-world tech skills,
instead of guessing importance from word frequency (TF-IDF) or grammar
(POS tagging). This avoids the "generic noun leakage" problem entirely --
we only ever look for things we already know are skills.
"""

import csv


def load_skills(csv_path):
    """Loads the skills taxonomy CSV into a list of lowercase skill strings."""
    skills = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            if row:
                skills.append(row[0].strip().lower())
    return skills


def extract_known_skills(text, skills_db):
    """
    Returns the list of skills (from skills_db) that appear in the given text.
    Uses simple substring matching -- good enough since skill names are
    fairly distinctive (e.g. "kubernetes" won't accidentally match other words).
    """
    text_lower = text.lower()
    found = [skill for skill in skills_db if skill in text_lower]
    return found


def compare_skills(resume_text, jd_text, skills_db):
    """
    Returns matched skills, missing skills, and a simple match ratio.
    """
    resume_skills = set(extract_known_skills(resume_text, skills_db))
    jd_skills = set(extract_known_skills(jd_text, skills_db))

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills

    match_ratio = len(matched) / len(jd_skills) if jd_skills else 0.0

    return {
        "resume_skills": sorted(resume_skills),
        "jd_skills": sorted(jd_skills),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "skill_match_ratio": match_ratio,
    }


# Quick manual test
if __name__ == "__main__":
    skills_db = load_skills("data/tech_skills.csv")

    resume_text = "Experienced with Docker, Kubernetes, Java, and REST APIs."
    jd_text = "Looking for someone skilled in Kubernetes, Terraform, Prometheus, and Grafana."

    result = compare_skills(resume_text, jd_text, skills_db)
    print("Matched:", result["matched_skills"])
    print("Missing:", result["missing_skills"])
    print(f"Skill Match Ratio: {result['skill_match_ratio'] * 100:.1f}%")