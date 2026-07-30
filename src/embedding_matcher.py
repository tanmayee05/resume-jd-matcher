"""
embedding_matcher.py
Calculates semantic similarity between resume and JD using sentence embeddings.
Unlike TF-IDF, this captures MEANING -- e.g. "Docker" and "containerization"
will score as related, even though they share no exact words.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load once at import time (small, fast, free, runs locally -- no API key needed)
# First run will download the model (~80MB), then it's cached locally.
#Python loads a pretrained AI model (all-MiniLM-L6-v2).
_model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_embedding_similarity(resume_text, jd_text):
    """
    Takes RAW or lightly-cleaned text (embeddings work fine even without
    heavy preprocessing -- unlike TF-IDF, they understand context/meaning,
    so you do NOT need to remove stopwords or lemmatize first).

    Returns a similarity score between 0 and 1.
    """
    embeddings = _model.encode([resume_text, jd_text])

    resume_embedding = embeddings[0].reshape(1, -1)
    jd_embedding = embeddings[1].reshape(1, -1)

    similarity_score = cosine_similarity(resume_embedding, jd_embedding)[0][0]
    return float(similarity_score)


# Quick manual test
if __name__ == "__main__":
    resume_text = "Experienced backend engineer with hands-on Docker container deployment."
    jd_text = "Looking for someone skilled in containerization technologies."

    score = calculate_embedding_similarity(resume_text, jd_text)
    print(f"Embedding Similarity Score: {score * 100:.2f}%")

    # Compare against TF-IDF on the same pair to see the difference
    from src.tfidf_matcher import calculate_tfidf_similarity
    from src.preprocessor import preprocess

    tfidf_score, _, _ = calculate_tfidf_similarity(
        preprocess(resume_text), preprocess(jd_text)
    )
    print(f"TF-IDF Similarity Score:   {tfidf_score * 100:.2f}%")