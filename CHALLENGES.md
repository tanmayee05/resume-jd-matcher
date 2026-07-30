# Challenges Faced & How They Were Resolved


## 1. NER Mislabeling Domain-Specific Terms
**Problem:** spaCy's default NER model mislabeled tech terms it wasn't
trained on — e.g. tagging "Kafka" and "Spring Boot" as `PERSON`,
"Kubernetes" as `ORG`.

**Resolution:** Initially worked around this using noun-chunk extraction
instead of entity-type filtering. Later, moved away from NER-based
scoring entirely in favor of a skills taxonomy approach (see #4 below),
which sidesteps the mislabeling problem completely.

**Takeaway:** General-purpose NER models aren't trained for
domain-specific vocabulary — this is exactly why companies build custom
NER models for specialized fields (legal, medical, tech recruiting).

---

## 2. Naive Keyword Extraction Surfacing Generic Filler Words
**Problem:** Using raw TF-IDF word-frequency to find "missing keywords"
surfaced generic, non-skill words that job descriptions repeat often —
e.g. "exposure", "familiarity", "learn", "willingness" — since TF-IDF has
no concept of what a *skill* actually is, only what's frequent.

**Resolution attempted:** First tried POS-tagging to keep only nouns —
this helped a little, but many generic words (e.g. "exposure",
"infrastructure") are grammatically valid nouns too, so filtering by
grammar alone wasn't enough. Manually blocklisting words was tried next,
but proved to be an unsustainable, ever-growing list.

**Final resolution:** Replaced frequency-based keyword guessing with a
**skills taxonomy approach** — matching resume/JD text against a curated
list of ~150 known real-world tech skills, instead of guessing importance
from word statistics. This eliminated generic-word leakage entirely,
since only words in the known-skills list are ever considered.

**Takeaway:** Statistical methods (TF-IDF) answer "what words are
frequent," not "what words are meaningful skills" — these are different
questions, and conflating them was the root cause of this issue.

---

## 3. TF-IDF vs Embeddings — Why the Score Changed Approach
**Problem:** Pure TF-IDF-based similarity scoring treats "Docker" and
"containerization" as completely unrelated, since it only matches exact
words — this produced unrealistically low/harsh scores for resumes that
were conceptually relevant but phrased differently than the JD.

**Resolution:** Added sentence-transformer embeddings (`all-MiniLM-L6-v2`)
to capture semantic/meaning-based similarity, which correctly identifies
related concepts even with no exact word overlap. This became the primary
scoring signal; TF-IDF's role was narrowed to a supporting role before
being replaced by the skills taxonomy for keyword-level matching.

---



# Known Drawbacks / Limitations (Current State)

1. **Skills taxonomy is manually curated and finite** — the system can
   only detect skills that exist in `tech_skills.csv`. A skill missing
   from this list (e.g. a brand-new framework) won't be detected, even if
   it's clearly present in the text. Requires manual maintenance/expansion
   over time.

2. **Job title matching is a simple word-overlap heuristic**, not a
   trained model — it doesn't understand title synonyms (e.g. "Software
   Engineer" vs "Software Developer" would only get partial credit based
   on shared words).

3. **No experience-duration matching** — the system doesn't check whether
   the resume shows enough *years* of experience with a given skill, which
   real ATS systems sometimes do. This was deliberately scoped out due to
   its complexity relative to project goals.

4. **PDF parsing quality varies by resume layout** — heavily formatted or
   multi-column resumes may still produce some text merging issues despite
   the cleanup step applied.

5. **Scoring weights (50/30/20) are reasoned estimates**, not empirically
   tuned against a large labeled dataset of real ATS outcomes — they're
   based on general industry descriptions of how ATS systems weight
   factors, not a trained/calibrated model.

6. **Not a substitute for real ATS tools** — this project was built to
   learn and demonstrate core NLP techniques (TF-IDF, embeddings, POS
   tagging, custom NER), not to exactly replicate commercial ATS scoring
   products, which use proprietary, more sophisticated pipelines.



