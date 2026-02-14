import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { Loader2 } from 'lucide-react';
import * as d3 from 'd3';
import { getSankeyData } from '../services/api';
import type { SankeyData } from '../types';
import './SankeyDiagram.css';

interface SankeyProps {
  minAmount?: number;
  includeRelationships?: boolean;
  onNodeClick?: (nodeName: string) => void;
  filterLevels?: number[];  // Filter by intel stack levels (1-6)
}

// Color map matching NetworkGraph
const colorMap: Record<string, string> = {
  'Corporation': '#5B4FFF',
  'Government Agency': '#FF6B35',
  'Investment Firm': '#E91E63',
  'Research Institution': '#FF9800',
  'Non-Profit': '#9C27B0',
  'Organization': '#00BCD4',
  'Facility': '#4CAF50',
  'Program': '#FF1744',
  'Individual': '#2196F3',
  'Unknown': '#9E9E9E',
  'default': '#BDBDBD'
};

// Intel Stack Level to Entity Category mapping for filtering
// Maps intel stack levels to entity types/categories
const INTEL_LEVEL_CATEGORY_MAP: Record<number, string[]> = {
  1: ['Organization'],  // Control Group - MITRE/JASON/NSC are Organizations
  2: ['Government Agency'],  // Administrators - IC agencies
  3: ['Research Institution'],  // FFRDCs
  4: ['Corporation', 'Investment Firm'],  // Prime Contractors
  5: ['Facility'],  // Facilities
  6: ['Program'],  // Programs
};

