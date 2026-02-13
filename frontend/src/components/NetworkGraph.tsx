import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { forceCollide, forceRadial } from 'd3-force';
import { scalePow } from 'd3-scale';
import { getEntityGraph } from '../services/api';
import type { GraphData as APIGraphData, GraphNode } from '../types';
import './NetworkGraph.css';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface ForceGraphNode extends GraphNode {
  val?: number;
  x?: number;
  y?: number;
  _connections?: number;
}

interface ForceGraphLink {
  source: string;
  target: string;
  label?: string;
  value?: number;
  count?: number;
}

interface ForceGraphData {
  nodes: ForceGraphNode[];
  links: ForceGraphLink[];
}

export interface NetworkGraphProps {
  filterLevels?: number[];
  selectedActor: string | null;
  onSelectActor: (name: string | null) => void;
  colorMode: 'type' | 'proximity';
  showInferred: boolean;
  minConnections: number;
  /** Expose processed data to parent */
  onDataReady?: (data: {
    nodeCount: number;
    linkCount: number;
    inferredCount: number;
    nodeIndex: { name: string; connections: number; type: string }[];
    rawLinks: ForceGraphLink[];
    totalRawLinks: number;
  }) => void;
}

/* ------------------------------------------------------------------ */
/*  Color Maps                                                         */
/* ------------------------------------------------------------------ */

export const ENTITY_COLOR_MAP: Record<string, string> = {
  Corporation: '#5B4FFF',
  'Government Agency': '#FF6B35',
  'Investment Firm': '#E91E63',
  'Research Institution': '#FF9800',
  'Non-Profit': '#9C27B0',
  Organization: '#00BCD4',
  Facility: '#4CAF50',
  Program: '#FF1744',
  Individual: '#2196F3',
  Unknown: '#9E9E9E',
  default: '#BDBDBD',
};

/* ------------------------------------------------------------------ */
/*  Intel-stack helpers                                                 */
/* ------------------------------------------------------------------ */

const INTEL_LEVEL_TYPE_MAP: Record<number, string[]> = {
  1: ['Organization'],
  2: ['Government Agency'],
  3: ['Research Institution'],
  4: ['Corporation', 'Investment Firm'],
  5: ['Facility'],
  6: ['Program'],
};

const getLinkNodeId = (ref: string | ForceGraphNode | any): string =>
  typeof ref === 'string' ? ref : ref?.id || '';

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

