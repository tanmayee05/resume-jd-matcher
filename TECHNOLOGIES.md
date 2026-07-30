# Technologies Used & Why

## 1. File Reading — PyPDF2 / python-docx
**Why:** Resumes come in PDF or DOCX. Need to convert file bytes into plain
text before any NLP can happen. PyPDF2 handles PDF; python-docx handles
Word files. Basic file-handling, not an NLP technique itself, but the
required first step.

## 2. Text Preprocessing — NLTK
**What:** Lowercasing, punctuation removal, stopword removal, lemmatization.
**Why:** TF-IDF is a pure word-frequency method — it treats "Working" and
"working" as different tokens, and common words like "the"/"is" would
dominate frequency counts if not removed. Preprocessing normalizes text so
TF-IDF compares meaningful words fairly.
**Important:** this is only applied before TF-IDF — NOT before embeddings,
since embeddings understand context/meaning better with natural sentence
structure intact.

## 3. Keyword Matching — TF-IDF + Cosine Similarity (scikit-learn)
**What:** Converts resume and JD text into weighted word-frequency vectors,
then measures the angle between them (cosine similarity) as a 0–1 score.
**Why:** Standard, interpretable baseline for "how many important words
overlap." Still used in this project specifically to generate the missing
keywords list.
**Limitation:** Only matches exact words — "Docker" and "containerization"
score as unrelated even though they mean similar things.

## 4. Semantic Matching — Sentence Embeddings (sentence-transformers)
**What:** Converts full sentences into dense numeric vectors that capture
*meaning*, not just word identity. Uses the `all-MiniLM-L6-v2` model —
small, fast, runs locally, no API cost.
**Why:** Solves TF-IDF's core weakness. "Experience with Docker" and
"containerization skills" score as related here, even with zero shared
words — much closer to how a human would judge relevance.
**This is the main driver of the final match score (50% weight).**

## 5. POS Tagging — spaCy
**What:** Labels each word's grammatical role (noun, verb, adjective, etc.)
**Why used here:** The missing-keywords list (from TF-IDF) was surfacing
generic filler words the JD repeats often — "learn", "exposure", "like" —
which aren't real skills. Filtering the list to NOUN/PROPN tokens only
keeps genuine skill terms ("kubernetes", "microservices") and drops noise.
**Note:** POS tagging is run BEFORE any lowercasing/lemmatization, since it
needs original word structure to tag accurately.

## 6. Job Title Alignment — custom word-overlap check
**What:** Simple check for whether the JD's job title (or its individual
words) appear in the resume text.
**Why:** Real ATS systems weight job-title match heavily (~20-30% of
score) — a resume for "Business Insights Specialist" may not register as
relevant for a "Data Analyst" posting even if the actual work overlaps.
This is intentionally simple (not ML-based) since the signal itself is
simple: does the resume mention this role/title.

## 7. Formatting Check — section header detection
**What:** Checks for standard resume sections (Experience, Education,
Skills, Projects, Certifications).
**Why:** Real ATS parsers fail silently on resumes with unusual formatting
(tables, columns, graphics) — if the parser can't find a "Skills" section,
it can't credit skills listed there. This is a simple proxy for
"is this resume structured in a way a parser can read."

---

# The Scoring Logic (Full Picture)

```
Final Score = (Keyword/Semantic Match × 50%)
            + (Job Title Alignment    × 30%)
            + (Formatting Check       × 20%)
```

This mirrors how real-world ATS scoring rubrics are commonly described:
keyword matching as the heaviest factor, title alignment second, and
formatting/parseability as a real but smaller factor. Experience-duration
matching (a 4th real-world factor) was deliberately left out — it requires
parsing dates tied to specific skills, which is disproportionately complex
for the value it adds to this project.

# What Was Tried and Removed

- **NER-based skill extraction** was explored but dropped from the final
  scoring logic — spaCy's default model frequently mislabeled tech terms
  (e.g. tagging "Kafka" as PERSON), and noun-chunk-based comparison added
  complexity without improving score accuracy over the simpler approach.
- **Blended TF-IDF + embedding score** was simplified to embeddings-only
  for the main score, since running both added complexity without a clear
  accuracy benefit — TF-IDF is now used only for its original, narrower
  purpose (missing keyword detection).