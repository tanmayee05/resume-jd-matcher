"""
ner_extractor.py
Runs POS tagging + NER on RAW text (before lowercasing/lemmatization),
since NER relies on original casing and sentence structure.
"""

import spacy

# Load spaCy's small English model (downloaded earlier via:
# python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")


def extract_entities(text):
    """
    Runs NER on raw text.
    Returns a dict grouping entities by their type,
    e.g. {'ORG': ['CDK Global'], 'GPE': ['Vijayawada'], ...}
    """
    doc = nlp(text)
    entities = {}

    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)

    return entities


def extract_pos_tags(text):
    """
    Runs POS tagging on raw text.
    Returns a list of (word, POS tag) tuples.
    """
    doc = nlp(text)
    return [(token.text, token.pos_) for token in doc]


def extract_noun_chunks(text):
    """
    Extracts noun phrases -- useful for pulling out skill-like terms,
    e.g. "backend development", "Spring Boot microservices"
    """
    doc = nlp(text)
    return [chunk.text for chunk in doc.noun_chunks]


# Quick manual test
if __name__ == "__main__":
    sample = (
        "Valluru Tanmayee worked at Nokia in Bangalore. "
        "She has experience with Spring Boot, Kafka, and Kubernetes."
    )

    print("Entities found:")
    print(extract_entities(sample))

    print("\nNoun chunks (potential skills/phrases):")
    print(extract_noun_chunks(sample))
    #output: ['Sai Krishna Arava', 'CDK Global', 'Vijayawada', 'He', 'experience', 'Spring Boot', 'Kafka', 'Kubernetes']
    #see the mislabeling I warned about (spaCy tagged "Spring Boot" and "Kafka" as PERSON, "Kubernetes" as ORG — it's guessing wrong on tech terms it wasn't trained on)

    print("\nPOS tags (first 10):")
    print(extract_pos_tags(sample)[:10])