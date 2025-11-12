import { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { getEntityGraph } from '../services/api';
import type { GraphData as APIGraphData, GraphNode } from '../types';
import './NetworkGraph.css';

interface ForceGraphNode extends GraphNode {
  val?: number;
}

interface ForceGraphLink {
  source: string;
  target: string;
  label?: string;
}

interface ForceGraphData {
  nodes: ForceGraphNode[];
  links: ForceGraphLink[];
}

function NetworkGraph() {
  const [graphData, setGraphData] = useState<ForceGraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fgRef = useRef<any>();

  useEffect(() => {
    loadGraphData();
  }, []);

  const loadGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data: APIGraphData = await getEntityGraph();
      
      // Convert API response (edges) to ForceGraph format (links)
      const forceGraphData: ForceGraphData = {
        nodes: data.nodes.map(node => ({
          ...node,
          val: node.value || 5,
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.label,
        })),
      };
      
      setGraphData(forceGraphData);
    } catch (err) {
      setError('Failed to load graph data');
      console.error('Error loading graph:', err);
    } finally {
      setLoading(false);
    }
  };

  const getNodeColor = (node: ForceGraphNode) => {
    // Purple & gold color scheme
    const colors: Record<string, string> = {
      'Corporation': '#5B4FFF',
      'Government Agency': '#FFD700',
      'Non-Profit': '#7B6FFF',
      'Research Institution': '#FFA500',
      'default': '#8B8B8B'
    };
    return colors[node.type || 'default'] || colors.default;
  };

  const getNodeSize = (node: ForceGraphNode) => {
    return node.val || 5;
  };

  if (loading) {
    return (
      <div className="network-graph-container">
        <div className="loading">Loading network graph...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="network-graph-container">
        <div className="error">{error}</div>
        <button onClick={loadGraphData}>Retry</button>
      </div>
    );
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="network-graph-container">
        <div className="empty">No network data available</div>
      </div>
    );
  }

  return (
    <div className="network-graph-container">
      <div className="graph-controls">
        <button onClick={() => fgRef.current?.zoomToFit(400)}>
          Fit to View
        </button>
        <button onClick={() => fgRef.current?.centerAt(0, 0, 1000)}>
          Center
        </button>
      </div>
      
      <div className="graph-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#5B4FFF' }}></span>
          <span>Corporation</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#FFD700' }}></span>
          <span>Government Agency</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#7B6FFF' }}></span>
          <span>Non-Profit</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#FFA500' }}></span>
          <span>Research Institution</span>
        </div>
      </div>

      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel="name"
        nodeColor={getNodeColor}
        nodeVal={getNodeSize}
        linkLabel="label"
        linkColor={() => 'rgba(91, 79, 255, 0.3)'}
        linkWidth={2}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={2}
        backgroundColor="#ffffff"
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12/globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

          // Draw node circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, getNodeSize(node), 0, 2 * Math.PI, false);
          ctx.fillStyle = getNodeColor(node);
          ctx.fill();
          
          // Draw label background
          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
          ctx.fillRect(
            node.x - bckgDimensions[0] / 2,
            node.y + getNodeSize(node) + 2,
            bckgDimensions[0],
            bckgDimensions[1]
          );

          // Draw label text
          ctx.textAlign = 'center';
          ctx.textBaseline = 'top';
          ctx.fillStyle = '#1a1a1a';
          ctx.fillText(label, node.x, node.y + getNodeSize(node) + 4);
        }}
        onNodeClick={(node) => {
          console.log('Clicked node:', node);
          // Could add modal or detail panel here
        }}
        cooldownTicks={100}
        onEngineStop={() => fgRef.current?.zoomToFit(400)}
      />

      <div className="graph-stats">
        <span>{graphData.nodes.length} nodes</span>
        <span>{graphData.links.length} connections</span>
      </div>
    </div>
  );
}

export default NetworkGraph;

