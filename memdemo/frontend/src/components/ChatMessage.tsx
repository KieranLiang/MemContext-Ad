import './ChatMessage.css';

interface ChatMessageProps {
  message: string;
  sender: 'user' | 'bot';
  timestamp?: string;
  isStreaming?: boolean;
}

export default function ChatMessage({ message, sender, timestamp, isStreaming }: ChatMessageProps) {
  const isUser = sender === 'user';

  return (
    <div className={`message-wrapper ${sender}-message`}>
      {!isUser && (
        <div className="message-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
        </div>
      )}
      <div className="message-bubble">
        <div className="message-content">
          {isUser ? (
            message
          ) : (
            <>
              {message ? (
                <div dangerouslySetInnerHTML={{ __html: message }} />
              ) : (
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
