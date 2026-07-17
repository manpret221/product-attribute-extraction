# Product Attribute Extraction

Converts unstructured fashion product descriptions into structured attributes
(Category, Silhouette, Fabric, Neckline, Sleeve, Length, Embellishment, Color)
via a REST API.

Input:  "Off shoulder satin ball gown with corset bodice and sweep train in royal navy"

Output: {
  "category": "Ball Gown Dress",
  "silhouette": "Ball Gown",
  "fabric": "Satin",
  "neckline": "Off Shoulder",
  "sleeve": "Not Specified",
  "length": "Sweep Train",
  "embellishment": "Corset Bodice",
  "color": ["Royal Navy"]
}

1. Approach

Why a hybrid model, not a pure ML model?

The assignment asks for a trained model, but with ~50 labeled examples a
pure statistical classifier will simply memorize the training set and fail
on any new phrasing at inference time. That would technically satisfy
"train a model" but would not actually work as an extraction system.

Instead this project uses the architecture a real attribute-extraction
system for a small fashion catalog would use in practice:


                       
   description  ──────> 1. Rule/Vocabulary  ──> found? ── > use it
                             Extractor        │
                        
                                  │ not found
                                  v
                        
                          2. Trained ML Model ──> confident? ─▶ use it
                          (TF-IDF + LogReg,   
                           one classifier per 
                           attribute)         
                        
                                  │ not confident
                                  v
                            "Not Specified"


~Layer 1 — Rule/vocabulary extractor: (`src/rule_extractor.py`)
A curated dictionary (`src/vocab.py`) maps every domain phrase a fashion
cataloguer would use ("v neckline", "off shoulder", "sweep train", ...) to a
canonical label. Matching is done with word-boundary regex, longest-phrase-
first, so e.g. "off shoulder" is preferred over a bare "shoulder" match.
This layer is deterministic and near-100% precise on vocabulary it knows,
and — importantly — it works correctly on the very first sentence it ever
sees, with zero training data.

~Layer 2 — Trained ML model: ('src/train_model.py', src/ml_extractor.py)
For each single-valued attribute (category, silhouette, fabric, neckline,
sleeve, length, embellishment) a `TfidfVectorizer` (character n-grams,
robust to compound/unseen spellings like "off-shoulder") feeds a
`LogisticRegression` classifier. Color is multi-label, so it is trained as
a `OneVsRestClassifier` over a `MultiLabelBinarizer`. This is the actual
"trained model" requirement, satisfies the requested evaluation metrics,
and is used as a genuine fallback whenever the rule layer has no vocabulary
match — e.g. for informal phrasing not in the dictionary.

~Layer 3 — Combination (`src/hybrid_extractor.py`)
Rule result wins if present; otherwise the ML prediction is used if its
confidence clears a threshold (0.35); otherwise the attribute is reported
as `"Not Specified"` rather than guessing.

This design means: (a) it works immediately, (b) it genuinely improves as
more labeled data is added (only the ML layer needs retraining), and
(c) failure is graceful — low-confidence attributes are flagged, not
silently wrong.

---

2. Dataset

`data/dataset.json` — 52 labeled descriptions:
 The 10 sample descriptions from the assignment brief, hand-labeled.
 42 additional descriptions assembled by `src/generate_dataset.py` from
 templates + the same controlled vocabulary. Because each sentence is
 built directly from the canonical vocabulary, gold labels are correct
 by construction while surface phrasing/order still varies across
 templates — giving the model genuine (if modest) variation to learn from
 without manual labeling errors.

Regenerate: `python -m src.generate_dataset`

Each record:
json
{
  "text": "...",
  "labels": {
    "category": "...", "silhouette": "...", "fabric": "...",
    "neckline": "...", "sleeve": "...", "length": "...",
    "embellishment": "...", "color": ["...", "..."]
  }
}

 3. Setup & Running


pip install -r requirements.txt

1. (Re)generate the dataset
python -m src.generate_dataset

2. Train the ML fallback model
python -m src.train_model

3. Evaluate on the held-out test split
python -m src.evaluate

4. Start the API
uvicorn src.api:app --reload --port 8000

 API

POST /extract
```bash
curl -X POST http://localhost:8000/extract 
     -H "Content-Type: application/json" 
     -d '{"text": "Lace mermaid wedding dress with long sleeves and scalloped hem"}'

Response:
json
{
  "input_text": "Lace mermaid wedding dress with long sleeves and scalloped hem",
  "attributes": {
    "category": "Wedding Dress",
    "silhouette": "Mermaid",
    "fabric": "Lace",
    "neckline": "Not Specified",
    "sleeve": "Long Sleeves",
    "length": "Not Specified",
    "embellishment": "Scalloped Hem",
    "color": ["Not Specified"]
  }
}


Set `"include_debug": true` in the request to also get, per attribute,
whether the value came from the rule layer, the ML layer, or neither.

GET /health  — liveness check.

Interactive docs (Swagger UI) are auto-generated by FastAPI at
`http://localhost:8000/docs`.

