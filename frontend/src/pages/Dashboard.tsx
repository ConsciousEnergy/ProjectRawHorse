import { useEffect, useState } from 'react';
import { getStats } from '../services/api';
import type { Stats } from '../types';

function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
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

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Overview of UAP research data and federal spending</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h4>Total Entities</h4>
          <p className="value">{stats?.total_entities || 0}</p>
        </div>
        
        <div className="stat-card">
          <h4>Money Flows</h4>
          <p className="value">{stats?.total_money_flows || 0}</p>
        </div>
        
        <div className="stat-card">
          <h4>Federal Awards</h4>
          <p className="value">{stats?.total_awards || 0}</p>
        </div>
        
        <div className="stat-card">
          <h4>FOIA Targets</h4>
          <p className="value">{stats?.total_foia_targets || 0}</p>
        </div>
        
        <div className="stat-card">
          <h4>Total Spending Tracked</h4>
          <p className="value">{formatCurrency(stats?.total_money_amount || 0)}</p>
        </div>
        
        <div className="stat-card">
          <h4>Date Range</h4>
          <p className="value">
            {stats?.date_range_start && stats?.date_range_end 
              ? formatDateRange(stats.date_range_start, stats.date_range_end)
              : 'N/A'
            }
          </p>
        </div>
      </div>

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
    </div>
  );
}

export default Dashboard;
