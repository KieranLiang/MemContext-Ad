import { useNavigate, useLocation } from 'react-router-dom';
import './FloatingNav.css';

interface FloatingNavProps {
  onLogout: () => void;
}

export default function FloatingNav({ onLogout }: FloatingNavProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="floating-nav-capsule">
      <button
        className={`nav-capsule-item ${isActive('/chat') ? 'active' : ''}`}
        onClick={() => navigate('/chat')}
        data-tooltip="聊天"
        aria-label="Chat"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>
      <button
        className={`nav-capsule-item ${isActive('/memory') ? 'active' : ''}`}
        onClick={() => navigate('/memory')}
        data-tooltip="记忆"
        aria-label="Memory"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 5a3 3 0 1 0-5.997.142 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588 4 4 0 0 0 7.636 2.106 3.2 3.2 0 0 0 .164-.546c.087-.27.13-.554.13-.846V5Z"></path>
          <path d="M12 5a3 3 0 1 1 5.997.142 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588 4 4 0 0 1-7.636 2.106 3.2 3.2 0 0 1-.164-.546A3.2 3.2 0 0 1 12 18V5Z"></path>
          <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"></path>
          <path d="M17.599 6.5a3 3 0 0 0 .399-1.375"></path>
          <path d="M6.003 5.125a3 3 0 0 0 .399 1.375"></path>
          <path d="M3.477 10.896a4 4 0 0 1 .585-.396"></path>
          <path d="M19.938 10.5a4 4 0 0 1 .585.396"></path>
          <path d="M6 18a4 4 0 0 1-1.967-.516"></path>
          <path d="M19.967 17.484A4 4 0 0 1 18 18"></path>
        </svg>
      </button>
      <div className="nav-capsule-divider"></div>
      <button
        className="nav-capsule-item"
        onClick={onLogout}
        data-tooltip="退出"
        aria-label="Logout"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
      </button>
    </div>
  );
}
