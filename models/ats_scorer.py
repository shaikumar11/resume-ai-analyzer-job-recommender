import re

# Common resume sections an ATS checks for
REQUIRED_SECTIONS = {
    "contact": [r"email", r"@", r"phone", r"\+\d"],
    "skills": [r"skills", r"technical skills", r"technologies"],
    "experience": [r"experience", r"work history", r"employment"],
    "education": [r"education", r"degree", r"b\.tech", r"bachelor", r"university", r"college"],
    "projects": [r"projects"],
}


def check_sections(raw_text):
    """Check which key resume sections are present."""
    text_lower = raw_text.lower()
    section_status = {}

    for section, patterns in REQUIRED_SECTIONS.items():
        found = any(re.search(pattern, text_lower) for pattern in patterns)
        section_status[section] = found

    return section_status


def keyword_match_details(cleaned_resume, cleaned_job):
    """
    Compare word sets between resume and job description.
    Returns matched keywords, missing keywords, and match percentage.
    """
    resume_words = set(cleaned_resume.split())
    job_words = set(cleaned_job.split())

    # Ignore very generic words that don't represent real skills
    matched = job_words & resume_words
    missing = job_words - resume_words

    match_percentage = round((len(matched) / len(job_words)) * 100, 2) if job_words else 0

    return {
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
        "match_percentage": match_percentage,
    }


def compute_ats_score(raw_text, cleaned_resume, cleaned_job):
    """
    Combine section-presence check and keyword match into a single ATS score (0-100).
    """
    sections = check_sections(raw_text)
    section_score = (sum(sections.values()) / len(sections)) * 100

    keywords = keyword_match_details(cleaned_resume, cleaned_job)
    keyword_score = keywords["match_percentage"]

    # Weighted: 40% section completeness, 60% keyword match
    final_score = round((section_score * 0.4) + (keyword_score * 0.6), 2)

    return {
        "ats_score": final_score,
        "sections": sections,
        "keyword_match_percentage": keyword_score,
        "matched_keywords": keywords["matched_keywords"],
        "missing_keywords": keywords["missing_keywords"],
    }