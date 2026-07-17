import json
import random
from src.vocab import NOT_SPECIFIED

random.seed(42)


# Hand-labeled samples from the assignment brief

HAND_LABELED = [
    {
        "text": "Floor length chiffon bridesmaid dress with pleated bodice and V neckline available in sage and dusty blue",
        "labels": {
            "category": "Bridesmaid Dress", "silhouette": "Not Specified",
            "fabric": "Chiffon", "neckline": "V Neckline", "sleeve": "Not Specified",
            "length": "Floor Length", "embellishment": "Pleated",
            "color": ["Sage", "Dusty Blue"],
        },
    },
    {
        "text": "Sparkly sequin fitted prom gown featuring a deep illusion neckline and open back",
        "labels": {
            "category": "Prom Dress", "silhouette": "Not Specified",
            "fabric": "Sequin", "neckline": "Illusion Neckline", "sleeve": "Not Specified",
            "length": "Not Specified", "embellishment": "Open Back",
            "color": ["Not Specified"],
        },
    },
    {
        "text": "Off shoulder satin ball gown with corset bodice and sweep train in royal navy",
        "labels": {
            "category": "Ball Gown Dress", "silhouette": "Ball Gown",
            "fabric": "Satin", "neckline": "Off Shoulder", "sleeve": "Not Specified",
            "length": "Sweep Train", "embellishment": "Corset Bodice",
            "color": ["Royal Navy"],
        },
    },
    {
        "text": "Lace mermaid wedding dress with long sleeves and scalloped hem",
        "labels": {
            "category": "Wedding Dress", "silhouette": "Mermaid",
            "fabric": "Lace", "neckline": "Not Specified", "sleeve": "Long Sleeves",
            "length": "Not Specified", "embellishment": "Scalloped Hem",
            "color": ["Not Specified"],
        },
    },
    {
        "text": "Short cocktail dress with feather trim and beaded waist detail",
        "labels": {
            "category": "Cocktail Dress", "silhouette": "Not Specified",
            "fabric": "Not Specified", "neckline": "Not Specified", "sleeve": "Not Specified",
            "length": "Short/Mini", "embellishment": "Feather Trim",
            "color": ["Not Specified"],
        },
    },
    {
        "text": "Tulle A line evening gown with floral embroidery and cap sleeves",
        "labels": {
            "category": "Evening Gown", "silhouette": "A-line",
            "fabric": "Tulle", "neckline": "Not Specified", "sleeve": "Cap Sleeves",
            "length": "Not Specified", "embellishment": "Embroidered",
            "color": ["Not Specified"],
        },
    },
    {
        "text": "Stretch jersey sheath dress with ruched waist and side slit",
        "labels": {
            "category": "Dress", "silhouette": "Sheath",
            "fabric": "Jersey", "neckline": "Not Specified", "sleeve": "Not Specified",
            "length": "Not Specified", "embellishment": "Ruched",
            "color": ["Not Specified"],
        },
    },
    {
        "text": "Strapless sweetheart neckline glitter gown with layered skirt",
        "labels": {
            "category": "Evening Gown", "silhouette": "Not Specified",
            "fabric": "Not Specified", "neckline": "Strapless", "sleeve": "Not Specified",
            "length": "Not Specified", "embellishment": "Glitter",
            "color": ["Not Specified"],
        },
    },
    {
        "text": "One shoulder draped chiffon dress with high slit and empire waist",
        "labels": {
            "category": "Dress", "silhouette": "Empire Waist",
            "fabric": "Chiffon", "neckline": "One Shoulder", "sleeve": "Not Specified",
            "length": "Not Specified", "embellishment": "Draped",
            "color": ["Not Specified"],
        },
    },
    {
        "text": "Velvet winter formal dress with square neckline and puff sleeves",
        "labels": {
            "category": "Formal Dress", "silhouette": "Not Specified",
            "fabric": "Velvet", "neckline": "Square Neckline", "sleeve": "Puff Sleeves",
            "length": "Not Specified", "embellishment": "Not Specified",
            "color": ["Not Specified"],
        },
    },
]


#  Template-driven generation for additional coverage

CATEGORY = [("wedding dress", "Wedding Dress"), ("bridesmaid dress", "Bridesmaid Dress"),
            ("prom dress", "Prom Dress"), ("evening gown", "Evening Gown"),
            ("cocktail dress", "Cocktail Dress"), ("formal dress", "Formal Dress"),
            ("party dress", "Party Dress")]

SILHOUETTE = [("fit and flare", "Fit and Flare"), ("a line", "A-line"),
              ("mermaid", "Mermaid"), ("trumpet", "Trumpet"),
              ("sheath", "Sheath"), ("empire waist", "Empire Waist"),
              ("ball gown", "Ball Gown")]

FABRIC = [("chiffon", "Chiffon"), ("satin", "Satin"), ("lace", "Lace"),
          ("tulle", "Tulle"), ("velvet", "Velvet"), ("organza", "Organza"),
          ("silk", "Silk"), ("stretch jersey", "Jersey")]

