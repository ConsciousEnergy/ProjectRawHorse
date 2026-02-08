/**
 * PyramidTooltip: Shared tooltip for pyramid viz. Shows tier summary, entity detail, or flow breakdown.
 * Positioned near cursor, avoids viewport edges.
 */
import type { PyramidEntitySummary, PyramidLevelSummary, CrossLevelFlow } from '../types';
import './PyramidTooltip.css';

function formatAmount(n: number): string {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}K`;
  return `$${n.toFixed(0)}`;
}

export type PyramidTooltipKind = 'tier' | 'entity' | 'flow';

export interface PyramidTooltipTierData {
  kind: 'tier';
  tier: PyramidLevelSummary;
  topEntities: string[];
}

export interface PyramidTooltipEntityData {
  kind: 'entity';
  entity: PyramidEntitySummary;
  level: number;
  levelName: string;
}

export interface PyramidTooltipFlowData {
  kind: 'flow';
  flow: CrossLevelFlow;
  fromName: string;
  toName: string;
}

export type PyramidTooltipData = PyramidTooltipTierData | PyramidTooltipEntityData | PyramidTooltipFlowData;

interface PyramidTooltipProps {
  data: PyramidTooltipData | null;
  x: number;
  y: number;
}

const TOOLTIP_OFFSET = 14;

export default function PyramidTooltip({ data, x, y }: PyramidTooltipProps) {
  if (!data) return null;

  const style: React.CSSProperties = {
    left: x + TOOLTIP_OFFSET,
    top: y + TOOLTIP_OFFSET,
  };

  return (
    <div className="pyramid-tooltip" style={style} role="tooltip">
      {data.kind === 'tier' && (
        <div className="pyramid-tooltip-tier">
          <div className="pyramid-tooltip-title" style={{ color: data.tier.color }}>
            L{data.tier.level}: {data.tier.name}
          </div>
          <div className="pyramid-tooltip-meta">
            {data.tier.entity_count} entities · {formatAmount(data.tier.total_money_flow_usd)} flow
          </div>
          {data.topEntities.length > 0 && (
            <div className="pyramid-tooltip-list">
              {data.topEntities.slice(0, 3).map((name) => (
                <span key={name} className="pyramid-tooltip-item">
                  {name}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
      {data.kind === 'entity' && (
        <div className="pyramid-tooltip-entity">
          <div className="pyramid-tooltip-title">{data.entity.display_name}</div>
          <div className="pyramid-tooltip-meta">
            {data.entity.entity_type ?? 'Unknown'} · L{data.level} {data.levelName}
          </div>
          {data.entity.description && (
            <p className="pyramid-tooltip-desc">{data.entity.description}</p>
          )}
          <div className="pyramid-tooltip-meta">
            {data.entity.relationship_count ?? 0} relationships · {formatAmount(data.entity.money_flow_total_usd ?? 0)} flow
          </div>
          {data.entity.key_connections && data.entity.key_connections.length > 0 && (
            <div className="pyramid-tooltip-list">
              <span className="pyramid-tooltip-label">Key connections:</span>
              {data.entity.key_connections.slice(0, 3).map((c) => (
                <span key={c} className="pyramid-tooltip-item">
                  {c}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
      {data.kind === 'flow' && (
        <div className="pyramid-tooltip-flow">
          <div className="pyramid-tooltip-title">
            {data.fromName} → {data.toName}
          </div>
          <div className="pyramid-tooltip-meta">
            {formatAmount(data.flow.total_usd)} · {data.flow.flow_count} flow(s)
          </div>
        </div>
      )}
    </div>
  );
}
