# StyleSense - Complete Setup Guide

## Quick Start (5 minutes)

### 1. Backend Setup

```bash
# Navigate to project
cd StyleSense

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your keys
# GEMINI_API_KEY=your-key-here
# JWT_SECRET_KEY=your-secret-key

# Initialize database
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     from app import Outfit
...     # Outfits will be created from CSV on first run
>>> exit()

# Start backend
python app.py
```

Backend runs on: **http://localhost:5000**

### 2. Frontend Setup

```bash
# In another terminal, navigate to frontend
cd StyleSense/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

## Complete Project Files

### Backend Structure
```
StyleSense/
├── app.py                          # Main Flask app
├── requirements.txt                # Dependencies
├── .env.example                    # Env template
├── .env                            # Your config (create this)
├── stylist.db                      # SQLite database (auto-created)
└── data/
    └── outfits.csv                 # Outfit dataset
```

### Frontend Structure
```
StyleSense/frontend/
├── src/
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Login.jsx
│   │   ├── Auth.css
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Dashboard.css
│   │   ├── AIStyler.jsx
│   │   ├── AIStyler.css
│   │   ├── Collection.jsx
│   │   ├── Collection.css
│   │   ├── Profile.jsx
│   │   └── Profile.css
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── Navbar.css
│   │   └── ProtectedRoute.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── App.jsx
│   ├── App.css
│   └── index.jsx
├── index.html
├── vite.config.js
├── package.json
└── .env                            # Frontend config
```

## Features Checklist

### ✅ Authentication
- [x] User registration with validation
- [x] Secure login with JWT
- [x] Protected routes
- [x] Logout functionality
- [x] Token persistence

### ✅ User Profile
- [x] View profile information
- [x] Edit style preferences
- [x] Update body type and skin tone
- [x] Manage color palette and style tags

### ✅ AI Stylist Chat
- [x] Real-time chat interface
- [x] Message history
- [x] Multiple conversations
- [x] Natural language preference extraction
- [x] Personalized recommendations

### ✅ Recommendation Engine
- [x] Content-based filtering
- [x] Cosine similarity calculation
- [x] Weighted scoring
- [x] Multi-factor matching
- [x] Match percentage display

### ✅ Outfit Collection
- [x] Browse all outfits
- [x] Save favorites
- [x] Remove favorites
- [x] View outfit details
- [x] Pagination support
- [x] Trending styles section

### ✅ Dashboard
- [x] Welcome message
- [x] Trending styles display
- [x] Recent conversations
- [x] Favorite outfits preview
- [x] Quick access buttons

## API Endpoints Reference

### 🔐 Authentication Endpoints

**Register**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}

Response: {
  "access_token": "jwt_token",
  "user": { ... }
}
```

**Login**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: {
  "access_token": "jwt_token",
  "user": { ... }
}
```

**Get Current User**
```bash
GET /api/auth/me
Authorization: Bearer {token}

Response: {
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  ...
}
```

### 👤 Profile Endpoints

**Get Profile**
```bash
GET /api/profile
Authorization: Bearer {token}

Response: {
  "primary_style": "Minimalist",
  "color_palette": "Neutrals",
  "preferred_fit": "Tailored",
  ...
}
```

**Update Profile**
```bash
PUT /api/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "primary_style": "Elegant",
  "color_palette": "Pastels",
  "preferred_fit": "Relaxed",
  "body_type": "Pear",
  "skin_tone": "Warm",
  "style_tags": "elegant,chic,modern"
}
```

### 💬 Conversation Endpoints

**Get Conversations**
```bash
GET /api/conversations
Authorization: Bearer {token}

Response: [
  {
    "id": 1,
    "title": "Formal Event",
    "created_at": "2024-01-15T10:00:00",
    "message_count": 5
  },
  ...
]
```

**Create Conversation**
```bash
POST /api/conversations
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "New Chat"
}

Response: {
  "id": 2,
  "title": "New Chat",
  "created_at": "2024-01-15T11:00:00",
  "message_count": 0
}
```

**Send Message**
```bash
POST /api/conversations/{conversation_id}/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "Suggest an outfit for a formal dinner"
}

Response: {
  "user_message": { ... },
  "assistant_message": {
    "content": {
      "text": "I found great recommendations...",
      "recommendations": [ ... ]
    }
  }
}
```

### 👗 Outfit Endpoints

**Get All Outfits**
```bash
GET /api/outfits?page=1&per_page=12

Response: {
  "outfits": [ ... ],
  "total": 50,
  "pages": 5,
  "current_page": 1
}
```

**Get Trending Outfits**
```bash
GET /api/outfits/trending?limit=4

Response: [ ... ]
```

**Get Recommendations**
```bash
POST /api/outfits/recommendations
Authorization: Bearer {token}
Content-Type: application/json

