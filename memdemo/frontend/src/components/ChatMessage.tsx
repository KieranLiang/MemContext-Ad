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
        <div className="message-avatar" style={{ fontSize: '20px' }}>
          🐬
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
