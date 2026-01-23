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
    // 当消息列表更新时，智能滚动到最新的用户消息
    if (messages.length > 0) {
      const lastUserMsgIndex = messages.findLastIndex(m => m.sender === 'user');
      
      if (lastUserMsgIndex !== -1) {
        const msgId = messages[lastUserMsgIndex].id;
        // 使用 setTimeout 确保 DOM 已经渲染更新
        setTimeout(() => {
          const msgElement = document.querySelector(`[data-message-id="${msgId}"]`);
          const container = document.getElementById('chat-content-area');
          
          if (msgElement && container) {
            // 手动计算滚动位置：
            // 目标位置 = 元素相对于容器的偏移 - Header高度及缓冲(80px)
            const elementTop = (msgElement as HTMLElement).offsetTop;
            // 注意：因为 container 有 padding-top: 64px，内容的起始 offsetTop 可能会包含这个。
            // 简单的做法是：滚动到 elementTop - 80。
            // 如果容器是 flex 布局且 justify-content 变化，offsetTop 可能会变，但此时已经是 flex-start。
            
            container.scrollTo({
              top: elementTop - 84, // 64px Header + 20px Gap
              behavior: 'smooth'
            });
          } else {
             messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
          }
        }, 50);
      } else {
         messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [messages.length]);

  // 监听流式输出时的自动滚动（保持在底部，或者保持当前可视区域？）
  // 如果用户希望“新消息在最上方”，那么流式输出时，应该保持用户消息在顶部，内容向下生长。
  // 只要不手动去滚到底部，内容生长会自动撑开高度，而视口位置不变（前提是scrollTop位置正确）。
  // 所以这里不需要额外的 useEffect 来监听 currentResponse 滚动到底部，
  // 除非内容超出了屏幕高度，用户可能想看最新的字。
  // 但需求是“旧消息移出屏幕”，说明重点是头部对齐。
  
  // 仅当是第一条消息生成过程中，为了防止过长内容看不见，可以微调，但通常 block: 'start' 已经够了。

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
            {messages.map((msg, index) => {
              const isLastBotMessage = msg.sender === 'bot' && index === messages.length - 1;
              const showLoading = isStreaming && isLastBotMessage && !msg.text;
              return (
                <div key={msg.id} className="message-with-ads" data-message-id={msg.id}>
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
