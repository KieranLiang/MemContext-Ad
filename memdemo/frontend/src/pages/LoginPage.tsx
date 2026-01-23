import { useState } from 'react';
import { initMemory } from '../services/api';
import './LoginPage.css';

interface LoginPageProps {
  onLogin: (sessionId: string, userId: string) => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [userId, setUserId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await initMemory({ user_id: userId.trim() });
      if (response.success && response.session_id && response.user_id) {
        onLogin(response.session_id, response.user_id);
      } else {
        setError(response.error || '登录失败');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '网络错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-section">
        {/* Top Navigation Buttons */}
        <div className="nav-buttons">
          <a
            href="https://baijia.online/homepage/index.html"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-button"
            aria-label="Contact us"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
          </a>
          <a
            href="https://github.com/EricSun0218/MemContext-Ad"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-button"
            aria-label="View on GitHub"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
          </a>
        </div>

        {/* Brand Section */}
        <div className="login-brand">
          <div className="login-brand-icon" style={{ fontSize: '48px' }}>
            🐬
          </div>
          <h1 className="login-brand-title">Demo：基于Memory的个性化广告推荐</h1>
          <p className="login-brand-subtitle">A memory operation system for personalized AI</p>
        </div>

        {/* Form Section */}
        <div className="login-form-section">
          <h2 className="login-title">Welcome Back</h2>
          <p className="login-subtitle">Enter your User ID to access the memory system</p>

          <form onSubmit={handleSubmit} aria-label="Login form">
            <div className="form-group">
              <label htmlFor="userId" className="form-label">User ID</label>
              <input
                type="text"
                className="form-control"
                id="userId"
                name="userId"
                placeholder="Enter your User ID"
                required
                autoComplete="username"
                autoFocus
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                aria-describedby="userId-help"
                aria-required="true"
              />
              <div className="form-text" id="userId-help">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                Your unique identifier
              </div>
            </div>

            {error && (
              <div className="error-message" role="alert">
                {error}
              </div>
            )}

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <div className="spinner-small"></div>
                  Initializing...
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                  Continue
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
