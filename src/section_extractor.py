"""
section_extractor.py
Splits resume text into sections based on common resume headers.

Matches headers CASE-SENSITIVELY against their UPPERCASE form, since real
resume section headers are almost always styled in all caps (EDUCATION,
EXPERIENCE, PROJECTS). This avoids false matches on casual lowercase use
of the same word in prose -- e.g. "hands-on experience in MERN Stack"
inside a Professional Summary, which previously got misdetected as the
start of the Experience section.
"""

import re

SECTION_HEADERS = {
    "education": ["education", "academic background"],
    "experience": ["experience", "work experience", "professional experience", "employment"],
    "projects": ["projects", "personal projects", "academic projects"],
    "skills": ["technical skills", "skills", "core competencies"],
    "certifications": ["certifications", "certificates"],
    "leadership": ["leadership", "extracurricular", "community involvement"],
}


def split_into_sections(resume_text):
    """
    Returns a dict: {section_name: section_text}.
    Only matches header phrases that appear in ALL CAPS in the raw text
    (case-sensitive match against phrase.upper()) -- this reliably
    distinguishes an actual section header from the same word used
    casually in a sentence.
    """
    matches = []
    for norm_name, variants in SECTION_HEADERS.items():
        for phrase in variants:
            upper_phrase = phrase.upper()
            pattern = re.compile(r"\b" + re.escape(upper_phrase) + r"\b")  # case-sensitive
            for m in pattern.finditer(resume_text):
                matches.append((m.start(), m.end(), norm_name))

    if not matches:
        return {"header": resume_text}

    matches.sort(key=lambda x: x[0])
    seen_sections = set()
    filtered = []
    for start, end, name in matches:
        if name not in seen_sections:
            filtered.append((start, end, name))
            seen_sections.add(name)

    sections = {"header": resume_text[: filtered[0][0]].strip()}

    for i, (start, end, name) in enumerate(filtered):
        section_start = end
        section_end = filtered[i + 1][0] if i + 1 < len(filtered) else len(resume_text)
        sections[name] = resume_text[section_start:section_end].strip()

    return sections


def get_section(resume_text, section_name, fallback_to_full_text=True):
    sections = split_into_sections(resume_text)
    section_text = sections.get(section_name, "")

    if not section_text and fallback_to_full_text:
        return resume_text

    return section_text


if __name__ == "__main__":
    sample = """VALLURU TANMAYEE
PROFESSIONAL SUMMARY
Computer Science graduate with hands-on experience in MERN Stack, Python, Kubernetes, DevOps, and NLP.
EDUCATION
B.Tech in Computer Science, KL University, Guntur Aug 2022 - May 2026
EXPERIENCE
Nokia Corporation | Student Intern | On-site Aug 2025 - Jun 2026
Automated deployment pipelines.
PROJECTS
Resume Matcher Jun 2026 - Jul 2026
Some project text."""

    sections = split_into_sections(sample)
    for name, text in sections.items():
        print(f"--- {name} ---")
        print(text)
        print()