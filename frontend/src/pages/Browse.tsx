import { useEffect, useState } from 'react';
import { getEntities, getMoneyFlows, getAwards, getFOIATargets } from '../services/api';
import type { Entity, MoneyFlow, Award, FOIATarget } from '../types';

type TabType = 'entities' | 'money-flows' | 'awards' | 'foia';

function Browse() {
  const [activeTab, setActiveTab] = useState<TabType>('entities');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Data states
  const [entities, setEntities] = useState<Entity[]>([]);
  const [moneyFlows, setMoneyFlows] = useState<MoneyFlow[]>([]);
  const [awards, setAwards] = useState<Award[]>([]);
  const [foiaTargets, setFOIATargets] = useState<FOIATarget[]>([]);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'entities':
          const entitiesData = await getEntities({ limit: 100 });
          setEntities(entitiesData);
          break;
        case 'money-flows':
          const flowsData = await getMoneyFlows({ limit: 100 });
          setMoneyFlows(flowsData);
          break;
        case 'awards':
          const awardsData = await getAwards({ limit: 100 });
          setAwards(awardsData);
          break;
        case 'foia':
          const foiaData = await getFOIATargets({ limit: 100 });
          setFOIATargets(foiaData);
          break;
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      loadData();
      return;
    }
    
    setLoading(true);
    try {
      switch (activeTab) {
        case 'entities':
          const entitiesData = await getEntities({ search: searchTerm });
          setEntities(entitiesData);
          break;
        case 'money-flows':
          const flowsData = await getMoneyFlows({ search: searchTerm });
          setMoneyFlows(flowsData);
          break;
        case 'awards':
          const awardsData = await getAwards({ search: searchTerm });
          setAwards(awardsData);
          break;
        case 'foia':
          const foiaData = await getFOIATargets({ search: searchTerm });
          setFOIATargets(foiaData);
          break;
      }
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
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
      </div>

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
