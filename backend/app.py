import os
import json
import csv
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from dotenv import load_dotenv
# NLP and recommendation logic defined locally below



load_dotenv()

app = Flask(__name__)

# ==================== CONFIG ====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stylist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-dev-key-change-in-prod')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# ==================== GEMINI SETUP ====================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
gemini_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini API connected successfully")
    except Exception as e:
        print(f"⚠️  Gemini API error: {e}")
else:
    print("⚠️  No GEMINI_API_KEY found — AI chat will use fallback mode")


# ==================== MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), default='')
    last_name = db.Column(db.String(80), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile = db.relationship('UserProfile', uselist=False, backref='user', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', cascade='all, delete-orphan')
    favorites = db.relationship('FavoriteOutfit', backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat()
        }


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    primary_style = db.Column(db.String(50), default='Minimalist')
    color_palette = db.Column(db.String(255), default='Neutrals')
    preferred_fit = db.Column(db.String(50), default='Tailored')
    body_type = db.Column(db.String(50), default='')
    skin_tone = db.Column(db.String(50), default='')
    style_tags = db.Column(db.String(255), default='elegant, chic')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'primary_style': self.primary_style or 'Minimalist',
            'color_palette': self.color_palette or 'Neutrals',
            'preferred_fit': self.preferred_fit or 'Tailored',
            'body_type': self.body_type or '',
            'skin_tone': self.skin_tone or '',
            'style_tags': self.style_tags or ''
        }


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), default='New Chat')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan', order_by='Message.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'message_count': len(self.messages)
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }


class Outfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500), default='')
    style_tags = db.Column(db.String(255), default='')
    colors = db.Column(db.String(255), default='')
    occasion = db.Column(db.String(100), default='')
    season = db.Column(db.String(50), default='all-season')
    body_type = db.Column(db.String(50), default='all')
    skin_tone = db.Column(db.String(50), default='all')
    description = db.Column(db.Text, default='')
    trending_score = db.Column(db.Float, default=0.5)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url,
            'style_tags': self.style_tags,
            'colors': self.colors,
            'occasion': self.occasion,
            'season': self.season,
            'body_type': self.body_type,
            'skin_tone': self.skin_tone,
            'description': self.description,
            'trending_score': self.trending_score
        }


class FavoriteOutfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    outfit_id = db.Column(db.Integer, db.ForeignKey('outfit.id'), nullable=False)
    outfit = db.relationship('Outfit')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'outfit': self.outfit.to_dict(),
            'created_at': self.created_at.isoformat()
        }


# ==================== RECOMMENDATION ENGINE ====================

STYLE_VECTORS = {
    'elegant':      [1.0, 0.8, 0.2, 0.1, 0.3, 0.0, 0.5],
    'chic':         [0.9, 0.8, 0.3, 0.2, 0.4, 0.1, 0.6],
    'formal':       [1.0, 0.9, 0.1, 0.0, 0.2, 0.0, 0.4],
    'business':     [0.9, 0.8, 0.2, 0.1, 0.3, 0.1, 0.5],
    'professional': [0.9, 0.8, 0.2, 0.1, 0.3, 0.1, 0.5],
    'smart':        [0.8, 0.7, 0.4, 0.3, 0.5, 0.2, 0.6],
    'modern':       [0.7, 0.6, 0.5, 0.4, 0.6, 0.3, 0.7],
    'classic':      [0.8, 0.7, 0.3, 0.2, 0.3, 0.1, 0.4],
    'minimal':      [0.7, 0.6, 0.3, 0.2, 0.2, 0.1, 0.3],
    'casual':       [0.2, 0.2, 0.9, 0.8, 0.7, 0.8, 0.5],
    'relaxed':      [0.1, 0.2, 1.0, 0.9, 0.8, 0.9, 0.4],
    'vacation':     [0.2, 0.3, 0.9, 1.0, 0.8, 0.9, 0.6],
    'breeze':       [0.2, 0.3, 0.8, 0.9, 0.7, 0.8, 0.5],
    'trendy':       [0.6, 0.6, 0.7, 0.6, 0.8, 0.5, 0.9],
    'bold':         [0.7, 0.6, 0.6, 0.5, 0.9, 0.6, 0.8],
    'edgy':         [0.6, 0.5, 0.6, 0.5, 0.9, 0.6, 0.7],
    'romantic':     [0.8, 0.7, 0.5, 0.4, 0.6, 0.3, 0.7],
    'feminine':     [0.7, 0.7, 0.5, 0.4, 0.6, 0.4, 0.6],
    'bohemian':     [0.3, 0.4, 0.8, 0.7, 0.7, 0.8, 0.7],
    'vintage':      [0.7, 0.6, 0.4, 0.3, 0.5, 0.3, 0.5],
    'preppy':       [0.7, 0.6, 0.5, 0.3, 0.4, 0.3, 0.5],
    'sporty':       [0.3, 0.3, 0.8, 0.7, 0.7, 0.9, 0.6],
    'fun':          [0.4, 0.4, 0.8, 0.7, 0.8, 0.7, 0.8],
    'dark':         [0.6, 0.5, 0.4, 0.3, 0.8, 0.4, 0.5],
}

