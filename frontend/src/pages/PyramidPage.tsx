/**
 * PyramidPage: Full-screen Intelligence Stack Pyramid view.
 * Fetches GET /analysis/intel-stack/pyramid, shows PyramidVisualization with optional
 * entity highlight from ?entity_id= or ?entity=. Links from Browse use ?entity_id=.
 */
import { useEffect, useState, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getPyramidData, getPyramidHierarchy, searchIntelStack } from '../services/api';
import type { IntelStackSearchResult } from '../types';
import type { PyramidData } from '../types';
import PyramidVisualization from '../components/PyramidVisualization';
import IntelStackFilter from '../components/IntelStackFilter';
import EntityDetailPanel from '../components/EntityDetailPanel';
import './PyramidPage.css';

export default function PyramidPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const highlightId = searchParams.get('entity') || searchParams.get('entity_id') || null;
  const [data, setData] = useState<PyramidData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showFlowLines, setShowFlowLines] = useState(true);
  const [activeLevels, setActiveLevels] = useState<number[]>([1, 2, 3, 4, 5, 6]);
  const [detailEntityId, setDetailEntityId] = useState<string | null>(null);
  const [chainMode, setChainMode] = useState(false);
  const [chainEntityIds, setChainEntityIds] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<IntelStackSearchResult[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const LEVEL_LEGEND = [
    { level: 1, name: 'Control Group', color: '#FF1744' },
    { level: 2, name: 'Administrators', color: '#FF6B35' },
    { level: 3, name: 'FFRDCs', color: '#FF9800' },
    { level: 4, name: 'Prime Contractors', color: '#5B4FFF' },
    { level: 5, name: 'Facilities', color: '#4CAF50' },
    { level: 6, name: 'Programs', color: '#E91E63' },
  ];

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getPyramidData()
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const entityIdForChain = detailEntityId || highlightId;
  useEffect(() => {
    if (!chainMode || !entityIdForChain) {
      setChainEntityIds(new Set());
      return;
    }
    getPyramidHierarchy(entityIdForChain)
      .then((h) => {
        const ids = new Set<string>();
        ids.add(h.target.entity_id);
        h.chain_up.forEach((n) => ids.add(n.entity_id));
        h.chain_down.forEach((n) => ids.add(n.entity_id));
        h.lateral?.forEach((n) => ids.add(n.entity_id));
        setChainEntityIds(ids);
      })
      .catch(() => setChainEntityIds(new Set()));
  }, [chainMode, entityIdForChain]);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const t = setTimeout(() => {
      searchIntelStack(searchQuery.trim(), 15).then((r) => setSearchResults(r.results));
    }, 300);
    return () => clearTimeout(t);
  }, [searchQuery]);

  const onSearchSelect = useCallback((entity: IntelStackSearchResult) => {
    setSearchParams({ entity_id: entity.entity_id });
    setDetailEntityId(entity.entity_id);
    setSearchQuery('');
    setSearchResults([]);
    setSearchOpen(false);
  }, [setSearchParams]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === '/' && !/^(input|textarea)$/i.test((e.target as HTMLElement)?.tagName)) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.key === 'Escape') {
        setHelpOpen(false);
        setSearchOpen(false);
        setDetailEntityId(null);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="pyramid-page">
      <div className="pyramid-page-top">
        <div className="page-header pyramid-page-header">
          <h1>Intelligence Stack Pyramid</h1>
          <p>Hierarchical view of entities by intel stack level</p>
          <div className="pyramid-search-wrap">
            <input
              ref={searchInputRef}
              type="search"
              placeholder="Search entities (/)"
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setSearchOpen(true); }}
              onFocus={() => setSearchOpen(true)}
              onBlur={() => setTimeout(() => setSearchOpen(false), 150)}
              className="pyramid-search-input"
              aria-label="Search pyramid entities"
            />
            {searchOpen && searchResults.length > 0 && (
              <ul className="pyramid-search-results">
                {searchResults.map((r) => (
                  <li key={r.entity_id}>
                    <button type="button" onClick={() => onSearchSelect(r)}>
                      {r.display_name}
                      {r.intel_stack_level != null && (
                        <span className="pyramid-search-level">L{r.intel_stack_level}</span>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className={`pyramid-page-detail-section ${detailEntityId ? 'pyramid-page-detail-section-has-detail' : ''}`}>
            {detailEntityId ? (
              <EntityDetailPanel
                entityId={detailEntityId}
                onClose={() => setDetailEntityId(null)}
                inline
              />
            ) : (
              <div className="pyramid-page-aside-empty">
                {chainMode ? (
                  <>Select an entity from the pyramid or search to trace its chain of command and view details.</>
                ) : (
                  <>Select an entity from the pyramid or search to view details and chain of command.</>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="pyramid-page-main">
        <div className="pyramid-controls">
          <IntelStackFilter
            activeLevels={activeLevels}
            onChange={setActiveLevels}
            showAll
            compact={false}
          />
          <label className="pyramid-toggle">
            <input
              type="checkbox"
              checked={showFlowLines}
              onChange={(e) => setShowFlowLines(e.target.checked)}
            />
            <span>Show flow lines</span>
          </label>
          <label className="pyramid-toggle">
            <input
              type="checkbox"
              checked={chainMode}
              onChange={(e) => setChainMode(e.target.checked)}
            />
            <span>Trace chain of command</span>
            {chainMode && chainEntityIds.size > 0 && (
              <span className="pyramid-chain-badge" title="Entities in chain">({chainEntityIds.size})</span>
            )}
          </label>
        </div>

        <PyramidVisualization
          data={data}
          loading={loading}
          highlightedEntityId={highlightId}
          showFlowLines={showFlowLines}
          activeLevels={activeLevels}
          chainEntityIds={chainMode ? chainEntityIds : undefined}
          onEntityClick={(ent) => {
            setSearchParams({ entity_id: ent.entity_id });
            setDetailEntityId(ent.entity_id);
          }}
        />
      </div>
      <div className="pyramid-legend">
        {LEVEL_LEGEND.map(({ level, name, color }) => (
          <span key={level} className="pyramid-legend-item">
            <span className="pyramid-legend-dot" style={{ backgroundColor: color }} /> L{level} {name}
          </span>
        ))}
      </div>
      <button type="button" className="pyramid-help-btn" onClick={() => setHelpOpen((o) => !o)} aria-label="Help" title="Help">?</button>
      {helpOpen && (
        <div className="pyramid-help-overlay" onClick={() => setHelpOpen(false)} role="presentation">
          <div className="pyramid-help-content" onClick={(e) => e.stopPropagation()}>
            <h3>Using the Intelligence Stack Pyramid</h3>
            <ul>
              <li><strong>Click a tier</strong> to expand and see entities in the sidebar.</li>
              <li><strong>Click an entity</strong> to open its detail in the right panel.</li>
              <li><strong>Search</strong> with the search bar or press <kbd>/</kbd> to find entities.</li>
              <li><strong>Trace chain of command</strong> to highlight an entity&apos;s hierarchy.</li>
              <li><strong>Flow lines</strong> show money flow between levels; hover for details.</li>
            </ul>
            <p><kbd>Escape</kbd> closes the detail panel or this help.</p>
            <button type="button" className="pyramid-help-close" onClick={() => setHelpOpen(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
