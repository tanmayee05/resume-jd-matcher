"""
tfidf_matcher.py
Calculates similarity between resume and job description using TF-IDF + cosine similarity.
Also extracts important JD keywords that are missing from the resume.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_tfidf_similarity(resume_text, jd_text):
    """
    Takes two PREPROCESSED (cleaned) strings and returns:
    - similarity score (0 to 1)
    - the fitted vectorizer (so we can inspect keywords later)
    - the tfidf matrix
    """
    documents = [resume_text, jd_text]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # cosine_similarity returns a matrix; we want the single score
    # comparing doc 0 (resume) with doc 1 (jd)
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return similarity_score, vectorizer, tfidf_matrix


def get_missing_keywords(resume_text, jd_text, top_n=15):
    """
    Finds important words in the JD (by TF-IDF weight) that are
    missing or underrepresented in the resume.
    """
    similarity_score, vectorizer, tfidf_matrix = calculate_tfidf_similarity(
        resume_text, jd_text
    )

    feature_names = vectorizer.get_feature_names_out()

    resume_vector = tfidf_matrix[0].toarray()[0]
    jd_vector = tfidf_matrix[1].toarray()[0]

    # Pair each word with its JD importance and resume importance
    word_scores = []
    for idx, word in enumerate(feature_names):
        jd_score = jd_vector[idx]
        resume_score = resume_vector[idx]
        if jd_score > 0:  # word actually appears in the JD
            word_scores.append((word, jd_score, resume_score))

    # Sort by JD importance (highest first)
    word_scores.sort(key=lambda x: x[1], reverse=True)

    # Keep words where resume score is much lower than JD score (i.e. missing/weak)
    missing = [
        word for word, jd_score, resume_score in word_scores
        if resume_score < (jd_score * 0.3)  # resume barely has this word
    ]

    return missing[:top_n]


# Quick manual test
if __name__ == "__main__":
    resume_clean = "backend engineer spring boot microservice kafka kubernetes java experience"
    jd_clean = "looking backend engineer spring boot kafka docker containerization aws experience"

    score, vectorizer, matrix = calculate_tfidf_similarity(resume_clean, jd_clean)
    print(f"Match Score: {score * 100:.2f}%")

    missing = get_missing_keywords(resume_clean, jd_clean)
    print("Missing/weak keywords from resume:", missing)