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
since only words in the known-skills list are ever considered. The list
was later expanded to ~500 skills using a public tech-skills dataset,
processed down to just the skill names (dropping category metadata not
needed by the matcher).

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

## 4. Section-Unaware Checks Caused False Positives (Education & Experience)
**Problem:** When first adding education-level and experience-duration
matching, both checks scanned the ENTIRE resume document rather than just
the relevant section. This caused two distinct false positives:
- A teammate's "Master's degree" mentioned in a Projects bullet
  (describing a collaborator) was misread as the candidate's own
  education level.
- The word "experience" used casually in the Professional Summary
  ("hands-on experience in MERN Stack...") was misdetected as the start
  of the actual Experience section.

**Resolution:** Built `section_extractor.py` to split the resume into
named sections (Education, Experience, Projects, Skills, Certifications,
Leadership) BEFORE running education/experience checks, so each check
only looks within its own relevant section. Falls back to scanning the
full document only if a section header genuinely cannot be found, rather
than silently failing.

**A follow-up bug within this fix:** the first version of
`section_extractor.py` split sections by checking each LINE of text
against known header phrases. This silently failed on resumes where PDF
extraction didn't preserve clean line breaks around headers (a recurring
issue in this project, also seen in Challenge PDF-parsing note below) —
causing the section split to fall back to the whole document, which
defeated the purpose of the fix entirely (experience was calculated as
7.3 years by summing date ranges from Education, Projects, AND
Experience combined, instead of just Experience).

**Second fix:** rewrote `section_extractor.py` to match header phrases by
POSITION in the raw text (via regex, not line-by-line), which works
regardless of how PDF extraction handled whitespace/newlines.

**A third, related bug:** even with position-based matching, a
case-insensitive match on the word "experience" still matched its casual
lowercase use in the Professional Summary before reaching the real
`EXPERIENCE` header. Fixed by matching header phrases CASE-SENSITIVELY
against their fully uppercase form (`EXPERIENCE`, `EDUCATION`), since
real resume section headers are consistently styled in all caps, while
casual prose use of the same word is not.

**Takeaway:** a single-layer fix (adding section awareness) isn't enough
on its own if the underlying section-detection logic has its own
weaknesses — this took three iterations (line-based → position-based →
case-sensitive uppercase matching) to become reliable, and each iteration
was caught by testing against a real resume rather than only synthetic
test text.

---

## 5. Regex Group Numbering Bug in Date-Range Parsing
**Problem:** `experience_matcher.py`'s date-range parser (for text like
"Aug 2025 - Jun 2026") used the same capturing group pattern twice within
one regex (once for the start month, once for the end month). Because
both used positional (numbered) groups, the second occurrence shifted the
group numbers for everything after it, causing `match.group(4)` to
sometimes return `None` when a year string was expected — crashing with
`int(None)`.

**Resolution:** Rewrote the regex using named groups
(`(?P<start_month>...)`, `(?P<end_year>...)`) instead of positional ones.
Named groups are referenced by name, not position, so reusing the same
sub-pattern twice in one regex no longer causes numbering conflicts.

**Takeaway:** any regex that reuses the same capturing group pattern more
than once should use named groups — positional group numbering becomes
fragile and error-prone the moment a sub-pattern is repeated.

---

# Known Drawbacks / Limitations (Current State)

1. **Skills taxonomy is manually curated and finite** — the system can
   only detect skills that exist in `tech_skills.csv`. A skill missing
   from this list (e.g. a brand-new framework) won't be detected, even if
   it's clearly present in the text. Requires manual maintenance/expansion
   over time. (Mitigated somewhat by expanding the list to ~500 skills,
   but still fundamentally a finite, curated list rather than a learned
   representation.)

2. **Job title matching is a simple word-overlap heuristic**, not a
   trained model — it doesn't understand title synonyms (e.g. "Software
   Engineer" vs "Software Developer" would only get partial credit based
   on shared words).

3. ~~No experience-duration matching~~ — **Update:** implemented via
   `experience_matcher.py`, which parses date ranges from the resume's
   Experience section rather than relying on explicit "X years" phrasing
   (which resumes rarely state — that phrasing is far more common in job
   descriptions than in resumes themselves). Known limitations of this
   specific implementation:
   - Overlapping date ranges are summed rather than de-duplicated (e.g.
     two concurrent part-time roles would double-count that overlapping
     period)
   - Only recognizes `Month Year - Month Year` and `Month Year - Present`
     formats; resumes using year-only ranges (e.g. "2023 - 2024" with no
     month) are not currently parsed
   - Does not tie years of experience to specific individual skills (only
     calculates total experience duration overall, not "3 years with
     Kubernetes specifically")

4. **PDF parsing quality varies by resume layout** — heavily formatted or
   multi-column resumes may still produce some text merging issues despite
   the cleanup step applied. This same underlying issue (inconsistent line
   breaks from PDF extraction) was the root cause of the section-detection
   bug described in Challenge #4 above.

5. **Scoring weights are reasoned estimates**, not empirically
   tuned against a large labeled dataset of real ATS outcomes — they're
   based on general industry descriptions of how ATS systems weight
   factors, not a trained/calibrated model. (Updated from the original
   50/30/20 three-factor split to a 35/20/15/15/15 five-factor split
   after adding education and experience matching — still reasoned
   estimates, not empirically calibrated.)

6. **Not a substitute for real ATS tools** — this project was built to
   learn and demonstrate core NLP techniques (TF-IDF, embeddings, POS
   tagging, custom NER), not to exactly replicate commercial ATS scoring
   products, which use proprietary, more sophisticated pipelines.

7. **Section header detection relies on all-caps styling** — the current
   fix for reliable section splitting assumes resume section headers are
   rendered in ALL CAPS in the extracted PDF text (true for the resumes
   tested so far). A resume using title-case or lowercase section headers
   (e.g. "Experience" instead of "EXPERIENCE") would not be correctly
   detected, and the system would fall back to scanning the whole
   document — reintroducing the false-positive risk described in
   Challenge #4.