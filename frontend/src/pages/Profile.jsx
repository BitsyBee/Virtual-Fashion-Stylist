import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../App';
import './Profile.css';

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  const [profile, setProfile] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    primary_style: '',
    color_palette: '',
    preferred_fit: '',
    body_type: '',
    skin_tone: '',
    style_tags: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData(data);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const response = await fetch(`${API_BASE}/api/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const updated = await response.json();
        setProfile(updated);
        setEditMode(false);
        alert('Profile updated successfully!');
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="profile">
        <Navbar />
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile">
      <Navbar />
      
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar">👤</div>
          <div className="profile-info">
            <h1>{user?.first_name || user?.username}</h1>
            <p>{user?.email}</p>
          </div>
        </div>

        <div className="profile-content">
          {/* Style Preferences */}
          <section className="profile-section">
            <div className="section-header">
              <h2>Your Style Profile</h2>
              {!editMode && (
                <button
                  className="edit-btn"
                  onClick={() => setEditMode(true)}
                >
                  Edit Profile
                </button>
              )}
            </div>

            {editMode ? (
              <form onSubmit={handleSaveProfile} className="profile-form">
                <div className="form-group">
                  <label htmlFor="primary_style">Primary Style</label>
                  <input
                    id="primary_style"
                    name="primary_style"
                    type="text"
                    value={formData.primary_style}
                    onChange={handleChange}
                    placeholder="e.g., Minimalist, Classic, Modern"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="color_palette">Color Palette</label>
                  <input
                    id="color_palette"
                    name="color_palette"
                    type="text"
                    value={formData.color_palette}
                    onChange={handleChange}
                    placeholder="e.g., Neutrals, Pastels, Bold"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="preferred_fit">Preferred Fit</label>
                  <input
                    id="preferred_fit"
                    name="preferred_fit"
                    type="text"
                    value={formData.preferred_fit}
                    onChange={handleChange}
                    placeholder="e.g., Tailored, Relaxed, Fitted"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="body_type">Body Type</label>
                  <input
                    id="body_type"
                    name="body_type"
                    type="text"
                    value={formData.body_type}
                    onChange={handleChange}
                    placeholder="e.g., Pear, Apple, Hourglass"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="skin_tone">Skin Tone</label>
                  <input
                    id="skin_tone"
                    name="skin_tone"
                    type="text"
                    value={formData.skin_tone}
                    onChange={handleChange}
                    placeholder="e.g., Warm, Cool, Neutral"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="style_tags">Style Tags (comma-separated)</label>
                  <textarea
                    id="style_tags"
                    name="style_tags"
                    value={formData.style_tags}
                    onChange={handleChange}
                    placeholder="e.g., elegant, casual, chic, trendy"
                    rows="3"
                  />
                </div>

                <div className="form-actions">
                  <button
                    type="submit"
                    className="save-btn"
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    className="cancel-btn"
                    onClick={() => {
                      setEditMode(false);
                      setFormData(profile);
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="profile-display">
                <div className="profile-item">
                  <span className="label">Primary Style</span>
                  <span className="value">{profile?.primary_style || 'Not set'}</span>
                </div>

                <div className="profile-item">
                  <span className="label">Color Palette</span>
                  <span className="value">{profile?.color_palette || 'Not set'}</span>
                </div>

                <div className="profile-item">
                  <span className="label">Preferred Fit</span>
                  <span className="value">{profile?.preferred_fit || 'Not set'}</span>
                </div>

                <div className="profile-item">
                  <span className="label">Body Type</span>
                  <span className="value">{profile?.body_type || 'Not set'}</span>
                </div>

                <div className="profile-item">
                  <span className="label">Skin Tone</span>
                  <span className="value">{profile?.skin_tone || 'Not set'}</span>
                </div>

                <div className="profile-item">
                  <span className="label">Style Tags</span>
                  <span className="value">{profile?.style_tags || 'Not set'}</span>
                </div>
              </div>
            )}
          </section>

          {/* Account Information */}
          <section className="profile-section">
            <h2>Account Information</h2>
            <div className="profile-display">
              <div className="profile-item">
                <span className="label">Email</span>
                <span className="value">{user?.email}</span>
              </div>

              <div className="profile-item">
                <span className="label">Username</span>
                <span className="value">{user?.username}</span>
              </div>

              <div className="profile-item">
                <span className="label">First Name</span>
                <span className="value">{user?.first_name || 'Not set'}</span>
              </div>

              <div className="profile-item">
                <span className="label">Last Name</span>
                <span className="value">{user?.last_name || 'Not set'}</span>
              </div>

              <div className="profile-item">
                <span className="label">Member Since</span>
                <span className="value">
                  {new Date(user?.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </section>

          {/* Danger Zone */}
          <section className="profile-section danger-zone">
            <h2>Actions</h2>
            <button className="logout-btn" onClick={handleLogout}>
              <span>⎘</span> Logout
            </button>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Profile;