def get_style_vector(tags_string):
    """Convert comma-separated style tags into a numeric vector."""
    vec = np.zeros(7)
    if not tags_string:
        return vec
    tags = [t.strip().lower() for t in re.split(r'[,;]', tags_string) if t.strip()]
    count = 0
    for tag in tags:
        if tag in STYLE_VECTORS:
            vec += np.array(STYLE_VECTORS[tag])
            count += 1
    if count:
        vec /= count
    return vec


def keyword_match_score(user_prefs, outfit):
    """Add bonus points for direct keyword matches."""
    bonus = 0
    user_text = ' '.join([
        user_prefs.get('occasion', ''),
        user_prefs.get('style', ''),
        user_prefs.get('colors', ''),
        user_prefs.get('season', ''),
        user_prefs.get('raw_query', '')
    ]).lower()

    outfit_text = ' '.join([
        outfit.occasion or '',
        outfit.style_tags or '',
        outfit.colors or '',
        outfit.season or '',
        outfit.name or ''
    ]).lower()

    # Check each word from user input against outfit attributes
    for word in user_text.split():
        if len(word) > 3 and word in outfit_text:
            bonus += 8

    # Specific field matches get bigger bonus
    if user_prefs.get('occasion') and outfit.occasion:
        if user_prefs['occasion'].lower() in outfit.occasion.lower():
            bonus += 15
    if user_prefs.get('season') and outfit.season:
        if user_prefs['season'].lower() in outfit.season.lower():
            bonus += 10
    if user_prefs.get('colors') and outfit.colors:
        for color in user_prefs['colors'].split(','):
            if color.strip().lower() in outfit.colors.lower():
                bonus += 8

    return bonus


def get_recommendations(user_preferences, limit=5):
    """Full recommendation engine: cosine similarity + keyword matching + trending boost."""
    outfits = Outfit.query.all()
    if not outfits:
        return []

    # Build user vector from style tags + style field from Gemini
    combined_tags = ', '.join(filter(None, [
        user_preferences.get('style_tags', ''),
        user_preferences.get('style', ''),
    ]))
    user_vec = get_style_vector(combined_tags)

    results = []
    for outfit in outfits:
        outfit_vec = get_style_vector(outfit.style_tags)

        # Cosine similarity (0–100)
        if np.any(user_vec) and np.any(outfit_vec):
            sim = float(cosine_similarity(
                user_vec.reshape(1, -1),
                outfit_vec.reshape(1, -1)
            )[0][0]) * 100
        else:
            sim = 50  # neutral score when no preferences set

        # Keyword match bonus
        kw_bonus = keyword_match_score(user_preferences, outfit)

        # Trending score boost (0–10)
        trending_boost = (outfit.trending_score or 0.5) * 10

        # Final score (capped at 100)
        final_score = min(100, sim + kw_bonus + trending_boost)

        results.append({'outfit': outfit, 'score': final_score})

    results.sort(key=lambda x: x['score'], reverse=True)

    return [
        {
            'outfit': r['outfit'].to_dict(),
            'match_percentage': round(r['score'], 1)
        }
        for r in results[:limit]
    ]


