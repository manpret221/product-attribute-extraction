"""

This file is NOT used by the API or model; it exists only
as proof/reference for the submission.

Run from the project root: python generate_brief_samples_output.py
"""
import json
from src.hybrid_extractor import extract

SAMPLES = [
    "Floor length chiffon bridesmaid dress with pleated bodice and V neckline available in sage and dusty blue",
    "Sparkly sequin fitted prom gown featuring a deep illusion neckline and open back",
    "Off shoulder satin ball gown with corset bodice and sweep train in royal navy",
    "Lace mermaid wedding dress with long sleeves and scalloped hem",
    "Short cocktail dress with feather trim and beaded waist detail",
    "Tulle A line evening gown with floral embroidery and cap sleeves",
    "Stretch jersey sheath dress with ruched waist and side slit",
    "Strapless sweetheart neckline glitter gown with layered skirt",
    "One shoulder draped chiffon dress with high slit and empire waist",
    "Velvet winter formal dress with square neckline and puff sleeves",
]


def main():
    out = []
    for text in SAMPLES:
        attrs, meta = extract(text)
        out.append({"text": text, "attributes": attrs})

    with open("docs/brief_samples_output.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {len(out)} results to docs/brief_samples_output.json")


if __name__ == "__main__":
    main()
