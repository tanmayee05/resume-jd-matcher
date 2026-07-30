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
├── app.py                    # Streamlit UI
├── requirements.txt          # Python dependencies
├── .gitignore                # Excludes venv, cache, personal resume files
├── README.md                 # Project overview
├── TECHNOLOGIES.md           # Tech stack + scoring logic explained
├── CHALLENGES.md             # Development journey, issues faced, drawbacks
├── build_skills_csv.py       # One-time utility: builds tech_skills.csv from a raw skills dataset
│
├── data/
│   └── tech_skills.csv       # Skills taxonomy (~500 known tech skills)
│
├── src/
│   ├── __init__.py
│   ├── file_reader.py        # Extract text from PDF/DOCX/TXT
│   ├── preprocessor.py       # Clean text for TF-IDF
│   ├── tfidf_matcher.py      # TF-IDF similarity (used for missing single-word keywords)
│   ├── embedding_matcher.py  # Semantic similarity scoring (main match score)
│   ├── skill_matcher.py      # Matches resume/JD against known skills taxonomy
│   ├── title_matcher.py      # Job title alignment check
│   ├── format_checker.py     # Resume section/formatting check
│   ├── ner_extractor.py      # POS/NER extraction (explored, not used in final scoring)
│   └── scorer.py             # Combines everything into final weighted score
│
└── models/
    └── skill_ner/             # Custom-trained NER model (experimental, Option B — not adopted)
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


## Build Steps (Development Order)

**Step 1: File reading**
Get `file_reader.py` working standalone — print extracted text from a sample PDF resume, confirm it looks right.

**Step 2: Preprocessing**
Get `preprocessor.py` working — feed it raw text, confirm you get clean, lowercase, stopword-free, lemmatized output.

**Step 3: NER extraction (exploratory)**
Get `ner_extractor.py` working — feed it resume text, confirm it pulls out organizations, skill-like nouns, etc. spaCy's default model mislabels domain-specific tech terms (e.g. tagging "Kafka" as PERSON) — this is expected. This module was later excluded from the final scoring pipeline in favor of the skills taxonomy approach (Step 7).

**Step 4: TF-IDF matching**
Get `tfidf_matcher.py` working — feed it two texts (resume + JD), confirm you get a similarity score between 0 and 1. Initially used as the main match score; later narrowed to a supporting role.

**Step 5: Wire it into Streamlit**
Build a first version of `app.py` — import the tested functions from `src/`, connect them to the upload button and text area.

**Step 6: Add sentence-transformers matching**
Add `embedding_matcher.py` for semantic/meaning-based similarity, since TF-IDF alone missed related concepts phrased differently (e.g. "Docker" vs "containerization"). This became the primary keyword/semantic score.

**Step 7: Replace keyword guessing with a skills taxonomy**
TF-IDF's "missing keywords" list surfaced generic filler words from repetitive JD phrasing ("exposure", "familiarity", "learn"). Built `skill_matcher.py` to match resume/JD text against a curated list of ~500 known real-world tech skills instead of guessing importance from word frequency — eliminated generic-word leakage entirely.

**Step 8: Add job title alignment**
Built `title_matcher.py` — a simple word-overlap check between the JD's job title and resume text, since real ATS systems weight title alignment heavily (~20-30% of score).

**Step 9: Add formatting/parseability check**
Built `format_checker.py` — checks for standard resume section headers (Experience, Education, Skills, etc.), since real ATS parsers fail silently on resumes they can't structurally read.

**Step 10: Combine into a realistic weighted score**
Built `scorer.py` to combine keyword/semantic match (50%), title alignment (30%), and formatting (20%) into one final ATS-style score — aligned to how real-world ATS scoring is commonly described, rather than relying on a single signal.

**Step 11 (explored, not adopted): Custom NER model training**
Attempted training a custom spaCy NER model (`train_ner.py`) to detect skills beyond the CSV list, using auto-labeled sentences from the skills taxonomy. With a small training set (~15 examples), the pipeline worked but didn't generalize well to unseen skills — documented in `CHALLENGES.md` as a deliberate stopping point rather than pursued further.

**Step 12: UI polish**
Redesigned `app.py` with custom CSS — score card, colored skill pills (matched/missing), multi-column layout — replacing the initial plain Streamlit defaults.



IF ANY ADDITIONAL FEATURE CAN CONSIDER THE BELOW CAN BE ADDED.

1. Contact Information
address, number, email-id, githublink, linkedin link

2. Education Match and Experience Match

3. mentioned soft skills also