# StyleSense - AI Virtual Fashion Stylist

A full-stack web application that provides personalized fashion recommendations using artificial intelligence and recommendation algorithms.

## Features

✨ **AI-Powered Recommendations**
- Chat with AI stylist using natural language
- Get personalized outfit suggestions
- Recommendations based on style preferences, occasion, colors, season, body type, and skin tone

👤 **User Authentication**
- Secure user registration and login
- JWT-based authentication
- User profile management

💬 **Conversational Interface**
- Chat history management
- Multiple conversations support
- Real-time message streaming

👗 **Outfit Collection**
- Browse trending styles
- Save favorite outfits
- View outfit details with match percentages
- Filter by occasion and season

🎨 **Personalization**
- Update style preferences
- Body type and skin tone matching
- Color palette selection
- Style tags management

## Tech Stack

### Frontend
- React 18
- React Router DOM
- Vite
- CSS3

### Backend
- Flask (Python)
- SQLAlchemy ORM
- JWT Authentication
- Scikit-learn (Recommendation Engine)
- Gemini API Integration

### Database
- SQLite

## Project Structure

```
StyleSense/
├── app.py                    # Flask main application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # Reusable components
│   │   ├── context/        # Auth context
│   │   ├── App.jsx         # Main App component
│   │   ├── App.css         # Global styles
│   │   └── index.jsx       # Entry point
│   ├── index.html          # HTML template
│   ├── vite.config.js      # Vite configuration
│   ├── package.json        # Dependencies
│   └── .env.example        # Frontend env variables
└── data/
    └── outfits.csv         # Sample outfit dataset
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to project directory:**
   ```bash
   cd StyleSense
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add:
   ```
   FLASK_ENV=development
   JWT_SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key
   ```

5. **Initialize database:**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```
   
   Or run:
   ```bash
   flask shell
   >>> from app import init_db
   >>> init_db()
   ```

6. **Run Flask server:**
   ```bash
   python app.py
   ```
   
   Server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```
   
   Frontend will run on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### User Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

### Conversations
- `GET /api/conversations` - Get all conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}/messages` - Get messages
- `POST /api/conversations/{id}/messages` - Send message

### Outfits
- `GET /api/outfits` - Get all outfits (paginated)
- `GET /api/outfits/trending` - Get trending styles
- `POST /api/outfits/recommendations` - Get recommendations

### Favorites
- `GET /api/favorites` - Get favorite outfits
- `POST /api/favorites` - Add to favorites
- `DELETE /api/favorites/{outfit_id}` - Remove from favorites

## Configuration

### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Generate an API key
3. Add to `.env`: `GEMINI_API_KEY=your-key`

### Database
The application uses SQLite by default. Data is stored in `stylist.db`.

To use a different database, modify `SQLALCHEMY_DATABASE_URI` in `app.py`.

## Usage

1. **Register/Login**
   - Create an account or login with existing credentials

2. **Update Profile**
   - Go to Profile page
   - Fill in your style preferences
   - Save changes

3. **Chat with AI Stylist**
   - Go to AI Stylist page
   - Type your fashion request
   - Receive personalized recommendations

4. **Save Favorites**
   - Click heart icon on outfits
   - View saved outfits in Collection

## Recommendation Engine

The system uses a multi-factor recommendation approach:

1. **Content-Based Filtering**
   - Analyzes outfit features
   - Matches with user preferences

2. **Cosine Similarity**
   - Calculates style embeddings
   - Ranks outfits by similarity score

3. **Weighted Scoring**
   - Combines multiple factors
   - Occasion matching
   - Color harmony
   - Seasonal suitability
   - Body type compatibility
   - Skin tone matching

4. **Gemini API Integration**
   - Extracts user preferences from natural language
   - Converts user input to structured preferences

## Testing

### Test User Credentials
After initialization, you can register a new account or use test credentials:

```
Email: test@example.com
Password: testpassword123
```

### Sample Requests

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

**Send Message:**
```bash
curl -X POST http://localhost:5000/api/conversations/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"content":"Suggest an outfit for a formal dinner"}'
```

## Troubleshooting

### Port Already in Use
- Flask: Change port in `app.py` → `app.run(port=5001)`
- React: Kill process on port 3000 or change in `vite.config.js`

### CORS Errors
- Ensure Flask-CORS is installed
- Check API URL in frontend matches backend URL

### Gemini API Errors
- Verify API key is valid
- Check API quota limits
- Ensure internet connection

### Database Errors
- Delete `stylist.db` and reinitialize
- Check database URI in `.env`

## File Structure Explanation

### Backend
- `app.py` - Main Flask application with all routes and models
- `requirements.txt` - Python package dependencies
- `.env.example` - Environment variables template

### Frontend
- `src/pages/` - Full page components (Login, Dashboard, etc.)
- `src/components/` - Reusable components (Navbar, etc.)
- `src/context/` - React context for state management
- `App.jsx` - Main application component with routing
- `App.css` - Global application styles

## Performance Tips

1. **Frontend Optimization**
   - Lazy load images
   - Cache API responses
   - Use React.memo for components

2. **Backend Optimization**
   - Index database queries
   - Cache outfit dataset
   - Implement pagination

3. **API Performance**
   - Use gzip compression
   - Implement caching headers
   - Optimize Gemini API calls

## Security Considerations

1. ✅ JWT authentication for API endpoints
2. ✅ Password hashing with Werkzeug
3. ✅ CORS protection
4. ⚠️ Use environment variables for secrets
5. ⚠️ Implement rate limiting in production
6. ⚠️ Use HTTPS in production
7. ⚠️ Add input validation

## Future Enhancements

- [ ] Avatar-based outfit visualization
- [ ] Advanced filtering options
- [ ] User-to-user style sharing
- [ ] Style trend analytics
- [ ] Social features (comments, ratings)
- [ ] Mobile app version
- [ ] Advanced search functionality
- [ ] Personal stylist matching
- [ ] Outfit planning calendar
- [ ] Integration with shopping platforms

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - feel free to use this project

## Support

For issues, questions, or suggestions:
1. Check existing documentation
2. Review API endpoints
3. Check troubleshooting section
4. Create an issue with details

## Credits

- Built with React, Flask, and modern web technologies
- Uses Gemini API for natural language processing
- Scikit-learn for recommendation algorithms
- Unsplash for sample outfit images

---

**StyleSense** - Your AI-Powered Virtual Fashion Stylist 👗✨
