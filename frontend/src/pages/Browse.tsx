import { useEffect, useState, useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getEntities, getMoneyFlows, getAwards, getFOIATargets } from '../services/api';
import type { Entity, MoneyFlow, Award, FOIATarget } from '../types';
import SkeletonLoader from '../components/SkeletonLoader';
import { useDataContext } from '../contexts/DataContext';
import { Link } from 'react-router-dom';
import { Triangle } from 'lucide-react';
import './Browse.css';

type TabType = 'entities' | 'money-flows' | 'awards' | 'foia';
type SortDirection = 'asc' | 'desc';

interface SortConfig {
  key: string;
  direction: SortDirection;
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Highlight matching text
function HighlightText({ text, highlight }: { text: string; highlight: string }) {
  if (!highlight.trim() || !text) {
    return <>{text}</>;
  }
  const tokens = highlight.trim().split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return <>{text}</>;
  const escaped = tokens.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const pattern = escaped.join('|');
  const regex = new RegExp(`(${pattern})`, 'gi');
  const parts = text.split(regex);
  return (
    <>
      {parts.map((part, i) =>
        i % 2 === 1 ? (
          <mark key={i} className="search-highlight">{part}</mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

function Browse() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { dataVersion } = useDataContext();
  const [activeTab, setActiveTab] = useState<TabType>('entities');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  
  // Sorting
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: '', direction: 'asc' });
  
  // Advanced filter states
  const [entityTypeFilter, setEntityTypeFilter] = useState<string[]>([]);
  const [intelStackFilter, setIntelStackFilter] = useState<number[]>([]);
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Quick search suggestions
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  
  // Data states
  const [entities, setEntities] = useState<Entity[]>([]);
  const [moneyFlows, setMoneyFlows] = useState<MoneyFlow[]>([]);
  const [awards, setAwards] = useState<Award[]>([]);
  const [foiaTargets, setFOIATargets] = useState<FOIATarget[]>([]);
  
  // Debounced search for auto-search
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Entity type options with counts
  const entityTypes = [
    'Corporation',
    'Government Agency', 
    'Individual',
    'Research Institution',
    'Facility',
    'Program',
    'Organization',
    'Investment Firm'
  ];

  // Intel stack levels
  const intelLevels = [
    { value: 1, label: 'Control Group' },
    { value: 2, label: 'Administrators' },
    { value: 3, label: 'FFRDCs' },
    { value: 4, label: 'Prime Contractors' },
    { value: 5, label: 'Facilities' },
    { value: 6, label: 'Programs' }
  ];

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  // Save search to recent
  const saveSearch = useCallback((term: string) => {
    if (!term.trim()) return;
    const updated = [term, ...recentSearches.filter(s => s !== term)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
  }, [recentSearches]);

  // Highlight row from SearchBar result (scroll + flash)
  const highlightId = searchParams.get('highlight') ?? '';

  // Initialize from URL parameters
  useEffect(() => {
    const tab = searchParams.get('tab') as TabType;
    const search = searchParams.get('search');
    const type = searchParams.get('type');
    const page = searchParams.get('page');
    
    if (tab && ['entities', 'money-flows', 'awards', 'foia'].includes(tab)) {
      setActiveTab(tab);
    }
    
    if (search) {
      setSearchTerm(search);
    }
    
    if (type) {
      setEntityTypeFilter([type]);
    }
    
    if (page) {
      setCurrentPage(parseInt(page));
    }
  }, [searchParams]);

  // Scroll to and flash the row matching highlightId when data is loaded
  useEffect(() => {
    if (!highlightId || loading) return;
    const prefix =
      activeTab === 'entities'
        ? 'row-entity-'
        : activeTab === 'money-flows'
          ? 'row-flow-'
          : activeTab === 'awards'
            ? 'row-award-'
            : activeTab === 'foia'
              ? 'row-foia-'
              : '';
    if (!prefix) return;
    const rowId = prefix + highlightId;
    const el = document.getElementById(rowId);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    el.classList.add('row-highlight-flash');
    const t = setTimeout(() => {
      el.classList.remove('row-highlight-flash');
      setSearchParams((prev) => {
        prev.delete('highlight');
        return prev;
      });
    }, 2500);
    return () => clearTimeout(t);
  }, [highlightId, activeTab, loading, setSearchParams]);

  // Auto-search on debounced term change
  useEffect(() => {
    loadData();
    // Update URL with search term
    if (debouncedSearchTerm) {
      setSearchParams(prev => {
        prev.set('search', debouncedSearchTerm);
        return prev;
      });
    }
  }, [debouncedSearchTerm, activeTab, entityTypeFilter, intelStackFilter, minAmount, maxAmount, startDate, endDate, agencyFilter, currentPage, dataVersion]);

  const buildParams = () => {
    const params: any = { 
      limit: itemsPerPage,
      offset: (currentPage - 1) * itemsPerPage 
    };
    
    if (debouncedSearchTerm.trim()) {
      params.search = debouncedSearchTerm;
    }
    
    if (activeTab === 'entities') {
      if (entityTypeFilter.length === 1) {
        params.entity_type = entityTypeFilter[0];
      }
      if (intelStackFilter.length > 0) {
        params.intel_stack_level = intelStackFilter[0];
      }
    }
    
    if ((activeTab === 'money-flows' || activeTab === 'awards') && minAmount) {
      params.min_amount = parseFloat(minAmount);
    }
    
    if ((activeTab === 'money-flows' || activeTab === 'awards') && maxAmount) {
      params.max_amount = parseFloat(maxAmount);
    }
    
    if ((activeTab === 'money-flows' || activeTab === 'awards') && startDate) {
      params.start_date = startDate;
    }
    
    if ((activeTab === 'money-flows' || activeTab === 'awards') && endDate) {
      params.end_date = endDate;
    }
    
    if ((activeTab === 'awards' || activeTab === 'foia') && agencyFilter) {
      params.agency = agencyFilter;
    }
    
    return params;
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const params = buildParams();
      
      switch (activeTab) {
        case 'entities':
          const entitiesData = await getEntities(params);
          setEntities(entitiesData);
          break;
        case 'money-flows':
          const flowsData = await getMoneyFlows(params);
          setMoneyFlows(flowsData);
          break;
        case 'awards':
          const awardsData = await getAwards(params);
          setAwards(awardsData);
          break;
        case 'foia':
          const foiaData = await getFOIATargets(params);
          setFOIATargets(foiaData);
          break;
      }
      
      if (debouncedSearchTerm.trim()) {
        saveSearch(debouncedSearchTerm);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key: string) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Sort data client-side
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return { entities, moneyFlows, awards, foiaTargets };
    
    const sortFn = (a: any, b: any) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      
      if (sortConfig.direction === 'asc') {
        return aStr.localeCompare(bStr);
      }
      return bStr.localeCompare(aStr);
    };
    
    return {
      entities: [...entities].sort(sortFn),
      moneyFlows: [...moneyFlows].sort(sortFn),
      awards: [...awards].sort(sortFn),
      foiaTargets: [...foiaTargets].sort(sortFn)
    };
  }, [entities, moneyFlows, awards, foiaTargets, sortConfig]);

  const handleClearFilters = () => {
    setSearchTerm('');
    setEntityTypeFilter([]);
    setIntelStackFilter([]);
    setMinAmount('');
    setMaxAmount('');
    setStartDate('');
    setEndDate('');
    setAgencyFilter('');
    setCurrentPage(1);
    setSearchParams({});
  };

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    setCurrentPage(1);
    setSortConfig({ key: '', direction: 'asc' });
    setSearchParams(prev => {
      prev.set('tab', tab);
      return prev;
    });
  };

  const toggleEntityType = (type: string) => {
    setEntityTypeFilter(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
    setCurrentPage(1);
  };

  const toggleIntelLevel = (level: number) => {
    setIntelStackFilter(prev =>
      prev.includes(level)
        ? prev.filter(l => l !== level)
        : [...prev, level]
    );
    setCurrentPage(1);
  };

  const removeFilter = (type: string, value: string | number) => {
    switch (type) {
      case 'entityType':
        setEntityTypeFilter(prev => prev.filter(t => t !== value));
        break;
      case 'intelLevel':
        setIntelStackFilter(prev => prev.filter(l => l !== value));
        break;
      case 'minAmount':
        setMinAmount('');
        break;
      case 'maxAmount':
        setMaxAmount('');
        break;
      case 'startDate':
        setStartDate('');
        break;
      case 'endDate':
        setEndDate('');
        break;
      case 'agency':
        setAgencyFilter('');
        break;
    }
    setCurrentPage(1);
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const SortableHeader = ({ column, label }: { column: string; label: string }) => {
    const getAriaSort = (): 'ascending' | 'descending' | 'none' => {
      if (sortConfig.key !== column) return 'none';
      return sortConfig.direction === 'asc' ? 'ascending' : 'descending';
    };
    
    return (
      <th 
        onClick={() => handleSort(column)} 
        className="sortable-header"
        role="columnheader"
        aria-sort={getAriaSort()}
      >
        {label}
        <span className="sort-indicator">
          {sortConfig.key === column ? (sortConfig.direction === 'asc' ? ' ▲' : ' ▼') : ' ⇅'}
        </span>
      </th>
    );
  };

  // Active filters display
  const activeFilters = useMemo(() => {
    const filters: { type: string; value: string | number; label: string }[] = [];
    
    entityTypeFilter.forEach(type => {
      filters.push({ type: 'entityType', value: type, label: `Type: ${type}` });
    });
    
    intelStackFilter.forEach(level => {
      const levelInfo = intelLevels.find(l => l.value === level);
      filters.push({ type: 'intelLevel', value: level, label: `Intel: ${levelInfo?.label || level}` });
    });
    
    if (minAmount) filters.push({ type: 'minAmount', value: minAmount, label: `Min: $${parseInt(minAmount).toLocaleString()}` });
    if (maxAmount) filters.push({ type: 'maxAmount', value: maxAmount, label: `Max: $${parseInt(maxAmount).toLocaleString()}` });
    if (startDate) filters.push({ type: 'startDate', value: startDate, label: `From: ${startDate}` });
    if (endDate) filters.push({ type: 'endDate', value: endDate, label: `To: ${endDate}` });
    if (agencyFilter) filters.push({ type: 'agency', value: agencyFilter, label: `Agency: ${agencyFilter}` });
    
    return filters;
  }, [entityTypeFilter, intelStackFilter, minAmount, maxAmount, startDate, endDate, agencyFilter]);

  const getCurrentDataLength = () => {
    switch (activeTab) {
      case 'entities': return sortedData.entities.length;
      case 'money-flows': return sortedData.moneyFlows.length;
      case 'awards': return sortedData.awards.length;
      case 'foia': return sortedData.foiaTargets.length;
      default: return 0;
    }
  };

  return (
    <div className="browse" role="main" aria-label="Browse page">
      <div className="page-header">
        <h1>Browse Data</h1>
        <p>Search and explore entities, money flows, awards, and FOIA targets</p>
      </div>

      {/* Enhanced Search Bar */}
      <div className="search-section">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by name, keyword, or ID... (auto-search enabled)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input-enhanced"
            aria-label="Search database"
          />
          {searchTerm && (
            <button 
              className="clear-search-btn"
              onClick={() => setSearchTerm('')}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>
        
        <div className="search-actions">
          <button 
            onClick={() => setShowFilters(!showFilters)} 
            className={`btn btn-secondary ${showFilters ? 'active' : ''}`}
          >
            {showFilters ? '▼ Filters' : '▶ Filters'}
          </button>
          {(searchTerm || activeFilters.length > 0) && (
            <button onClick={handleClearFilters} className="btn btn-outline">
              Clear All
            </button>
          )}
        </div>

        {/* Recent Searches */}
        {!searchTerm && recentSearches.length > 0 && (
          <div className="recent-searches">
            <span className="recent-label">Recent:</span>
            {recentSearches.map((term, idx) => (
              <button 
                key={idx} 
                className="recent-search-chip"
                onClick={() => setSearchTerm(term)}
              >
                {term}
              </button>
            ))}
          </div>
        )}

        {/* Quick Search Suggestions */}
        {!searchTerm && (
          <div className="quick-searches">
            <span className="quick-label">Quick:</span>
            <button className="quick-chip" onClick={() => { setActiveTab('entities'); setEntityTypeFilter(['Corporation']); }}>
              Corporations
            </button>
            <button className="quick-chip" onClick={() => { setActiveTab('entities'); setEntityTypeFilter(['Government Agency']); }}>
              Gov Agencies
            </button>
            <button className="quick-chip" onClick={() => { setActiveTab('entities'); setEntityTypeFilter(['Individual']); }}>
              Individuals
            </button>
            <button className="quick-chip" onClick={() => { setActiveTab('money-flows'); setMinAmount('1000000'); }}>
              Flows &gt; $1M
            </button>
            <button className="quick-chip" onClick={() => { setActiveTab('foia'); }}>
              FOIA Targets
            </button>
          </div>
        )}
      </div>

      {/* Active Filters Chips */}
      {activeFilters.length > 0 && (
        <div className="active-filters">
          {activeFilters.map((filter, idx) => (
            <span key={idx} className="filter-chip">
              {filter.label}
              <button 
                className="remove-filter"
                onClick={() => removeFilter(filter.type, filter.value)}
                aria-label={`Remove ${filter.label} filter`}
              >
                ✕
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="tabs" role="tablist" aria-label="Data type tabs">
        <button 
          className={activeTab === 'entities' ? 'active' : ''} 
          onClick={() => handleTabChange('entities')}
          role="tab"
          aria-selected={activeTab === 'entities'}
        >
          Entities
          <span className="tab-count">{activeTab === 'entities' ? getCurrentDataLength() : ''}</span>
        </button>
        <button 
          className={activeTab === 'money-flows' ? 'active' : ''} 
          onClick={() => handleTabChange('money-flows')}
          role="tab"
          aria-selected={activeTab === 'money-flows'}
        >
          Money Flows
          <span className="tab-count">{activeTab === 'money-flows' ? getCurrentDataLength() : ''}</span>
        </button>
        <button 
          className={activeTab === 'awards' ? 'active' : ''} 
          onClick={() => handleTabChange('awards')}
          role="tab"
          aria-selected={activeTab === 'awards'}
        >
          Awards
          <span className="tab-count">{activeTab === 'awards' ? getCurrentDataLength() : ''}</span>
        </button>
        <button 
          className={activeTab === 'foia' ? 'active' : ''} 
          onClick={() => handleTabChange('foia')}
          role="tab"
          aria-selected={activeTab === 'foia'}
        >
          FOIA Targets
          <span className="tab-count">{activeTab === 'foia' ? getCurrentDataLength() : ''}</span>
        </button>
      </div>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div className="filters-panel">
          <h4>Advanced Filters</h4>
          
          {activeTab === 'entities' && (
            <>
              <div className="filter-group">
                <label>Entity Types:</label>
                <div className="filter-checkboxes">
                  {entityTypes.map(type => (
                    <label key={type} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={entityTypeFilter.includes(type)}
                        onChange={() => toggleEntityType(type)}
                      />
                      {type}
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="filter-group">
                <label>Intel Stack Level:</label>
                <div className="filter-checkboxes">
                  {intelLevels.map(level => (
                    <label key={level.value} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={intelStackFilter.includes(level.value)}
                        onChange={() => toggleIntelLevel(level.value)}
                      />
                      {level.value}. {level.label}
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}
          
          {(activeTab === 'money-flows' || activeTab === 'awards') && (
            <>
              <div className="filter-group">
                <label>Amount Range:</label>
                <div className="range-inputs">
                  <input
                    type="number"
                    placeholder="Min ($)"
                    value={minAmount}
                    onChange={(e) => { setMinAmount(e.target.value); setCurrentPage(1); }}
                  />
                  <span>to</span>
                  <input
                    type="number"
                    placeholder="Max ($)"
                    value={maxAmount}
                    onChange={(e) => { setMaxAmount(e.target.value); setCurrentPage(1); }}
                  />
                </div>
              </div>
              
              <div className="filter-group">
                <label>Date Range:</label>
                <div className="range-inputs">
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => { setStartDate(e.target.value); setCurrentPage(1); }}
                  />
                  <span>to</span>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => { setEndDate(e.target.value); setCurrentPage(1); }}
                  />
                </div>
              </div>
            </>
          )}
          
          {(activeTab === 'awards' || activeTab === 'foia') && (
            <div className="filter-group">
              <label>Agency:</label>
              <input
                type="text"
                placeholder="Filter by agency name..."
                value={agencyFilter}
                onChange={(e) => { setAgencyFilter(e.target.value); setCurrentPage(1); }}
              />
            </div>
          )}
        </div>
      )}

      {/* Results Info Bar */}
      <div className="results-bar">
        <div className="results-count">
          {loading ? (
            <span>Loading...</span>
          ) : (
            <span>
              Showing {getCurrentDataLength()} result{getCurrentDataLength() !== 1 ? 's' : ''}
              {debouncedSearchTerm && ` for "${debouncedSearchTerm}"`}
            </span>
          )}
        </div>
        <div className="results-controls">
          <label>
            Show:
            <select 
              value={itemsPerPage} 
              onChange={(e) => { setItemsPerPage(parseInt(e.target.value)); setCurrentPage(1); }}
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </label>
          <div className="pagination">
            <button 
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(p => p - 1)}
              className="btn btn-sm"
            >
              ← Prev
            </button>
            <span className="page-info">Page {currentPage}</span>
            <button 
              disabled={getCurrentDataLength() < itemsPerPage}
              onClick={() => setCurrentPage(p => p + 1)}
              className="btn btn-sm"
            >
              Next →
            </button>
          </div>
        </div>
      </div>

      {/* Data Tables */}
      <div className="card">
        {loading ? (
          <SkeletonLoader type="table" />
        ) : (
          <div className="fade-in" role="tabpanel">
            {activeTab === 'entities' && (
              <>
                {sortedData.entities.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">🔍</div>
                    <h3>No entities found</h3>
                    <p>Try adjusting your search or filters, or browse all entities.</p>
                    <button className="btn btn-primary" onClick={handleClearFilters}>
                      Clear Filters
                    </button>
                  </div>
                ) : (
                  <div className="data-table-wrapper">
                    <table className="data-table" role="table" aria-label="Entities table">
                      <thead>
                        <tr>
                          <SortableHeader column="display_name" label="Display Name" />
                          <SortableHeader column="entity_type" label="Type" />
                          <SortableHeader column="intel_stack_level" label="Intel Level" />
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sortedData.entities.map((entity) => (
                          <tr key={entity.entity_id} id={`row-entity-${entity.entity_id}`} className="clickable-row">
                            <td>
                              <HighlightText text={entity.display_name} highlight={debouncedSearchTerm} />
                            </td>
                            <td>
                              <span className={`type-badge type-${entity.entity_type?.toLowerCase().replace(/\s+/g, '-')}`}>
                                {entity.entity_type || 'Unknown'}
                              </span>
                            </td>
                            <td>
                              {entity.intel_stack_level ? (
                                <span className={`intel-badge level-${entity.intel_stack_level}`}>
                                  L{entity.intel_stack_level}
                                </span>
                              ) : '-'}
                            </td>
                            <td>
                              <button 
                                className="btn btn-sm btn-outline"
                                onClick={() => navigate(`/analysis/network?highlight=${entity.entity_id}`)}
                              >
                                View Network
                              </button>
                              {entity.intel_stack_level != null && (
                                <Link
                                  to={`/analysis/pyramid?entity_id=${encodeURIComponent(entity.entity_id)}`}
                                  className="browse-pyramid-link"
                                  title="View on Pyramid"
                                  aria-label={`View ${entity.display_name} on Intelligence Stack Pyramid`}
                                >
                                  <Triangle size={18} />
                                </Link>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}

            {activeTab === 'money-flows' && (
              <>
                {sortedData.moneyFlows.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">💰</div>
                    <h3>No money flows found</h3>
                    <p>Try adjusting your search or amount filters.</p>
                    <button className="btn btn-primary" onClick={handleClearFilters}>
                      Clear Filters
                    </button>
                  </div>
                ) : (
                  <div className="data-table-wrapper">
                    <table className="data-table" role="table" aria-label="Money flows table">
                      <thead>
                        <tr>
                          <SortableHeader column="source" label="Source" />
                          <SortableHeader column="target" label="Target" />
                          <SortableHeader column="relationship" label="Relationship" />
                          <SortableHeader column="amount_usd" label="Amount" />
                          <SortableHeader column="start_date" label="Date" />
                        </tr>
                      </thead>
                      <tbody>
                        {sortedData.moneyFlows.map((flow) => (
                          <tr key={flow.id} id={`row-flow-${flow.id}`}>
                            <td>
                              <HighlightText text={flow.source} highlight={debouncedSearchTerm} />
                            </td>
                            <td>
                              <HighlightText text={flow.target} highlight={debouncedSearchTerm} />
                            </td>
                            <td>
                              <span className="relationship-badge">
                                {flow.relationship || 'N/A'}
                              </span>
                            </td>
                            <td className="amount-cell">
                              {formatCurrency(flow.amount_usd)}
                            </td>
                            <td>{flow.start_date || 'N/A'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}

            {activeTab === 'awards' && (
              <>
                {sortedData.awards.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">🏆</div>
                    <h3>No awards found</h3>
                    <p>Try adjusting your search, agency, or amount filters.</p>
                    <button className="btn btn-primary" onClick={handleClearFilters}>
                      Clear Filters
                    </button>
                  </div>
                ) : (
                  <div className="data-table-wrapper">
                    <table className="data-table" role="table" aria-label="Awards table">
                      <thead>
                        <tr>
                          <SortableHeader column="piid" label="PIID" />
                          <SortableHeader column="recipient_name" label="Recipient" />
                          <SortableHeader column="awarding_agency" label="Agency" />
                          <SortableHeader column="award_amount" label="Amount" />
                          <SortableHeader column="action_date" label="Date" />
                        </tr>
                      </thead>
                      <tbody>
                        {sortedData.awards.map((award) => (
                          <tr key={award.id} id={`row-award-${award.id}`}>
                            <td className="piid-cell">{award.piid || 'N/A'}</td>
                            <td>
                              <HighlightText text={award.recipient_name || ''} highlight={debouncedSearchTerm} />
                            </td>
                            <td>
                              <HighlightText text={award.awarding_agency || ''} highlight={debouncedSearchTerm} />
                            </td>
                            <td className="amount-cell">
                              {formatCurrency(award.award_amount)}
                            </td>
                            <td>{award.action_date || 'N/A'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}

            {activeTab === 'foia' && (
              <>
                {sortedData.foiaTargets.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">📋</div>
                    <h3>No FOIA targets found</h3>
                    <p>Try adjusting your search or agency filter.</p>
                    <button className="btn btn-primary" onClick={handleClearFilters}>
                      Clear Filters
                    </button>
                  </div>
                ) : (
                  <div className="data-table-wrapper">
                    <table className="data-table" role="table" aria-label="FOIA targets table">
                      <thead>
                        <tr>
                          <SortableHeader column="agency" label="Agency" />
                          <SortableHeader column="record_request" label="Record Request" />
                          <SortableHeader column="timeframe" label="Timeframe" />
                          <SortableHeader column="priority_score" label="Priority" />
                          <SortableHeader column="specificity_score" label="Specificity" />
                          <SortableHeader column="likelihood_score" label="Likelihood" />
                        </tr>
                      </thead>
                      <tbody>
                        {sortedData.foiaTargets.map((foia) => (
                          <tr key={foia.id} id={`row-foia-${foia.id}`}>
                            <td>
                              <HighlightText text={foia.agency} highlight={debouncedSearchTerm} />
                            </td>
                            <td className="record-request-cell">
                              <HighlightText text={foia.record_request} highlight={debouncedSearchTerm} />
                            </td>
                            <td>{foia.timeframe || 'N/A'}</td>
                            <td>
                              {foia.priority_score !== null && foia.priority_score !== undefined ? (
                                <span className={`score-badge ${foia.priority_score >= 0.7 ? 'high' : foia.priority_score >= 0.4 ? 'medium' : 'low'}`}>
                                  {(foia.priority_score * 100).toFixed(0)}%
                                </span>
                              ) : 'N/A'}
                            </td>
                            <td>
                              {foia.specificity_score !== null && foia.specificity_score !== undefined ? (
                                <span className={`score-badge ${foia.specificity_score >= 0.7 ? 'high' : foia.specificity_score >= 0.4 ? 'medium' : 'low'}`}>
                                  {(foia.specificity_score * 100).toFixed(0)}%
                                </span>
                              ) : 'N/A'}
                            </td>
                            <td>
                              {foia.likelihood_score !== null && foia.likelihood_score !== undefined ? (
                                <span className={`score-badge ${foia.likelihood_score >= 0.6 ? 'high' : foia.likelihood_score >= 0.3 ? 'medium' : 'low'}`}>
                                  {(foia.likelihood_score * 100).toFixed(0)}%
                                </span>
                              ) : 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Browse;
