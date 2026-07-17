"""
Demo script for the screen recording deliverable.

Walks through:
  1. Loading the dataset
  2. Running the hybrid extractor on the 10 brief sample descriptions
  3. Hitting the live API (start it first: uvicorn src.api:app --port 8000)
  4. Showing evaluation metrics

Run: python3 demo.py
"""
import json
import time
import requests

from src.hybrid_extractor import extract

SAMPLES = [
    "Floor length chiffon bridesmaid dress with pleated bodice and V neckline available in sage and dusty blue",
    "Sparkly sequin fitted prom gown featuring a deep illusion neckline and open back",
    "Off shoulder satin ball gown with corset bodice and sweep train in royal navy",
    "Lace mermaid wedding dress with long sleeves and scalloped hem",
    "Short cocktail dress with feather trim and beaded waist detail",
]


def demo_local():
    print("=" * 70)
    print("PART 1: Local extraction (no server needed)")
    print("=" * 70)
    for text in SAMPLES:
        attrs, _ = extract(text)
        print(f"\nINPUT:  {text}")
        print("OUTPUT:", json.dumps(attrs, indent=2))
        time.sleep(0.3)


def demo_api(base_url="http://localhost:8000"):
    print("\n" + "=" * 70)
    print("PART 2: Live API call to POST /extract")
    print("=" * 70)
    text = "Velvet winter formal dress with square neckline and puff sleeves"
    try:
        resp = requests.post(f"{base_url}/extract", json={"text": text}, timeout=5)
        print(f"\nPOST {base_url}/extract")
        print("Request body:", json.dumps({"text": text}))
        print("Response:", json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Could not reach API at {base_url} ({e}). "
              f"Start it first with: uvicorn src.api:app --port 8000")


if __name__ == "__main__":
    demo_local()
    demo_api()
