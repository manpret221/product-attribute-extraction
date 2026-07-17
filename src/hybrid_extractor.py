
from src.vocab import ATTRIBUTES, NOT_SPECIFIED
from src.rule_extractor import rule_based_extract
from src.ml_extractor import ml_extract

MULTI_VALUE_ATTRIBUTES = {"color"}


def extract(text, use_ml_fallback=True):
    rule_result = rule_based_extract(text)
    if not use_ml_fallback:
        return rule_result, {"source": {a: "rule" for a in ATTRIBUTES}}

    ml_result = ml_extract(text)

    final = {}
    source = {}
    for attr in ATTRIBUTES:
        if attr in MULTI_VALUE_ATTRIBUTES:
            rule_vals = [v for v in rule_result[attr] if v != NOT_SPECIFIED]
            ml_vals = [v for v in ml_result[attr] if v != NOT_SPECIFIED]
            merged = rule_vals + [v for v in ml_vals if v not in rule_vals]
            final[attr] = merged if merged else [NOT_SPECIFIED]
            source[attr] = "rule+ml" if rule_vals and ml_vals else (
                "rule" if rule_vals else ("ml" if ml_vals else "none")
            )
        else:
            if rule_result[attr] != NOT_SPECIFIED:
                final[attr] = rule_result[attr]
                source[attr] = "rule"
            elif ml_result[attr] != NOT_SPECIFIED:
                final[attr] = ml_result[attr]
                source[attr] = "ml"
            else:
                final[attr] = NOT_SPECIFIED
                source[attr] = "none"
    return final, {"source": source}


if __name__ == "__main__":
    import json
    text = "Short cocktail dress with feather trim and beaded waist detail"
    result, meta = extract(text)
    print(json.dumps({"input": text, "attributes": result, "meta": meta}, indent=2))





"""
Combines the rule-based extractor (high precision Precision = True Positives / (True Positives + False Positives), deterministic) with the
trained ML model (fallback for phrasing the rule layer doesn't recognise).
rules
  1. If the rule layer found a value -> use it (rules encode exact domain
     vocabulary, so when they fire they are essentially always correct).
  2. Else, use the ML model's prediction if it is confident.
  3. Else -> "Not Specified".

For color (multi-valued): union of rule-found colors and confident ML
predictions, de-duplicated.
"""