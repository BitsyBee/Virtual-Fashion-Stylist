"""
Response service – generates the conversational AI text that accompanies
outfit recommendations.  Falls back gracefully when no Gemini key is set.
"""


def generate_response(preferences, recommendations):
    """
    Build a friendly stylist response.  Tries Gemini first; falls back to
    a template-based string so the app always returns something useful.
    """
    # Try to use Gemini if available
    try:
        from app import gemini_model, generate_ai_chat_response
        if gemini_model:
            raw_query = preferences.get("raw_query", "")
            return generate_ai_chat_response(raw_query, recommendations, preferences)
    except Exception as e:
        print(f"[response_service] Gemini unavailable: {e}")

    # ── Template fallback ─────────────────────────────────────────────────
    if not recommendations:
        return (
            "I couldn't find exact matches right now, but here are some "
            "great outfit ideas that might inspire you!"
        )

    style   = preferences.get("style")   or "fashionable"
    occasion = preferences.get("occasion") or "any"
    colors  = preferences.get("colors")  or ""
    total   = len(recommendations)
    top_name = recommendations[0]["outfit"]["name"] if recommendations else ""

    color_phrase = f" in {colors}" if colors else ""
    top_phrase   = f' Starting with "{top_name}" — ' if top_name else ""

    return (
        f"I found {total} {style} outfit{'s' if total != 1 else ''} "
        f"perfect for a {occasion} look{color_phrase}. "
        f"{top_phrase}"
        f"Each recommendation has been personalised to your style profile. "
        f"Tap the heart ❤️ to save your favourites!"
    )
