import { Link } from 'react-router-dom';
import { Network, GitBranch, BarChart3, TrendingUp, Triangle, Lock } from 'lucide-react';

function AnalysisOverview() {
  return (
    <div className="analysis-overview fade-in" role="main" aria-label="Analysis overview page">
      <div className="page-header">
        <h1>Analysis</h1>
        <p>Visualize relationships and financial networks</p>
      </div>

      <div className="visualization-cards">
        <Link to="/analysis/network" className="viz-card">
          <div className="viz-card-icon">
            <Network size={48} />
          </div>
          <div className="viz-card-content">
            <h3>Entity Network Graph</h3>
            <p>
              Interactive force-directed graph showing relationships between entities. 
              Explore connections between government agencies, contractors, and research institutions.
            </p>
            <ul className="viz-card-features">
              <li>Click and drag nodes to explore</li>
              <li>Filter by connection count</li>
              <li>Toggle inferred relationships</li>
              <li>Zoom and pan controls</li>
            </ul>
          </div>
          <span className="viz-card-arrow">→</span>
        </Link>

        <Link to="/analysis/sankey" className="viz-card">
          <div className="viz-card-icon">
            <GitBranch size={48} />
          </div>
          <div className="viz-card-content">
            <h3>Sankey Flow Diagram</h3>
            <p>
              Visualize money flows and relationships between entities. 
              Track funding paths from government agencies to contractors.
            </p>
            <ul className="viz-card-features">
              <li>Filter by minimum amount</li>
              <li>Toggle flow types (money/relationships)</li>
              <li>Click nodes to highlight connections</li>
              <li>Hover for detailed tooltips</li>
            </ul>
          </div>
          <span className="viz-card-arrow">→</span>
        </Link>

        <div className="viz-card viz-card-coming-soon">
          <div className="viz-card-icon" style={{ background: 'linear-gradient(135deg, #6b7280, #9ca3af)' }}>
            <Triangle size={48} />
          </div>
          <div className="viz-card-content">
            <h3>
              Intelligence Stack Pyramid
              <span className="coming-soon-badge">Coming Soon</span>
            </h3>
            <p>
              Hierarchical visualization of U.S. intelligence agencies and their roles in 
              UAP programs. Interactive pyramid showing command structure and oversight relationships.
            </p>
            <ul className="viz-card-features">
              <li>6-tier hierarchy: Control Group → Programs</li>
              <li>Click tiers to filter entities</li>
              <li>Visualize agency relationships</li>
              <li>Track chain of command</li>
            </ul>
            <div className="pyramid-preview">
              <div className="pyramid-tier tier-1">Control Group</div>
              <div className="pyramid-tier tier-2">Administrators (NRO, CIA, DIA, NSA)</div>
              <div className="pyramid-tier tier-3">FFRDCs (MITRE, Battelle, National Labs)</div>
              <div className="pyramid-tier tier-4">Prime Contractors (LM, NG, RTX, Boeing)</div>
              <div className="pyramid-tier tier-5">Facilities (Area 51, S4, Edwards AFB)</div>
              <div className="pyramid-tier tier-6">Programs (Immaculate Constellation, Kona Blue)</div>
            </div>
          </div>
          <span className="viz-card-lock">
            <Lock size={20} />
          </span>
        </div>
      </div>

      <div className="card">
        <h3>
          <BarChart3 size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          Quick Stats
        </h3>
        <p>
          Summary statistics and financial data are available on the Dashboard. 
          Use the visualizations above for detailed network exploration.
        </p>
        <Link to="/" className="btn btn-secondary" style={{ marginTop: '12px' }}>
          <TrendingUp size={16} style={{ marginRight: '6px' }} />
          View Dashboard
        </Link>
      </div>

      <style>{`
        .visualization-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 24px;
          margin-bottom: 24px;
        }

        .viz-card {
          display: flex;
          align-items: flex-start;
          gap: 20px;
          background: var(--card-bg);
          border: 1px solid var(--border-color);
          border-radius: 12px;
          padding: 24px;
          text-decoration: none;
          color: inherit;
          transition: all 0.2s ease;
          position: relative;
        }

        .viz-card:hover {
          border-color: var(--primary-color);
          box-shadow: 0 4px 20px rgba(91, 79, 255, 0.15);
          transform: translateY(-2px);
        }

        .viz-card-icon {
          flex-shrink: 0;
          width: 80px;
          height: 80px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, var(--primary-color), #7c6fff);
          border-radius: 12px;
          color: white;
        }

        .viz-card-content {
          flex: 1;
        }

        .viz-card-content h3 {
          margin: 0 0 8px 0;
          font-size: 1.25rem;
          color: var(--text-primary);
        }

        .viz-card-content p {
          margin: 0 0 12px 0;
          color: var(--text-secondary);
          line-height: 1.5;
        }

        .viz-card-features {
          margin: 0;
          padding-left: 20px;
          color: var(--text-muted);
          font-size: 0.9rem;
        }

        .viz-card-features li {
          margin-bottom: 4px;
        }

        .viz-card-arrow {
          position: absolute;
          right: 20px;
          top: 50%;
          transform: translateY(-50%);
          font-size: 24px;
          color: var(--primary-color);
          opacity: 0;
          transition: opacity 0.2s ease;
        }

        .viz-card:hover .viz-card-arrow {
          opacity: 1;
        }

        .viz-card-coming-soon {
          opacity: 0.85;
          cursor: default;
          border-style: dashed;
        }

        .viz-card-coming-soon:hover {
          transform: none;
          box-shadow: none;
          border-color: var(--border-color);
        }

        .coming-soon-badge {
          display: inline-block;
          font-size: 0.7rem;
          background: linear-gradient(135deg, #f59e0b, #d97706);
          color: white;
          padding: 2px 8px;
          border-radius: 4px;
          margin-left: 10px;
          vertical-align: middle;
          font-weight: 600;
          text-transform: uppercase;
        }

        .viz-card-lock {
          position: absolute;
          right: 20px;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-muted);
        }

        .pyramid-preview {
          margin-top: 16px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
        }

        .pyramid-tier {
          text-align: center;
          padding: 4px 8px;
          font-size: 0.7rem;
          font-weight: 500;
          border-radius: 2px;
          color: white;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .pyramid-tier.tier-1 {
          width: 30%;
          background: #dc2626;
        }

        .pyramid-tier.tier-2 {
          width: 45%;
          background: #ea580c;
        }

        .pyramid-tier.tier-3 {
          width: 60%;
          background: #f59e0b;
        }

        .pyramid-tier.tier-4 {
          width: 75%;
          background: #5b4fff;
        }

        .pyramid-tier.tier-5 {
          width: 90%;
          background: #10b981;
        }

        .pyramid-tier.tier-6 {
          width: 100%;
          background: #6366f1;
        }

        @media (max-width: 768px) {
          .visualization-cards {
            grid-template-columns: 1fr;
          }

          .viz-card {
            flex-direction: column;
            text-align: center;
          }

          .viz-card-icon {
            margin: 0 auto;
          }

          .viz-card-features {
            text-align: left;
          }

          .viz-card-arrow {
            display: none;
          }

          .pyramid-tier {
            font-size: 0.6rem;
          }
        }
      `}</style>
    </div>
  );
}

export default AnalysisOverview;