function SankeyDiagram({ minAmount = 0, includeRelationships = true, onNodeClick, filterLevels = [] }: SankeyProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<SankeyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredLink, setHoveredLink] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; content: string } | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [minAmountFilter, setMinAmountFilter] = useState(minAmount);
  const [viewType, setViewType] = useState<'money' | 'relationships' | 'combined'>('combined');
  const [showLegend, setShowLegend] = useState(true);

  useEffect(() => {
    loadData();
  }, [minAmountFilter, includeRelationships, viewType]);
  
  // Helper to check if node matches intel stack filter by category type
  const matchesIntelFilter = useCallback((node: { name: string; category: string }): boolean => {
    if (filterLevels.length === 0) return true;
    
    // Check if node category matches any selected level
    for (const level of filterLevels) {
      const matchingCategories = INTEL_LEVEL_CATEGORY_MAP[level] || [];
      if (matchingCategories.includes(node.category)) {
        return true;
      }
    }
    return false;
  }, [filterLevels]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const sankeyData = await getSankeyData({
        min_amount: minAmountFilter > 0 ? minAmountFilter : undefined,
        include_relationships: includeRelationships && (viewType === 'relationships' || viewType === 'combined'),
        limit: 200
      });
      setData(sankeyData);
    } catch (err) {
      console.error('Error loading Sankey data:', err);
      setError('Failed to load Sankey diagram data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (data && svgRef.current && containerRef.current) {
      renderSankey();
    }
  }, [data, selectedNode, hoveredLink, zoom, pan, viewType, filterLevels]);
  
  // Get unique categories from actual data for legend
  const uniqueCategories = useMemo(() => {
    if (!data) return [];
    const categories = new Set(data.nodes.map(n => n.category).filter(Boolean));
    return Array.from(categories).sort();
  }, [data]);

  const renderSankey = () => {
    if (!data || !svgRef.current || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = Math.max(600, container.clientHeight || 600);
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    svg.attr('width', width).attr('height', height);

    // Filter data based on view type
    let filteredLinks = data.links;
    if (viewType === 'money') {
      filteredLinks = data.links.filter(l => l.type === 'money_flow');
    } else if (viewType === 'relationships') {
      filteredLinks = data.links.filter(l => l.type === 'relationship');
    }

    // Get unique nodes from filtered links
    const nodeNames = new Set<string>();
    filteredLinks.forEach(link => {
      nodeNames.add(link.source);
      nodeNames.add(link.target);
    });

    // Apply intel stack filter if active
    let filteredNodes = data.nodes.filter(n => nodeNames.has(n.name));
    if (filterLevels.length > 0) {
      filteredNodes = filteredNodes.filter(n => matchesIntelFilter(n));
      // Re-filter links to only include those connecting filtered nodes
      const filteredNodeNames = new Set(filteredNodes.map(n => n.name));
      filteredLinks = filteredLinks.filter(l => 
        filteredNodeNames.has(l.source) && filteredNodeNames.has(l.target)
      );
    }

    if (filteredNodes.length === 0 || filteredLinks.length === 0) {
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('fill', 'currentColor')
        .text('No data to display');
      return;
    }

    // Create a simple layered layout
    const layers: string[][] = [];
    const nodeLayer = new Map<string, number>();
    const processed = new Set<string>();

    // Build layers using BFS
    const queue: { name: string; layer: number }[] = [];
    
    // Find sources (nodes with no incoming links)
    const hasIncoming = new Set<string>();
    filteredLinks.forEach(link => hasIncoming.add(link.target));
    
    filteredNodes.forEach(node => {
      if (!hasIncoming.has(node.name)) {
        queue.push({ name: node.name, layer: 0 });
      }
    });

    // If no sources found, start with first node
    if (queue.length === 0 && filteredNodes.length > 0) {
      queue.push({ name: filteredNodes[0].name, layer: 0 });
    }

    while (queue.length > 0) {
      const { name, layer } = queue.shift()!;
      if (processed.has(name)) continue;
      
      processed.add(name);
      nodeLayer.set(name, layer);
      
      if (!layers[layer]) layers[layer] = [];
      layers[layer].push(name);

      // Add targets to next layer
      filteredLinks.forEach(link => {
        if (link.source === name && !processed.has(link.target)) {
          queue.push({ name: link.target, layer: layer + 1 });
        }
      });
    }

    // Assign remaining nodes to last layer
    filteredNodes.forEach(node => {
      if (!nodeLayer.has(node.name)) {
        const lastLayer = layers.length;
        nodeLayer.set(node.name, lastLayer);
        if (!layers[lastLayer]) layers[lastLayer] = [];
        layers[lastLayer].push(node.name);
      }
    });

    // Calculate node positions
    const nodeHeight = 20;
    const nodeSpacing = 30;
    const layerWidth = (width - margin.left - margin.right) / Math.max(layers.length, 1);
    const nodePositions = new Map<string, { x: number; y: number; width: number; height: number }>();

    layers.forEach((layerNodes, layerIdx) => {
      const layerY = margin.top + (height - margin.top - margin.bottom) / 2;
      const layerX = margin.left + layerIdx * layerWidth;
      const totalHeight = layerNodes.length * (nodeHeight + nodeSpacing) - nodeSpacing;
      const startY = layerY - totalHeight / 2;

      layerNodes.forEach((nodeName, nodeIdx) => {
        const node = filteredNodes.find(n => n.name === nodeName);
        const nodeValue = node?.value || 1;
        const nodeWidth = Math.max(10, Math.min(50, Math.sqrt(nodeValue) * 2));
        
        nodePositions.set(nodeName, {
          x: layerX,
          y: startY + nodeIdx * (nodeHeight + nodeSpacing),
          width: nodeWidth,
          height: nodeHeight
        });
      });
    });

    // Create groups for zoom/pan
    const g = svg.append('g')
      .attr('transform', `translate(${pan.x}, ${pan.y}) scale(${zoom})`);

    // Draw links
    const linkGroup = g.append('g').attr('class', 'links');
    filteredLinks.forEach((link) => {
      const sourcePos = nodePositions.get(link.source);
      const targetPos = nodePositions.get(link.target);
      
      if (!sourcePos || !targetPos) return;

      const isSelected = selectedNode === link.source || selectedNode === link.target;
      const isHovered = hoveredLink === `${link.source}-${link.target}`;
      const isDimmed = selectedNode && selectedNode !== link.source && selectedNode !== link.target;

      const opacity = isDimmed ? 0.1 : (isHovered ? 0.8 : 0.3);
      const strokeWidth = isHovered ? 4 : (isSelected ? 3 : 2);

      // Create curved path
      const path = d3.path();
      const sourceX = sourcePos.x + sourcePos.width;
      const sourceY = sourcePos.y + sourcePos.height / 2;
      const targetX = targetPos.x;
      const targetY = targetPos.y + targetPos.height / 2;
      
      const midX = (sourceX + targetX) / 2;
      
      path.moveTo(sourceX, sourceY);
      path.bezierCurveTo(midX, sourceY, midX, targetY, targetX, targetY);

      linkGroup.append('path')
        .attr('d', path.toString())
        .attr('stroke', '#999')
        .attr('stroke-width', strokeWidth)
        .attr('fill', 'none')
        .attr('opacity', opacity)
        .attr('data-link-id', `${link.source}-${link.target}`)
        .on('mouseenter', (e) => {
          setHoveredLink(`${link.source}-${link.target}`);
          const tooltipContent = `${link.source} → ${link.target}\n${link.label || ''}\nValue: ${formatValue(link.value)}`;
          setTooltip({ x: e.pageX, y: e.pageY, content: tooltipContent });
        })
        .on('mouseleave', () => {
          setHoveredLink(null);
          setTooltip(null);
        });
    });

    // Draw nodes
    const nodeGroup = g.append('g').attr('class', 'nodes');
    filteredNodes.forEach(node => {
      const pos = nodePositions.get(node.name);
      if (!pos) return;

      const isSelected = selectedNode === node.name;
      const nodeColor = colorMap[node.category] || colorMap['default'];

      nodeGroup.append('rect')
        .attr('x', pos.x)
        .attr('y', pos.y)
        .attr('width', pos.width)
        .attr('height', pos.height)
        .attr('fill', nodeColor)
        .attr('stroke', isSelected ? '#fff' : 'none')
        .attr('stroke-width', isSelected ? 2 : 0)
        .attr('opacity', selectedNode && !isSelected ? 0.3 : 1)
        .attr('cursor', 'pointer')
        .attr('data-node-name', node.name)
        .on('click', () => {
          const newSelected = isSelected ? null : node.name;
          setSelectedNode(newSelected);
          if (onNodeClick) {
            onNodeClick(newSelected || '');
          }
        })
        .on('mouseenter', (e) => {
          const tooltipContent = `${node.name}\nCategory: ${node.category}\nValue: ${formatValue(node.value)}`;
          setTooltip({ x: e.pageX, y: e.pageY, content: tooltipContent });
        })
        .on('mouseleave', () => {
          if (!hoveredLink) setTooltip(null);
        });

      // Add label
      nodeGroup.append('text')
        .attr('x', pos.x + pos.width + 5)
        .attr('y', pos.y + pos.height / 2)
        .attr('dy', '0.35em')
        .attr('fill', 'currentColor')
        .attr('font-size', '12px')
        .attr('opacity', selectedNode && !isSelected ? 0.3 : 0.8)
        .text(node.name.length > 20 ? node.name.substring(0, 20) + '...' : node.name);
    });
  };

  const formatValue = (value: number): string => {
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(2)}B`;
    } else if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(2)}M`;
    } else if (value >= 1_000) {
      return `$${(value / 1_000).toFixed(1)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  const handleWheel = useCallback((e: React.WheelEvent<SVGSVGElement>) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(prev => Math.max(0.5, Math.min(3, prev * delta)));
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (e.button === 0) { // Left mouse button
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  }, [pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNode(null);
  };

  if (loading) {
    return (
      <div className="sankey-container loading-state">
        <Loader2 size={32} className="loading-spinner" />
        <span>Loading Sankey diagram...</span>
      </div>
    );
  }

  if (error) {
    return <div className="sankey-container error">{error}</div>;
  }

  return (
    <div className="sankey-container" ref={containerRef}>
      <div className="sankey-controls">
        <div className="control-group">
          <label>View Type:</label>
          <select value={viewType} onChange={(e) => setViewType(e.target.value as any)}>
            <option value="combined">Combined</option>
            <option value="money">Money Flows Only</option>
            <option value="relationships">Relationships Only</option>
          </select>
        </div>
        <div className="control-group">
          <label>Min Amount: {formatValue(minAmountFilter)}</label>
          <input
            type="range"
            min="0"
            max={data?.links.reduce((max, l) => Math.max(max, l.value), 0) || 1000000000}
            step="1000000"
            value={minAmountFilter}
            onChange={(e) => setMinAmountFilter(Number(e.target.value))}
          />
        </div>
        <button onClick={resetView} className="btn btn-secondary">Reset View</button>
        {selectedNode && (
          <button onClick={() => setSelectedNode(null)} className="btn btn-secondary">
            Clear Selection
          </button>
        )}
        <button 
          onClick={() => setShowLegend(!showLegend)} 
          className={`btn btn-secondary ${showLegend ? 'active' : ''}`}
          title="Toggle Legend"
        >
          Legend {showLegend ? '▼' : '▲'}
        </button>
      </div>
      
      {/* Legend */}
      {showLegend && uniqueCategories.length > 0 && (
        <div className="sankey-legend">
          <h5>Entity Types</h5>
          <div className="legend-items">
            {uniqueCategories.map(category => (
              <div key={category} className="legend-item">
                <span 
                  className="legend-color" 
                  style={{ backgroundColor: colorMap[category] || colorMap['default'] }}
                />
                <span className="legend-label">{category}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <svg
        ref={svgRef}
        className="sankey-svg"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      />
      
      {/* Stats bar */}
      <div className="sankey-stats">
        <span>{data?.nodes.length || 0} entities</span>
        <span>{data?.links.length || 0} flows</span>
        {filterLevels.length > 0 && (
          <span className="filter-badge">Filtered</span>
        )}
      </div>
      
      {tooltip && (
        <div
          className="sankey-tooltip"
          style={{ left: tooltip.x + 10, top: tooltip.y + 10 }}
        >
          {tooltip.content.split('\n').map((line, idx) => (
            <div key={idx}>{line}</div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SankeyDiagram;
