import { useState, useRef, useEffect } from 'react';
import './ChatInput.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  showSuggestions?: boolean;
}

const SUGGESTIONS = [
  '最近有哪些电影上线？',
  '明天中午吃什么呢？',
  '朋友过生日送什么礼物？',
];

export default function ChatInput({ onSend, disabled, showSuggestions: externalShowSuggestions }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [internalShowSuggestions, setInternalShowSuggestions] = useState(true);
  const showSuggestions = externalShowSuggestions !== undefined ? externalShowSuggestions : internalShowSuggestions;
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.max(48, Math.min(textareaRef.current.scrollHeight, 200)) + 'px';
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      setInternalShowSuggestions(false);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSuggestionClick = (text: string) => {
    setMessage(text);
    setInternalShowSuggestions(false);
    textareaRef.current?.focus();
  };

  return (
    <div className="chat-input-area">
      <form className="chat-input-wrapper" onSubmit={handleSubmit}>
        <div className="chat-input-content">
          <textarea
            ref={textareaRef}
            className="chat-input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="今天想聊点什么？"
            rows={2}
            autoComplete="off"
          />
        </div>
        <div className="chat-input-controls">
          <div className="chat-input-left-controls">
            <button
              type="button"
              className="chat-input-attach-btn"
              aria-label="Attach file"
              title="Attach file"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
            <button
              type="button"
              className="chat-input-tools-btn"
              aria-label="Tools"
              title="Tools"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"></path>
              </svg>
              工具
            </button>
          </div>
          <div className="chat-input-right-controls">
            <button
              type="button"
              className="chat-input-mode-btn"
              aria-label="Thinking mode"
              title="Thinking mode"
            >
              思考
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
            <button
              type="button"
              className="chat-input-voice-btn"
              aria-label="Voice input"
              title="Voice input"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
              </svg>
            </button>
            <button
              type="submit"
              className="chat-input-send-btn"
              disabled={!message.trim() || disabled}
              aria-label="Send message"
              title="Send (Enter)"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      </form>
      {showSuggestions && (
        <div className="chat-suggestions">
          {SUGGESTIONS.map((suggestion, index) => (
            <button
              key={index}
              className="chat-suggestion-chip"
              onClick={() => handleSuggestionClick(suggestion)}
              type="button"
            >
              <div className="chat-suggestion-chip-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2v4m0 12v4M5.64 5.64l2.83 2.83m7.06 7.06l2.83 2.83M2 12h4m12 0h4M5.64 18.36l2.83-2.83m7.06-7.06l2.83-2.83"></path>
                </svg>
              </div>
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
