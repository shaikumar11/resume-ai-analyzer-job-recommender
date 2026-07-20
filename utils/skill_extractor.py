"""
Dynamic keyword/skill extraction — replaces the fixed TECH_SKILLS whitelist.

Uses scikit-learn's TfidfVectorizer (the same library already used in
nlp_matcher.py) instead of a hand-curated word list. Term importance is
ranked by TF-IDF weight with English stopwords removed and 1-2 word
n-grams allowed, so it adapts to whatever domain the text is actually
in (data, cloud, finance, marketing, etc.) instead of only recognizing
words someone pre-typed into a list.

No extra dependencies — sklearn is already a project requirement.
"""

from sklearn.feature_extraction.text import TfidfVectorizer

# Generic words that show up in almost every resume/job post and aren't
# meaningful "skills" on their own — filtered out after ranking.
GENERIC_TERMS = {
    "experience", "work", "team", "role", "company", "years", "year",
    "using", "including", "skills", "job", "candidate", "strong",
    "ability", "knowledge", "understanding", "environment",
    "responsibilities", "requirements", "opportunity", "position",
    "join", "looking", "excellent", "good", "based", "related",
    "work experience", "years experience", "strong understanding",
}

# Only keep tokens that look like real words/technical terms
# (letters, plus + # . - for things like "c++", "node.js", "asp.net").
_TOKEN_PATTERN = r"(?u)\b[a-zA-Z][a-zA-Z+\-#.]{1,}\b"


def extract_keywords(text, top_n=30):
    """
    Extract the top_n most relevant keywords/phrases from `text`.

    Returns a set of lowercase strings (1-2 word phrases), so it can be
    intersected/diffed the same way the old whitelist-based sets were.
    """
    text = (text or "").strip()
    if not text:
        return set()

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=200,
        token_pattern=_TOKEN_PATTERN,
    )

    try:
        matrix = vectorizer.fit_transform([text])
    except ValueError:
        # happens if the text is entirely stopwords/too short after cleaning
        return set()

    scores = matrix.toarray()[0]
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(zip(terms, scores), key=lambda pair: pair[1], reverse=True)

    keywords = set()
    for term, score in ranked:
        if score <= 0:
            continue
        if term in GENERIC_TERMS or len(term) < 3:
            continue
        keywords.add(term)
        if len(keywords) >= top_n:
            break

    return keywords