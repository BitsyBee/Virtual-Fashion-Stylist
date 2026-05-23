import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">✨</span>
          StyleSense
        </Link>

        <div className="nav-menu">
          <Link to="/dashboard" className="nav-link">Home</Link>
          <Link to="/ai-stylist" className="nav-link">AI Stylist</Link>
          <Link to="/collection" className="nav-link">Collection</Link>
          <Link to="/profile" className="nav-link">Profile</Link>
        </div>

        <div className="nav-user">
          {user && (
            <>
              <span className="user-name">{user.username}</span>
              <button onClick={handleLogout} className="logout-btn">
                <span>⎘</span>
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
