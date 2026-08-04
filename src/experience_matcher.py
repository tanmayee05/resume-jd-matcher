"""
experience_matcher.py
Extracts required years of experience from the JD, and calculates the
candidate's actual experience from the RESUME by parsing date ranges
(e.g. "Aug 2025 - June 2026", "Jun 2020 - Present") -- since resumes
almost always show experience this way, not as an explicit "X years" statement.
"""

import re
from datetime import datetime
from src.section_extractor import get_section

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}


def extract_required_years(jd_text):
    text_lower = jd_text.lower()
    matches = re.findall(r"(\d+)\s*\+?\s*-?\s*\d*\s*years?", text_lower)
    years_found = [int(m) for m in matches if m.isdigit()]
    return min(years_found) if years_found else None


def _parse_date_ranges(text):
    """
    Finds patterns like 'Aug 2025 - June 2026' or 'Jun 2020 - Present'.
    Uses NAMED groups so we never rely on fragile positional group numbers.
    """
    month_pattern = r"(?:" + "|".join(MONTHS.keys()) + r")"

    range_pattern = re.compile(
        r"(?P<start_month>" + month_pattern + r")\.?\s*(?P<start_year>\d{4})"
        r"\s*[-\u2013\u2014]+\s*"
        r"(?:(?P<end_month>" + month_pattern + r")\.?\s*(?P<end_year>\d{4})"
        r"|(?P<present>present|current))",
        re.IGNORECASE,
    )

    ranges = []
    for match in range_pattern.finditer(text.lower()):
        start_month = MONTHS[match.group("start_month")]
        start_year = int(match.group("start_year"))
        start_date = datetime(start_year, start_month, 1)

        if match.group("present"):
            end_date = datetime.now()
        else:
            end_month = MONTHS[match.group("end_month")]
            end_year = int(match.group("end_year"))
            end_date = datetime(end_year, end_month, 1)

        ranges.append((start_date, end_date))

    return ranges


def calculate_total_experience_years(text):
    ranges = _parse_date_ranges(text)
    if not ranges:
        return None

    total_days = sum((end - start).days for start, end in ranges if end > start)
    return round(total_days / 365.25, 1)


def check_experience_match(resume_text, jd_text):
    required_years = extract_required_years(jd_text)

    if required_years is None:
        return {"score": 1.0, "required_years": None, "resume_years": None, "status": "no_requirement_stated"}

    experience_section = get_section(resume_text, "experience")
    resume_years = calculate_total_experience_years(experience_section)

    if resume_years is None:
        has_internship = bool(re.search(r"\bintern(ship)?\b", resume_text.lower()))
        score = 0.6 if has_internship else 0.3
        return {"score": score, "required_years": required_years, "resume_years": None, "status": "no_date_range_found"}

    if resume_years >= required_years:
        return {"score": 1.0, "required_years": required_years, "resume_years": resume_years, "status": "meets_requirement"}
    else:
        score = max(0.0, round(resume_years / required_years, 2))
        return {"score": score, "required_years": required_years, "resume_years": resume_years, "status": "below_requirement"}


if __name__ == "__main__":
    resume = """
    EXPERIENCE
    Nokia Corporation | Student Intern | On-site
    August 2025 - June 2026
    Automated deployment pipelines...
    """
    jd = "Requires a minimum of 2 years of experience in DevOps."

    result = check_experience_match(resume, jd)
    print(result)

    # extra test: Present-ended range
    resume2 = "EXPERIENCE\nSoftware Engineer | Jun 2020 - Present"
    print(check_experience_match(resume2, jd))