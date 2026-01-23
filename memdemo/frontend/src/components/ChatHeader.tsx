import './ChatHeader.css';

interface ChatHeaderProps {
  userId: string;
}

export default function ChatHeader({ userId }: ChatHeaderProps) {
  // 从 userId 生成用户头像的字母
  const userInitial = userId.charAt(0).toUpperCase();

  return (
    <div className="chat-header">
      <div className="chat-header-left">
        <div className="chat-header-logo" style={{ fontSize: '24px' }}>
          🐬
        </div>
        <span className="chat-header-title">Demo：基于Memory的个性化广告推荐</span>
      </div>
      <div className="chat-header-right">
        <div className="chat-header-user">
          <div className="chat-header-user-avatar">
            {userInitial}
          </div>
        </div>
      </div>
    </div>
  );
}
