import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { getTimeline } from '../services/api';
import './SpendingTimeline.css';

interface TimelineData {
  period: string;
  total: number;
  [key: string]: any;  // Dynamic agency fields
}

interface AgencyData {
  name: string;
  total: number;
}

const SpendingTimeline: React.FC = () => {
  const [timelineData, setTimelineData] = useState<TimelineData[]>([]);
  const [topAgencies, setTopAgencies] = useState<AgencyData[]>([]);
  const [groupBy, setGroupBy] = useState<'year' | 'month' | 'quarter'>('year');
  const [chartType, setChartType] = useState<'line' | 'area'>('area');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTimelineData();
  }, [groupBy]);

  const loadTimelineData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const responseData = await getTimeline(groupBy);
      
      // Safely handle response data
      if (!responseData) {
        console.warn('Empty response from timeline API');
        setTimelineData([]);
        setTopAgencies([]);
        return;
      }
      
      setTimelineData(responseData.timeline || []);
      setTopAgencies(responseData.top_agencies || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load timeline data');
      console.error('Error loading timeline:', err);
    } finally {
      setLoading(false);
    }
  };

  // Format currency for tooltips
  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(2)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(2)}K`;
    }
    return `$${value.toFixed(2)}`;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="tooltip-entry" style={{ color: entry.color }}>
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Color palette for agencies
  const colors = [
    '#5B4FFF', '#FFD700', '#FF6B9D', '#FFA500', '#4169E1',
    '#20B2AA', '#9370DB', '#00D4AA', '#FF8C00', '#7B6FFF'
  ];

  if (loading) {
    return (
      <div className="spending-timeline-container">
        <div className="loading">Loading timeline data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="spending-timeline-container">
        <div className="error">{error}</div>
        <button onClick={loadTimelineData} className="retry-button">Retry</button>
      </div>
    );
  }

  if (timelineData.length === 0) {
    return (
      <div className="spending-timeline-container">
        <div className="empty-state">
          <p>No timeline data available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="spending-timeline-container">
      <div className="timeline-header">
        <h3>📊 Spending Timeline</h3>
        <p className="timeline-description">
          Track spending patterns over time. View total spending or breakdown by agency.
        </p>
      </div>

      <div className="timeline-controls">
        <div className="control-group">
          <label>Time Period:</label>
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value as any)}
            className="control-select"
          >
            <option value="year">Yearly</option>
            <option value="quarter">Quarterly</option>
            <option value="month">Monthly</option>
          </select>
        </div>

        <div className="control-group">
          <label>Chart Type:</label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value as any)}
            className="control-select"
          >
            <option value="area">Stacked Area</option>
            <option value="line">Line Chart</option>
          </select>
        </div>
      </div>

      <div className="timeline-stats">
        <div className="stat-card">
          <div className="stat-label">Total Periods</div>
          <div className="stat-value">{timelineData.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Spending</div>
          <div className="stat-value">
            {formatCurrency(timelineData.reduce((sum, d) => sum + d.total, 0))}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Tracked Agencies</div>
          <div className="stat-value">{topAgencies.length}</div>
        </div>
      </div>

      <div className="chart-container">
        {chartType === 'area' ? (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis tickFormatter={(value) => formatCurrency(value)} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {topAgencies.slice(0, 5).map((agency, index) => (
                <Area
                  key={agency.name}
                  type="monotone"
                  dataKey={agency.name}
                  stackId="1"
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.6}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis tickFormatter={(value) => formatCurrency(value)} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="total"
                stroke="#5B4FFF"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              {topAgencies.slice(0, 5).map((agency, index) => (
                <Line
                  key={agency.name}
                  type="monotone"
                  dataKey={agency.name}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="agency-summary">
        <h4>Top Agencies by Total Spending</h4>
        <div className="agency-list">
          {topAgencies.map((agency, index) => (
            <div key={agency.name} className="agency-item">
              <span className="agency-rank">#{index + 1}</span>
              <span
                className="agency-color"
                style={{ backgroundColor: colors[index % colors.length] }}
              ></span>
              <span className="agency-name">{agency.name}</span>
              <span className="agency-total">{formatCurrency(agency.total)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SpendingTimeline;

