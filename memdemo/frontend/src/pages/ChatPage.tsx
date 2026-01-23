import { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import FloatingNav from '../components/FloatingNav';
import ChatHeader from '../components/ChatHeader';
import ChatWelcome from '../components/ChatWelcome';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import AdRecommendations from '../components/AdRecommendations';
import { useChatStream } from '../hooks/useSSE';
import './ChatPage.css';

interface ChatPageProps {
  userId: string;
  sessionId: string;
  onLogout: () => void;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
  ads?: any[];
}

export default function ChatPage({ userId, sessionId, onLogout }: ChatPageProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentResponse, setCurrentResponse] = useState('');
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage, isStreaming, error } = useChatStream();

  useEffect(() => {
    // 当有消息时，切换到聊天模式
    if (messages.length > 0) {
      document.body.classList.add('chat-active');
    } else {
      document.body.classList.remove('chat-active');
    }
  }, [messages]);

  useEffect(() => {
    // column-reverse 时最新消息在顶部，滚动到顶部让新消息显示、老消息上移消失
    if (messages.length > 0) {
      const scrollToTop = () => {
        const area = document.getElementById('chat-content-area');
        if (area) {
          area.scrollTop = 0;
        }
      };
      // 等 React 渲染完成后再滚动
      const id = setTimeout(scrollToTop, 0);
      return () => clearTimeout(id);
    }
  }, [messages.length]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    // 如果是第一条消息，触发下移动画
    if (isFirstMessage) {
      setIsFirstMessage(false);
    }

    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setCurrentResponse('');

    const botMessageId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      {
        id: botMessageId,
        text: '',
        sender: 'bot' as const,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);

    let accumulatedResponse = '';

    // 发送消息并接收流式响应
    await sendMessage(
      { message: text.trim(), user_id: userId },
      (chunk) => {
        accumulatedResponse += chunk;
        setCurrentResponse(accumulatedResponse);
        // 更新机器人消息
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId ? { ...msg, text: accumulatedResponse } : msg
          )
        );
      },
      (ads) => {
        // 更新机器人消息，添加广告推荐
        if (ads && ads.length > 0) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === botMessageId ? { ...msg, ads: ads } : msg
            )
          );
        }
      }
    );

    setCurrentResponse('');
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="chat-page-wrapper">
      <ChatHeader userId={userId} />
      <FloatingNav onLogout={onLogout} />
      <div id="chat-content-area" className={`chat-content-area ${hasMessages ? 'has-messages' : ''} ${isFirstMessage ? 'initial-state' : ''}`}>
        {!hasMessages ? (
          <div className="chat-initial-container">
            <div className="chat-messages-container">
              <ChatWelcome />
            </div>
            <div className="chat-input-container centered">
              <ChatInput onSend={handleSend} disabled={isStreaming} />
            </div>
          </div>
        ) : (
          <div className="chat-messages-container" id="chat-messages-container">
            {[...messages].reverse().map((msg, index) => {
              const originalIndex = messages.length - 1 - index;
              const isLastBotMessage = msg.sender === 'bot' && originalIndex === messages.length - 1;
              const showLoading = isStreaming && isLastBotMessage && !msg.text;
              return (
                <div key={msg.id} className="message-with-ads">
                  <ChatMessage
                    message={msg.sender === 'bot' && msg.text ? marked.parse(msg.text) : msg.text}
                    sender={msg.sender}
                    isStreaming={showLoading}
                  />
                  {msg.sender === 'bot' && msg.ads && msg.ads.length > 0 && (
                    <AdRecommendations ads={msg.ads} />
                  )}
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      {hasMessages && (
        <div className="chat-input-container fixed">
          <ChatInput onSend={handleSend} disabled={isStreaming} showSuggestions={false} />
        </div>
      )}
      {error && (
        <div className="error-toast" role="alert">
          {error}
        </div>
      )}
    </div>
  );
}
