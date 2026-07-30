"""
preprocessor.py
Cleans raw text: lowercase, remove punctuation, remove stopwords, lemmatize.
This is used AFTER any POS tagging / NER (which need the original raw text).
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# One-time downloads (only runs the first time, then cached)
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("wordnet", quiet=True)

STOPWORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def to_lowercase(text):
    return text.lower()


def remove_punctuation(text):
    # keep only letters, numbers, and spaces
    return re.sub(r"[^\w\s]", " ", text)


def remove_extra_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text):
    return word_tokenize(text)


def remove_stopwords(tokens):
    return [word for word in tokens if word not in STOPWORDS]


def lemmatize(tokens):
    return [lemmatizer.lemmatize(word) for word in tokens]


def preprocess(text):
    """
    Full pipeline: lowercase -> remove punctuation -> tokenize
    -> remove stopwords -> lemmatize.
    Returns a single cleaned string (ready for TF-IDF).
    """
    text = to_lowercase(text)
    text = remove_punctuation(text)
    text = remove_extra_whitespace(text)

    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)

    return " ".join(tokens)


# Quick manual test
if __name__ == "__main__":
    sample = "I am currently WORKING as a Backend Engineer, building APIs with Spring Boot!!"
    cleaned = preprocess(sample)
    print("Original: ", sample)
    print("Cleaned:  ", cleaned)