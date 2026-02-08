/**
 * PyramidVisualization: Renders the 6-tier Intelligence Stack pyramid from API data.
 * - True trapezoid pyramid geometry (narrow at top, wide at bottom).
 * - Click a tier to expand and list entities; click an entity to highlight (onEntityClick).
 * - Optional animated flow lines between tiers (cross_level_flows).
 * - Supports activeLevels filtering and responsive viewBox.
 */
import { useState, useMemo, useCallback } from 'react';
import type { PyramidData, PyramidEntitySummary, PyramidLevelSummary } from '../types';
import PyramidTooltip, { type PyramidTooltipData } from './PyramidTooltip';
import './PyramidVisualization.css';

interface PyramidVisualizationProps {
  data: PyramidData | null;
  loading?: boolean;
  highlightedEntityId?: string | null;
  onEntityClick?: (entity: PyramidEntitySummary, level: number) => void;
  showFlowLines?: boolean;
  /** Levels to show (1-6). If empty or [1,2,3,4,5,6], show all. */
  activeLevels?: number[];
  /** When set (chain tracer mode), dim entities not in this set. */
  chainEntityIds?: Set<string>;
}

const SVG_WIDTH = 600;
const SVG_HEIGHT = 420;
const MIN_TIER_HEIGHT = 44;
const MAX_TIER_HEIGHT = 90;
const PYRAMID_CENTER_X = SVG_WIDTH / 2;
/** Half-width at top of pyramid (tier 1) and at bottom (tier 6) as fraction of SVG width */
const TOP_HALF_WIDTH = 0.12 * SVG_WIDTH;
const BOTTOM_HALF_WIDTH = 0.42 * SVG_WIDTH;

