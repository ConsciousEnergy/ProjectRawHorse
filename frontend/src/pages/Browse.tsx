import { useEffect, useState } from 'react';
import { getEntities, getMoneyFlows, getAwards, getFOIATargets } from '../services/api';
import type { Entity, MoneyFlow, Award, FOIATarget } from '../types';

type TabType = 'entities' | 'money-flows' | 'awards' | 'foia';

function Browse() {
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

  useEffect(() => {
    loadData();
  }, [activeTab]);

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
    <div className="browse">
      <div className="page-header">
        <h2>Browse Data</h2>
        <p>Explore entities, money flows, awards, and FOIA targets</p>
      </div>

      <div className="tabs">
        <button 
          className={activeTab === 'entities' ? 'active' : ''} 
          onClick={() => setActiveTab('entities')}
        >
          Entities
        </button>
        <button 
          className={activeTab === 'money-flows' ? 'active' : ''} 
          onClick={() => setActiveTab('money-flows')}
        >
          Money Flows
        </button>
        <button 
          className={activeTab === 'awards' ? 'active' : ''} 
          onClick={() => setActiveTab('awards')}
        >
          Awards
        </button>
        <button 
          className={activeTab === 'foia' ? 'active' : ''} 
          onClick={() => setActiveTab('foia')}
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
                <option value="Non-Profit">Non-Profit</option>
                <option value="Research Institution">Research Institution</option>
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
          <div className="loading">Loading...</div>
        ) : (
          <>
            {activeTab === 'entities' && (
              <table className="data-table">
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
            )}

            {activeTab === 'money-flows' && (
              <table className="data-table">
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
            )}

            {activeTab === 'awards' && (
              <table className="data-table">
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
            )}

            {activeTab === 'foia' && (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Agency</th>
                    <th>Record Request</th>
                    <th>Timeframe</th>
                    <th>Relevance</th>
                  </tr>
                </thead>
                <tbody>
                  {foiaTargets.map((foia) => (
                    <tr key={foia.id}>
                      <td>{foia.agency}</td>
                      <td>{foia.record_request}</td>
                      <td>{foia.timeframe || 'N/A'}</td>
                      <td>{foia.relevance || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Browse;