{
  "occasion": "formal",
  "colors": "black,gold",
  "season": "winter",
  "limit": 5
}

Response: {
  "recommendations": [
    {
      "outfit": { ... },
      "match_percentage": 95.5
    },
    ...
  ]
}
```

### ❤️ Favorites Endpoints

**Get Favorites**
```bash
GET /api/favorites
Authorization: Bearer {token}

Response: [
  {
    "id": 1,
    "outfit": { ... },
    "created_at": "2024-01-15T10:00:00"
  },
  ...
]
```

**Add Favorite**
```bash
POST /api/favorites
Authorization: Bearer {token}
Content-Type: application/json

{
  "outfit_id": 5
}

Response: {
  "id": 1,
  "outfit": { ... },
  "created_at": "2024-01-15T10:00:00"
}
```

**Remove Favorite**
```bash
DELETE /api/favorites/{outfit_id}
Authorization: Bearer {token}

Response: {
  "message": "Removed from favorites"
}
```

## Environment Variables

### Backend (.env)
```
FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET_KEY=your-super-secret-key-change-this
GEMINI_API_KEY=your-gemini-api-key
SQLALCHEMY_DATABASE_URI=sqlite:///stylist.db
```

### Frontend (.env - optional)
```
VITE_API_URL=http://localhost:5000
```

## Getting Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Paste in `.env` file as `GEMINI_API_KEY`

## Running in Production

### Backend Production Build
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend Production Build
```bash
cd frontend

# Build for production
npm run build

# Output in frontend/dist
# Serve with: npx serve dist
```

## Database Schema

### Users Table
```
id: Integer (Primary Key)
email: String (Unique)
username: String (Unique)
password_hash: String
first_name: String
last_name: String
created_at: DateTime
```

### User Profiles Table
```
id: Integer (Primary Key)
user_id: Integer (Foreign Key)
primary_style: String
color_palette: String
preferred_fit: String
body_type: String
skin_tone: String
style_tags: String
updated_at: DateTime
```

### Conversations Table
```
id: Integer (Primary Key)
user_id: Integer (Foreign Key)
title: String
created_at: DateTime
```

### Messages Table
```
id: Integer (Primary Key)
conversation_id: Integer (Foreign Key)
role: String (user/assistant)
content: Text
created_at: DateTime
```

### Outfits Table
```
id: Integer (Primary Key)
name: String
image_url: String
style_tags: String
colors: String
occasion: String
season: String
body_type: String
skin_tone: String
description: Text
trending_score: Float
```

### Favorites Table
```
id: Integer (Primary Key)
user_id: Integer (Foreign Key)
outfit_id: Integer (Foreign Key)
created_at: DateTime
```

## Troubleshooting

### "Module not found" Error
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### Port Already in Use
```bash
# Find process on port 5000
lsof -i :5000
# Kill it
kill -9 <PID>

# Or change port in app.py
app.run(port=5001)
```

### CORS Errors
- Ensure `Flask-CORS` is installed
- Check frontend API URL matches backend
- Check backend is running on port 5000

### Database Locked
```bash
# Remove database and reinitialize
rm stylist.db
python app.py
```

### JWT Errors
- Verify token is sent in Authorization header
- Check token hasn't expired
- Verify JWT_SECRET_KEY matches between requests

## Testing Credentials

After running the app, register a test account:

**Email:** test@stylesense.com
**Password:** Test123!@#

Or use curl:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@stylesense.com",
    "username":"testuser",
    "password":"Test123!@#",
    "first_name":"Test",
    "last_name":"User"
  }'
```

## Performance Tips

1. **Database**
   - Use indexes on foreign keys
   - Cache frequent queries
   - Implement pagination

2. **API**
   - Enable gzip compression
   - Implement caching headers
   - Rate limiting for APIs

3. **Frontend**
   - Lazy load images
   - Code splitting for routes
   - Minimize CSS/JS

4. **Gemini API**
   - Cache preference extractions
   - Batch requests when possible
   - Handle rate limits

## Security Checklist

- [x] JWT authentication
- [x] Password hashing
- [x] CORS configuration
- [x] Input validation
- [ ] HTTPS in production
- [ ] Rate limiting
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection (React escapes by default)
- [ ] CSRF tokens (for POST requests)
- [ ] Environment variables for secrets

## Support & Debugging

### Enable Debug Logging
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Connectivity
```bash
curl http://localhost:5000/api/health
# Should return: {"status":"ok"}
```

### View Database
```bash
# Using SQLite CLI
sqlite3 stylist.db
> .tables
> SELECT * FROM user;
> .exit
```

### React DevTools
- Install React DevTools browser extension
- Inspect component props and state
- Track component renders

---

**StyleSense** is ready to deploy! 🎉

For more help, check the main README.md or create an issue.
