import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { API_BASE } from '../App';
import './Dashboard.css';

const Dashboard = () => {
  const [trendingStyles, setTrendingStyles] = useState([]);
  const [favoriteOutfits, setFavoriteOutfits] = useState([]);
  const [recentConversations, setRecentConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch trending styles
      const trendsRes = await fetch(`${API_BASE}/api/outfits/trending?limit=4`);
      if (trendsRes.ok) {
        const trends = await trendsRes.json();
        setTrendingStyles(trends);
      }

      // Fetch favorites
      const favsRes = await fetch(`${API_BASE}/api/favorites`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (favsRes.ok) {
        const favs = await favsRes.json();
        setFavoriteOutfits(favs);
      }

      // Fetch conversations
      const convsRes = await fetch(`${API_BASE}/api/conversations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (convsRes.ok) {
        const convs = await convsRes.json();
        setRecentConversations(convs.slice(0, 3));
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const trendingStylesData = [
    { id: 1, name: 'Quiet Luxury', percentage: 95, image: 'https://images.unsplash.com/photo-1539533057592-4d14fc9d4a91?w=200' },
    { id: 2, name: 'Coastal Grandmother', percentage: 88, image: 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=200' },
    { id: 3, name: 'Dark Academia', percentage: 82, image: 'https://images.unsplash.com/photo-1434598747652-e7ad8d3b3b5f?w=200' },
    { id: 4, name: 'Athleisure', percentage: 78, image: 'https://images.unsplash.com/photo-1506629082632-401d5d59a368?w=200' }
  ];

  return (
    <div className="dashboard">
      <Navbar />
      
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="header-content">
            <h1>Welcome back! ✨</h1>
            <p>Discover personalized fashion recommendations tailored to your style</p>
          </div>
          <Link to="/ai-stylist" className="cta-button">
            <span>Chat with AI Stylist</span>
            <span className="arrow">→</span>
          </Link>
        </div>

        {/* AI Stylist Section */}
        <section className="dashboard-section">
          <div className="section-card ai-stylist-card">
            <div className="ai-icon">🤖</div>
            <h2>AI Stylist</h2>
            <p>Get personalized recommendations based on your preferences</p>
            <Link to="/ai-stylist" className="section-btn">
              Start Styling
            </Link>
          </div>
        </section>

        {/* Trending Styles */}
        <section className="dashboard-section">
          <div className="section-header">
            <h2>Trending Styles</h2>
            <a href="#" className="view-all">View More →</a>
          </div>
          <div className="trending-grid">
            {trendingStylesData.map(style => (
              <div key={style.id} className="trending-item">
                <div className="trending-image">
                  <img src={style.image} alt={style.name} />
                  <div className="trending-overlay">
                    <span className="trending-percentage">{style.percentage}%</span>
                  </div>
                </div>
                <h3>{style.name}</h3>
                <div className="trending-bar">
                  <div className="bar-fill" style={{ width: `${style.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Favorite Outfits */}
        {favoriteOutfits.length > 0 && (
          <section className="dashboard-section">
            <div className="section-header">
              <h2>Your Favorite Outfits</h2>
              <Link to="/collection" className="view-all">View All →</Link>
            </div>
            <div className="outfits-grid">
              {favoriteOutfits.slice(0, 3).map(favorite => (
                <div key={favorite.id} className="outfit-card">
                  <div className="outfit-image">
                    <img src={favorite.outfit.image_url} alt={favorite.outfit.name} />
                  </div>
                  <div className="outfit-info">
                    <h3>{favorite.outfit.name}</h3>
                    <p className="outfit-tags">{favorite.outfit.style_tags}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Recent Conversations */}
        {recentConversations.length > 0 && (
          <section className="dashboard-section">
            <div className="section-header">
              <h2>Recent Conversations</h2>
              <Link to="/ai-stylist" className="view-all">View All →</Link>
            </div>
            <div className="conversations-list">
              {recentConversations.map(conv => (
                <div key={conv.id} className="conversation-item">
                  <div className="conv-icon">💬</div>
                  <div className="conv-content">
                    <h3>{conv.title}</h3>
                    <p className="conv-date">
                      {new Date(conv.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className="conv-messages">{conv.message_count} messages</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
