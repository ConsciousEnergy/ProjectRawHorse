import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getEntities, getMoneyFlows, getAwards, getFOIATargets } from '../services/api';
import type { Entity, MoneyFlow, Award, FOIATarget } from '../types';
import SkeletonLoader from '../components/SkeletonLoader';
import { useDataContext } from '../contexts/DataContext';

type TabType = 'entities' | 'money-flows' | 'awards' | 'foia';

function Browse() {
  const [searchParams] = useSearchParams();
  const { dataVersion } = useDataContext();
  const [activeTab, setActiveTab] = useState<TabType>('entities');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Advanced filter states
  const [entityTypeFilter, setEntityTypeFilter] = useState('');
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Data states
  const [entities, setEntities] = useState<Entity[]>([]);
  const [moneyFlows, setMoneyFlows] = useState<MoneyFlow[]>([]);
  const [awards, setAwards] = useState<Award[]>([]);
  const [foiaTargets, setFOIATargets] = useState<FOIATarget[]>([]);

  // Initialize from URL parameters
  useEffect(() => {
    const tab = searchParams.get('tab') as TabType;
    const search = searchParams.get('search');
    const highlight = searchParams.get('highlight');
    
    if (tab && ['entities', 'money-flows', 'awards', 'foia'].includes(tab)) {
      setActiveTab(tab);
    }
    
    if (search) {
      setSearchTerm(search);
    }
    
    // Store highlight ID for later use (could add visual highlighting)
    if (highlight) {
      sessionStorage.setItem('highlightId', highlight);
    }
  }, [searchParams]);

  useEffect(() => {
    loadData();
  }, [activeTab, searchTerm, dataVersion]);

  const buildParams = () => {
    const params: any = { limit: 100 };
    
    if (searchTerm.trim()) {
      params.search = searchTerm;
    }
    
    if (activeTab === 'entities' && entityTypeFilter) {
      params.entity_type = entityTypeFilter;
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
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadData();
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setEntityTypeFilter('');
    setMinAmount('');
    setMaxAmount('');
    setStartDate('');
    setEndDate('');
    loadData();
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="browse" role="main" aria-label="Browse page">
      <div className="page-header">
        <h1>Browse Data</h1>
        <p>Explore entities, money flows, awards, and FOIA targets</p>
      </div>

      <div className="tabs" role="tablist" aria-label="Data type tabs">
        <button 
          className={activeTab === 'entities' ? 'active' : ''} 
          onClick={() => setActiveTab('entities')}
          role="tab"
          aria-selected={activeTab === 'entities'}
          aria-controls="entities-panel"
          id="entities-tab"
        >
          Entities
        </button>
        <button 
          className={activeTab === 'money-flows' ? 'active' : ''} 
          onClick={() => setActiveTab('money-flows')}
          role="tab"
          aria-selected={activeTab === 'money-flows'}
          aria-controls="money-flows-panel"
          id="money-flows-tab"
        >
          Money Flows
        </button>
        <button 
          className={activeTab === 'awards' ? 'active' : ''} 
          onClick={() => setActiveTab('awards')}
          role="tab"
          aria-selected={activeTab === 'awards'}
          aria-controls="awards-panel"
          id="awards-tab"
        >
          Awards
        </button>
        <button 
          className={activeTab === 'foia' ? 'active' : ''} 
          onClick={() => setActiveTab('foia')}
          role="tab"
          aria-selected={activeTab === 'foia'}
          aria-controls="foia-panel"
          id="foia-tab"
        >
          FOIA Targets
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch} className="btn btn-primary">Search</button>
        <button onClick={() => setShowFilters(!showFilters)} className="btn btn-secondary">
          {showFilters ? 'Hide Filters' : 'Show Filters'}
        </button>
        <button onClick={handleClearFilters} className="btn btn-secondary">Clear All</button>
      </div>

      {showFilters && (
        <div className="filters-panel">
          <h4>Advanced Filters</h4>
          
          {activeTab === 'entities' && (
            <div className="filter-group">
              <label>Entity Type:</label>
              <select value={entityTypeFilter} onChange={(e) => setEntityTypeFilter(e.target.value)}>
                <option value="">All Types</option>
                <option value="Corporation">Corporation</option>
                <option value="Government Agency">Government Agency</option>
                <option value="Individual">Individual</option>
                <option value="Non-Profit">Non-Profit</option>
                <option value="Research Institution">Research Institution</option>
                <option value="Facility">Facility</option>
                <option value="Program">Program</option>
                <option value="Organization">Organization</option>
                <option value="Investment Firm">Investment Firm</option>
              </select>
            </div>
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
                    onChange={(e) => setMinAmount(e.target.value)}
                  />
                  <span>to</span>
                  <input
                    type="number"
                    placeholder="Max ($)"
                    value={maxAmount}
                    onChange={(e) => setMaxAmount(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="filter-group">
                <label>Date Range:</label>
                <div className="range-inputs">
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                  <span>to</span>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>
            </>
          )}
          
          <button onClick={handleSearch} className="btn btn-primary">Apply Filters</button>
        </div>
      )}

      <div className="card">
        {loading ? (
          <SkeletonLoader type="table" />
        ) : (
          <div className="fade-in" role="tabpanel" aria-labelledby={`${activeTab}-tab`} id={`${activeTab}-panel`}>
          {activeTab === 'entities' && (
            <>
              {entities.length === 0 ? (
                <div className="empty-state">
                  <p>No entities found. Try adjusting your search or filters.</p>
                </div>
              ) : (
                <div className="data-table-wrapper">
                  <table className="data-table" role="table" aria-label="Entities table">
                    <thead>
                      <tr>
                        <th>Entity ID</th>
                        <th>Display Name</th>
                        <th>Normalized Name</th>
                        <th>Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {entities.map((entity) => (
                        <tr key={entity.entity_id}>
                          <td>{entity.entity_id}</td>
                          <td>{entity.display_name}</td>
                          <td>{entity.normalized_name}</td>
                          <td>{entity.entity_type || 'N/A'}</td>
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
                {moneyFlows.length === 0 ? (
                  <div className="empty-state">
                    <p>No money flows found. Try adjusting your search or filters.</p>
                  </div>
                ) : (
                  <div className="data-table-wrapper">
                    <table className="data-table" role="table" aria-label="Money flows table">
                      <thead>
                        <tr>
                          <th>Source</th>
                          <th>Target</th>
                          <th>Relationship</th>
                          <th>Amount</th>
                          <th>Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {moneyFlows.map((flow) => (
                          <tr key={flow.id}>
                            <td>{flow.source}</td>
                            <td>{flow.target}</td>
                            <td>{flow.relationship || 'N/A'}</td>
                            <td>{formatCurrency(flow.amount_usd)}</td>
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
                {awards.length === 0 ? (
                  <div className="empty-state">
                    <p>No awards found. Try adjusting your search or filters.</p>
                  </div>
                ) : (
                  <div className="data-table-wrapper">
                    <table className="data-table" role="table" aria-label="Awards table">
                      <thead>
                        <tr>
                          <th>PIID</th>
                          <th>Recipient</th>
                          <th>Agency</th>
                          <th>Amount</th>
                          <th>Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {awards.map((award) => (
                          <tr key={award.id}>
                            <td>{award.piid || 'N/A'}</td>
                            <td>{award.recipient_name || 'N/A'}</td>
                            <td>{award.awarding_agency || 'N/A'}</td>
                            <td>{formatCurrency(award.award_amount)}</td>
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
                {foiaTargets.length === 0 ? (
                  <div className="empty-state">
                    <p>No FOIA targets found. Try adjusting your search or filters.</p>
                  </div>
                ) : (
                  <div className="data-table-wrapper">
                    <table className="data-table" role="table" aria-label="FOIA targets table">
                      <thead>
                        <tr>
                          <th>Agency</th>
                          <th>Record Request</th>
                          <th>Timeframe</th>
                          <th>Priority</th>
                          <th>Specificity</th>
                          <th>Likelihood</th>
                        </tr>
                      </thead>
                      <tbody>
                        {foiaTargets.map((foia) => (
                          <tr key={foia.id}>
                            <td>{foia.agency}</td>
                            <td>{foia.record_request}</td>
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