### Demo script
`python demo.py` runs the pipeline on brief sample descriptions locally
and then calls the live API (start the server first).

---

4. Evaluation

Run `python -m src.evaluate`. It evaluates the full hybrid pipeline
(not just the ML layer in isolation) on an 80/20 train/test split of the
52-example dataset, and writes `docs/evaluation_report.json`.

Latest run (test size = 11):

| Attribute      | Accuracy | F1    |
|----------------|----------|-------|
| category       | 1.000    | 1.000 |
| silhouette     | 1.000    | 1.000 |
| fabric         | 0.909    | 0.938 |
| neckline       | 1.000    | 1.000 |
| sleeve         | 1.000    | 1.000 |
| length         | 1.000    | 1.000 |
| embellishment  | 0.818    | 0.875 |
| color (multi)  | 1.000    | 1.000 (micro) |

**Overall macro accuracy: 0.966**
**Overall average F1: 0.977**

These numbers are high because the template-generated portion of the
dataset shares vocabulary with the extractor's dictionary by design — they mainly validate that the pipeline is implemented
correctly, not that it generalizes to arbitrary catalog copy.
below gives a realistic account of where it actually breaks.

Failure cases (real, observed)

1. Substring collisions between fabric and embellishment vocabulary.**
   "lace applique" contains the literal word "lace", so the fabric rule
   fires ("Lace") even when the sentence never states the garment's fabric
   — it only says the *trim* is lace. Example:
   `"Mermaid cocktail dress featuring lace applique and off shoulder"` →
   fabric incorrectly predicted as `"Lace"` (gold: `"Not Specified"`).
   Fix direction:* exclude phrase spans already consumed by a longer
   embellishment match from being re-scanned by the fabric matcher.

2. **ML fallback hallucinating "Lace Applique" on unrelated descriptions.**
   When the rule layer finds no embellishment and the sentence is short,
   the ML model (trained on only ~40 examples) sometimes predicts the
   majority-ish class ("Lace Applique") with just-over-threshold
   confidence. This is the classic small-data overfitting failure mode —
   *fix direction:* more labeled data per attribute, or raise the
   confidence threshold for lower-frequency attributes.

3. Unseen / informal phrasing not in the vocabulary.** e.g. "boho",
   "beachy", "figure-hugging" have no dictionary entry and no training
   signal, so they correctly fall through to `"Not Specified"` rather than
   a wrong guess — but that also means real information is dropped.
   *Fix direction:* expand the vocabulary iteratively from real catalog
   copy, and/or replace char n-gram TF-IDF with sentence embeddings once
   more data is available.

4. Multi-attribute ambiguity in one word.** "gown" alone is mapped to
   category "Evening Gown" as a default, but a "wedding gown" or "prom
   gown" should override that — the rule ordering (longer phrase first)
   handles the common cases but any phrase not explicitly listed will
   fall back to the generic mapping and can be wrong for edge phrasing.

5. Color list truncation.** If a description lists 3+ colors in an
   unusual conjunction pattern ("available in black, red, or emerald"),
   the current regex still finds each color independently and this case
   works, but colors expressed as ranges or swatch codes ("colors 1-4")
   are not covered by the vocabulary and are correctly reported as
   `"Not Specified"`.

--
5. Project structure

```
product-attribute-extraction/
├── data/
│   └── dataset.json              # 52 labeled examples
├── models/                       # trained artifacts (generated)
│   ├── tfidf_vectorizer.joblib
│   ├── clf_<attribute>.joblib
│   ├── label_encoders.joblib
│   └── split.joblib
├── docs/
│   ├── evaluation_report.json    # generated by src/evaluate.py
│   └── brief_samples_output.json # pipeline output on the 10 brief samples
├── src/
│   ├── vocab.py                  # controlled vocabulary (single source of truth)
│   ├── rule_extractor.py         # Layer 1: deterministic rule/regex extraction
│   ├── train_model.py            # trains Layer 2 ML classifiers
│   ├── ml_extractor.py           # Layer 2: ML inference
│   ├── hybrid_extractor.py       # Layer 3: combines rule + ML
│   ├── generate_dataset.py       # builds data/dataset.json
│   ├── evaluate.py               # accuracy / F1 / failure report
│   └── api.py                    # FastAPI app (POST /extract)
├── demo.py                       # end-to-end demo script
├── requirements.txt
└── README.md
```

 6. Extending this project

- Add more real (non-generated) labeled descriptions to `data/dataset.json`
  and re-run `train_model.py` — the ML layer improves automatically without
  any code changes.
- Add new vocabulary/phrases to `src/vocab.py` to instantly improve rule
  precision on new phrasing, with zero retraining needed.
- Swap `TfidfVectorizer` for a pretrained sentence-embedding model
  (e.g. `sentence-transformers`) once the dataset is large enough (a few
  hundred+ examples) to benefit from it.
