"""
Loads the trained TF-IDF + per-attribute classifiers and exposes
ml_extract(text) -> dict, mirroring the rule extractor's output shape.
"""
import joblib
from src.vocab import ATTRIBUTES, NOT_SPECIFIED

_vectorizer = None
_encoders = None
_clfs = {}


def _lazy_load():
    global _vectorizer, _encoders, _clfs
    if _vectorizer is None:
        _vectorizer = joblib.load("models/tfidf_vectorizer.joblib")
        _encoders = joblib.load("models/label_encoders.joblib")
        for attr in ATTRIBUTES:
            _clfs[attr] = joblib.load(f"models/clf_{attr}.joblib")


def ml_extract(text, min_confidence=0.35):
    """Returns dict attribute -> predicted label (str) or list[str] for color.
    Predictions below min_confidence are reported as NOT_SPECIFIED, since a
    low-confidence guess from a model trained on only ~40 examples is more
    likely to mislead than help."""
    _lazy_load()
    X = _vectorizer.transform([text])
    result = {}

    for attr in ATTRIBUTES:
        clf = _clfs[attr]
        if attr == "color":
            mlb = _encoders["color"]
            probs = clf.predict_proba(X)[0]
            labels = [mlb.classes_[i] for i, p in enumerate(probs) if p >= min_confidence]
            labels = [l for l in labels if l != NOT_SPECIFIED]
            result["color"] = labels if labels else [NOT_SPECIFIED]
        else:
            le = _encoders[attr]
            probs = clf.predict_proba(X)[0]
            best_idx = probs.argmax()
            best_prob = probs[best_idx]
            label = le.inverse_transform([best_idx])[0]
            if best_prob < min_confidence:
                result[attr] = NOT_SPECIFIED
            else:
                result[attr] = label
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(ml_extract(
        "Sparkly sequin fitted prom gown featuring a deep illusion neckline and open back"
    ), indent=2))
