import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { API_BASE } from '../App';
import './AIStyler.css';

const SUGGESTIONS = [
  "Suggest an outfit for a formal dinner",
  "I need a casual summer look",
  "Recommend elegant black outfits",
  "Business casual outfit ideas",
  "What should I wear to a beach wedding?",
  "Help me create a capsule wardrobe",
];

const AIStyler = () => {
  const [conversations, setConversations] = useState([]);
  const [currentConv, setCurrentConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingConvs, setLoadingConvs] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const token = localStorage.getItem('access_token');

  useEffect(() => { fetchConversations(); }, []);
  useEffect(() => { scrollToBottom(); }, [messages, sending]);
  useEffect(() => {
    if (currentConv) fetchMessages(currentConv.id);
  }, [currentConv?.id]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const authHeaders = () => ({
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  });

  const fetchConversations = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/conversations`, { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
        if (data.length > 0) setCurrentConv(data[0]);
      }
    } catch (e) { console.error(e); }
    finally { setLoadingConvs(false); }
  };

  const fetchMessages = async (convId) => {
    setLoadingMsgs(true);
    setMessages([]);
    try {
      const res = await fetch(`${API_BASE}/api/conversations/${convId}/messages`, { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setMessages(data.map(parseMessage));
      }
    } catch (e) { console.error(e); }
    finally { setLoadingMsgs(false); }
  };

  const parseMessage = (msg) => {
    if (msg.role === 'assistant') {
      try {
        const parsed = typeof msg.content === 'string' ? JSON.parse(msg.content) : msg.content;
        return { ...msg, parsed };
      } catch { return { ...msg, parsed: { text: msg.content, recommendations: [] } }; }
    }
    return msg;
  };

  const createConversation = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/conversations`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ title: 'New Chat' })
      });
      if (res.ok) {
        const conv = await res.json();
        setConversations(prev => [conv, ...prev]);
        setCurrentConv(conv);
        setMessages([]);
        inputRef.current?.focus();
      }
    } catch (e) { console.error(e); }
  };

  const deleteConversation = async (e, convId) => {
    e.stopPropagation();
    try {
      await fetch(`${API_BASE}/api/conversations/${convId}`, {
        method: 'DELETE', headers: authHeaders()
      });
      const updated = conversations.filter(c => c.id !== convId);
      setConversations(updated);
      if (currentConv?.id === convId) {
        setCurrentConv(updated[0] || null);
        setMessages([]);
      }
    } catch (e) { console.error(e); }
  };

  const sendMessage = async (text) => {
  const content = (text || input).trim();

  if (!content || sending) return;

  let activeConv = currentConv;

  // Create conversation automatically if none exists
  if (!activeConv) {
    try {
      const res = await fetch(`${API_BASE}/api/conversations`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ title: content.slice(0, 50) })
      });

      if (res.ok) {
        const conv = await res.json();

        setConversations(prev => [conv, ...prev]);
        setCurrentConv(conv);

        activeConv = conv;
      } else {
        alert("Failed to create conversation");
        return;
      }
    } catch (err) {
      console.error(err);
      return;
    }
  }

  setInput('');
  setSending(true);

  const tempUserMsg = {
    id: Date.now(),
    role: 'user',
    content,
    created_at: new Date().toISOString()
  };

  setMessages(prev => [...prev, tempUserMsg]);

  try {
    const res = await fetch(
      `${API_BASE}/api/conversations/${activeConv.id}/messages`,
      {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ content })
      }
    );

    if (res.ok) {
      const data = await res.json();

      setMessages(prev => [
        ...prev.filter(m => m.id !== tempUserMsg.id),
        data.user_message,
        parseMessage(data.assistant_message)
      ]);

      setConversations(prev =>
        prev.map(c =>
          c.id === activeConv.id
            ? {
                ...c,
                title: content.slice(0, 60),
                message_count: (c.message_count || 0) + 2
              }
            : c
        )
      );
    } else {
      alert("Failed to send message");
    }
  } catch (err) {
    console.error(err);
  } finally {
    setSending(false);
  }
};

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="ai-styler">
      <Navbar />
      <div className="styler-container">

        {/* ── SIDEBAR ── */}
        <aside className="styler-sidebar">
          <button className="new-chat-btn" onClick={createConversation}>
            <span>＋</span> New Chat
          </button>

          <div className="sidebar-section-label">Recent Conversations</div>

          {loadingConvs ? (
            <div className="sidebar-loading"><div className="mini-spinner" /></div>
          ) : conversations.length === 0 ? (
            <p className="sidebar-empty">No conversations yet. Start a new chat!</p>
          ) : (
            conversations.map(conv => (
              <div
                key={conv.id}
                className={`sidebar-conv ${currentConv?.id === conv.id ? 'active' : ''}`}
                onClick={() => setCurrentConv(conv)}
              >
                <div className="conv-body">
                  <span className="conv-title">{conv.title || 'New Chat'}</span>
                  <span className="conv-time">
                    {new Date(conv.created_at).toLocaleDateString()}
                  </span>
                </div>
                <button
                  className="conv-delete"
                  onClick={(e) => deleteConversation(e, conv.id)}
                  title="Delete"
                >×</button>
              </div>
            ))
          )}
        </aside>

        {/* ── MAIN CHAT ── */}
        <main className="styler-main">

          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="chat-avatar">🤖</div>
              <div>
                <h2>AI Fashion Stylist</h2>
                <p className="chat-status">
                  <span className="status-dot" />
                  Online · Powered by Gemini AI
                </p>
              </div>
            </div>
            <div className="chat-header-right">
              <Link to="/collection" className="header-link-btn">View Collection →</Link>
            </div>
          </div>

          {/* Messages */}
          <div className="messages-area">
            {loadingMsgs ? (
              <div className="chat-center-state">
                <div className="spinner" />
                <p>Loading messages…</p>
              </div>
            ) : messages.length === 0 ? (
              /* Empty state */
              <div className="chat-empty-state">
                <div className="empty-avatar">✨</div>
                <h3>Hello! I'm your AI Fashion Stylist</h3>
                <p>Tell me about your style, occasion, or what look you're going for and I'll find perfect outfit recommendations for you.</p>
                <div className="suggestions-grid">
                  {SUGGESTIONS.map(s => (
                    <button key={s} className="suggestion-chip" onClick={() => sendMessage(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* Message list */
              <>
                {messages.map((msg, i) => (
                  <div key={msg.id || i} className={`message-row ${msg.role}`}>
                    <div className="message-avatar-icon">
                      {msg.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="message-bubble-wrap">
                      {msg.role === 'user' ? (
                        <div className="bubble user-bubble">{msg.content}</div>
                      ) : (
                        <div className="bubble assistant-bubble">
                          {/* AI text */}
                          {msg.parsed?.text && (
                            <p className="ai-text">{msg.parsed.text}</p>
                          )}
                          {/* Outfit recommendation cards */}
                          {msg.parsed?.recommendations?.length > 0 && (
                            <div className="rec-cards">
                              {msg.parsed.recommendations.map((rec, ri) => (
                                <OutfitCard key={ri} rec={rec} token={token} />
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                      <span className="msg-time">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}

                {/* Typing indicator while waiting */}
                {sending && (
                  <div className="message-row assistant">
                    <div className="message-avatar-icon">🤖</div>
                    <div className="message-bubble-wrap">
                      <div className="bubble assistant-bubble typing-bubble">
                        <span /><span /><span />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input */}
          <div className="chat-input-area">
          
            <div className="input-row">
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask your AI stylist anything… e.g. 'Suggest a formal dinner outfit'"
                disabled={sending}
                rows={1}
              />
              <button
                className="send-btn"
                onClick={() => sendMessage()}
                disabled={sending || !input.trim()}
              >
                {sending ? <div className="mini-spinner white" /> : '↑'}
              </button>
            </div>
            <p className="input-hint">Press Enter to send · Shift+Enter for new line</p>
          </div>
        </main>
      </div>
    </div>
  );
};

/* ── OUTFIT CARD COMPONENT ── */
const OutfitCard = ({ rec, token }) => {
  const [favorited, setFavorited] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleFavorite = async () => {
    setLoading(true);
    try {
      if (favorited) {
        await fetch(`${API_BASE}/api/favorites/${rec.outfit.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setFavorited(false);
      } else {
        const res = await fetch(`${API_BASE}/api/favorites`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ outfit_id: rec.outfit.id })
        });
        if (res.ok || res.status === 409) setFavorited(true);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const pct = Math.min(99, Math.max(60, rec.match_percentage));

  return (
    <div className="rec-card">
      <div className="rec-img-wrap">
        <img src={rec.outfit.image_url} alt={rec.outfit.name} loading="lazy" />
        <div className="rec-match-badge">{pct}% match</div>
        <button
          className={`rec-fav-btn ${favorited ? 'faved' : ''}`}
          onClick={toggleFavorite}
          disabled={loading}
          title={favorited ? 'Remove from favorites' : 'Save to favorites'}
        >
          {favorited ? '❤️' : '🤍'}
        </button>
      </div>
      <div className="rec-info">
        <h4>{rec.outfit.name}</h4>
        <p className="rec-desc">{rec.outfit.description}</p>
        <div className="rec-tags">
          {(rec.outfit.style_tags || '').split(',').slice(0, 3).map(tag => (
            <span key={tag} className="rec-tag">{tag.trim()}</span>
          ))}
        </div>
        {rec.outfit.occasion && (
          <p className="rec-occasion">📍 {rec.outfit.occasion}</p>
        )}
      </div>
    </div>
  );
};

export default AIStyler;
