"""
scorer.py
Combines file_reader, preprocessor, ner_extractor, tfidf_matcher,
and embedding_matcher into a single end-to-end scoring pipeline.
"""

from src.file_reader import extract_text
from src.preprocessor import preprocess
from src.ner_extractor import extract_entities, extract_noun_chunks
from src.tfidf_matcher import calculate_tfidf_similarity, get_missing_keywords
from src.embedding_matcher import calculate_embedding_similarity


def score_resume_against_jd(resume_path, jd_text_raw, jd_is_file=False):
    """
    Full pipeline:
    1. Read resume file (and JD if it's also a file)
    2. Run NER/noun-chunk extraction on RAW text (before cleaning)
    3. Preprocess both texts (clean for TF-IDF)
    4. Calculate TF-IDF similarity score (exact keyword match)
    5. Calculate embedding similarity score (semantic/meaning match)
    6. Combine both into a final blended score
    7. Find missing keywords
    """

    # 1. Get raw text
    resume_raw = extract_text(resume_path)
    jd_raw = extract_text(jd_text_raw) if jd_is_file else jd_text_raw

    # 2. NER / noun chunks on RAW text
    resume_entities = extract_entities(resume_raw)
    resume_skills = extract_noun_chunks(resume_raw)

    jd_entities = extract_entities(jd_raw)
    jd_skills = extract_noun_chunks(jd_raw)

    # 3. Preprocess (clean) both texts for TF-IDF
    resume_clean = preprocess(resume_raw)
    jd_clean = preprocess(jd_raw)

    # 4. TF-IDF similarity score (exact keyword overlap)
    tfidf_score, vectorizer, tfidf_matrix = calculate_tfidf_similarity(
        resume_clean, jd_clean
    )

    # 5. Embedding similarity score (semantic/meaning overlap)
    # Uses lightly-cleaned RAW text, not the heavily stripped TF-IDF version
    embedding_score = calculate_embedding_similarity(resume_raw, jd_raw)

    # 6. Blended final score -- weight embeddings higher since they
    # capture meaning better; TF-IDF still contributes for exact keyword signal
    final_score = (0.4 * tfidf_score) + (0.6 * embedding_score)

    # 7. Missing keywords (still TF-IDF based -- good for exact keyword gaps)
    missing_keywords = get_missing_keywords(resume_clean, jd_clean)

    return {
        "match_score_percent": round(final_score * 100, 2),
        "tfidf_score_percent": round(tfidf_score * 100, 2),
        "embedding_score_percent": round(embedding_score * 100, 2),
        "missing_keywords": missing_keywords,
        "resume_entities": resume_entities,
        "jd_entities": jd_entities,
        "resume_skills_noun_chunks": resume_skills,
        "jd_skills_noun_chunks": jd_skills,
        "resume_raw_preview": resume_raw[:300],
        "jd_raw_preview": jd_raw[:300],
    }


# Quick manual test
if __name__ == "__main__":
    result = score_resume_against_jd(
        resume_path="data/Tanmayee_Valluru_Resume",
        jd_text_raw="We are looking for a Backend Engineer with experience in Spring Boot, Kafka, Docker, and AWS.",
        jd_is_file=False,
    )

    print("Final Blended Score:", result["match_score_percent"], "%")
    print("  -> TF-IDF component:    ", result["tfidf_score_percent"], "%")
    print("  -> Embedding component: ", result["embedding_score_percent"], "%")
    print("Missing Keywords:", result["missing_keywords"])