function formatAmount(n: number): string {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}K`;
  return `$${n.toFixed(0)}`;
}

/** Entity type to color (matches NetworkGraph/Sankey) */
const ENTITY_TYPE_COLORS: Record<string, string> = {
  Corporation: '#5B4FFF',
  'Government Agency': '#FF6B35',
  'Research Institution': '#FF9800',
  Facility: '#4CAF50',
  Program: '#E91E63',
  Individual: '#2196F3',
  Organization: '#00BCD4',
  'Investment Firm': '#E91E63',
  Unknown: '#9E9E9E',
};

function getEntityColor(entityType?: string | null): string {
  return (entityType && ENTITY_TYPE_COLORS[entityType]) || ENTITY_TYPE_COLORS.Unknown;
}

const MAX_ENTITY_NODES_VISIBLE = 8;
const ENTITY_LABEL_MAX_LEN = 10;

function truncateLabel(name: string): string {
  if (name.length <= ENTITY_LABEL_MAX_LEN) return name;
  return name.slice(0, ENTITY_LABEL_MAX_LEN - 1) + '…';
}

/** Sort entities by relationship_count then money_flow_total for "top" display */
function topEntities(entities: PyramidEntitySummary[]): PyramidEntitySummary[] {
  return [...entities].sort((a, b) => {
    const rc = (b.relationship_count ?? 0) - (a.relationship_count ?? 0);
    if (rc !== 0) return rc;
    return (b.money_flow_total_usd ?? 0) - (a.money_flow_total_usd ?? 0);
  });
}

export default function PyramidVisualization(props: PyramidVisualizationProps) {
  const {
    data,
    loading = false,
    highlightedEntityId = null,
    onEntityClick,
    showFlowLines = true,
    activeLevels = [1, 2, 3, 4, 5, 6],
    chainEntityIds,
  } = props;
  const inChain = (entityId: string) => !chainEntityIds || chainEntityIds.size === 0 || chainEntityIds.has(entityId);
  const [expandedLevel, setExpandedLevel] = useState<number | null>(null);
  const [hoverLevel, setHoverLevel] = useState<number | null>(null);
  const [tooltip, setTooltip] = useState<{ data: PyramidTooltipData; x: number; y: number } | null>(null);

  const handleTierHover = useCallback(
    (tier: PyramidLevelSummary, ev: React.MouseEvent) => {
      setHoverLevel(tier.level);
      const topNames = topEntities(tier.entities).slice(0, 3).map((e) => e.display_name);
      setTooltip({
        data: { kind: 'tier', tier, topEntities: topNames },
        x: ev.clientX,
        y: ev.clientY,
      });
    },
    []
  );
  const handleTierLeave = useCallback(() => {
    setHoverLevel(null);
    setTooltip(null);
  }, []);
  const handleEntityLeave = useCallback(() => setTooltip(null), []);

  const levels = data?.levels ?? [];
  const cross_level_flows = data?.cross_level_flows ?? [];

  const filteredLevels = useMemo(() => {
    const set = new Set(activeLevels.length ? activeLevels : [1, 2, 3, 4, 5, 6]);
    return levels.filter((l) => set.has(l.level));
  }, [levels, activeLevels]);

  const pyramidTiers = useMemo(() => {
    const total = filteredLevels.reduce((s, l) => s + Math.max(l.entity_count, 1), 0) || 1;
    let yAcc = 20;
    const tierRects: Array<PyramidLevelSummary & { yTop: number; yBottom: number; halfWidthTop: number; halfWidthBottom: number }> = [];
    for (let i = 0; i < filteredLevels.length; i++) {
      const lev = filteredLevels[i];
      const ratio = Math.max(lev.entity_count, 1) / total;
      const rawHeight = (SVG_HEIGHT - 60) * ratio;
      const height = Math.min(MAX_TIER_HEIGHT, Math.max(MIN_TIER_HEIGHT, rawHeight));
      const yBottom = yAcc + height;
      const levelIndex = lev.level - 1;
      const halfWidthTop = TOP_HALF_WIDTH + (BOTTOM_HALF_WIDTH - TOP_HALF_WIDTH) * (levelIndex / 5);
      const halfWidthBottom = TOP_HALF_WIDTH + (BOTTOM_HALF_WIDTH - TOP_HALF_WIDTH) * ((levelIndex + 1) / 5);
      tierRects.push({
        ...lev,
        yTop: yAcc,
        yBottom,
        halfWidthTop,
        halfWidthBottom,
      });
      yAcc = yBottom + 2;
    }
    return tierRects;
  }, [filteredLevels]);

  if (loading) {
    return (
      <div className="pyramid-viz pyramid-viz-loading">
        <p>Loading pyramid data…</p>
      </div>
    );
  }

  if (!data || levels.length === 0) {
    return (
      <div className="pyramid-viz pyramid-viz-empty">
        <p>No pyramid data. Ensure entities have intel_stack_level set.</p>
      </div>
    );
  }

  return (
    <div className="pyramid-viz">
      <svg
        className="pyramid-svg"
        viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        preserveAspectRatio="xMidYMid meet"
        aria-label="Intelligence stack pyramid"
      >
        <defs>
          {pyramidTiers.map((tier) => (
            <linearGradient
              key={`grad-${tier.level}`}
              id={`pyramid-grad-${tier.level}`}
              x1="0%"
              y1="0%"
              x2="0%"
              y2="100%"
            >
              <stop offset="0%" stopColor={tier.color} stopOpacity={1} />
              <stop offset="100%" stopColor={tier.color} stopOpacity={0.75} />
            </linearGradient>
          ))}
          {showFlowLines &&
            cross_level_flows
              .filter((f) => f.flow_count > 0)
              .slice(0, 14)
              .map((flow, i) => {
                const fromTier = pyramidTiers.find((t) => t.level === flow.from_level);
                const toTier = pyramidTiers.find((t) => t.level === flow.to_level);
                if (!fromTier || !toTier) return null;
                const y1 = (fromTier.yTop + fromTier.yBottom) / 2;
                const y2 = (toTier.yTop + toTier.yBottom) / 2;
                return (
                  <linearGradient
                    key={`flow-grad-${i}`}
                    id={`flow-grad-${i}`}
                    x1="0"
                    y1={y1}
                    x2="0"
                    y2={y2}
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop offset="0%" stopColor={fromTier.color} />
                    <stop offset="100%" stopColor={toTier.color} />
                  </linearGradient>
                );
              })}
        </defs>

        {showFlowLines &&
          cross_level_flows
            .filter((f) => f.flow_count > 0)
            .slice(0, 14)
            .map((flow, i) => {
              const fromTier = pyramidTiers.find((t) => t.level === flow.from_level);
              const toTier = pyramidTiers.find((t) => t.level === flow.to_level);
              if (!fromTier || !toTier) return null;
              const y1 = (fromTier.yTop + fromTier.yBottom) / 2;
              const y2 = (toTier.yTop + toTier.yBottom) / 2;
              const x1 = PYRAMID_CENTER_X;
              const x2 = PYRAMID_CENTER_X;
              const midY = (y1 + y2) / 2;
              const maxUsd = Math.max(...cross_level_flows.map((f) => f.total_usd), 1);
              const logWidth = Math.log10(1 + (flow.total_usd / maxUsd) * 9);
              const strokeW = Math.min(12, Math.max(3, 3 + logWidth * 6));
              const levelNames = ['', 'Control', 'Admin', 'FFRDCs', 'Primes', 'Facilities', 'Programs'];
              return (
                <path
                  key={`flow-${flow.from_level}-${flow.to_level}-${i}`}
                  d={`M ${x1} ${y1} Q ${x1} ${midY} ${(x1 + x2) / 2} ${midY} T ${x2} ${y2}`}
                  fill="none"
                  stroke={`url(#flow-grad-${i})`}
                  strokeWidth={strokeW}
                  strokeOpacity={0.7}
                  strokeLinecap="round"
                  className="pyramid-flow-line pyramid-flow-band"
                  onMouseEnter={(ev) => {
                    setTooltip({
                      data: {
                        kind: 'flow',
                        flow,
                        fromName: `L${flow.from_level} ${levelNames[flow.from_level] ?? ''}`,
                        toName: `L${flow.to_level} ${levelNames[flow.to_level] ?? ''}`,
                      },
                      x: ev.nativeEvent.clientX,
                      y: ev.nativeEvent.clientY,
                    });
                  }}
                  onMouseLeave={handleEntityLeave}
                />
              );
            })}

        {pyramidTiers.map((tier) => {
          const isExpanded = expandedLevel === tier.level;
          const isHover = hoverLevel === tier.level;
          const pathD = `M ${PYRAMID_CENTER_X - tier.halfWidthTop} ${tier.yTop}
            L ${PYRAMID_CENTER_X + tier.halfWidthTop} ${tier.yTop}
            L ${PYRAMID_CENTER_X + tier.halfWidthBottom} ${tier.yBottom}
            L ${PYRAMID_CENTER_X - tier.halfWidthBottom} ${tier.yBottom} Z`;
          return (
            <g
              key={tier.level}
              className={`pyramid-tier-group ${chainEntityIds?.size ? (tier.entities.some((e) => chainEntityIds.has(e.entity_id)) ? 'pyramid-tier-in-chain' : 'pyramid-tier-dimmed') : ''}`}
              onMouseEnter={(ev) => handleTierHover(tier, ev as unknown as React.MouseEvent)}
              onMouseLeave={handleTierLeave}
            >
              <path
                d={pathD}
                fill={`url(#pyramid-grad-${tier.level})`}
                stroke="var(--border-color)"
                strokeWidth={isHover ? 2.5 : 1}
                className="pyramid-tier-rect pyramid-tier-trapezoid"
                onClick={() => setExpandedLevel(isExpanded ? null : tier.level)}
                style={{ cursor: 'pointer' }}
              />
              <text
                x={PYRAMID_CENTER_X}
                y={tier.yTop + 16}
                textAnchor="middle"
                fill="white"
                fontSize={12}
                fontWeight={600}
                className="pyramid-tier-label"
              >
                L{tier.level}: {tier.name} ({tier.entity_count})
              </text>
              {tier.entities.length > 0 && (
                <g className="pyramid-tier-entities">
                  {(() => {
                    const top = topEntities(tier.entities).slice(0, MAX_ENTITY_NODES_VISIBLE);
                    const moreCount = tier.entity_count - top.length;
                    const nodeCount = top.length;
                    const totalW = Math.min(tier.halfWidthBottom * 1.8, nodeCount * 28);
                    const startX = PYRAMID_CENTER_X - totalW / 2 + (nodeCount > 1 ? totalW / (nodeCount + 1) : totalW / 2) / 2;
                    const stepX = nodeCount > 1 ? totalW / (nodeCount + 1) : 0;
                    const nodeY = (tier.yTop + tier.yBottom) / 2 + 4;
                    return (
                      <>
                        {top.map((ent, idx) => {
                          const cx = nodeCount === 1 ? PYRAMID_CENTER_X : startX + stepX * (idx + 1);
                          const isHighlighted = highlightedEntityId === ent.entity_id;
                          const inChainSet = inChain(ent.entity_id);
                          return (
                            <g
                              key={ent.entity_id}
                              className={`pyramid-entity-node ${isHighlighted ? 'pyramid-entity-node-highlighted' : ''} ${!inChainSet ? 'pyramid-entity-node-dimmed' : ''}`}
                              onClick={(ev) => {
                                ev.stopPropagation();
                                onEntityClick?.(ent, tier.level);
                              }}
                              onMouseEnter={(ev) => {
                                const e = ev.nativeEvent;
                                setTooltip({
                                  data: { kind: 'entity', entity: ent, level: tier.level, levelName: tier.name },
                                  x: e.clientX,
                                  y: e.clientY,
                                });
                              }}
                              onMouseLeave={handleEntityLeave}
                              style={{ cursor: 'pointer' }}
                            >
                              <circle
                                cx={cx}
                                cy={nodeY}
                                r={10}
                                fill={getEntityColor(ent.entity_type)}
                                stroke={isHighlighted ? 'white' : 'var(--border-color)'}
                                strokeWidth={isHighlighted ? 2.5 : 1}
                              />
                              <text
                                x={cx}
                                y={nodeY + 22}
                                textAnchor="middle"
                                fill="var(--text-primary)"
                                fontSize={9}
                                className="pyramid-entity-node-label"
                              >
                                {truncateLabel(ent.display_name)}
                              </text>
                            </g>
                          );
                        })}
                        {moreCount > 0 && (
                          <text
                            x={PYRAMID_CENTER_X}
                            y={nodeY + (tier.yBottom - tier.yTop) / 2 - 4}
                            textAnchor="middle"
                            fill="var(--text-muted)"
                            fontSize={10}
                            className="pyramid-entity-more"
                          >
                            +{moreCount} more
                          </text>
                        )}
                      </>
                    );
                  })()}
                </g>
              )}
            </g>
          );
        })}
      </svg>

      {expandedLevel !== null && (
        <div className="pyramid-sidebar">
          {(() => {
            const tier = levels.find((l) => l.level === expandedLevel);
            if (!tier) return null;
            return (
              <>
                <h4 style={{ color: tier.color, marginBottom: 8 }}>
                  L{tier.level}: {tier.name}
                </h4>
                <p className="pyramid-tier-stats">
                  {tier.entity_count} entities · {formatAmount(tier.total_money_flow_usd)} flow
                </p>
                <ul className="pyramid-entity-list">
                  {tier.entities.map((ent) => (
                    <li key={ent.entity_id}>
                      <button
                        type="button"
                        className={`pyramid-entity-btn ${highlightedEntityId === ent.entity_id ? 'highlighted' : ''}`}
                        onClick={() => onEntityClick?.(ent, tier.level)}
                      >
                        <span
                          className="pyramid-entity-dot"
                          style={{ backgroundColor: getEntityColor(ent.entity_type) }}
                        />
                        {ent.display_name}
                        {ent.entity_type && (
                          <span className="pyramid-entity-type">{ent.entity_type}</span>
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            );
          })()}
        </div>
      )}
      {tooltip && (
        <PyramidTooltip data={tooltip.data} x={tooltip.x} y={tooltip.y} />
      )}
    </div>
  );
}
