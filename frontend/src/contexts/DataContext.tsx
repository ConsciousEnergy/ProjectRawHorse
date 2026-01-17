import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { getDataVersion, refreshData } from '../services/api';

interface DataContextType {
  dataVersion: number;
  lastUpdated: string | null;
  isStale: boolean;
  isRefreshing: boolean;
  refreshData: () => Promise<void>;
  checkVersion: () => Promise<void>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const useDataContext = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useDataContext must be used within DataProvider');
  }
  return context;
};

interface DataProviderProps {
  children: ReactNode;
  pollInterval?: number; // Polling interval in milliseconds (default: 30 seconds)
}

export const DataProvider: React.FC<DataProviderProps> = ({ 
  children, 
  pollInterval = 30000 
}) => {
  const [dataVersion, setDataVersion] = useState<number>(0);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [isStale, setIsStale] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [initialVersion, setInitialVersion] = useState<number | null>(null);

  const checkVersion = useCallback(async () => {
    try {
      const versionData = await getDataVersion();
      
      if (initialVersion === null) {
        // First load - set initial version
        setInitialVersion(versionData.version);
        setDataVersion(versionData.version);
        setLastUpdated(versionData.last_updated);
        setIsStale(false);
      } else if (versionData.version !== dataVersion) {
        // Version changed - data is stale
        setDataVersion(versionData.version);
        setLastUpdated(versionData.last_updated);
        setIsStale(true);
      } else {
        // Version unchanged - data is fresh
        setIsStale(false);
      }
    } catch (error) {
      console.error('Error checking data version:', error);
      // Don't set stale on error to avoid false positives
    }
  }, [dataVersion, initialVersion]);

  const handleRefresh = useCallback(async () => {
    try {
      setIsRefreshing(true);
      const result = await refreshData();
      
      // Update version after refresh
      setDataVersion(result.version);
      setLastUpdated(result.last_updated);
      setIsStale(false);
      
      // Trigger a page reload or emit event for components to refresh
      window.dispatchEvent(new CustomEvent('dataRefreshed', { 
        detail: { version: result.version } 
      }));
    } catch (error) {
      console.error('Error refreshing data:', error);
      throw error;
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  // Initial version check
  useEffect(() => {
    checkVersion();
  }, []);

  // Set up polling
  useEffect(() => {
    if (pollInterval > 0) {
      const interval = setInterval(() => {
        checkVersion();
      }, pollInterval);

      return () => clearInterval(interval);
    }
  }, [checkVersion, pollInterval]);

  // Listen for navigation events to check version
  useEffect(() => {
    const handleNavigation = () => {
      // Small delay to ensure route has changed
      setTimeout(() => {
        checkVersion();
      }, 100);
    };

    window.addEventListener('popstate', handleNavigation);
    
    // Also check on focus (user returns to tab)
    window.addEventListener('focus', checkVersion);

    return () => {
      window.removeEventListener('popstate', handleNavigation);
      window.removeEventListener('focus', checkVersion);
    };
  }, [checkVersion]);

  const value: DataContextType = {
    dataVersion,
    lastUpdated,
    isStale,
    isRefreshing,
    refreshData: handleRefresh,
    checkVersion
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
