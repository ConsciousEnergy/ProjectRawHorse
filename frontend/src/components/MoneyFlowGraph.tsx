import React, { useEffect, useState, useCallback, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { getMoneyFlowGraph } from '../services/api';
import './MoneyFlowGraph.css';

interface ForceGraphNode {
  id: string;
  name: string;
  type: string;
  val?: number;
  full_name?: string;
  x?: number;
  y?: number;
}

interface ForceGraphLink {
  source: string | ForceGraphNode;
  target: string | ForceGraphNode;
  value?: number;
  label?: string;
}

const MoneyFlowGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<{ nodes: ForceGraphNode[]; links: ForceGraphLink[] }>({
    nodes: [],
    links: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [minAmount, setMinAmount] = useState<number>(0);
  const fgRef = useRef<any>();

  const loadGraphData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const responseData = await getMoneyFlowGraph(minAmount > 0 ? minAmount : undefined);
      
      // Safely handle response data
      if (!responseData || !responseData.nodes || !responseData.edges) {
        console.warn('Invalid response structure:', responseData);
        setGraphData({ nodes: [], links: [] });
        return;
      }
      
      // Convert to force graph format
      const nodes: ForceGraphNode[] = (responseData.nodes || []).map(n => ({
        id: n.id,
        name: n.name,
        type: n.type || 'Unknown',
        val: n.value || 10,
        full_name: n.full_name
      }));

      const links: ForceGraphLink[] = (responseData.edges || []).map(e => ({
        source: e.source,
        target: e.target,
        value: e.value || 0,
        label: e.label
      }));

      setGraphData({ nodes, links });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load money flow graph';
      setError(msg);
      console.error('Error loading money flow graph:', err);
    } finally {
      setLoading(false);
    }
  }, [minAmount]);

  useEffect(() => {
    loadGraphData();
  }, [loadGraphData]);

  // Color map for entity types (matching NetworkGraph)
  const colorMap: Record<string, string> = {
    'Corporation': '#5B4FFF',
    'Government Agency': '#FFD700',
    'Investment Firm': '#FF6B9D',
    'Research Institution': '#FFA500',
    'FFRDC': '#4169E1',
    'National Laboratory': '#20B2AA',
    'Academic Institution': '#9370DB',
    'Non-Profit': '#7B6FFF',
    'Organization': '#00D4AA',
    'Individual': '#FF8C00',
    'Unknown': '#8B8B8B',
    'default': '#9B9B9B'
  };

  const getNodeColor = (node: ForceGraphNode) => {
    return colorMap[node.type] || colorMap.default;
  };

  // Get edge color based on flow amount (green for high, blue for low)
  const getEdgeColor = (link: ForceGraphLink) => {
    const value = link.value || 0;
    if (value === 0) return '#666666';
    
    // Find min/max values for normalization
    const values = graphData.links.map(l => l.value || 0).filter(v => v > 0);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    
    if (minVal === maxVal) return '#00AA00';
    
    // Normalize to 0-1
    const normalized = (value - minVal) / (maxVal - minVal);
    
    // Interpolate from blue (low) to green (high)
    const r = Math.round(0 + (0 - 0) * normalized);
    const g = Math.round(100 + (170 - 100) * normalized);
    const b = Math.round(200 + (0 - 200) * normalized);
    
    return `rgb(${r}, ${g}, ${b})`;
  };

  // Get edge width based on flow amount (log scale)
  const getEdgeWidth = (link: ForceGraphLink) => {
    const value = link.value || 0;
    if (value === 0) return 1;
    
    // Log scale for edge width
    const width = 1 + Math.log10(value) * 0.5;
    return Math.max(1, Math.min(width, 8));  // Clamp between 1 and 8
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    if (amount >= 1000000000) {
      return `$${(amount / 1000000000).toFixed(2)}B`;
    } else if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(2)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(2)}K`;
    }
    return `$${amount.toFixed(2)}`;
  };

  // Zoom controls
  const handleZoomToFit = () => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400);
    }
  };

  const handleCenterGraph = () => {
    if (fgRef.current) {
      fgRef.current.centerAt(0, 0, 1000);
      fgRef.current.zoom(1, 1000);
    }
  };

  const handleZoomIn = () => {
    if (fgRef.current) {
      const currentZoom = fgRef.current.zoom();
      fgRef.current.zoom(currentZoom * 1.3, 300);
    }
  };

  const handleZoomOut = () => {
    if (fgRef.current) {
      const currentZoom = fgRef.current.zoom();
      fgRef.current.zoom(currentZoom * 0.7, 300);
    }
  };

  // Get unique types for legend
  const uniqueTypes = React.useMemo(() => {
    const types = new Set(graphData.nodes.map(n => n.type).filter(Boolean));
    return Array.from(types).sort();
  }, [graphData.nodes]);

  if (loading) {
    return (
      <div className="money-flow-graph-container">
        <div className="loading">Loading money flow graph...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="money-flow-graph-container">
        <div className="error">{error}</div>
        <button onClick={loadGraphData} className="retry-button">Retry</button>
      </div>
    );
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="money-flow-graph-container">
        <div className="empty-state">
          <p>No money flow data available.</p>
          {minAmount > 0 && (
            <p>Try reducing the minimum amount filter.</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="money-flow-graph-container">
      <div className="graph-header">
        <h3>💰 Weighted Money Flow Graph</h3>
        <p className="graph-description">
          Explore financial flows between entities. Edge thickness represents transaction amount.
          Green = high amounts, Blue = low amounts.
        </p>
      </div>

      <div className="graph-controls">
        <div className="filter-group">
          <label htmlFor="min-amount">Minimum Amount:</label>
          <input
            id="min-amount"
            type="number"
            min="0"
            step="100000"
            value={minAmount}
            onChange={(e) => setMinAmount(Number(e.target.value))}
            placeholder="0"
          />
          <button onClick={loadGraphData} className="btn-secondary">Apply Filter</button>
        </div>

        <div className="zoom-controls">
          <button onClick={handleZoomToFit} className="zoom-btn" title="Fit to View">
            📐 Fit
          </button>
          <button onClick={handleCenterGraph} className="zoom-btn" title="Center">
            🎯 Center
          </button>
          <button onClick={handleZoomIn} className="zoom-btn" title="Zoom In">
            ➕
          </button>
          <button onClick={handleZoomOut} className="zoom-btn" title="Zoom Out">
            ➖
          </button>
        </div>
      </div>

      <div className="graph-stats">
        <span className="stat-item">
          <strong>{graphData.nodes.length}</strong> entities
        </span>
        <span className="stat-item">
          <strong>{graphData.links.length}</strong> flow connections
        </span>
        <span className="stat-item">
          <strong>{formatCurrency(graphData.links.reduce((sum, l) => sum + (l.value || 0), 0))}</strong> total
        </span>
      </div>

      <div className="graph-canvas">
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel={(node: any) => {
            const n = node as ForceGraphNode;
            const fullName = n.full_name ? `${n.name} - ${n.full_name}` : n.name;
            return `${fullName} (${n.type})`;
          }}
          nodeColor={getNodeColor}
          nodeVal={(node: any) => (node as ForceGraphNode).val || 10}
          nodeCanvasObject={(node: any, ctx, globalScale) => {
            const n = node as ForceGraphNode;
            const label = n.name;
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = getNodeColor(n);
            
            // Draw circle
            const size = (n.val || 10) / 2;
            ctx.beginPath();
            ctx.arc(n.x || 0, n.y || 0, size, 0, 2 * Math.PI);
            ctx.fill();
            
            // Draw label
            ctx.fillStyle = '#ffffff';
            ctx.fillText(label, n.x || 0, (n.y || 0) + size + fontSize + 2);
          }}
          linkLabel={(link: any) => {
            const l = link as ForceGraphLink;
            const amount = formatCurrency(l.value || 0);
            const label = l.label || 'Money Flow';
            return `${label}\nAmount: ${amount}`;
          }}
          linkColor={getEdgeColor}
          linkWidth={getEdgeWidth}
          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={1}
          linkDirectionalParticles={2}
          linkDirectionalParticleWidth={(link: any) => getEdgeWidth(link as ForceGraphLink)}
          linkDirectionalParticleSpeed={0.003}
          linkCurvature={0.15}
          onNodeClick={(node: any) => {
            if (fgRef.current) {
              fgRef.current.centerAt(node.x, node.y, 1000);
              fgRef.current.zoom(2, 1000);
            }
          }}
          cooldownTicks={100}
          onEngineStop={() => fgRef.current?.zoomToFit(400)}
        />
      </div>

      <div className="graph-legend">
        <h4>Entity Types</h4>
        <div className="legend-items">
          {uniqueTypes.map(type => (
            <div key={type} className="legend-item">
              <span
                className="legend-color"
                style={{ backgroundColor: colorMap[type] || colorMap.default }}
              ></span>
              <span className="legend-label">{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MoneyFlowGraph;