NECKLINE = [("v neckline", "V Neckline"), ("sweetheart neckline", "Sweetheart Neckline"),
            ("off shoulder", "Off Shoulder"), ("illusion neckline", "Illusion Neckline"),
            ("square neckline", "Square Neckline"), ("one shoulder", "One Shoulder"),
            ("strapless", "Strapless"), ("halter neckline", "Halter")]

SLEEVE = [("long sleeves", "Long Sleeves"), ("cap sleeves", "Cap Sleeves"),
          ("puff sleeves", "Puff Sleeves"), ("sleeveless", "Sleeveless"),
          ("short sleeves", "Short Sleeves"), ("three-quarter sleeves", "Three-Quarter Sleeves")]

LENGTH = [("floor length", "Floor Length"), ("tea length", "Tea Length"),
          ("knee length", "Knee Length"), ("sweep train", "Sweep Train"),
          ("high-low", "High-Low Hem")]

EMBELLISH = [("beaded", "Beaded"), ("feather trim", "Feather Trim"),
             ("embroidered", "Embroidered"), ("ruched", "Ruched"),
             ("draped", "Draped"), ("lace applique", "Lace Applique"),
             ("glitter", "Glitter"), ("scalloped hem", "Scalloped Hem"),
             ("pleated", "Pleated"), ("corset bodice", "Corset Bodice")]

COLOR = [("black", "Black"), ("white", "White"), ("ivory", "Ivory"), ("red", "Red"),
         ("blush", "Blush"), ("burgundy", "Burgundy"), ("emerald", "Emerald"),
         ("gold", "Gold"), ("silver", "Silver"), ("champagne", "Champagne"),
         ("sage", "Sage"), ("dusty blue", "Dusty Blue"), ("royal navy", "Royal Navy")]

TEMPLATES = [
    "{length} {fabric} {category} with {neckline} and {sleeve} in {color}",
    "{silhouette} {category} featuring {embellishment} and {neckline}",
    "{fabric} {silhouette} {category} with {embellishment} in {color}",
    "{color} {category} with {sleeve}, {neckline} and {embellishment}",
    "{length} {category} in {fabric} with {silhouette} silhouette and {embellishment}",
    "{silhouette} {fabric} {category} with {neckline}, {sleeve} and {length}",
]


def build_generated_examples(n=42):
    examples = []
    combos_used = set()
    attempts = 0
    while len(examples) < n and attempts < 2000:
        attempts += 1
        cat_txt, cat_lbl = random.choice(CATEGORY)
        sil_txt, sil_lbl = random.choice(SILHOUETTE)
        fab_txt, fab_lbl = random.choice(FABRIC)
        nec_txt, nec_lbl = random.choice(NECKLINE)
        sle_txt, sle_lbl = random.choice(SLEEVE)
        len_txt, len_lbl = random.choice(LENGTH)
        emb_txt, emb_lbl = random.choice(EMBELLISH)
        col_txt, col_lbl = random.choice(COLOR)

        template = random.choice(TEMPLATES)
        text = template.format(
            length=len_txt, fabric=fab_txt, category=cat_txt, neckline=nec_txt,
            sleeve=sle_txt, color=col_txt, silhouette=sil_txt, embellishment=emb_txt,
        )
        text = text[0].upper() + text[1:]

        if text in combos_used:
            continue
        combos_used.add(text)

        labels = {
            "category": cat_lbl,
            "silhouette": sil_lbl if "{silhouette}" in template else "Not Specified",
            "fabric": fab_lbl if "{fabric}" in template else "Not Specified",
            "neckline": nec_lbl if "{neckline}" in template else "Not Specified",
            "sleeve": sle_lbl if "{sleeve}" in template else "Not Specified",
            "length": len_lbl if "{length}" in template else "Not Specified",
            "embellishment": emb_lbl if "{embellishment}" in template else "Not Specified",
            "color": [col_lbl] if "{color}" in template else ["Not Specified"],
        }
        examples.append({"text": text, "labels": labels})
    return examples


def main():
    generated = build_generated_examples(42)
    dataset = HAND_LABELED + generated
    with open("data/dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Wrote {len(dataset)} examples to data/dataset.json")


if __name__ == "__main__":
    main()


"""
Builds data/dataset.json: a labeled dataset of product descriptions.

Two sources of examples:
  A) The 10 sample descriptions given in the assignment brief, labeled by
     hand (ground truth reviewed manually).
  B) 40+ additional descriptions assembled from template + vocabulary
     combinations. Because each sentence is assembled FROM the same
     canonical vocabulary used by the extractor, the gold labels are
     correct by construction (no manual re-labeling errors), while the
     surface text still varies in wording/order so the dataset isn't
     trivially just "the vocab list".

Run: python3 -m src.generate_dataset
"""