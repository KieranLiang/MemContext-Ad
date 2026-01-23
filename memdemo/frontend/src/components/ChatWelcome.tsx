import './ChatWelcome.css';

export default function ChatWelcome() {
  return (
    <div className="chat-welcome-section">
      <div className="chat-welcome-greeting">
        <div className="chat-welcome-logo">
          <div className="chat-welcome-logo-inner" style={{ fontSize: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            🐬
          </div>
        </div>
        <div className="chat-welcome-text">
          <h1 className="chat-welcome-title">Demo：基于Memory的个性化广告推荐</h1>
        </div>
      </div>
    </div>
  );
}