function NetworkGraph({
  filterLevels = [],
  selectedActor,
  onSelectActor,
  colorMode,
  showInferred,
  minConnections,
  onDataReady,
}: NetworkGraphProps) {
  const [rawGraphData, setRawGraphData] = useState<ForceGraphData>({ nodes: [], links: [] });
  const [graphData, setGraphData] = useState<ForceGraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasCentered, setHasCentered] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<ForceGraphNode | null>(null);
  // tooltip position tracked for future enhancement

  const fgRef = useRef<any>();
  const containerRef = useRef<HTMLDivElement>(null);
  const centerTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* ---------- load data ---------- */
  useEffect(() => { loadGraphData(); }, []);

  const loadGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data: APIGraphData = await getEntityGraph();

      // Edge deduplication: group same source-target pairs
      const edgeMap = new Map<string, ForceGraphLink>();
      for (const edge of data.edges) {
        const key = `${edge.source}|||${edge.target}`;
        const rev = `${edge.target}|||${edge.source}`;
        const existing = edgeMap.get(key) || edgeMap.get(rev);
        if (existing) {
          existing.count = (existing.count || 1) + 1;
          if (edge.value && (!existing.value || edge.value > existing.value)) {
            existing.value = edge.value;
          }
        } else {
          edgeMap.set(key, {
            source: edge.source,
            target: edge.target,
            label: edge.label,
            value: edge.value,
            count: 1,
          });
        }
      }

      // Count connections per node (on deduplicated edges)
      const connCounts = new Map<string, number>();
      for (const link of edgeMap.values()) {
        connCounts.set(link.source, (connCounts.get(link.source) || 0) + (link.count || 1));
        connCounts.set(link.target, (connCounts.get(link.target) || 0) + (link.count || 1));
      }

      const forceData: ForceGraphData = {
        nodes: data.nodes.map(node => ({
          ...node,
          val: connCounts.get(node.id) || 1,
          _connections: connCounts.get(node.id) || 0,
        })),
        links: Array.from(edgeMap.values()),
      };

      setRawGraphData(forceData);
    } catch (err) {
      setError('Failed to load graph data');
      console.error('Error loading graph:', err);
    } finally {
      setLoading(false);
    }
  };

  /* ---------- filtering ---------- */
  useEffect(() => {
    if (rawGraphData.nodes.length === 0) {
      setGraphData({ nodes: [], links: [] });
      return;
    }

    const connMap = new Map<string, number>();
    rawGraphData.links.forEach(l => {
      const s = getLinkNodeId(l.source);
      const t = getLinkNodeId(l.target);
      const c = l.count || 1;
      connMap.set(s, (connMap.get(s) || 0) + c);
      connMap.set(t, (connMap.get(t) || 0) + c);
    });

    const matchesIntel = (node: ForceGraphNode): boolean => {
      if (node.intel_stack_level) return filterLevels.includes(node.intel_stack_level);
      if (node.type) {
        for (const lv of filterLevels) {
          if ((INTEL_LEVEL_TYPE_MAP[lv] || []).includes(node.type)) return true;
        }
      }
      return false;
    };

    const primaryIds = new Set<string>();
    if (filterLevels.length > 0) {
      rawGraphData.nodes.forEach(n => { if (matchesIntel(n)) primaryIds.add(n.id); });
    }

    const connectedIds = new Set<string>();
    if (filterLevels.length > 0 && primaryIds.size > 0) {
      rawGraphData.links.forEach(l => {
        const s = getLinkNodeId(l.source), t = getLinkNodeId(l.target);
        if (primaryIds.has(s)) connectedIds.add(t);
        if (primaryIds.has(t)) connectedIds.add(s);
      });
    }

    const filteredNodes = rawGraphData.nodes.filter(node => {
      const c = connMap.get(node.id) || 0;
      if (c < minConnections) return false;
      if (filterLevels.length > 0 && !matchesIntel(node) && !connectedIds.has(node.id)) return false;
      return true;
    });

    const visibleIds = new Set(filteredNodes.map(n => n.id));

    const filteredLinks: ForceGraphLink[] = [];
    rawGraphData.links.forEach(l => {
      const s = getLinkNodeId(l.source), t = getLinkNodeId(l.target);
      if (!showInferred && l.label &&
        (l.label.includes('Co-Recipient') || l.label.includes('Same Industry') || l.label.includes('Award Recipient')))
        return;
      if (visibleIds.has(s) && visibleIds.has(t)) {
        filteredLinks.push({ source: s, target: t, label: l.label, value: l.value, count: l.count });
      }
    });

    setGraphData({ nodes: filteredNodes, links: filteredLinks });
  }, [rawGraphData, showInferred, minConnections, filterLevels]);

  /* ---------- expose data to parent ---------- */
  const nodeIndex = useMemo(() =>
    graphData.nodes.map(n => ({
      name: n.name || n.id,
      connections: n._connections || 0,
      type: n.type || 'Unknown',
    })).sort((a, b) => b.connections - a.connections),
    [graphData.nodes]
  );

  useEffect(() => {
    const inferredCount = graphData.links.filter(l =>
      l.label?.includes('Co-Recipient') || l.label?.includes('Same Industry') || l.label?.includes('Award Recipient')
    ).length;
    onDataReady?.({
      nodeCount: graphData.nodes.length,
      linkCount: graphData.links.length,
      inferredCount,
      nodeIndex,
      rawLinks: graphData.links,
      totalRawLinks: rawGraphData.links.length,
    });
  }, [graphData, nodeIndex, rawGraphData.links.length]);

  /* ---------- node radius scale (sqrt) ---------- */
  const radiusScale = useMemo(() => {
    const maxConn = Math.max(1, ...graphData.nodes.map(n => n._connections || 1));
    return scalePow().exponent(0.5).domain([1, maxConn]).range([4, 40]).clamp(true);
  }, [graphData.nodes]);

  /* ---------- selected actor adjacency sets ---------- */
  const { selectedNeighbors, selectedLinkSet } = useMemo(() => {
    if (!selectedActor) return { selectedNeighbors: new Set<string>(), selectedLinkSet: new Set<string>() };
    const neighbors = new Set<string>();
    const linkSet = new Set<string>();
    graphData.links.forEach(l => {
      const s = getLinkNodeId(l.source), t = getLinkNodeId(l.target);
      if (s === selectedActor || t === selectedActor) {
        neighbors.add(s);
        neighbors.add(t);
        linkSet.add(`${s}|||${t}`);
        linkSet.add(`${t}|||${s}`);
      }
    });
    return { selectedNeighbors: neighbors, selectedLinkSet: linkSet };
  }, [selectedActor, graphData.links]);

  /* ---------- proximity coloring ---------- */
  const getNodeColor = useCallback((node: ForceGraphNode) => {
    if (colorMode === 'proximity' && selectedActor) {
      if (node.id === selectedActor || node.name === selectedActor) return '#dc2626';
      if (selectedNeighbors.has(node.id) || selectedNeighbors.has(node.name || '')) {
        return '#f59e0b'; // warm orange for direct connections
      }
      return 'hsl(120, 40%, 45%)'; // green for distant
    }
    // Default: entity type coloring
    return ENTITY_COLOR_MAP[node.type || 'default'] || ENTITY_COLOR_MAP.default;
  }, [colorMode, selectedActor, selectedNeighbors]);

  /* ---------- configure forces ---------- */
  useEffect(() => {
    if (!fgRef.current || graphData.nodes.length === 0) return;
    const fg = fgRef.current;
    const nodeCount = graphData.nodes.length;
    const chargeStrength = nodeCount > 100 ? -250 : -350;
    fg.d3Force('charge')?.strength(chargeStrength).distanceMax(300);
    fg.d3Force('link')?.distance(60).strength(0.7);

    // Collision based on node radius
    fg.d3Force('collision', forceCollide()
      .radius((n: any) => radiusScale(n._connections || 1) + 6)
      .strength(0.8)
    );

    // Radial force: push high-connection nodes toward center
    fg.d3Force('radial', forceRadial(
      (n: any) => {
        const conn = Math.min(n._connections || 0, 50);
        return (50 - conn) * 12 + 60; // high-conn = small radius = center
      },
      0, 0
    ).strength(0.3));

    fg.d3Force('center')?.strength(0.05);
    fg.d3ReheatSimulation();
  }, [graphData, radiusScale]);

  /* ---------- auto-center ---------- */
  useEffect(() => {
    if (graphData.nodes.length > 0 && !hasCentered && fgRef.current) {
      if (centerTimeoutRef.current) clearTimeout(centerTimeoutRef.current);
      centerTimeoutRef.current = setTimeout(() => {
        fgRef.current?.zoomToFit(600, 40);
        setHasCentered(true);
      }, 2500);
    }
    return () => { if (centerTimeoutRef.current) clearTimeout(centerTimeoutRef.current); };
  }, [graphData, hasCentered]);

  /* ---------- zoom to selected actor ---------- */
  useEffect(() => {
    if (!selectedActor || !fgRef.current) return;
    const node = graphData.nodes.find(n => n.id === selectedActor || n.name === selectedActor);
    if (node && node.x !== undefined && node.y !== undefined) {
      fgRef.current.centerAt(node.x, node.y, 800);
      fgRef.current.zoom(2.5, 800);
    }
  }, [selectedActor]);

  /* ---------- render ---------- */
  if (loading) {
    return <div className="network-graph-container"><div className="loading">Loading network graph...</div></div>;
  }
  if (error) {
    return <div className="network-graph-container"><div className="error">{error}<button onClick={loadGraphData} style={{ marginTop: 12 }}>Retry</button></div></div>;
  }
  if (graphData.nodes.length === 0) {
    return <div className="network-graph-container"><div className="empty">No network data available</div></div>;
  }

  return (
    <div className="network-graph-container" ref={containerRef}>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        backgroundColor="#030712"
        d3AlphaDecay={0.025}
        d3VelocityDecay={0.4}
        warmupTicks={200}
        cooldownTicks={300}
        cooldownTime={8000}
        minZoom={0.01}
        maxZoom={10}
        nodeVal={(node: any) => radiusScale(node._connections || 1)}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const r = radiusScale(node._connections || 1);
          const label = node.name || node.id || '';
          const isSelected = selectedActor && (node.id === selectedActor || node.name === selectedActor);
          const isNeighbor = selectedActor && (selectedNeighbors.has(node.id) || selectedNeighbors.has(node.name || ''));
          const dimmed = selectedActor && !isSelected && !isNeighbor;

          // Node circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
          ctx.fillStyle = dimmed ? 'rgba(100,100,100,0.25)' : getNodeColor(node);
          ctx.fill();

          // Border
          if (isSelected) {
            ctx.strokeStyle = '#06b6d4';
            ctx.lineWidth = 3;
          } else {
            ctx.strokeStyle = dimmed ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.6)';
            ctx.lineWidth = 1;
          }
          ctx.stroke();

          // Labels
          if (globalScale > 0.4 || isSelected || (isNeighbor && globalScale > 0.25)) {
            const fontSize = Math.max(3, Math.min(11, 12 / globalScale));
            ctx.font = `${isSelected ? 'bold ' : ''}${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';

            const textY = node.y + r + 2;
            if (!dimmed) {
              ctx.fillStyle = 'rgba(255,255,255,0.92)';
              ctx.fillText(label, node.x, textY);
            }
          }
        }}
        linkColor={(link: any) => {
          if (!selectedActor) {
            const lbl = link.label || '';
            if (lbl.includes('Money Flow') || lbl.includes('$')) return 'rgba(91, 79, 255, 0.35)';
            if (lbl.includes('Award')) return 'rgba(250, 204, 21, 0.3)';
            return 'rgba(255,255,255,0.12)';
          }
          const s = getLinkNodeId(link.source), t = getLinkNodeId(link.target);
          const key = `${s}|||${t}`;
          if (selectedLinkSet.has(key)) return '#06b6d4';
          return 'rgba(255,255,255,0.04)';
        }}
        linkWidth={(link: any) => {
          if (!selectedActor) return (link.count || 1) > 1 ? 2 : 1;
          const s = getLinkNodeId(link.source), t = getLinkNodeId(link.target);
          return selectedLinkSet.has(`${s}|||${t}`) ? 2.5 : 0.3;
        }}
        linkDirectionalParticles={(link: any) => {
          if (!selectedActor) return 0;
          const s = getLinkNodeId(link.source), t = getLinkNodeId(link.target);
          return selectedLinkSet.has(`${s}|||${t}`) ? 3 : 0;
        }}
        linkDirectionalParticleWidth={2}
        linkDirectionalParticleSpeed={0.008}
        onNodeClick={(node: any) => {
          const name = node.name || node.id;
          onSelectActor(selectedActor === name ? null : name);
        }}
        onNodeHover={(node: any, _prevNode: any) => {
          document.body.style.cursor = node ? 'pointer' : 'default';
          setHoveredNode(node || null);
        }}
        onBackgroundClick={() => onSelectActor(null)}
      />

      {/* Tooltip */}
      {hoveredNode && (
        <div
          className="graph-tooltip"
          style={{
            position: 'absolute',
            pointerEvents: 'none',
            left: 0,
            top: 0,
            /* We position via a separate listener; for simplicity show at fixed position */
          }}
        >
          {/* Implemented via nodeLabel below for simplicity */}
        </div>
      )}

      {/* Instructions Banner */}
      <div className="graph-instructions-bar">
        <span>Click nodes to explore relationships</span>
        <span className="separator">&#x2022;</span>
        <span>Scroll to zoom</span>
        <span className="separator">&#x2022;</span>
        <span>Drag to pan</span>
      </div>
    </div>
  );
}

export default NetworkGraph;
