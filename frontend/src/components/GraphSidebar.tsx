import { useState, useEffect, useRef, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import IntelStackFilter from './IntelStackFilter';
import './GraphSidebar.css';

interface GraphSidebarProps {
  nodeCount: number;
  linkCount: number;
  inferredCount: number;
  selectedActor: string | null;
  onClearActor: () => void;
  onSelectActor: (name: string) => void;
  /** All node names + connection counts for search autocomplete */
  nodeIndex: { name: string; connections: number; type: string }[];
  // Filters
  showInferred: boolean;
  onShowInferredChange: (val: boolean) => void;
  minConnections: number;
  onMinConnectionsChange: (val: number) => void;
  colorMode: 'type' | 'proximity';
  onColorModeChange: (mode: 'type' | 'proximity') => void;
  filterLevels: number[];
  onFilterLevelsChange: (levels: number[]) => void;
  // Legend
  colorMap: Record<string, string>;
  uniqueTypes: string[];
}

export default function GraphSidebar({
  nodeCount,
  linkCount,
  inferredCount,
  selectedActor,
  onClearActor,
  onSelectActor,
  nodeIndex,
  showInferred,
  onShowInferredChange,
  minConnections,
  onMinConnectionsChange,
  colorMode,
  onColorModeChange,
  filterLevels,
  onFilterLevelsChange,
  colorMap,
  uniqueTypes,
}: GraphSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showFilters, setShowFilters] = useState(true);
  const [showLegend, setShowLegend] = useState(false);
  const [showIntelStack, setShowIntelStack] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowSearchResults(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase();
    return nodeIndex
      .filter(n => n.name.toLowerCase().includes(q))
      .sort((a, b) => b.connections - a.connections)
      .slice(0, 20);
  }, [searchQuery, nodeIndex]);

  const handleSelectResult = (name: string) => {
    onSelectActor(name);
    setSearchQuery('');
    setShowSearchResults(false);
  };

  return (
    <aside className="graph-sidebar">
      {/* Header */}
      <div className="graph-sidebar-header">
        <Link to="/analysis" className="back-link">
          <ChevronLeft size={14} />
          <span>Back to Analysis</span>
        </Link>
        <h2>Entity Network</h2>
      </div>

      {/* Stats */}
      <div className="graph-sidebar-stats">
        <div className="stat-row">
          <span className="stat-label">Entities:</span>
          <span className="stat-value">{nodeCount.toLocaleString()}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Connections:</span>
          <span className="stat-value">{linkCount.toLocaleString()}</span>
        </div>
        {inferredCount > 0 && (
          <div className="stat-row">
            <span className="stat-label">Inferred:</span>
            <span className="stat-value" style={{ color: '#facc15' }}>{inferredCount.toLocaleString()}</span>
          </div>
        )}
      </div>

      {/* Selected Actor */}
      {selectedActor && (
        <div className="graph-sidebar-selected">
          <div className="selected-actor-header">
            <span className="actor-label">Selected actor:</span>
            <button className="clear-actor-btn" onClick={onClearActor}>Clear</button>
          </div>
          <div className="selected-actor-name">{selectedActor}</div>
        </div>
      )}

      {/* Search */}
      <div className="graph-search-container" ref={searchRef}>
        <label>Search entities:</label>
        <input
          className="graph-search-input"
          type="text"
          placeholder="e.g., Lockheed Martin"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setShowSearchResults(true);
          }}
          onFocus={() => { if (searchQuery.trim()) setShowSearchResults(true); }}
        />
        {showSearchResults && searchResults.length > 0 && (
          <div className="search-results-dropdown">
            {searchResults.map(r => (
              <div
                key={r.name}
                className="search-result-item"
                onClick={() => handleSelectResult(r.name)}
              >
                <span className="result-name">{r.name}</span>
                <span className="result-count">{r.connections} conn.</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Filters Section */}
      <div className="sidebar-section">
        <button className="section-toggle" onClick={() => setShowFilters(!showFilters)}>
          <span>Filters</span>
          <span className="toggle-arrow">{showFilters ? '▼' : '▶'}</span>
        </button>
        {showFilters && (
          <div className="section-content">
            <div className="filter-row">
              <label>
                <input
                  type="checkbox"
                  checked={showInferred}
                  onChange={(e) => onShowInferredChange(e.target.checked)}
                />
                Show inferred
              </label>
            </div>
            <div className="filter-row">
              <label>
                Min connections:
                <input
                  type="number"
                  min={0}
                  max={20}
                  value={minConnections}
                  onChange={(e) => onMinConnectionsChange(parseInt(e.target.value) || 0)}
                />
              </label>
            </div>
            <div style={{ marginTop: 8 }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Color by:</span>
              <div className="color-mode-toggle">
                <button
                  className={`color-mode-btn ${colorMode === 'type' ? 'active' : ''}`}
                  onClick={() => onColorModeChange('type')}
                >
                  Entity Type
                </button>
                <button
                  className={`color-mode-btn ${colorMode === 'proximity' ? 'active' : ''}`}
                  onClick={() => onColorModeChange('proximity')}
                >
                  Proximity
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Intel Stack Section */}
      <div className="sidebar-section">
        <button className="section-toggle" onClick={() => setShowIntelStack(!showIntelStack)}>
          <span>Intel Stack</span>
          <span className="toggle-arrow">{showIntelStack ? '▼' : '▶'}</span>
        </button>
        {showIntelStack && (
          <div className="section-content">
            <IntelStackFilter
              activeLevels={filterLevels}
              onChange={onFilterLevelsChange}
              compact
            />
          </div>
        )}
      </div>

      {/* Legend Section */}
      <div className="sidebar-section">
        <button className="section-toggle" onClick={() => setShowLegend(!showLegend)}>
          <span>Legend</span>
          <span className="toggle-arrow">{showLegend ? '▼' : '▶'}</span>
        </button>
        {showLegend && (
          <div className="section-content">
            <div className="sidebar-legend-items">
              {uniqueTypes.map(type => (
                <div key={type} className="sidebar-legend-item">
                  <span className="sidebar-legend-color" style={{ backgroundColor: colorMap[type] || '#9B9B9B' }} />
                  <span>{type}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
