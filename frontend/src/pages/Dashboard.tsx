import { useEffect, useState } from 'react';
import { getStats } from '../services/api';
import type { Stats } from '../types';
import SkeletonLoader from '../components/SkeletonLoader';
import { useDataContext } from '../contexts/DataContext';

function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { dataVersion } = useDataContext();

  useEffect(() => {
    loadStats();
  }, [dataVersion]);

  const loadStats = async () => {
    try {
      setError(null);
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
      setError('Failed to load dashboard statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    // Format large numbers with abbreviations (B, M, K)
    if (amount >= 1_000_000_000) {
      return `$${(amount / 1_000_000_000).toFixed(2)}B`;
    } else if (amount >= 1_000_000) {
      return `$${(amount / 1_000_000).toFixed(2)}M`;
    } else if (amount >= 1_000) {
      return `$${(amount / 1_000).toFixed(1)}K`;
    }
    return `$${amount.toFixed(0)}`;
  };

  const formatDateRange = (startDate: string, endDate: string) => {
    // Extract just the year from ISO date strings
    const startYear = startDate.split('-')[0];
    const endYear = endDate.split('-')[0];
    return `${startYear} - ${endYear}`;
  };

  return (
    <div className="dashboard fade-in" role="main" aria-label="Dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of UAP research data and federal spending</p>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
          <button onClick={loadStats} className="btn btn-secondary" style={{ marginLeft: '12px', padding: '6px 12px' }}>
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="stats-grid">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="stat-card">
              <SkeletonLoader type="stat" />
            </div>
          ))}
        </div>
      ) : (
        <div className="stats-grid fade-in" role="region" aria-label="Statistics overview">
          <div className="stat-card" role="article" aria-label="Total entities statistic">
            <h4>Total Entities</h4>
            <p className="value" aria-live="polite">{stats?.total_entities || 0}</p>
          </div>
          
          <div className="stat-card" role="article" aria-label="Money flows statistic">
            <h4>Money Flows</h4>
            <p className="value" aria-live="polite">{stats?.total_money_flows || 0}</p>
          </div>
          
          <div className="stat-card" role="article" aria-label="Federal awards statistic">
            <h4>Federal Awards</h4>
            <p className="value" aria-live="polite">{stats?.total_awards || 0}</p>
          </div>
          
          <div className="stat-card" role="article" aria-label="FOIA targets statistic">
            <h4>FOIA Targets</h4>
            <p className="value" aria-live="polite">{stats?.total_foia_targets || 0}</p>
          </div>
          
          <div className="stat-card" role="article" aria-label="Total spending tracked statistic">
            <h4>Total Spending Tracked</h4>
            <p className="value" aria-live="polite">{formatCurrency(stats?.total_money_amount || 0)}</p>
          </div>
          
          <div className="stat-card" role="article" aria-label="Date range statistic">
            <h4>Date Range</h4>
            <p className="value" aria-live="polite">
              {stats?.date_range_start && stats?.date_range_end 
                ? formatDateRange(stats.date_range_start, stats.date_range_end)
                : 'N/A'
              }
            </p>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Welcome to Project RawHorse</h3>
        <p>
          This application provides comprehensive access to publicly available data related to 
          Unidentified Anomalous Phenomena (UAP) research, federal contracting, and related entities.
        </p>
        <p>
          Use the navigation menu to:
        </p>
        <ul>
          <li><strong>Browse:</strong> Explore entities, money flows, awards, and FOIA targets</li>
          <li><strong>Analysis:</strong> Visualize relationships and financial networks</li>
          <li><strong>Export:</strong> Download data in CSV, JSON, or PDF formats</li>
          <li><strong>Contribute:</strong> Submit new data via automated GitHub pull requests</li>
        </ul>
      </div>

      <div className="card">
        <h3>Data Sources</h3>
        <p>All data is sourced from official public databases:</p>
        <ul>
          <li>USAspending.gov - Federal spending and contracts</li>
          <li>SAM.gov - Entity registrations and awards</li>
          <li>Federal agency FOIA reading rooms</li>
          <li>DOE, NASA, DHS, and other public databases</li>
        </ul>
      </div>

      <div className="card support-card">
        <div className="support-header">
          <h3>💜 Support This Project</h3>
        </div>
        <p>
          Project RawHorse is open-source and freely available. If you find this tool valuable 
          for UAP research and transparency advocacy, please consider supporting our work.
        </p>
        <p>
          Your donations help fund development, server costs, and support our broader research 
          into advanced energy systems and LENR fusion experiments.
        </p>
        <div className="support-actions">
          <a 
            href="https://conscious.energy/donations/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn btn-primary support-btn"
          >
            ❤️ Support via Donations
          </a>
          <a 
            href="https://github.com/ConsciousEnergy/ProjectRawHorse" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn btn-secondary"
          >
            ⭐ Star on GitHub
          </a>
        </div>
        <p className="support-note">
          <small>
            Donations accepted via Bitcoin, PayPal, and GoFundMe • 
            <a href="https://conscious.energy" target="_blank" rel="noopener noreferrer"> Learn more about Conscious Energy</a>
          </small>
        </p>
      </div>
    </div>
  );
}

export default Dashboard;
