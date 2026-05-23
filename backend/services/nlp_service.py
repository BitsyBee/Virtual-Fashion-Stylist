import re


def extract_preferences(text):
    """
    Rule-based NLP extraction of fashion preferences from natural language.
    Returns keys that match what recommendation_service and app.py expect.
    """
    lower = text.lower()

    preferences = {
        "occasion": "",
        "colors": "",      # plural – matches recommendation engine & app.py
        "style": "",
        "style_tags": "",
        "season": "",
        "body_type": "",
        "skin_tone": "",
        "raw_query": text,
        "ai_response": "",
    }

    # ── Occasion ──────────────────────────────────────────────────────────
    occasion_map = {
        "formal":    ["formal", "gala", "black tie", "ceremony"],
        "dinner":    ["dinner"],
        "evening":   ["evening", "party", "cocktail", "wedding", "date night"],
        "business":  ["business", "office", "work", "meeting", "corporate"],
        "casual":    ["casual", "everyday", "day out", "brunch"],
        "vacation":  ["beach", "vacation", "holiday", "resort", "travel"],
        "active":    ["gym", "sport", "workout", "active", "athletic"],
        "summer":    ["summer"],
        "winter":    ["winter"],
        "date":      ["date"],
    }
    for occ, keywords in occasion_map.items():
        if any(kw in lower for kw in keywords):
            preferences["occasion"] = occ
            break

    # ── Style ─────────────────────────────────────────────────────────────
    style_map = {
        "elegant":    ["elegant", "sophisticated", "luxurious", "luxury"],
        "casual":     ["casual", "relaxed", "comfortable", "comfy"],
        "chic":       ["chic", "stylish"],
        "trendy":     ["trendy", "fashionable"],
        "bohemian":   ["bohemian", "boho"],
        "vintage":    ["vintage", "retro"],
        "minimal":    ["minimal", "minimalist", "clean", "simple"],
        "bold":       ["bold", "statement"],
        "romantic":   ["romantic", "feminine"],
        "edgy":       ["edgy", "rebellious", "rock"],
        "sporty":     ["sporty", "athletic"],
        "preppy":     ["preppy", "ivy"],
        "business":   ["professional", "corporate"],
        "modern":     ["modern", "contemporary"],
        "dark":       ["dark", "gothic"],
    }
    for style, keywords in style_map.items():
        if any(kw in lower for kw in keywords):
            preferences["style"] = style
            break

    # ── Season ────────────────────────────────────────────────────────────
    if any(w in lower for w in ["summer", "hot", "warm", "sunny"]):
        preferences["season"] = "summer"
    elif any(w in lower for w in ["winter", "cold", "snow", "cozy"]):
        preferences["season"] = "winter"
    elif any(w in lower for w in ["spring", "fresh"]):
        preferences["season"] = "spring"
    elif any(w in lower for w in ["fall", "autumn"]):
        preferences["season"] = "fall"

    # ── Colors ────────────────────────────────────────────────────────────
    color_list = [
        "black", "white", "red", "blue", "navy", "green", "pink",
        "beige", "cream", "gold", "brown", "gray", "grey", "purple",
        "silver", "coral", "yellow", "orange", "burgundy", "rose",
    ]
    found_colors = [c for c in color_list if c in lower]
    preferences["colors"] = ", ".join(found_colors)

    # ── style_tags: combine occasion + style + extra keywords ─────────────
    tags = []
    if preferences["style"]:
        tags.append(preferences["style"])
    if preferences["occasion"] in ("formal", "dinner", "evening"):
        tags.extend(["elegant", "chic", "formal"])
    elif preferences["occasion"] == "business":
        tags.extend(["business", "smart", "professional"])
    elif preferences["occasion"] == "vacation":
        tags.extend(["vacation", "relaxed", "breeze"])
    elif preferences["occasion"] == "active":
        tags.extend(["sporty", "casual", "modern"])
    else:
        tags.extend(["casual", "smart"])

    preferences["style_tags"] = ", ".join(dict.fromkeys(tags))  # deduplicate

    # ── Friendly response ─────────────────────────────────────────────────
    occ_label = preferences["occasion"] or "style"
    preferences["ai_response"] = (
        f"Great! I'm finding the best {occ_label} outfit recommendations for you."
    )

    return preferences