# ==================== GEMINI AI CHAT ====================

def extract_preferences_with_gemini(user_message):
    """Use Gemini to extract structured fashion preferences from a natural language message."""
    if not gemini_model:
        # Fallback: basic keyword extraction without Gemini
        return fallback_preference_extraction(user_message)

    try:
        prompt = f"""You are a fashion AI assistant. A user sent this message:
"{user_message}"

Extract fashion preferences and return ONLY a valid JSON object (no markdown, no explanation):
{{
  "occasion": "formal | casual | business | evening | vacation | active | (empty string if not mentioned)",
  "style": "elegant | chic | smart | casual | trendy | bohemian | romantic | edgy | (empty string if not mentioned)",
  "colors": "comma-separated colors or empty string",
  "season": "spring | summer | fall | winter | all-season | (empty string if not mentioned)",
  "body_type": "body type if mentioned or empty string",
  "skin_tone": "skin tone if mentioned or empty string",
  "style_tags": "comma-separated style keywords extracted from the message",
  "ai_response": "A warm, helpful 1-2 sentence response acknowledging what the user wants and that you are finding recommendations"
}}"""

        response = gemini_model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if present
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        prefs = json.loads(text)
        prefs['raw_query'] = user_message
        return prefs

    except Exception as e:
        print(f"Gemini error: {e}")
        return fallback_preference_extraction(user_message)


def fallback_preference_extraction(user_message):
    """Rule-based fallback when Gemini is unavailable."""
    msg = user_message.lower()
    prefs = {'raw_query': user_message, 'style_tags': '', 'ai_response': ''}

    # Occasion detection
    if any(w in msg for w in ['formal', 'dinner', 'gala', 'ceremony', 'black tie']):
        prefs['occasion'] = 'formal'
        prefs['style_tags'] = 'elegant, chic, formal'
    elif any(w in msg for w in ['business', 'office', 'work', 'meeting', 'corporate']):
        prefs['occasion'] = 'business'
        prefs['style_tags'] = 'business, smart, professional'
    elif any(w in msg for w in ['wedding', 'party', 'event', 'cocktail']):
        prefs['occasion'] = 'evening'
        prefs['style_tags'] = 'elegant, chic, formal'
    elif any(w in msg for w in ['beach', 'vacation', 'holiday', 'resort', 'travel']):
        prefs['occasion'] = 'vacation'
        prefs['style_tags'] = 'vacation, relaxed, breeze'
    elif any(w in msg for w in ['gym', 'sport', 'workout', 'active', 'athletic']):
        prefs['occasion'] = 'active'
        prefs['style_tags'] = 'sporty, casual, modern'
    else:
        prefs['occasion'] = 'casual'
        prefs['style_tags'] = 'casual, smart, modern'

    # Style detection
    if any(w in msg for w in ['elegant', 'sophisticated', 'luxury', 'luxurious']):
        prefs['style'] = 'elegant'
    elif any(w in msg for w in ['casual', 'relaxed', 'comfortable', 'comfy']):
        prefs['style'] = 'casual'
    elif any(w in msg for w in ['trendy', 'fashionable', 'stylish', 'chic']):
        prefs['style'] = 'trendy'
    elif any(w in msg for w in ['bohemian', 'boho', 'vintage', 'retro']):
        prefs['style'] = 'bohemian'
    elif any(w in msg for w in ['minimal', 'minimalist', 'clean', 'simple']):
        prefs['style'] = 'minimal'

    # Season
    if any(w in msg for w in ['summer', 'hot', 'warm', 'sunny']):
        prefs['season'] = 'summer'
    elif any(w in msg for w in ['winter', 'cold', 'snow', 'cozy']):
        prefs['season'] = 'winter'
    elif any(w in msg for w in ['spring', 'fresh']):
        prefs['season'] = 'spring'
    elif any(w in msg for w in ['fall', 'autumn', 'autumn']):
        prefs['season'] = 'fall'

    # Colors
    colors_found = []
    for color in ['black', 'white', 'red', 'blue', 'navy', 'green', 'pink',
                  'beige', 'cream', 'gold', 'brown', 'gray', 'grey', 'purple']:
        if color in msg:
            colors_found.append(color)
    if colors_found:
        prefs['colors'] = ', '.join(colors_found)

    prefs['ai_response'] = f"I found some great {prefs.get('occasion', 'style')} outfit recommendations for you!"
    return prefs


