import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import MemoryPage from './pages/MemoryPage';
import './App.css';

// 配置 marked
import { marked } from 'marked';
marked.setOptions({
  breaks: true,
  gfm: true,
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  // 检查是否已登录（从 sessionStorage）
  useEffect(() => {
    const savedSessionId = sessionStorage.getItem('sessionId');
    const savedUserId = sessionStorage.getItem('userId');
    if (savedSessionId && savedUserId) {
      setSessionId(savedSessionId);
      setUserId(savedUserId);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (sessionId: string, userId: string) => {
    setSessionId(sessionId);
    setUserId(userId);
    setIsAuthenticated(true);
    sessionStorage.setItem('sessionId', sessionId);
    sessionStorage.setItem('userId', userId);
  };

  const handleLogout = () => {
    setSessionId(null);
    setUserId(null);
    setIsAuthenticated(false);
    sessionStorage.removeItem('sessionId');
    sessionStorage.removeItem('userId');
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/chat" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/chat"
          element={
            isAuthenticated ? (
              <ChatPage userId={userId!} sessionId={sessionId!} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/memory"
          element={
            isAuthenticated ? (
              <MemoryPage userId={userId!} sessionId={sessionId!} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="/" element={<Navigate to={isAuthenticated ? '/chat' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
