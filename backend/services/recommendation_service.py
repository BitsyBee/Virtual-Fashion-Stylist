"""
Recommendation service – uses the full scoring pipeline defined in app.py.

The function signature matches how app.py calls it:
    get_recommendations(preferences, profile)

It delegates to the richer engine already built in app.py to avoid
duplicating logic and to guarantee the cosine-similarity + keyword-match
+ trending-boost scoring is always used.
"""


def get_recommendations(preferences, profile=None, limit=6):
    """
    Thin wrapper that calls the full recommendation engine in app.py.
    Having a separate service module keeps imports clean while reusing
    the well-tested engine.
    """
    # Import inside function to avoid circular-import at module load time
    from app import get_recommendations as _engine

    # Merge user profile style tags into preferences
    if profile and profile.style_tags:
        existing = preferences.get("style_tags", "")
        merged = ", ".join(filter(None, [existing, profile.style_tags]))
        preferences = {**preferences, "style_tags": merged}

    return _engine(preferences, limit=limit)