def generate_ai_chat_response(user_message, recommendations, preferences):
    """Generate a conversational AI response using Gemini."""
    if not gemini_model:
        return preferences.get('ai_response') or f"Here are some {preferences.get('occasion', 'great')} outfit recommendations for you!"

    try:
        outfit_names = [r['outfit']['name'] for r in recommendations[:3]]
        prompt = f"""You are StyleSense, a friendly and knowledgeable AI fashion stylist.

User asked: "{user_message}"

You found these outfit recommendations: {', '.join(outfit_names)}

Write a warm, helpful, conversational response (2-3 sentences) that:
1. Acknowledges what the user is looking for
2. Briefly introduces the recommendations
3. Mentions one styling tip

Keep it friendly and fashion-forward. Do NOT use markdown formatting."""

        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini chat response error: {e}")
        return preferences.get('ai_response') or f"Here are some {preferences.get('occasion', 'great')} outfit recommendations for you!"


# ==================== SEED DATA ====================

SAMPLE_OUTFITS = [
    {
        'name': 'Elegant Evening',
        'image_url': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&q=80',
        'style_tags': 'elegant, chic, formal, romantic',
        'colors': 'black, gold, white',
        'occasion': 'evening, formal',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Sophisticated evening wear with flowing silhouette and elegant accessories. Perfect for galas and formal dinners.',
        'trending_score': 0.95
    },
    {
        'name': 'Smart Casual',
        'image_url': 'https://images.unsplash.com/photo-1552062407-c551eeda4921?w=600&q=80',
        'style_tags': 'casual, smart, modern, classic',
        'colors': 'navy, white, khaki, beige',
        'occasion': 'casual, business',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'The perfect blend of comfort and style. Great for day-to-night plans and social gatherings.',
        'trending_score': 0.88
    },
    {
        'name': 'Beach Resort',
        'image_url': 'https://images.unsplash.com/photo-1517635676447-30ab6d67d25b?w=600&q=80',
        'style_tags': 'vacation, relaxed, breeze, casual, fun',
        'colors': 'blue, white, pastel, coral',
        'occasion': 'vacation, casual',
        'season': 'summer',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Lightweight and breathable pieces in soft colours. Effortlessly chic for sunny weather and beach days.',
        'trending_score': 0.91
    },
    {
        'name': 'Business Power Look',
        'image_url': 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=600&q=80',
        'style_tags': 'business, professional, smart, formal, bold',
        'colors': 'navy, black, white, charcoal',
        'occasion': 'business, formal',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'A commanding office look that exudes confidence and professionalism. Sharp tailoring with modern touches.',
        'trending_score': 0.85
    },
    {
        'name': 'Quiet Luxury',
        'image_url': 'https://images.unsplash.com/photo-1539533057592-4d14fc9d4a91?w=600&q=80',
        'style_tags': 'elegant, minimal, chic, classic, modern',
        'colors': 'cream, beige, camel, ivory, white',
        'occasion': 'casual, business, evening',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Understated elegance with premium minimalist pieces. The art of looking expensive without trying.',
        'trending_score': 0.96
    },
    {
        'name': 'Coastal Grandmother',
        'image_url': 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=600&q=80',
        'style_tags': 'casual, relaxed, trendy, breeze, classic',
        'colors': 'blue, white, sand, linen, sky',
        'occasion': 'casual, vacation',
        'season': 'summer, spring',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Effortless coastal vibes with relaxed linen and breezy silhouettes. A timeless summer aesthetic.',
        'trending_score': 0.89
    },
    {
        'name': 'Dark Academia',
        'image_url': 'https://images.unsplash.com/photo-1434598747652-e7ad8d3b3b5f?w=600&q=80',
        'style_tags': 'classic, smart, vintage, dark, edgy, bold',
        'colors': 'black, brown, burgundy, forest green, camel',
        'occasion': 'casual, business',
        'season': 'fall, winter',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Moody, literary-inspired fashion. Dark tones meet structured layers for an intellectual aesthetic.',
        'trending_score': 0.83
    },
    {
        'name': 'Athleisure Edit',
        'image_url': 'https://images.unsplash.com/photo-1506629082632-401d5d59a368?w=600&q=80',
        'style_tags': 'casual, sporty, modern, trendy, fun',
        'colors': 'black, white, grey, neon, olive',
        'occasion': 'casual, active',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Activewear elevated with style. Comfortable enough for the gym, polished enough for everywhere else.',
        'trending_score': 0.86
    },
    {
        'name': 'Date Night Look',
        'image_url': 'https://images.unsplash.com/photo-1564598958223-4fbf27fef26f?w=600&q=80',
        'style_tags': 'elegant, romantic, chic, feminine, bold',
        'colors': 'red, black, gold, burgundy, rose',
        'occasion': 'evening, casual',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Romantic and effortlessly chic. Turn heads on any evening out with this confident, eye-catching look.',
        'trending_score': 0.90
    },
    {
        'name': 'Minimalist Chic',
        'image_url': 'https://images.unsplash.com/photo-1559831243-641fa84f62f0?w=600&q=80',
        'style_tags': 'minimal, chic, modern, clean, elegant',
        'colors': 'white, black, grey, stone, off-white',
        'occasion': 'casual, business',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Less is more. Clean lines, neutral tones, and perfectly chosen basics create a timeless, polished look.',
        'trending_score': 0.82
    },
    {
        'name': 'Bohemian Vibes',
        'image_url': 'https://images.unsplash.com/photo-1564379588828-fcd236b03c32?w=600&q=80',
        'style_tags': 'bohemian, casual, relaxed, vintage, fun, trendy',
        'colors': 'earthy, rust, sage, cream, terracotta',
        'occasion': 'casual, vacation',
        'season': 'spring, summer',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Free-spirited layers, earthy tones, and flowing fabrics. A carefree, artistic style for the adventurous soul.',
        'trending_score': 0.80
    },
    {
        'name': 'Office Chic',
        'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&q=80',
        'style_tags': 'business, chic, smart, elegant, professional, modern',
        'colors': 'grey, white, navy, blush, camel',
        'occasion': 'business, formal',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Polished, feminine, and professional. Combines structure with softness for the modern workplace.',
        'trending_score': 0.87
    },
    {
        'name': 'Summer Sundress',
        'image_url': 'https://images.unsplash.com/photo-1595853646649-bca3b0b04199?w=600&q=80',
        'style_tags': 'casual, fun, breeze, feminine, romantic, vacation',
        'colors': 'pastel, floral, white, yellow, sky blue',
        'occasion': 'casual, vacation',
        'season': 'summer, spring',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Light, breezy, and effortlessly pretty. The ultimate warm-weather dress for sunshine and good vibes.',
        'trending_score': 0.79
    },
    {
        'name': 'Edgy Street Style',
        'image_url': 'https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=600&q=80',
        'style_tags': 'edgy, bold, trendy, casual, dark, modern',
        'colors': 'black, grey, white, silver, red',
        'occasion': 'casual, evening',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Rebellious edge meets urban cool. Statement pieces and attitude make this look unforgettable.',
        'trending_score': 0.75
    },
    {
        'name': 'Preppy Classic',
        'image_url': 'https://images.unsplash.com/photo-1518520113411-fbce202b1cb0?w=600&q=80',
        'style_tags': 'preppy, classic, smart, clean, casual',
        'colors': 'navy, white, red, green, pastel',
        'occasion': 'casual, business',
        'season': 'all-season',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Timeless Ivy League energy. Crisp, clean, and always put-together with a collegiate twist.',
        'trending_score': 0.77
    },
    {
        'name': 'Festival Fit',
        'image_url': 'https://images.unsplash.com/photo-1571844307880-751a962ff3ae?w=600&q=80',
        'style_tags': 'bold, fun, trendy, bohemian, casual, feminine',
        'colors': 'multicolor, bright, gold, neon, pastels',
        'occasion': 'casual, vacation',
        'season': 'summer, spring',
        'body_type': 'all',
        'skin_tone': 'all',
        'description': 'Vibrant, expressive, and full of personality. Made for music festivals and carefree summer moments.',
        'trending_score': 0.73
    },
]


