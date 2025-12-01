import { useEffect, useState } from 'react';
import { getFinancialFlows, getTimeline } from '../services/api';
import NetworkGraph from '../components/NetworkGraph';
import MoneyFlowGraph from '../components/MoneyFlowGraph';
import SpendingTimeline from '../components/SpendingTimeline';
import FinancialDashboard from '../components/FinancialDashboard';
import FlowTracer from '../components/FlowTracer';

function Analysis() {
  const [financialData, setFinancialData] = useState<any>(null);
  const [timelineData, setTimelineData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = async () => {
    try {
      const [financial, timeline] = await Promise.all([
        getFinancialFlows(),
        getTimeline()
      ]);
      
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
        <h3>Entity Network Graph</h3>
        <p>
          Interactive visualization of entity relationships. Click and drag nodes to explore connections.
          Use controls to zoom and center the view.
        </p>
        <NetworkGraph />
      </div>

      <div className="card">
        <MoneyFlowGraph />
      </div>

      <div className="card">
        <SpendingTimeline />
      </div>

      <div className="card">
        <FinancialDashboard />
      </div>

      <div className="card">
        <FlowTracer />
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
