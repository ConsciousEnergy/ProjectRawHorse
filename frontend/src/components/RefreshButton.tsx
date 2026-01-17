import { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { useDataContext } from '../contexts/DataContext';
import './RefreshButton.css';

interface RefreshButtonProps {
  position?: 'header' | 'floating';
  showBadge?: boolean;
}

function RefreshButton({ position = 'floating', showBadge = true }: RefreshButtonProps) {
  const { isStale, isRefreshing, refreshData, lastUpdated } = useDataContext();
  const [isHovered, setIsHovered] = useState(false);

  const handleRefresh = async () => {
    try {
      await refreshData();
      // Optionally show success message
    } catch (error) {
      console.error('Failed to refresh data:', error);
      // Optionally show error message
    }
  };

  const formatLastUpdated = (dateString: string | null): string => {
    if (!dateString) return 'Unknown';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      
      return date.toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  if (position === 'header') {
    return (
      <div className="refresh-button-header">
        <button
          className={`refresh-btn ${isStale ? 'stale' : ''} ${isRefreshing ? 'refreshing' : ''}`}
          onClick={handleRefresh}
          disabled={isRefreshing}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          title={isStale ? 'New data available - click to refresh' : 'Refresh data'}
          aria-label={isStale ? 'New data available - click to refresh' : 'Refresh data'}
        >
          <RefreshCw size={18} className={isRefreshing ? 'spinning' : ''} />
          {showBadge && isStale && (
            <span className="refresh-badge" aria-label="New data available">
              !
            </span>
          )}
        </button>
        {isHovered && lastUpdated && (
          <div className="refresh-tooltip">
            Last updated: {formatLastUpdated(lastUpdated)}
          </div>
        )}
      </div>
    );
  }

  // Floating position (default)
  return (
    <div className="refresh-button-floating">
      {isStale && showBadge && (
        <div className="refresh-notification">
          <span>New data available</span>
          <button
            className="refresh-notification-btn"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            Refresh
          </button>
        </div>
      )}
      <button
        className={`refresh-btn-floating ${isStale ? 'stale' : ''} ${isRefreshing ? 'refreshing' : ''}`}
        onClick={handleRefresh}
        disabled={isRefreshing}
        title={isStale ? 'New data available - click to refresh' : 'Refresh data'}
        aria-label={isStale ? 'New data available - click to refresh' : 'Refresh data'}
      >
        <RefreshCw size={20} className={isRefreshing ? 'spinning' : ''} />
        {showBadge && isStale && (
          <span className="refresh-badge-floating" aria-label="New data available">
            !
          </span>
        )}
      </button>
    </div>
  );
}

export default RefreshButton;
