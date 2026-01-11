import { useEffect, useState } from 'react';
import { getFinancialFlows, getTimeline } from '../services/api';
import NetworkGraph from '../components/NetworkGraph';
import SkeletonLoader from '../components/SkeletonLoader';

function Analysis() {
  const [financialData, setFinancialData] = useState<any>(null);
  const [timelineData, setTimelineData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = async () => {
    try {
      setError(null);
      const [financial, timeline] = await Promise.all([
        getFinancialFlows(),
        getTimeline()
      ]);
      
      setFinancialData(financial);
      setTimelineData(timeline);
    } catch (error) {
      console.error('Error loading analysis data:', error);
      setError('Failed to load analysis data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="analysis fade-in" role="main" aria-label="Analysis page">
      <div className="page-header">
        <h1>Analysis</h1>
        <p>Visualize relationships and financial networks</p>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
          <button onClick={loadAnalysisData} className="btn btn-secondary" style={{ marginLeft: '12px', padding: '6px 12px' }}>
            Retry
          </button>
        </div>
      )}

      <div className="card">
        <h3>Entity Network Graph</h3>
        <p>
          Interactive visualization of entity relationships. Click and drag nodes to explore connections.
          Use controls to zoom and center the view.
        </p>
        <NetworkGraph />
      </div>

      {loading ? (
        <>
          <div className="card">
            <h3>Top Recipients (Inflows)</h3>
            <SkeletonLoader type="table" />
          </div>
          <div className="card">
            <h3>Top Sources (Outflows)</h3>
            <SkeletonLoader type="table" />
          </div>
          <div className="card">
            <h3>Timeline</h3>
            <SkeletonLoader type="table" />
          </div>
        </>
      ) : (
        <>
          <div className="card fade-in">
            <h3>Top Recipients (Inflows)</h3>
            <div className="data-table-wrapper">
              <table className="data-table" role="table" aria-label="Top recipients by inflows">
                <thead>
                  <tr>
                    <th>Entity</th>
                    <th>Total Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {financialData?.inflows?.slice(0, 10).map((item: any, idx: number) => (
                    <tr key={idx}>
                      <td>{item.entity}</td>
                      <td>{formatCurrency(item.amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card fade-in">
            <h3>Top Sources (Outflows)</h3>
            <div className="data-table-wrapper">
              <table className="data-table" role="table" aria-label="Top sources by outflows">
                <thead>
                  <tr>
                    <th>Entity</th>
                    <th>Total Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {financialData?.outflows?.slice(0, 10).map((item: any, idx: number) => (
                    <tr key={idx}>
                      <td>{item.entity}</td>
                      <td>{formatCurrency(item.amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card fade-in">
            <h3>Timeline</h3>
            <div className="data-table-wrapper">
              <table className="data-table" role="table" aria-label="Financial timeline">
                <thead>
                  <tr>
                    <th>Year</th>
                    <th>Transaction Count</th>
                    <th>Total Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {timelineData?.timeline?.map((item: any) => (
                    <tr key={item.year}>
                      <td>{item.year}</td>
                      <td>{item.count}</td>
                      <td>{formatCurrency(item.total_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Analysis;
