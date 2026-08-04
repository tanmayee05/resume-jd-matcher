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

**Update:** the tool now also checks education level match and years of
experience match (see "Update: Expanded Scoring Model" section below).

## How the Score Is Calculated

Real ATS systems score resumes across multiple weighted factors, not just
"does this word appear." This project follows that same structure:

| Factor | Weight | How it's measured |
|---|---|---|
| Keyword / Semantic Match | 50% | Sentence embeddings (meaning-based similarity) |
| Job Title Alignment | 30% | Word-overlap between JD title and resume text |
| Formatting / Parseability | 20% | Presence of standard section headers |

> **Note:** these weights were the original v1 model. See "Update: Expanded
> Scoring Model" below for the current, rebalanced 5-factor version.

**Why embeddings instead of plain keyword matching?**
Plain keyword matching (TF-IDF) treats "Docker" and "containerization" as
completely unrelated, since they share no exact words. Sentence embeddings
capture *meaning*, so conceptually related terms score as similar even with
different wording — closer to how a human recruiter would read a resume.

**Missing keywords are filtered by part-of-speech (POS tagging)** to keep
only meaningful nouns (e.g. "kubernetes", "microservices") and filter out
generic filler words the JD repeats often (e.g. "learn", "exposure").

> **Update:** missing-keyword detection was later replaced entirely by a
> skills-taxonomy approach (matching against a curated list of ~500 known
> tech skills) rather than POS-filtered word frequency — see Step 7 in
> Build Steps below, and Challenge #2 in CHALLENGES.md.

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
│   ├── section_extractor.py  # Splits resume into sections (Education, Experience, etc.) for scoped checks
│   ├── education_matcher.py  # Compares resume education level against JD requirement
│   ├── experience_matcher.py # Parses resume date ranges to estimate years of experience vs JD requirement
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
- ~~Does not evaluate years of experience against specific skills~~ —
  **Update:** years-of-experience matching was later implemented (see
  below) by parsing date ranges from the resume's Experience section and
  comparing against the JD's stated requirement. It does not, however,
  tie specific years to specific individual skills (e.g. "3 years of
  Kubernetes specifically") — only total experience duration overall.

## What I Learned Building This

Started with a naive TF-IDF-only approach, discovered it couldn't catch
synonyms/related concepts, and added sentence embeddings. Also discovered
that naive keyword extraction surfaces generic filler words from repetitive
JD phrasing — fixed by filtering missing keywords to nouns only via POS
tagging. Iterated the scoring model itself once I compared it against how
real ATS systems weight keyword match, title alignment, and formatting.

---

## Update: Expanded Scoring Model (Education + Experience Matching)

After the initial 3-factor model (keyword/title/formatting) was working,
the model was expanded to include education level and years-of-experience
matching, since these are real factors ATS systems check and were flagged
as missing in the original "Known Limitations" section above.

**Current 5-factor weighted score:**

| Factor | Weight | How it's measured |
|---|---|---|
| Keyword / Semantic Match | 35% | Sentence embeddings |
| Job Title Alignment | 20% | Word-overlap between JD title and resume text |
| Formatting / Parseability | 15% | Presence of standard section headers |
| Education Match | 15% | Degree-level hierarchy check (B.Tech / M.Tech / PhD, etc.) against the resume's Education section |
| Experience Match | 15% | Years of experience calculated by parsing date ranges (e.g. "Aug 2025 - Jun 2026") in the resume's Experience section, compared against the JD's stated minimum |

**Why section-scoped checks were needed:** checking the whole resume
document for degree/date mentions caused false positives — e.g. the word
"experience" appearing casually in the Professional Summary ("hands-on
experience in MERN Stack...") getting misdetected as the start of the
Experience section, or a teammate's "Master's degree" mentioned in a
Projects bullet being misread as the candidate's own education level.
Built `section_extractor.py` to split the resume into sections first, so
education and experience checks only look within their relevant section
(falling back to the full document if a header truly can't be detected).

See CHALLENGES.md for the specific bugs hit while building this
(regex group numbering, line-based vs position-based header detection,
case-sensitivity of header matching) and how each was resolved.

## Running Locally (updated dependency)

The experience-date parsing uses Python's built-in `datetime` module only
— no additional dependency required beyond what's already in
`requirements.txt`.

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
TF-IDF's "missing keywords" list surfaced generic filler words from repetitive JD phrasing ("exposure", "familiarity", "learn"). Built `skill_matcher.py` to match resume/JD text against a curated list of known real-world tech skills instead of guessing importance from word frequency — eliminated generic-word leakage entirely. The skills list was later expanded from an initial ~150 entries to ~500 entries by processing a public tech-skills dataset.

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

**Step 13: Section-aware parsing infrastructure**
Built `section_extractor.py` to split resume text into named sections
(Education, Experience, Projects, Skills, Certifications, Leadership) by
locating section headers in the raw text, so later checks can be scoped
to the correct section instead of scanning the whole document.

**Step 14: Education level matching**
Built `education_matcher.py` — extracts the degree level required by the
JD (using a simple hierarchy: Diploma < Bachelor's < Master's < PhD) and
compares it against the degree level found in the resume's Education
section. A higher degree than required still counts as a full match.

**Step 15: Experience duration matching**
Built `experience_matcher.py` — extracts the JD's minimum required years
of experience, then calculates the candidate's actual experience by
parsing date ranges (e.g. "Aug 2025 - Jun 2026", "Jun 2020 - Present")
found in the resume's Experience section, since resumes almost never
state "X years of experience" explicitly the way job descriptions do.

**Step 16: Rebalanced the scoring model**
Updated `scorer.py` to combine all five factors (keyword/semantic, title,
formatting, education, experience) into the final weighted score, moving
from the original 3-factor model to the current 5-factor model described
above.

## Possible Future Additions (Not Yet Implemented)

- Contact information completeness check (address, phone, email,
  LinkedIn/GitHub links all present)
- Matching soft skills mentioned in the JD against soft skills evidenced
  in the resume's bullet points (not just a keyword list, since soft
  skills as a bare list were deliberately removed from the resume itself
  per ATS best-practice feedback — see the resume-writing conversation)
- In experience section can able to calculate the year of experience
  if job title match to  the job decription.