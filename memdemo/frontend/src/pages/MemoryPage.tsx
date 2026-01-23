import { useState, useEffect } from 'react';
import FloatingNav from '../components/FloatingNav';
import { getMemoryState, triggerAnalysis, getPersonalityAnalysis, clearMemory, importConversations } from '../services/api';
import type { MemoryStateResponse } from '../types/api';
import './MemoryPage.css';

interface MemoryPageProps {
  userId: string;
  sessionId: string;
  onLogout: () => void;
}

export default function MemoryPage({ userId, sessionId, onLogout }: MemoryPageProps) {
  const [memoryState, setMemoryState] = useState<MemoryStateResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'short-term' | 'mid-term' | 'long-term'>('short-term');
  const [loading, setLoading] = useState(false);
  const [personalityData, setPersonalityData] = useState<any>(null);
  const [showPersonalityModal, setShowPersonalityModal] = useState(false);

  useEffect(() => {
    loadMemoryState();
    const interval = setInterval(loadMemoryState, 10000); // 每10秒更新
    return () => clearInterval(interval);
  }, []);

  const loadMemoryState = async () => {
    try {
      const data = await getMemoryState();
      setMemoryState(data);
    } catch (error) {
      console.error('Failed to load memory state:', error);
    }
  };

  const handleTriggerAnalysis = async () => {
    setLoading(true);
    try {
      await triggerAnalysis();
      await loadMemoryState();
      alert('记忆更新成功！');
    } catch (error) {
      alert('更新失败: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handlePersonalityAnalysis = async () => {
    setLoading(true);
    try {
      const data = await getPersonalityAnalysis();
      if (data.success) {
        setPersonalityData(data.personality_analysis);
        setShowPersonalityModal(true);
      } else {
        alert('分析失败: ' + data.error);
      }
    } catch (error) {
      alert('分析失败: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleClearMemory = async () => {
    if (!confirm('确定要清空所有记忆吗？此操作不可撤销。')) return;
    setLoading(true);
    try {
      await clearMemory();
      await loadMemoryState();
      alert('记忆已清空！');
    } catch (error) {
      alert('清空失败: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    const jsonText = prompt('请输入对话 JSON 数据:');
    if (!jsonText) return;
    try {
      const conversations = JSON.parse(jsonText);
      await importConversations({ conversations });
      await loadMemoryState();
      alert('导入成功！');
    } catch (error) {
      alert('导入失败: ' + (error instanceof Error ? error.message : 'Invalid JSON'));
    }
  };

  return (
    <div className="memory-page-wrapper">
      <FloatingNav onLogout={onLogout} />
      <div className="memory-content-area">
        <div className="memory-container">
          <div className="memory-header">
            <h2 className="memory-title">Memory Management</h2>
            <p className="memory-subtitle">View and manage your memory system</p>
          </div>

          {/* Memory Controls */}
          <div className="memory-controls">
            <h4 className="memory-controls-title">Memory Controls</h4>
            <div className="memory-controls-grid">
              <button
                className="memory-control-btn"
                onClick={handlePersonalityAnalysis}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                Analysis
              </button>
              <button
                className="memory-control-btn"
                onClick={handleTriggerAnalysis}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
                Update
              </button>
              <button
                className="memory-control-btn"
                onClick={handleImport}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                Import
              </button>
              <button
                className="memory-control-btn danger"
                onClick={handleClearMemory}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                Clear
              </button>
            </div>
          </div>

          {/* Memory Tabs */}
          <div className="memory-tabs-container">
            <div className="memory-tab-nav">
              <button
                className={`memory-tab-btn ${activeTab === 'short-term' ? 'active' : ''}`}
                onClick={() => setActiveTab('short-term')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                Short-term
              </button>
              <button
                className={`memory-tab-btn ${activeTab === 'mid-term' ? 'active' : ''}`}
                onClick={() => setActiveTab('mid-term')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1.5-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path>
                </svg>
                Mid-term
              </button>
              <button
                className={`memory-tab-btn ${activeTab === 'long-term' ? 'active' : ''}`}
                onClick={() => setActiveTab('long-term')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                  <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                  <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
                </svg>
                Long-term
              </button>
            </div>

            <div className="memory-tab-content">
              {activeTab === 'short-term' && (
                <div className="memory-tab-pane">
                  <div className="tab-header-info">
                    <h5>Short-term Memory</h5>
                    <span className="tab-capacity-badge">
                      {memoryState ? `${memoryState.short_term.current_count}/${memoryState.short_term.capacity}` : '0/5'}
                    </span>
                  </div>
                  <div className="memory-content">
                    {memoryState && memoryState.short_term.memories.length > 0 ? (
                      memoryState.short_term.memories.map((mem, idx) => (
                        <div key={idx} className="memory-item">
                          <strong>Q:</strong> {mem.user_input}<br />
                          <strong>A:</strong> {mem.agent_response}
                          <div className="timestamp">{mem.timestamp}</div>
                        </div>
                      ))
                    ) : (
                      <p className="empty-state">No short-term memories yet</p>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'mid-term' && (
                <div className="memory-tab-pane">
                  <div className="tab-header-info">
                    <h5>Mid-term Memory</h5>
                    <span className="tab-capacity-badge">
                      {memoryState ? `${memoryState.mid_term.current_count}/${memoryState.mid_term.capacity}` : '0/20'}
                    </span>
                  </div>
                  <div className="memory-content">
                    {memoryState && memoryState.mid_term.sessions.length > 0 ? (
                      memoryState.mid_term.sessions.map((session, idx) => {
                        const heatClass = session.heat >= memoryState.mid_term.heat_threshold ? 'heat-high' :
                                         session.heat >= 1.0 ? 'heat-medium' : 'heat-low';
                        return (
                          <div key={idx} className="memory-item">
                            <div className="memory-item-header">
                              <span className={`heat-indicator ${heatClass}`}></span>
                              <strong>Segment</strong>
                              <span className="heat-badge">Heat: {session.heat.toFixed(2)}</span>
                            </div>
                            {session.keywords && session.keywords.length > 0 && (
                              <div className="keywords-display">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                                  <line x1="7" y1="7" x2="7.01" y2="7"></line>
                                </svg>
                                {session.keywords.join(', ')}
                              </div>
                            )}
                            <div className="memory-item-meta">
                              Visits: {session.visit_count} | Pages: {session.page_count}
                            </div>
                            <div>{session.summary}</div>
                            <div className="timestamp">{session.last_visit}</div>
                          </div>
                        );
                      })
                    ) : (
                      <p className="empty-state">No mid-term segments yet</p>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'long-term' && (
                <div className="memory-tab-pane">
                  <div className="tab-header-info">
                    <h5>Long-term Memory</h5>
                    <span className="tab-capacity-badge">Persistent</span>
                  </div>
                  <div className="memory-content">
                    {memoryState && (
                      <>
                        <div className="profile-section">
                          <h6>User Profile</h6>
                          <div className="scrollable-content">
                            <div className="markdown-content">
                              {memoryState.long_term.user_profile === 'None' 
                                ? 'No profile data yet' 
                                : memoryState.long_term.user_profile}
                            </div>
                          </div>
                        </div>
                        <div className="knowledge-section">
                          <h6>User Knowledge</h6>
                          <div className="scrollable-content">
                            {memoryState.long_term.user_knowledge.length > 0 ? (
                              memoryState.long_term.user_knowledge.map((k, idx) => (
                                <div key={idx} className="knowledge-item">{k}</div>
                              ))
                            ) : (
                              <p>No user knowledge yet</p>
                            )}
                          </div>
                        </div>
                        <div className="knowledge-section">
                          <h6>Assistant Knowledge</h6>
                          <div className="scrollable-content">
                            {memoryState.long_term.assistant_knowledge.length > 0 ? (
                              memoryState.long_term.assistant_knowledge.map((k, idx) => (
                                <div key={idx} className="knowledge-item">{k}</div>
                              ))
                            ) : (
                              <p>No assistant knowledge yet</p>
                            )}
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Personality Analysis Modal */}
      {showPersonalityModal && personalityData && (
        <div className="modal-overlay" onClick={() => setShowPersonalityModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>用户画像分析</h3>
              <button className="modal-close" onClick={() => setShowPersonalityModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {/* 简化显示，可根据需要扩展 */}
              <pre>{JSON.stringify(personalityData, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
