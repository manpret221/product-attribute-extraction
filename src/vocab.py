
ATTRIBUTES = [
    "category",
    "silhouette",
    "fabric",
    "neckline",
    "sleeve",
    "length",
    "embellishment",
    "color",
]

# Order inside each list matters when a description contains overlapping
# substrings (e.g. "off shoulder" must be checked before "shoulder").
# Longer / more specific phrases are listed first.

VOCAB = {
    "category": {
        "wedding dress": "Wedding Dress",
        "bridal gown": "Wedding Dress",
        "bridesmaid dress": "Bridesmaid Dress",
        "prom gown": "Prom Dress",
        "prom dress": "Prom Dress",
        "evening gown": "Evening Gown",
        "cocktail dress": "Cocktail Dress",
        "formal dress": "Formal Dress",
        "party dress": "Party Dress",
        "ball gown": "Ball Gown Dress",
        "gown": "Evening Gown",
        "dress": "Dress",
    },
    "silhouette": {
        "fit and flare": "Fit and Flare",
        "a line": "A-line",
        "a-line": "A-line",
        "ball gown": "Ball Gown",
        "mermaid": "Mermaid",
        "trumpet": "Trumpet",
        "sheath": "Sheath",
        "empire waist": "Empire Waist",
    },
    "fabric": {
        "chiffon": "Chiffon",
        "satin": "Satin",
        "lace": "Lace",
        "tulle": "Tulle",
        "velvet": "Velvet",
        "sequin": "Sequin",
        "sparkly sequin": "Sequin",
        "jersey": "Jersey",
        "organza": "Organza",
        "silk": "Silk",
        "stretch jersey": "Jersey",
    },
    "neckline": {
        "v neckline": "V Neckline",
        "v-neck": "V Neckline",
        "sweetheart neckline": "Sweetheart Neckline",
        "off shoulder": "Off Shoulder",
        "off-shoulder": "Off Shoulder",
        "illusion neckline": "Illusion Neckline",
        "square neckline": "Square Neckline",
        "one shoulder": "One Shoulder",
        "strapless": "Strapless",
        "halter neckline": "Halter",
        "halter": "Halter",
    },
    "sleeve": {
        "long sleeves": "Long Sleeves",
        "cap sleeves": "Cap Sleeves",
        "puff sleeves": "Puff Sleeves",
        "sleeveless": "Sleeveless",
        "short sleeves": "Short Sleeves",
        "three-quarter sleeves": "Three-Quarter Sleeves",
        "three quarter sleeves": "Three-Quarter Sleeves",
    },
    "length": {
        "floor length": "Floor Length",
        "tea length": "Tea Length",
        "knee length": "Knee Length",
        "sweep train": "Sweep Train",
        "high-low": "High-Low Hem",
        "high low": "High-Low Hem",
        "short": "Short/Mini",
        "mini": "Short/Mini",
    },
    "embellishment": {
        "corset bodice": "Corset Bodice",
        "pleated bodice": "Pleated",
        "pleated": "Pleated",
        "beaded waist detail": "Beaded",
        "beaded": "Beaded",
        "feather trim": "Feather Trim",
        "floral embroidery": "Embroidered",
        "embroidered": "Embroidered",
        "embroidery": "Embroidered",
        "ruched waist": "Ruched",
        "ruched": "Ruched",
        "draped": "Draped",
        "lace applique": "Lace Applique",
        "glitter": "Glitter",
        "scalloped hem": "Scalloped Hem",
        "layered skirt": "Layered",
        "side slit": "Side Slit",
        "high slit": "High Slit",
        "open back": "Open Back",
    },
    "color": {
        "sage": "Sage",
        "dusty blue": "Dusty Blue",
        "royal navy": "Royal Navy",
        "black": "Black",
        "white": "White",
        "ivory": "Ivory",
        "red": "Red",
        "blush": "Blush",
        "burgundy": "Burgundy",
        "emerald": "Emerald",
        "gold": "Gold",
        "silver": "Silver",
        "champagne": "Champagne",
        "navy": "Royal Navy",
    },
}

NOT_SPECIFIED = "Not Specified"



"""
Controlled vocabulary for the fashion product-attribute extraction task.

Each attribute maps SURFACE FORMS (as they appear in free text, lowercase)
to a single CANONICAL LABEL. This dictionary powers:
  1. the rule-based extractor (src/rule_extractor.py)
  2. the synthetic-but-realistic dataset generator (src/generate_dataset.py)

Keeping one source of truth for vocabulary avoids label drift between the
data and the extractor.
"""
