import React, { useEffect, useState, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { forceCollide } from 'd3-force';
import { getEntityGraph } from '../services/api';
import type { GraphData as APIGraphData, GraphNode } from '../types';
import './NetworkGraph.css';

interface ForceGraphNode extends GraphNode {
  val?: number;
  x?: number;
  y?: number;
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
  const [viewLocked, setViewLocked] = useState(false);
  const [hasCentered, setHasCentered] = useState(false);
  const [isCentering, setIsCentering] = useState(false);
  const [showInferred, setShowInferred] = useState(true);
  const [minConnections, setMinConnections] = useState(0);
  const [rawGraphData, setRawGraphData] = useState<ForceGraphData>({ nodes: [], links: [] });
  const fgRef = useRef<any>();
  const centerTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    loadGraphData();
  }, []);

  // Center graph function
  const centerGraph = useCallback((immediate = false) => {
    if (!fgRef.current || graphData.nodes.length === 0) return;
    
    setIsCentering(true);
    const delay = immediate ? 0 : 800; // Wait for simulation to stabilize
    
    setTimeout(() => {
      if (fgRef.current) {
        // Calculate bounding box of all nodes
        const nodesWithPositions = graphData.nodes.filter(n => n.x !== undefined && n.y !== undefined);
        if (nodesWithPositions.length > 0) {
          const xs = nodesWithPositions.map(n => n.x!);
          const ys = nodesWithPositions.map(n => n.y!);
          const minX = Math.min(...xs);
          const maxX = Math.max(...xs);
          const minY = Math.min(...ys);
          const maxY = Math.max(...ys);
          
          const centerX = (minX + maxX) / 2;
          const centerY = (minY + maxY) / 2;
          
          // Center and fit to view
          fgRef.current.centerAt(centerX, centerY, 1000);
          setTimeout(() => {
            if (fgRef.current) {
              fgRef.current.zoomToFit(400, 50);
            }
          }, 100);
        } else {
          // Fallback: center at origin and fit
          fgRef.current.centerAt(0, 0, 1000);
          setTimeout(() => {
            if (fgRef.current) {
              fgRef.current.zoomToFit(400, 50);
            }
          }, 100);
        }
        setIsCentering(false);
      }
    }, delay);
  }, [graphData.nodes]);

  // Reset view to initial centered state
  const resetView = useCallback(() => {
    setHasCentered(false);
    setViewLocked(false);
    centerGraph(true);
    setTimeout(() => {
      setHasCentered(true);
    }, 1500);
  }, [centerGraph]);

  // Configure forces after data loads for better clustering
  useEffect(() => {
    if (fgRef.current && graphData.nodes.length > 0) {
      const fg = fgRef.current;
      
      // Reduced repulsion to bring nodes closer together
      // Adjust based on number of nodes for better scaling
      const nodeCount = graphData.nodes.length;
      const chargeStrength = nodeCount > 100 ? -300 : -400;
      fg.d3Force('charge').strength(chargeStrength).distanceMax(200);
      
      // Shorter link distance to keep connected nodes closer
      fg.d3Force('link').distance(80).strength(0.8);
      
      // Add collision force to prevent node overlap (smaller radius for tighter packing)
      fg.d3Force('collision', forceCollide()
        .radius((node: any) => (node.val || 6) + 15)
        .strength(0.7)
      );
      
      // Add centering force to keep graph centered
      fg.d3Force('center').strength(0.1);
      
      // Reheat simulation to apply new forces
      fg.d3ReheatSimulation();
    }
  }, [graphData]);

  // Auto-center after data loads and simulation stabilizes
  useEffect(() => {
    if (graphData.nodes.length > 0 && !hasCentered && !viewLocked && fgRef.current) {
      // Clear any existing timeout
      if (centerTimeoutRef.current) {
        clearTimeout(centerTimeoutRef.current);
      }
      
      // Wait longer for simulation to stabilize with new clustering
      centerTimeoutRef.current = setTimeout(() => {
        centerGraph();
        setHasCentered(true);
      }, 3000); // Longer delay for better clustering
    }
    
    return () => {
      if (centerTimeoutRef.current) {
        clearTimeout(centerTimeoutRef.current);
      }
    };
  }, [graphData, hasCentered, viewLocked, centerGraph]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!fgRef.current) return;
      
      // Space to center
      if (e.code === 'Space' && !e.target || (e.target as HTMLElement).tagName !== 'INPUT') {
        e.preventDefault();
        centerGraph(true);
      }
      // +/- for zoom
      else if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        fgRef.current.zoom(1.5, 400);
      }
      else if (e.key === '-') {
        e.preventDefault();
        fgRef.current.zoom(0.5, 400);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [centerGraph]);

  const loadGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data: APIGraphData = await getEntityGraph();
      
      // Convert API response to ForceGraph format (store raw data)
      const forceGraphData: ForceGraphData = {
        nodes: data.nodes.map(node => ({
          ...node,
          val: node.value || 5,
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.label,
          value: edge.value,
        })),
      };
      
      setRawGraphData(forceGraphData);
    } catch (err) {
      setError('Failed to load graph data');
      console.error('Error loading graph:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Apply filters to raw graph data
  useEffect(() => {
    if (rawGraphData.nodes.length === 0) {
      setGraphData({ nodes: [], links: [] });
      return;
    }
    
    // Calculate connection counts for filtering
    const nodeConnectionCounts = new Map<string, number>();
    rawGraphData.links.forEach(link => {
      nodeConnectionCounts.set(link.source as string, (nodeConnectionCounts.get(link.source as string) || 0) + 1);
      nodeConnectionCounts.set(link.target as string, (nodeConnectionCounts.get(link.target as string) || 0) + 1);
    });
    
    // Filter nodes by minimum connections
    const filteredNodes = rawGraphData.nodes.filter(node => {
      const connections = nodeConnectionCounts.get(node.id) || 0;
      return connections >= minConnections;
    });
    
    // Filter edges to only include those connecting visible nodes
    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = rawGraphData.links.filter(link => {
      // Optionally filter out inferred relationships
      if (!showInferred && link.label && 
          (link.label.includes('Co-Recipient') || link.label.includes('Same Industry') || link.label.includes('Award Recipient'))) {
        return false;
      }
      return visibleNodeIds.has(link.source as string) && visibleNodeIds.has(link.target as string);
    });
    
    setGraphData({
      nodes: filteredNodes,
      links: filteredEdges,
    });
  }, [rawGraphData, showInferred, minConnections]);

  // Color map - high contrast palette for better visual distinction
  const colorMap: Record<string, string> = {
    'Corporation': '#5B4FFF',           // Vibrant purple-blue
    'Government Agency': '#FF6B35',     // Bright coral-orange (high contrast)
    'Investment Firm': '#E91E63',       // Deep pink/magenta
    'Research Institution': '#FF9800',  // Bright orange
    'Non-Profit': '#9C27B0',            // Deep purple (distinct from Corporation)
    'Organization': '#00BCD4',          // Bright cyan
    'Facility': '#4CAF50',              // Vibrant green (nature/facilities)
    'Program': '#FF1744',               // Bright vivid red (high visibility)
    'Individual': '#2196F3',            // Bright blue (sky blue, distinct from cyan)
    'Unknown': '#9E9E9E',               // Light gray
    'default': '#BDBDBD'                // Default medium-light gray
  };

  const getNodeColor = (node: ForceGraphNode) => {
    // Use the single source of truth color map
    return colorMap[node.type || 'default'] || colorMap.default;
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
      <div className="graph-filters">
        <label className="filter-label">
          <input
            type="checkbox"
            checked={showInferred}
            onChange={(e) => setShowInferred(e.target.checked)}
            aria-label="Show inferred relationships"
          />
          <span>Show Inferred Connections</span>
        </label>
        <label className="filter-label">
          <span>Min Connections:</span>
          <input
            type="number"
            min="0"
            max="10"
            value={minConnections}
            onChange={(e) => setMinConnections(parseInt(e.target.value) || 0)}
            aria-label="Minimum connections filter"
            style={{ width: '60px', marginLeft: '8px' }}
          />
        </label>
      </div>
      
      <div className="graph-controls" role="toolbar" aria-label="Graph controls">
        <button
          onClick={() => fgRef.current?.zoomToFit(400, 50)}
          aria-label="Fit graph to view"
          title="Fit to View"
        >
          <span className="button-icon">⛶</span>
          <span className="button-label">Fit</span>
        </button>
        <button
          onClick={() => centerGraph(true)}
          aria-label="Center graph"
          title="Center (Space)"
        >
          <span className="button-icon">⟲</span>
          <span className="button-label">Center</span>
        </button>
        <button
          onClick={resetView}
          aria-label="Reset view to initial state"
          title="Reset View"
        >
          <span className="button-icon">↻</span>
          <span className="button-label">Reset</span>
        </button>
        <button
          onClick={() => fgRef.current?.zoom(1.5, 400)}
          aria-label="Zoom in"
          title="Zoom In (+)"
        >
          <span className="button-icon">+</span>
          <span className="button-label">In</span>
        </button>
        <button
          onClick={() => fgRef.current?.zoom(0.5, 400)}
          aria-label="Zoom out"
          title="Zoom Out (-)"
        >
          <span className="button-icon">−</span>
          <span className="button-label">Out</span>
        </button>
        <button
          onClick={() => {
            setViewLocked(!viewLocked);
            if (!viewLocked) {
              // When locking, stop auto-centering
              if (centerTimeoutRef.current) {
                clearTimeout(centerTimeoutRef.current);
              }
            }
          }}
          aria-label={viewLocked ? "Unlock view" : "Lock view"}
          aria-pressed={viewLocked}
          title={viewLocked ? "Unlock View (prevents auto-centering)" : "Lock View (prevents auto-centering)"}
          className={viewLocked ? 'active' : ''}
        >
          <span className="button-icon">{viewLocked ? '🔒' : '🔓'}</span>
          <span className="button-label">{viewLocked ? 'Locked' : 'Lock'}</span>
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
        aria-label="Interactive entity relationship network graph"
        nodeLabel={(node: any) => {
          // Build tooltip with full name if available
          let label = node.name;
          if (node.full_name) {
            label = `${node.name} - ${node.full_name}`;
          }
          if (node.type) {
            label += ` (${node.type})`;
          }
          return label;
        }}
        nodeColor={getNodeColor}
        nodeVal={getNodeSize}
        linkLabel="label"
        linkColor={(link: any) => {
          // Color links based on relationship type
          const label = link.label || '';
          if (label.includes('Money Flow') || label.includes('$')) {
            return 'rgba(91, 79, 255, 0.5)'; // Purple for financial
          } else if (label.includes('Award')) {
            return 'rgba(212, 162, 24, 0.5)'; // Gold for awards
          } else if (label.includes('NAICS') || label.includes('Industry')) {
            return 'rgba(0, 212, 170, 0.4)'; // Teal for industry
          }
          return 'rgba(91, 79, 255, 0.4)'; // Default purple
        }}
        linkWidth={(link: any) => {
          // Thicker lines for stronger relationships (money flows)
          const label = link.label || '';
          if (label.includes('Money Flow') || link.value) {
            return 3;
          }
          return 2;
        }}
        linkDirectionalParticles={4}
        linkDirectionalParticleWidth={2.5}
        linkDirectionalParticleSpeed={0.006}
        backgroundColor="#ffffff"
        // Improved force simulation for better clustering
        d3AlphaDecay={0.0228}  // Faster decay for quicker stabilization
        d3VelocityDecay={0.4}  // Higher velocity decay for smoother movement
        warmupTicks={200}       // More warmup for better initial layout
        cooldownTicks={300}    // More cooldown for final positioning
        cooldownTime={8000}     // Longer cooldown time
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
        onEngineStop={() => {
          // Only auto-center if view is not locked and we haven't manually interacted
          if (!viewLocked && hasCentered && !isCentering) {
            // Debounce auto-center to avoid constant re-centering
            if (centerTimeoutRef.current) {
              clearTimeout(centerTimeoutRef.current);
            }
            centerTimeoutRef.current = setTimeout(() => {
              if (!viewLocked && fgRef.current) {
                fgRef.current.zoomToFit(400, 50);
              }
            }, 500);
          }
        }}
        minZoom={0.3}
        maxZoom={8}
      />

      <div className="graph-stats">
        <span>{graphData.nodes.length} nodes</span>
        <span>{graphData.links.length} connections</span>
        {(() => {
          const inferredCount = graphData.links.filter(l => 
            l.label?.includes('Co-Recipient') || 
            l.label?.includes('Same Industry') || 
            l.label?.includes('Award Recipient')
          ).length;
          return inferredCount > 0 ? (
            <span className="inferred-badge">
              {inferredCount} inferred
            </span>
          ) : null;
        })()}
      </div>
    </div>
  );
}

export default NetworkGraph;

