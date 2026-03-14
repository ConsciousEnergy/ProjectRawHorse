import React, { useState } from 'react';
import api from '../services/api';
import './FlowTracer.css';

interface FlowPath {
  path: string[];
  amounts: number[];
  relationships: string[];
  total_amount: number;
  hops: number;
}

interface Intermediary {
  entity: string;
  path_count: number;
  total_flow: number;
}

interface FlowSummary {
  source: string;
  target: string;
  paths_found: number;
  paths: FlowPath[];
  total_flow: number;
  intermediaries: Intermediary[];
  statistics: {
    avg_flow_per_path: number;
    max_flow: number;
    min_flow: number;
    avg_hops: number;
  };
}

const FlowTracer: React.FC = () => {
  const [source, setSource] = useState('');
  const [target, setTarget] = useState('');
  const [maxHops, setMaxHops] = useState(5);
  const [summary, setSummary] = useState<FlowSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPath, setSelectedPath] = useState<number | null>(null);

  const handleTrace = async () => {
    if (!source || !target) {
      setError('Please enter both source and target entities');
      return;
    }

    setLoading(true);
    setError(null);
    setSummary(null);
    setSelectedPath(null);

    try {
      const response = await api.get('/analysis/flow-trace', {
        params: {
          source,
          target,
          max_hops: maxHops
        }
      });

      setSummary(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to trace flows');
      console.error('Error tracing flows:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    if (amount >= 1000000000) {
      return `$${(amount / 1000000000).toFixed(2)}B`;
    } else if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(2)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(2)}K`;
    }
    return `$${amount.toFixed(2)}`;
  };

  const renderPath = (path: FlowPath, index: number) => {
    const isSelected = selectedPath === index;

    return (
      <div
        key={index}
        className={`flow-path ${isSelected ? 'selected' : ''}`}
        onClick={() => setSelectedPath(isSelected ? null : index)}
      >
        <div className="path-header">
          <span className="path-number">Path {index + 1}</span>
          <span className="path-hops">{path.hops} hops</span>
          <span className="path-total">{formatCurrency(path.total_amount)}</span>
        </div>

        {isSelected && (
          <div className="path-details">
            <div className="path-visualization">
              {path.path.map((entity, i) => (
                <React.Fragment key={i}>
                  <div className="path-node">
                    <div className="node-label">{entity}</div>
                    {i < path.amounts.length && (
                      <div className="node-amount">{formatCurrency(path.amounts[i])}</div>
                    )}
                  </div>
                  {i < path.path.length - 1 && (
                    <div className="path-arrow">
                      <span>→</span>
                      {path.relationships[i] && (
                        <div className="arrow-label">{path.relationships[i]}</div>
                      )}
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flow-tracer">
      <div className="tracer-header">
        <h2>🔍 Multi-Hop Flow Tracer</h2>
        <p className="tracer-description">
          Trace money flows through multiple entities to discover indirect financial connections.
        </p>
      </div>

      <div className="tracer-controls">
        <div className="control-row">
          <div className="input-group">
            <label htmlFor="source">Source Entity</label>
            <input
              id="source"
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              placeholder="e.g., DARPA, Pentagon, Lockheed Martin"
            />
          </div>

          <div className="input-group">
            <label htmlFor="target">Target Entity</label>
            <input
              id="target"
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="e.g., Raytheon, AARO, NASA"
            />
          </div>

          <div className="input-group small">
            <label htmlFor="max-hops">Max Hops</label>
            <input
              id="max-hops"
              type="number"
              min="1"
              max="10"
              value={maxHops}
              onChange={(e) => setMaxHops(Number(e.target.value))}
            />
          </div>

          <button onClick={handleTrace} className="btn-primary" disabled={loading}>
            {loading ? 'Tracing...' : 'Trace Flows'}
          </button>
        </div>
      </div>

      {error && (
        <div className="tracer-error">
          <p>{error}</p>
        </div>
      )}

      {summary && (
        <div className="tracer-results">
          <div className="results-summary">
            <h3>Results Summary</h3>
            <div className="summary-cards">
              <div className="summary-card">
                <div className="card-value">{summary.paths_found}</div>
                <div className="card-label">Paths Found</div>
              </div>
              <div className="summary-card">
                <div className="card-value">{formatCurrency(summary.total_flow)}</div>
                <div className="card-label">Total Flow</div>
              </div>
              <div className="summary-card">
                <div className="card-value">{summary.statistics.avg_hops.toFixed(1)}</div>
                <div className="card-label">Avg Hops</div>
              </div>
              <div className="summary-card">
                <div className="card-value">{formatCurrency(summary.statistics.avg_flow_per_path)}</div>
                <div className="card-label">Avg Per Path</div>
              </div>
            </div>
          </div>

          {summary.intermediaries && summary.intermediaries.length > 0 && (
            <div className="intermediaries-section">
              <h3>Critical Intermediaries</h3>
              <p className="section-description">
                Entities that appear in multiple paths or control significant flows.
              </p>
              <div className="intermediaries-list">
                {summary.intermediaries.map((intermediary, index) => (
                  <div key={index} className="intermediary-item">
                    <div className="intermediary-name">{intermediary.entity}</div>
                    <div className="intermediary-stats">
                      <span className="stat">{intermediary.path_count} paths</span>
                      <span className="stat">{formatCurrency(intermediary.total_flow)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {summary.paths && summary.paths.length > 0 && (
            <div className="paths-section">
              <h3>Discovered Paths</h3>
              <p className="section-description">
                Click on a path to see the detailed flow visualization.
              </p>
              <div className="paths-list">
                {summary.paths.map((path, index) => renderPath(path, index))}
              </div>
            </div>
          )}

          {summary.paths_found === 0 && (
            <div className="no-paths">
              <p>No paths found between {summary.source} and {summary.target}.</p>
              <p>Try increasing the maximum number of hops or checking entity names.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FlowTracer;