def seed_outfits():
    """Add sample outfits to the database if empty."""
    if Outfit.query.count() == 0:
        for data in SAMPLE_OUTFITS:
            outfit = Outfit(**data)
            db.session.add(outfit)
        db.session.commit()
        print(f"✅ Seeded {len(SAMPLE_OUTFITS)} outfits")
    else:
        print(f"✅ Database already has {Outfit.query.count()} outfits")


# ==================== AUTH ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'error': 'Email, username and password are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'This username is already taken'}), 409

    user = User(
        email=data['email'].strip().lower(),
        username=data['username'].strip(),
        first_name=data.get('first_name', '').strip(),
        last_name=data.get('last_name', '').strip()
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    profile = UserProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({'message': 'Account created successfully', 'access_token': token, 'user': user.to_dict()}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email'].strip().lower()).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Incorrect email or password'}), 401

    token = create_access_token(identity=user.id)
    return jsonify({'message': 'Login successful', 'access_token': token, 'user': user.to_dict()}), 200


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200


# ==================== PROFILE ROUTES ====================

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    profile = UserProfile.query.filter_by(user_id=get_jwt_identity()).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    return jsonify(profile.to_dict()), 200


@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    data = request.get_json()
    profile = UserProfile.query.filter_by(user_id=get_jwt_identity()).first()
    if not profile:
        profile = UserProfile(user_id=get_jwt_identity())
        db.session.add(profile)

    fields = ['primary_style', 'color_palette', 'preferred_fit', 'body_type', 'skin_tone', 'style_tags']
    for field in fields:
        if field in data:
            setattr(profile, field, data[field])

    profile.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(profile.to_dict()), 200


