import './AdRecommendations.css';

interface Ad {
  ad_id: string;
  title: string;
  description: string;
  image_url?: string;
  link_url?: string;
  keywords?: string[];
  topics?: string[];
  priority?: number;
}

interface AdRecommendationsProps {
  ads: Ad[];
}

export default function AdRecommendations({ ads }: AdRecommendationsProps) {
  if (!ads || ads.length === 0) {
    return null;
  }

  return (
    <div className="ad-recommendations">
      <div className="ad-header">
        <div className="ad-header-left">
          <div className="ad-header-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
          </div>
          <span className="ad-header-brand">MemContext</span>
          <span className="ad-header-sponsored">Sponsored</span>
        </div>
        <button className="ad-header-menu" aria-label="More options">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="1"></circle>
            <circle cx="12" cy="5" r="1"></circle>
            <circle cx="12" cy="19" r="1"></circle>
          </svg>
        </button>
      </div>
      <p className="ad-intro">这些选项可能对你有帮助。</p>
      <div className="ad-cards-container">
        <div className="ad-cards-scroll">
          {ads.map((ad) => (
            <div key={ad.ad_id} className="ad-card">
              <div className="ad-card-content">
                <div className="ad-card-text">
                  <h4 className="ad-card-title">{ad.title}</h4>
                  <div className="ad-card-meta">
                    <span className="ad-card-stock">现货</span>
                    <span className="ad-card-separator">•</span>
                    <span className="ad-card-price">¥{Math.floor(Math.random() * 200 + 50)}</span>
                  </div>
                  <div className="ad-card-delivery">25-35 分钟</div>
                </div>
                <div className="ad-card-image">
                  {ad.image_url ? (
                    <img src={ad.image_url} alt={ad.title} />
                  ) : (
                    <div className="ad-card-image-placeholder">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                      </svg>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
