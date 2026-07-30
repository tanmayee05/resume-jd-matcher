# Resume ↔ Job Description Matcher

An NLP-based tool that scores how well a resume matches a job description,
similar to how real Applicant Tracking Systems (ATS) evaluate candidates —
built to understand and practice core NLP techniques, not just call an LLM.

## What It Does

Upload a resume (PDF/DOCX/TXT), paste a job title and job description, and
get back:
- An overall ATS-style match score (0–100%)
- A breakdown of *why* — keyword match, title alignment, formatting
- A list of important skill keywords missing from the resume
- A list of standard resume sections that are missing

## How the Score Is Calculated

Real ATS systems score resumes across multiple weighted factors, not just
"does this word appear." This project follows that same structure:

| Factor | Weight | How it's measured |
|---|---|---|
| Keyword / Semantic Match | 50% | Sentence embeddings (meaning-based similarity) |
| Job Title Alignment | 30% | Word-overlap between JD title and resume text |
| Formatting / Parseability | 20% | Presence of standard section headers |

**Why embeddings instead of plain keyword matching?**
Plain keyword matching (TF-IDF) treats "Docker" and "containerization" as
completely unrelated, since they share no exact words. Sentence embeddings
capture *meaning*, so conceptually related terms score as similar even with
different wording — closer to how a human recruiter would read a resume.

**Missing keywords are filtered by part-of-speech (POS tagging)** to keep
only meaningful nouns (e.g. "kubernetes", "microservices") and filter out
generic filler words the JD repeats often (e.g. "learn", "exposure").

## Tech Stack

- **Python** — core language
- **Streamlit** — web UI
- **spaCy** — POS tagging (keyword filtering)
- **scikit-learn** — TF-IDF vectorization, cosine similarity
- **sentence-transformers** — semantic embedding similarity
- **NLTK** — text preprocessing (stopwords, lemmatization)
- **pdfplumber / python-docx** — resume file parsing

## Project Structure

```
resume-matcher/
├── app.py                 # Streamlit UI
├── src/
│   ├── file_reader.py     # Extract text from PDF/DOCX/TXT
│   ├── preprocessor.py    # Clean text for TF-IDF
│   ├── tfidf_matcher.py   # Keyword matching + missing keyword detection
│   ├── embedding_matcher.py # Semantic similarity scoring
│   ├── title_matcher.py   # Job title alignment check
│   ├── format_checker.py  # Resume section/formatting check
│   └── scorer.py          # Combines everything into final score
```

## Running Locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

## Known Limitations

- PDF text extraction can merge text across tightly-spaced resume sections
  (a known limitation of PDF parsing generally, not specific to this tool)
- Job title matching is a simple word-overlap heuristic, not a trained model
- Does not evaluate years of experience against specific skills (a common
  but complex ATS feature, out of scope for this version)

## What I Learned Building This

Started with a naive TF-IDF-only approach, discovered it couldn't catch
synonyms/related concepts, and added sentence embeddings. Also discovered
that naive keyword extraction surfaces generic filler words from repetitive
JD phrasing — fixed by filtering missing keywords to nouns only via POS
tagging. Iterated the scoring model itself once I compared it against how
real ATS systems weight keyword match, title alignment, and formatting.





//creating the folder
mkdir resume-matcher
cd resume-matcher

//creating the virtual envirnment for our project for isolation.
python -m venv venv 
venv\Scripts\activate

//run the following comands for downloading the requirements in our project.
pip install streamlit pypdf2 python-docx scikit-learn spacy sentence-transformers pandas nltk
python -m spacy download en_core_web_sm

//download the below packages which have dependencies in the preprocessor.py
 Download NLTK data:
   python -m nltk.downloader stopwords  // from nltk download stopwords
   python -m nltk.downloader punkt      // from nltk download for tokenize
   python -m nltk.downloader wordnet    // from nltk download for lemmatization 

//command to run our app
streamlit run app.py



resume-matcher/
│
├── app.py                      # Streamlit UI — main entry point
├── requirements.txt            # dependencies
├── README.md                   # project description (important for resume link!)
│
├── src/
│   ├── __init__.py
│   ├── file_reader.py          # extract text from PDF/DOCX
│   ├── preprocessor.py         # lowercase, remove punctuation, stopwords, lemmatize
│   ├── ner_extractor.py        # POS tagging + NER (skills, orgs, degrees)
│   ├── tfidf_matcher.py        # TF-IDF vectorization + cosine similarity
│   ├── embedding_matcher.py    # sentence-transformers similarity (Version 2 upgrade)
│   └── scorer.py               # combines everything into final match score
│
├── data/
│   └── sample_resume.pdf       # test files for development
│
└── tests/
    └── test_preprocessor.py    # (optional, but nice to have — shows testing discipline)



Step 1: File reading

Get file_reader.py working standalone — just print extracted text from a sample PDF resume, confirm it looks right.

Step 2: Preprocessing

Get preprocessor.py working — feed it raw text, confirm you get clean, lowercase, stopword-free, lemmatized output.

Step 3: NER extraction

Get ner_extractor.py working — feed it resume text, confirm it correctly pulls out organizations, skills-like nouns, etc. (spaCy's default model won't catch everything — that's expected and okay for v1).

Step 4: TF-IDF matching

Get tfidf_matcher.py working — feed it two texts (resume + JD), confirm you get a similarity score between 0 and 1.

Step 5: Wire it into Streamlit

Only now build app.py — import your already-tested functions from src/, connect them to the upload button and text area.

Step 6 (upgrade): Add sentence-transformers matching

Once the TF-IDF version fully works end-to-end, add embedding_matcher.py as a second score, show both side-by-side in the UI.