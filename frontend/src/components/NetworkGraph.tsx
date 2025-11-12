import React, { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { forceCollide } from 'd3-force';
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

  // Configure forces after data loads for better spacing
  useEffect(() => {
    if (fgRef.current && graphData.nodes.length > 0) {
      const fg = fgRef.current;
      
      // Stronger repulsion to prevent clustering
      fg.d3Force('charge').strength(-600).distanceMax(500);
      
      // Longer link distance for more spread
      fg.d3Force('link').distance(150);
      
      // Add collision force to prevent node overlap
      fg.d3Force('collision', forceCollide()
        .radius((node: any) => (node.val || 6) + 30)
        .strength(0.9)
      );
      
      // Reheat simulation to apply new forces
      fg.d3ReheatSimulation();
    }
  }, [graphData]);

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
    // Enhanced color scheme with more types
    const colors: Record<string, string> = {
      'Corporation': '#5B4FFF',           // Purple (primary)
      'Government Agency': '#FFD700',     // Gold (accent)
      'Investment Firm': '#FF6B9D',       // Pink
      'Research Institution': '#FFA500',  // Orange
      'Non-Profit': '#7B6FFF',           // Light purple
      'Organization': '#00D4AA',          // Teal
      'Unknown': '#8B8B8B',               // Gray
      'default': '#9B9B9B'                // Default gray
    };
    return colors[node.type || 'default'] || colors.default;
  };

  const getNodeSize = (node: ForceGraphNode) => {
    // Use value if provided, otherwise calculate from connections
    return node.val || 6;  // Slightly larger default
  };

  // Get unique types from actual data
  const uniqueTypes = React.useMemo(() => {
    const types = new Set(graphData.nodes.map(n => n.type).filter(Boolean));
    return Array.from(types).sort();
  }, [graphData.nodes]);

  // Color map for legend
  const colorMap: Record<string, string> = {
    'Corporation': '#5B4FFF',
    'Government Agency': '#FFD700',
    'Investment Firm': '#FF6B9D',
    'Research Institution': '#FFA500',
    'Non-Profit': '#7B6FFF',
    'Organization': '#00D4AA',
    'Unknown': '#8B8B8B',
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
        <button onClick={() => fgRef.current?.zoom(1.5, 400)}>
          Zoom In
        </button>
        <button onClick={() => fgRef.current?.zoom(0.5, 400)}>
          Zoom Out
        </button>
      </div>
      
      <div className="graph-legend">
        <h5 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#999' }}>Entity Types:</h5>
        {uniqueTypes.map(type => (
          <div key={type} className="legend-item">
            <span className="legend-color" style={{ backgroundColor: colorMap[type] || '#9B9B9B' }}></span>
            <span>{type}</span>
          </div>
        ))}
      </div>

      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel={(node: any) => `${node.name}${node.type ? ` (${node.type})` : ''}`}
        nodeColor={getNodeColor}
        nodeVal={getNodeSize}
        linkLabel="label"
        linkColor={() => 'rgba(91, 79, 255, 0.4)'}
        linkWidth={2}
        linkDirectionalParticles={4}
        linkDirectionalParticleWidth={2.5}
        linkDirectionalParticleSpeed={0.006}
        backgroundColor="#ffffff"
        // Improved force simulation for better spacing
        d3AlphaDecay={0.01}
        d3VelocityDecay={0.15}
        warmupTicks={100}
        cooldownTicks={200}
        cooldownTime={5000}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.name;
          const nodeSize = getNodeSize(node);
          const fontSize = Math.max(10, 14/globalScale);
          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.3);

          // Draw node circle with border
          ctx.beginPath();
          ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI, false);
          ctx.fillStyle = getNodeColor(node);
          ctx.fill();
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
          ctx.lineWidth = 1.5;
          ctx.stroke();
          
          // Only draw label if zoomed in enough
          if (globalScale > 0.5) {
            // Draw label background
            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
            ctx.shadowBlur = 4;
            ctx.fillRect(
              node.x - bckgDimensions[0] / 2,
              node.y + nodeSize + 4,
              bckgDimensions[0],
              bckgDimensions[1]
            );
            ctx.shadowBlur = 0;

            // Draw label text
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillStyle = '#1a1a1a';
            ctx.fillText(label, node.x, node.y + nodeSize + 6);
          }
        }}
        onNodeClick={(node) => {
          // Zoom to node
          fgRef.current?.centerAt(node.x, node.y, 1000);
          fgRef.current?.zoom(2, 1000);
        }}
        onNodeHover={(node) => {
          document.body.style.cursor = node ? 'pointer' : 'default';
        }}
        onEngineStop={() => fgRef.current?.zoomToFit(400, 50)}
        minZoom={0.3}
        maxZoom={8}
      />

      <div className="graph-stats">
        <span>{graphData.nodes.length} nodes</span>
        <span>{graphData.links.length} connections</span>
      </div>
    </div>
  );
}

export default NetworkGraph;

