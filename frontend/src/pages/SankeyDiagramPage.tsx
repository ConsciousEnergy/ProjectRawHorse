import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, Layers } from 'lucide-react';
import SankeyDiagram from '../components/SankeyDiagram';
import IntelStackFilter from '../components/IntelStackFilter';

function SankeyDiagramPage() {
  const [filterLevels, setFilterLevels] = useState<number[]>([]);
  const [showFilter, setShowFilter] = useState(false);

  return (
    <div className="visualization-page fade-in" role="main" aria-label="Sankey Flow Diagram">
      <div className="viz-page-header">
        <Link to="/analysis" className="back-link">
          <ChevronLeft size={20} />
          <span>Back to Analysis</span>
        </Link>
        <div className="viz-page-title">
          <h1>Sankey Flow Diagram</h1>
          <p>Visualize money flows and relationships between entities. Use controls to filter and interact.</p>
        </div>
      </div>

      <div className="viz-fullscreen-container">
        <SankeyDiagram filterLevels={filterLevels} />
        
        {/* Intel Stack Filter Toggle */}
        <button 
          className="intel-filter-toggle"
          onClick={() => setShowFilter(!showFilter)}
          title="Toggle Intelligence Stack Filter"
        >
          <Layers size={20} />
          <span>Intel Stack</span>
        </button>
        
        {/* Intel Stack Filter Panel */}
        {showFilter && (
          <div className="intel-filter-panel">
            <IntelStackFilter
              activeLevels={filterLevels}
              onChange={setFilterLevels}
              compact
            />
          </div>
        )}
      </div>

      <style>{`
        .visualization-page {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 40px);
          padding: 20px;
        }

        .viz-page-header {
          flex-shrink: 0;
          margin-bottom: 16px;
        }

        .back-link {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          color: var(--text-secondary);
          text-decoration: none;
          font-size: 0.9rem;
          margin-bottom: 8px;
          transition: color 0.2s ease;
        }

        .back-link:hover {
          color: var(--primary-color);
        }

        .viz-page-title h1 {
          margin: 0 0 4px 0;
          font-size: 1.5rem;
        }

        .viz-page-title p {
          margin: 0;
          color: var(--text-secondary);
          font-size: 0.95rem;
        }

        .viz-fullscreen-container {
          flex: 1;
          min-height: 0;
          background: var(--card-bg);
          border: 1px solid var(--border-color);
          border-radius: 12px;
          overflow: hidden;
          position: relative;
        }

        .viz-fullscreen-container .sankey-container {
          height: 100% !important;
          min-height: unset !important;
        }

        .intel-filter-toggle {
          position: absolute;
          top: 12px;
          right: 12px;
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          background: var(--card-bg);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          color: var(--text-primary);
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s ease;
          z-index: 100;
        }

        .intel-filter-toggle:hover {
          border-color: var(--primary-color);
          color: var(--primary-color);
        }

        .intel-filter-panel {
          position: absolute;
          top: 56px;
          right: 12px;
          z-index: 100;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }

        @media (max-width: 768px) {
          .visualization-page {
            padding: 12px;
            height: calc(100vh - 24px);
          }

          .viz-page-title h1 {
            font-size: 1.25rem;
          }

          .intel-filter-toggle span {
            display: none;
          }

          .intel-filter-panel {
            right: 8px;
            top: 48px;
          }
        }
      `}</style>
    </div>
  );
}

export default SankeyDiagramPage;