# ==================== CONVERSATION ROUTES ====================

@app.route('/api/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    convs = Conversation.query.filter_by(user_id=get_jwt_identity()).order_by(
        Conversation.created_at.desc()
    ).all()
    return jsonify([c.to_dict() for c in convs]), 200


@app.route('/api/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    data = request.get_json() or {}
    conv = Conversation(user_id=get_jwt_identity(), title=data.get('title', 'New Chat'))
    db.session.add(conv)
    db.session.commit()
    return jsonify(conv.to_dict()), 201


@app.route('/api/conversations/<int:conv_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=get_jwt_identity()).first()
    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404
    db.session.delete(conv)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


@app.route('/api/conversations/<int:conv_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=get_jwt_identity()).first()
    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404
    msgs = Message.query.filter_by(conversation_id=conv_id).order_by(Message.created_at).all()
    return jsonify([m.to_dict() for m in msgs]), 200


@app.route('/api/conversations/<int:conv_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conv_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    user_text = (data.get('content') or '').strip()
    if not user_text:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Save user message
    user_msg = Message(conversation_id=conv_id, role='user', content=user_text)
    db.session.add(user_msg)

    # Update conversation title from first message
    if not conv.messages or len(conv.messages) == 0:
        conv.title = user_text[:80]

    db.session.commit()

    # Pull user profile to enrich preferences
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    profile_tags = profile.style_tags if profile else ''

    # Extract structured preferences via Gemini (or fallback)
    # Extract preferences
    try:
        preferences = extract_preferences_with_gemini(user_text)
    except Exception as e:
        print("Preference extraction error:", e)
        preferences = {}

    print("Preferences:", preferences)

    # Merge user profile style tags into preferences for personalisation
    if profile and profile.style_tags:
        existing_tags = preferences.get('style_tags', '')
        merged_tags = ', '.join(filter(None, [existing_tags, profile.style_tags]))
        preferences['style_tags'] = merged_tags
    if profile and profile.skin_tone:
        preferences.setdefault('skin_tone', profile.skin_tone)
    if profile and profile.body_type:
        preferences.setdefault('body_type', profile.body_type)

    # Generate recommendations using the local cosine-similarity engine
    try:
        recommendations = get_recommendations(preferences, limit=5)
    except Exception as e:
        print("Recommendation error:", e)
        recommendations = []

    # Generate AI response
    try:
        ai_text = generate_ai_chat_response(
            user_text,
            recommendations,
            preferences
        )
    except Exception as e:
        print("Response generation error:", e)
        ai_text = preferences.get('ai_response') or "Here are some great outfit recommendations for you!"

    assistant_payload = {
        "text": ai_text,
        "recommendations": recommendations
    }

    assistant_msg = Message(
        conversation_id=conv_id,
        role='assistant',
        content=json.dumps(assistant_payload)
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        'user_message': user_msg.to_dict(),
        'assistant_message': assistant_msg.to_dict()
    }), 201


# ==================== OUTFIT ROUTES ====================

@app.route('/api/outfits', methods=['GET'])
def get_outfits():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    paginated = Outfit.query.order_by(Outfit.trending_score.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'outfits': [o.to_dict() for o in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@app.route('/api/outfits/trending', methods=['GET'])
def get_trending():
    limit = request.args.get('limit', 4, type=int)
    outfits = Outfit.query.order_by(Outfit.trending_score.desc()).limit(limit).all()
    return jsonify([o.to_dict() for o in outfits]), 200


@app.route('/api/outfits/recommendations', methods=['POST'])
@jwt_required()
def outfit_recommendations():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    prefs = {
        'style_tags': profile.style_tags if profile else '',
        'occasion': data.get('occasion', ''),
        'colors': data.get('colors', ''),
        'season': data.get('season', ''),
        'style': data.get('style', '')
    }
    recs = get_recommendations(prefs, limit=data.get('limit', 5))
    return jsonify({'recommendations': recs}), 200


# ==================== FAVORITES ROUTES ====================

@app.route('/api/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    favs = FavoriteOutfit.query.filter_by(user_id=get_jwt_identity()).order_by(
        FavoriteOutfit.created_at.desc()
    ).all()
    return jsonify([f.to_dict() for f in favs]), 200


@app.route('/api/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    data = request.get_json()
    outfit_id = data.get('outfit_id')
    outfit = Outfit.query.get(outfit_id)
    if not outfit:
        return jsonify({'error': 'Outfit not found'}), 404

    existing = FavoriteOutfit.query.filter_by(user_id=get_jwt_identity(), outfit_id=outfit_id).first()
    if existing:
        return jsonify({'error': 'Already in favorites'}), 409

    fav = FavoriteOutfit(user_id=get_jwt_identity(), outfit_id=outfit_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.to_dict()), 201


@app.route('/api/favorites/<int:outfit_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(outfit_id):
    fav = FavoriteOutfit.query.filter_by(user_id=get_jwt_identity(), outfit_id=outfit_id).first()
    if not fav:
        return jsonify({'error': 'Not in favorites'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': 'Removed from favorites'}), 200


# ==================== MISC ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'gemini': 'connected' if gemini_model else 'fallback mode',
        'outfits': Outfit.query.count()
    }), 200


# ==================== STARTUP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_outfits()
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, port=port)
