"""
Evaluates the extraction pipeline (hybrid = rule layer + ML fallback) on the
held-out test split created during training (models/split.joblib), and
reports:
  - Per-attribute accuracy (single-valued attributes)
  - Per-attribute micro-F1 (color, multi-label)
  - Overall macro accuracy / macro F1 across all attributes
  - A confusion / failure sample dump for manual inspection

Run: python3 -m src.evaluate
"""
import json
import os
import joblib
from sklearn.metrics import accuracy_score, f1_score

from src.vocab import ATTRIBUTES, NOT_SPECIFIED
from src.hybrid_extractor import extract

# Always resolve paths relative to the project root (parent of src/), so this
# script works correctly whether you run it as `python3 -m src.evaluate` from
# the project root, or accidentally from inside src/.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "docs", "evaluation_report.json")
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "dataset.json")
SPLIT_PATH = os.path.join(PROJECT_ROOT, "models", "split.joblib")

SINGLE_ATTRS = [a for a in ATTRIBUTES if a != "color"]


def load_dataset(path=None):
    path = path or DATASET_PATH
    with open(path) as f:
        return json.load(f)


def color_f1(true_lists, pred_lists, all_labels):
    # micro-F1 over the multi-label color set
    tp = fp = fn = 0
    for true, pred in zip(true_lists, pred_lists):
        true_set = set(true)
        pred_set = set(pred)
        tp += len(true_set & pred_set)
        fp += len(pred_set - true_set)
        fn += len(true_set - pred_set)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def main():
    data = load_dataset()
    split = joblib.load(SPLIT_PATH)
    test_idx = split["test_idx"]
    test_set = [data[i] for i in test_idx]

    print(f"Evaluating on {len(test_set)} held-out test examples\n")

    preds = []
    for ex in test_set:
        attrs, _ = extract(ex["text"])
        preds.append(attrs)

    results = {}
    failure_log = []

    for attr in SINGLE_ATTRS:
        y_true = [ex["labels"][attr] for ex in test_set]
        y_pred = [p[attr] for p in preds]
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        results[attr] = {"accuracy": round(acc, 3), "macro_f1": round(f1, 3)}

        for ex, yt, yp in zip(test_set, y_true, y_pred):
            if yt != yp:
                failure_log.append({
                    "text": ex["text"], "attribute": attr,
                    "expected": yt, "predicted": yp,
                })

    # color (multi-label)
    y_true_color = [ex["labels"]["color"] for ex in test_set]
    y_pred_color = [p["color"] for p in preds]
    all_color_labels = sorted({c for lst in y_true_color for c in lst})
    precision, recall, f1c = color_f1(y_true_color, y_pred_color, all_color_labels)
    color_acc = accuracy_score(
        [tuple(sorted(t)) for t in y_true_color],
        [tuple(sorted(p)) for p in y_pred_color],
    )
    results["color"] = {"accuracy": round(color_acc, 3), "micro_f1": round(f1c, 3),
                          "precision": round(precision, 3), "recall": round(recall, 3)}
    for ex, yt, yp in zip(test_set, y_true_color, y_pred_color):
        if set(yt) != set(yp):
            failure_log.append({
                "text": ex["text"], "attribute": "color",
                "expected": yt, "predicted": yp,
            })

    overall_acc = sum(r["accuracy"] for r in results.values()) / len(results)
    overall_f1 = sum(r.get("macro_f1", r.get("micro_f1")) for r in results.values()) / len(results)

    print("Per-attribute metrics:")
    for attr, r in results.items():
        print(f"  {attr:15s} {r}")

    print(f"\nOverall macro accuracy: {round(overall_acc, 3)}")
    print(f"Overall macro/micro F1 (avg across attributes): {round(overall_f1, 3)}")

    print(f"\nFailure cases ({len(failure_log)}):")
    for f in failure_log:
        print(f"  [{f['attribute']}] '{f['text']}' -> expected={f['expected']!r} predicted={f['predicted']!r}")

    # Guarantee the docs/ folder exists before writing — this is the fix:
    # previously, if docs/ was missing (e.g. deleted, or first-ever run from
    # a fresh checkout), open() raised FileNotFoundError and the report was
    # never written, even though all the metrics printed fine to console.
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump({
            "test_size": len(test_set),
            "per_attribute_metrics": results,
            "overall_macro_accuracy": round(overall_acc, 3),
            "overall_avg_f1": round(overall_f1, 3),
            "failure_cases": failure_log,
        }, f, indent=2)
    print(f"\nSaved full report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
