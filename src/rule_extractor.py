"""
Deterministic, dictionary/regex based attribute extractor.

With 50 approx  labeled examples, a purely statistical model has almost no chance
of generalising to unseen phrasing . it will just memorise the training set.
The most defensible production architecture for this problem size is
a HYBRID:

A curated vocabulary / regex layer (this file) that captures the
domain knowledge a fashion cataloguer already has (this is high precision, deterministic, and works even on the very first
description it ever sees).
    
A trained multi-label TF-IDF + Logistic Regression model
(src/train_model.py) that is used as a FALLBACK whenever the rule layer finds no match for a given attribute, and that also gives us
te "trained model" + real evaluation metrics the assignment ask  for.

This file implements layer 1. See src/hybrid_extractor.py for how the
two layers are combined at inference time.
"""

import re
from src.vocab import VOCAB, NOT_SPECIFIED, ATTRIBUTES


def _find_all_matches(text_lower, phrase_dict):
    """Return list of (canonical_label, phrase, start_index) for every
    vocabulary phrase that appears in text_lower, matched on word
    boundaries so 'red' doesn't match inside 'bored'."""
    matches = []
    for phrase, canonical in phrase_dict.items():
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        m = re.search(pattern, text_lower)
        if m:
            matches.append((canonical, phrase, m.start()))
    return matches


def extract_single(text_lower, attribute):
    """Pick the single best match for a single-valued attribute: prefer
    the longest / most specific phrase"""
    matches = _find_all_matches(text_lower, VOCAB[attribute])
    if not matches:
        return None
    matches.sort(key=lambda m: (-len(m[1]), m[2]))
    return matches[0][0]


def extract_multi(text_lower, attribute):
    """Return every distinct canonical value found (used for color, which
    frequently lists 2+ options"""
    matches = _find_all_matches(text_lower, VOCAB[attribute])
    if not matches:
        return []
    matches.sort(key=lambda m: m[2])
    seen = []
    for canonical, phrase, pos in matches:
        if canonical not in seen:
            seen.append(canonical)
    return seen


MULTI_VALUE_ATTRIBUTES = {"color"}


def rule_based_extract(text):
    """Extract all 8 attributes from a raw description string.
    Returns a dict attribute -> canonical label (str), or for 'color',
    attribute -> list[str]. Missing attributes are NOT_SPECIFIED / [].
    """
    text_lower = text.lower()
    result = {}
    for attr in ATTRIBUTES:
        if attr in MULTI_VALUE_ATTRIBUTES:
            vals = extract_multi(text_lower, attr)
            result[attr] = vals if vals else [NOT_SPECIFIED]
        else:
            val = extract_single(text_lower, attr)
            result[attr] = val if val else NOT_SPECIFIED
    return result


if __name__ == "__main__":
    samples = [
        "Floor length chiffon bridesmaid dress with pleated bodice and V neckline available in sage and dusty blue",
        "Off shoulder satin ball gown with corset bodice and sweep train in royal navy",
    ]
    import json
    for s in samples:
        print(s)
        print(json.dumps(rule_based_extract(s), indent=2))
        print()
