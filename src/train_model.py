import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split

from src.vocab import ATTRIBUTES, NOT_SPECIFIED
import warnings

warnings.filterwarnings('ignore')


SINGLE_ATTRS = [a for a in ATTRIBUTES if a != "color"]


def load_dataset(path="data/dataset.json"):
    with open(path) as f:
        return json.load(f)


def main():
    data = load_dataset()
    texts = [d["text"] for d in data]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(2, 5), min_df=1, lowercase=True
    )
    X = vectorizer.fit_transform(texts)

    train_idx, test_idx = train_test_split(
        range(len(texts)), test_size=0.3, random_state=42
    )
    X_train, X_test = X[train_idx], X[test_idx]

    encoders = {}
    for attr in SINGLE_ATTRS:
        y = [d["labels"][attr] for d in data]
        le = LabelEncoder()
        y_enc = le.fit_transform(y)
        y_train = [y_enc[i] for i in train_idx]

        clf = LogisticRegression(max_iter=2000)
        clf.fit(X_train, y_train)

        joblib.dump(clf, f"models/clf_{attr}.joblib")
        encoders[attr] = le

    # multi-label color
    color_lists = [d["labels"]["color"] for d in data]
    mlb = MultiLabelBinarizer()
    y_color = mlb.fit_transform(color_lists)
    y_color_train = y_color[train_idx]
    color_clf = OneVsRestClassifier(LogisticRegression(max_iter=2000))
    color_clf.fit(X_train, y_color_train)
    joblib.dump(color_clf, "models/clf_color.joblib")
    encoders["color"] = mlb

    joblib.dump(vectorizer, "models/tfidf_vectorizer.joblib")
    joblib.dump(encoders, "models/label_encoders.joblib")
    joblib.dump({"train_idx": train_idx, "test_idx": test_idx}, "models/split.joblib")

    print("Training complete.")
    print(f"Train size: {len(train_idx)}, Test size: {len(test_idx)}")
    print("Saved vectorizer, per-attribute classifiers, and encoders to models/")


if __name__ == "__main__":
    main()





"""
Trains one multinomial Logistic Regression classifier per single-valued
attribute (category, silhouette, fabric, neckline, sleeve, length,
embellishment), plus a multi-label OneVsRest classifier for color
(since a description can list more than one color).

Features: character n-gram TF-IDF (robust to the small dataset size and
to compound/unseen words like "off-shoulder" vs "off shoulder").

Artifacts saved to models/:
   tfidf_vectorizer.joblib
   clf_<attribute>.joblib for each single-valued attribute
   clf_color.joblib (MultiLabelBinarizer + OneVsRestClassifier)
   label_encoders.joblib
these are the save under the model folder that i make 
for run this command Run: python3 -m src.train_model """