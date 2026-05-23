import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { API_BASE } from '../App';
import './Collection.css';

const Collection = () => {
  const [favorites, setFavorites] = useState([]);
  const [allOutfits, setAllOutfits] = useState([]);
  const [activeTab, setActiveTab] = useState('favorites');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (activeTab === 'favorites') {
      fetchFavorites();
    } else {
      fetchAllOutfits(page);
    }
  }, [activeTab, page]);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/favorites`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setFavorites(data);
      }
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllOutfits = async (pageNum) => {
    try {
      setLoading(true);
      const response = await fetch(
        `API_BASE/api/outfits?page=${pageNum}&per_page=12`
      );
      if (response.ok) {
        const data = await response.json();
        setAllOutfits(data.outfits);
        setTotalPages(data.pages);
      }
    } catch (error) {
      console.error('Failed to fetch outfits:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (outfitId) => {
    try {
      const isFavorited = favorites.some(f => f.outfit.id === outfitId);
      
      if (isFavorited) {
        const response = await fetch(
          `API_BASE/api/favorites/${outfitId}`,
          {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );
        if (response.ok) {
          setFavorites(favorites.filter(f => f.outfit.id !== outfitId));
        }
      } else {
        const response = await fetch(`${API_BASE}/api/favorites`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ outfit_id: outfitId })
        });
        if (response.ok) {
          const newFav = await response.json();
          setFavorites([newFav, ...favorites]);
        }
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const isFavorited = (outfitId) => {
    return favorites.some(f => f.outfit.id === outfitId);
  };

  const displayData = activeTab === 'favorites' ? favorites.map(f => ({ ...f.outfit, favorite_id: f.id })) : allOutfits;

  return (
    <div className="collection">
      <Navbar />
      
      <div className="collection-container">
        <div className="collection-header">
          <div>
            <h1>Your Collection</h1>
            <p>Build and manage your personalized fashion collection</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="collection-tabs">
          <button
            className={`tab ${activeTab === 'favorites' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('favorites');
              setPage(1);
            }}
          >
            <span>❤️</span> Favorites ({favorites.length})
          </button>
          <button
            className={`tab ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('all');
              setPage(1);
            }}
          >
            <span>🎨</span> All Outfits
          </button>
        </div>

        {/* Outfits Grid */}
        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading outfits...</p>
          </div>
        ) : displayData.length > 0 ? (
          <>
            <div className="outfits-grid">
              {displayData.map(outfit => (
                <div key={outfit.id} className="outfit-card">
                  <div className="outfit-image-container">
                    <img src={outfit.image_url} alt={outfit.name} />
                    <button
                      className={`favorite-btn ${isFavorited(outfit.id) ? 'favorited' : ''}`}
                      onClick={() => toggleFavorite(outfit.id)}
                      title={isFavorited(outfit.id) ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      <span>{isFavorited(outfit.id) ? '❤️' : '🤍'}</span>
                    </button>
                    <div className="outfit-overlay">
                      <div className="overlay-content">
                        <h3>{outfit.name}</h3>
                      </div>
                    </div>
                  </div>
                  <div className="outfit-details">
                    <h3>{outfit.name}</h3>
                    <p className="outfit-tags">{outfit.style_tags}</p>
                    <div className="outfit-meta">
                      {outfit.occasion && (
                        <span className="meta-tag occasion">{outfit.occasion}</span>
                      )}
                      {outfit.season && (
                        <span className="meta-tag season">{outfit.season}</span>
                      )}
                    </div>
                    {outfit.description && (
                      <p className="outfit-description">{outfit.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {activeTab === 'all' && totalPages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => setPage(prev => Math.max(1, prev - 1))}
                  disabled={page === 1}
                >
                  ← Previous
                </button>
                <span className="page-info">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={page === totalPages}
                >
                  Next →
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <h2>No outfits yet</h2>
            <p>
              {activeTab === 'favorites'
                ? 'Start exploring and add outfits to your favorites!'
                : 'No outfits available.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Collection;
