import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Landing.css';

const Landing = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="landing">
      {/* Navbar */}
      <nav className={`landing-nav ${scrolled ? 'scrolled' : ''}`}>
        <div className="landing-nav-inner">
          <div className="landing-logo">
            <span className="logo-star">✦</span>
            Style Sense
          </div>
          <div className="landing-nav-links">
            <a href="#home">Home</a>
            <a href="#features">AI Stylist</a>
            <a href="#collection">Collection</a>
            <a href="#preview">Preview</a>
          </div>
          <Link to="/login" className="landing-login-btn">
            <span>⊙</span> Login
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero" id="home">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-star">✦</span>
            Your Virtual Fashion Stylist
          </div>
          <h1 className="hero-title">
            Style <span className="gold-text">Sense</span>
          </h1>
          <h2 className="hero-subtitle">Your Virtual Fashion Stylist</h2>
          <p className="hero-desc">
            Discover personalized outfit recommendations tailored to your style,
            preferences, and every occasion. Let AI bring out the best in you.
          </p>
          <Link to="/register" className="hero-cta">
            Start Styling &nbsp;→
          </Link>
        </div>
        <div className="hero-image">
          <img
            src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=90"
            alt="Fashion Model"
          />
          <div className="hero-image-overlay"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="features-inner">
          <div className="section-label">✦ What We Offer</div>
          <h2>AI-Powered Fashion Intelligence</h2>
          <p className="section-sub">
            Our system learns your style, understands your needs, and delivers
            outfit recommendations that feel personally curated — every time.
          </p>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI Stylist Chat</h3>
              <p>
                Talk naturally to your AI stylist. Ask for outfit ideas for any
                occasion and get intelligent, personalized responses instantly.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">✨</div>
              <h3>Smart Recommendations</h3>
              <p>
                Our recommendation engine uses cosine similarity and weighted
                scoring to rank outfits by how well they match your profile.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👗</div>
              <h3>Style Profiling</h3>
              <p>
                Set your body type, skin tone, colour palette, and preferred fit.
                The more we know, the better we style you.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">❤️</div>
              <h3>Curated Collection</h3>
              <p>
                Save your favourite outfits, browse trending styles, and build
                a personal wardrobe collection you can revisit anytime.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Trend Tracking</h3>
              <p>
                Stay on top of the latest fashion movements — from Quiet Luxury
                to Dark Academia — ranked by real trend scores.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Private & Secure</h3>
              <p>
                Your style profile and conversations are protected with JWT
                authentication and secure password hashing.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works" id="preview">
        <div className="how-inner">
          <div className="section-label">✦ Simple Process</div>
          <h2>How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">01</div>
              <h3>Create Your Profile</h3>
              <p>Sign up and tell us about your style preferences, body type, and colour palette.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">02</div>
              <h3>Chat with AI Stylist</h3>
              <p>Type any fashion request in plain language and our AI understands your needs.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">03</div>
              <h3>Get Recommendations</h3>
              <p>Receive personalised outfit suggestions with match percentages and style explanations.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">04</div>
              <h3>Save Favourites</h3>
              <p>Build your collection by saving the outfits you love to revisit them any time.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Trending Styles Preview */}
      <section className="trending-preview" id="collection">
        <div className="trending-inner">
          <div className="section-label">✦ Right Now</div>
          <h2>Trending Styles</h2>
          <div className="trending-cards">
            {[
              { name: 'Quiet Luxury', pct: 95, img: 'https://images.unsplash.com/photo-1539533057592-4d14fc9d4a91?w=400' },
              { name: 'Coastal Grandmother', pct: 88, img: 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400' },
              { name: 'Dark Academia', pct: 82, img: 'https://images.unsplash.com/photo-1434598747652-e7ad8d3b3b5f?w=400' },
              { name: 'Athleisure', pct: 78, img: 'https://images.unsplash.com/photo-1506629082632-401d5d59a368?w=400' },
            ].map((style) => (
              <div className="trending-card" key={style.name}>
                <div className="trending-card-img">
                  <img src={style.img} alt={style.name} />
                  <span className="trending-pct">{style.pct}%</span>
                </div>
                <div className="trending-card-info">
                  <h3>{style.name}</h3>
                  <div className="trend-bar">
                    <div className="trend-fill" style={{ width: `${style.pct}%` }}></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-inner">
          <span className="cta-badge">✦ Get Started Free</span>
          <h2>Ready to Elevate Your Style?</h2>
          <p>Join thousands of fashion-forward individuals who let AI guide their wardrobe decisions.</p>
          <div className="cta-buttons">
            <Link to="/register" className="cta-primary">Create Free Account →</Link>
            <Link to="/login" className="cta-secondary">Sign In</Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-inner">
          <div className="footer-logo">
            <span className="logo-star">✦</span> Style Sense
          </div>
          <p>Your AI-Powered Virtual Fashion Stylist</p>
          <div className="footer-links">
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </div>
          <p className="footer-copy">© 2026 StyleSense. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
