import { useEffect, useState } from 'react';
import { getMoneyFlowGraph, getFinancialFlows, getTimeline } from '../services/api';

function Analysis() {
  const [graphData, setGraphData] = useState<any>(null);
  const [financialData, setFinancialData] = useState<any>(null);
  const [timelineData, setTimelineData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = async () => {
    try {
      const [graph, financial, timeline] = await Promise.all([
        getMoneyFlowGraph(1000000),
        getFinancialFlows(),
        getTimeline()
      ]);
      
      setGraphData(graph);
      setFinancialData(financial);
      setTimelineData(timeline);
    } catch (error) {
      console.error('Error loading analysis data:', error);
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

  if (loading) {
    return <div className="loading">Loading analysis data...</div>;
  }

  return (
    <div className="analysis">
      <div className="page-header">
        <h2>Analysis</h2>
        <p>Visualize relationships and financial networks</p>
      </div>

      <div className="card">
        <h3>Network Graph</h3>
        <p>
          Showing {graphData?.nodes?.length || 0} entities and {graphData?.edges?.length || 0} money flows 
          (minimum $1M). For detailed interactive visualization, use external tools like Gephi with exported data.
        </p>
        <div style={{ padding: '40px', textAlign: 'center', backgroundColor: '#1a1a1a', borderRadius: '8px' }}>
          <p>Interactive D3.js network graph would be rendered here</p>
          <p style={{ fontSize: '0.9rem', color: '#888' }}>
            Node count: {graphData?.nodes?.length || 0} | Edge count: {graphData?.edges?.length || 0}
          </p>
        </div>
      </div>

      <div className="card">
        <h3>Top Recipients (Inflows)</h3>
        <table className="data-table">
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

      <div className="card">
        <h3>Top Sources (Outflows)</h3>
        <table className="data-table">
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

      <div className="card">
        <h3>Timeline</h3>
        <table className="data-table">
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
  );
}

export default Analysis;
