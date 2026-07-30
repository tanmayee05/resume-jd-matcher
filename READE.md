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