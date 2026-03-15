import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { getTopRecipientsByType, getAgencySpendingBreakdown, getAmountDistribution } from '../services/api';
import './FinancialDashboard.css';

interface RecipientData {
  entity: string;
  amount: number;
}

interface AgencyData {
  agency: string;
  amount: number;
  percentage: number;
}

interface DistributionBin {
  label: string;
  count: number;
}

interface DistributionStats {
  count: number;
  total: number;
  mean: number;
  median: number;
  min: number;
  max: number;
  std_dev: number;
  distribution_bins: DistributionBin[];
}

const FinancialDashboard: React.FC = () => {
  const [topRecipients, setTopRecipients] = useState<RecipientData[]>([]);
  const [agencyBreakdown, setAgencyBreakdown] = useState<AgencyData[]>([]);
  const [distribution, setDistribution] = useState<DistributionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [recipientsData, agenciesData, distributionData] = await Promise.all([
        getTopRecipientsByType(),
        getAgencySpendingBreakdown(),
        getAmountDistribution()
      ]);

      // Safely handle response data
      setTopRecipients(recipientsData?.recipients || []);
      setAgencyBreakdown(agenciesData?.agencies || []);
      setDistribution(distributionData?.count !== undefined ? distributionData : null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load dashboard data';
      setError(msg);
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number | undefined | null) => {
    if (!value || isNaN(value)) return '$0.00';
    
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(2)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(2)}K`;
    }
    return `$${value.toFixed(2)}`;
  };

  const COLORS = [
    '#5B4FFF', '#FFD700', '#FF6B9D', '#FFA500', '#4169E1',
    '#20B2AA', '#9370DB', '#00D4AA', '#FF8C00', '#7B6FFF'
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{payload[0].name || payload[0].payload.entity}</p>
          <p className="tooltip-value">{formatCurrency(payload[0].value)}</p>
        </div>
      );
    }
    return null;
  };

  const PieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{payload[0].payload.agency}</p>
          <p className="tooltip-value">{formatCurrency(payload[0].value)}</p>
          <p className="tooltip-percentage">{payload[0].payload.percentage.toFixed(1)}%</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="financial-dashboard-container">
        <div className="loading">Loading dashboard data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="financial-dashboard-container">
        <div className="error">{error}</div>
        <button onClick={loadDashboardData} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="financial-dashboard-container">
      <div className="dashboard-header">
        <h3>📈 Financial Analytics Dashboard</h3>
        <p className="dashboard-description">
          Comprehensive financial statistics and spending patterns.
        </p>
      </div>

      {distribution && (
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <div className="stat-label">Total Spending</div>
              <div className="stat-value">{formatCurrency(distribution.total)}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-label">Total Transactions</div>
              <div className="stat-value">{distribution.count.toLocaleString()}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📉</div>
            <div className="stat-content">
              <div className="stat-label">Average Amount</div>
              <div className="stat-value">{formatCurrency(distribution.mean)}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📌</div>
            <div className="stat-content">
              <div className="stat-label">Median Amount</div>
              <div className="stat-value">{formatCurrency(distribution.median)}</div>
            </div>
          </div>
        </div>
      )}

      <div className="charts-grid">
        <div className="chart-card">
          <h4>Top 10 Recipients</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topRecipients} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={(value) => formatCurrency(value)} />
              <YAxis type="category" dataKey="entity" width={150} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="amount" fill="#5B4FFF" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h4>Spending by Agency</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={agencyBreakdown.slice(0, 8)}
                dataKey="amount"
                nameKey="agency"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(entry) => `${entry.agency}: ${entry.percentage.toFixed(1)}%`}
              >
                {agencyBreakdown.slice(0, 8).map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<PieTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {distribution && distribution.distribution_bins && (
          <div className="chart-card full-width">
            <h4>Amount Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distribution.distribution_bins}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#FFD700" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="agency-details">
        <h4>Complete Agency Breakdown</h4>
        <div className="agency-table">
          {agencyBreakdown.map((agency, index) => (
            <div key={agency.agency} className="agency-row">
              <span className="agency-rank">#{index + 1}</span>
              <span
                className="agency-indicator"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              ></span>
              <span className="agency-name">{agency.agency}</span>
              <span className="agency-amount">{formatCurrency(agency.amount)}</span>
              <span className="agency-percent">{agency.percentage.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FinancialDashboard;

