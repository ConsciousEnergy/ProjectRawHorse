/**
 * EntityDetailPanel: Slide-in drawer showing entity detail, chain of command, relationships, and flows.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getPyramidEntityDetail, getPyramidHierarchy } from '../services/api';
import type { EntityDetail, HierarchyChain } from '../types';
import './EntityDetailPanel.css';

interface EntityDetailPanelProps {
  entityId: string | null;
  onClose: () => void;
  /** When true, render inline in layout (no overlay). */
  inline?: boolean;
}

function formatAmount(n: number): string {
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}K`;
  return `$${n.toFixed(0)}`;
}

const LEVEL_NAMES: Record<number, string> = {
  1: 'Control Group',
  2: 'Administrators',
  3: 'FFRDCs',
  4: 'Prime Contractors',
  5: 'Facilities',
  6: 'Programs',
};

export default function EntityDetailPanel({ entityId, onClose, inline = false }: EntityDetailPanelProps) {
  const [detail, setDetail] = useState<EntityDetail | null>(null);
  const [hierarchy, setHierarchy] = useState<HierarchyChain | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!entityId) {
      setDetail(null);
      setHierarchy(null);
      return;
    }
    setLoading(true);
    Promise.all([
      getPyramidEntityDetail(entityId),
      getPyramidHierarchy(entityId).catch(() => null),
    ])
      .then(([d, h]) => {
        setDetail(d);
        setHierarchy(h ?? null);
      })
      .finally(() => setLoading(false));
  }, [entityId]);

  if (!entityId) return null;

  const panelContent = (
    <div className={`entity-detail-panel ${inline ? 'entity-detail-panel-inline' : ''}`} role="dialog" aria-label="Entity detail">
        <div className="entity-detail-panel-header">
          <h3>Entity detail</h3>
          <button type="button" className="entity-detail-panel-close" onClick={onClose} aria-label="Close">×</button>
        </div>
        {loading && <div className="entity-detail-panel-loading">Loading…</div>}
        {!loading && detail && (
          <div className="entity-detail-panel-body">
            <h2 className="entity-detail-name">{detail.display_name}</h2>
            <div className="entity-detail-meta">
              {detail.entity_type && <span className="entity-detail-badge">{detail.entity_type}</span>}
              {detail.intel_stack_level != null && (
                <span className="entity-detail-badge entity-detail-level">
                  L{detail.intel_stack_level} {LEVEL_NAMES[detail.intel_stack_level] ?? ''}
                </span>
              )}
            </div>
            {detail.description && <p className="entity-detail-desc">{detail.description}</p>}
            {hierarchy && (hierarchy.chain_up.length > 0 || hierarchy.chain_down.length > 0) && (
              <section className="entity-detail-section">
                <h4>Chain of command</h4>
                <div className="entity-detail-chain">
                  {hierarchy.chain_up.length > 0 && (
                    <div className="entity-detail-chain-up">
                      <span className="entity-detail-chain-label">Up (toward L1)</span>
                      {hierarchy.chain_up.map((n) => (
                        <div key={n.entity_id} className="entity-detail-chain-node">L{n.intel_stack_level ?? '?'} {n.display_name}</div>
                      ))}
                    </div>
                  )}
                  <div className="entity-detail-chain-target">→ {detail.display_name}</div>
                  {hierarchy.chain_down.length > 0 && (
                    <div className="entity-detail-chain-down">
                      <span className="entity-detail-chain-label">Down (toward L6)</span>
                      {hierarchy.chain_down.map((n) => (
                        <div key={n.entity_id} className="entity-detail-chain-node">L{n.intel_stack_level ?? '?'} {n.display_name}</div>
                      ))}
                    </div>
                  )}
                </div>
              </section>
            )}
            {detail.relationships_by_type && Object.keys(detail.relationships_by_type).length > 0 && (
              <section className="entity-detail-section">
                <h4>Relationships</h4>
                {Object.entries(detail.relationships_by_type).map(([type, rels]) => (
                  <div key={type} className="entity-detail-rel-group">
                    <span className="entity-detail-rel-type">{type}</span>
                    <ul>
                      {rels.map((r, i) => (
                        <li key={i}>
                          {r.source === detail.display_name ? r.target : r.source}
                          {r.description && <span className="entity-detail-rel-desc"> — {r.description}</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </section>
            )}
            {detail.money_flows && detail.money_flows.length > 0 && (
              <section className="entity-detail-section">
                <h4>Money flows</h4>
                <ul className="entity-detail-flows">
                  {detail.money_flows.slice(0, 15).map((f, i) => (
                    <li key={i}>{f.source} → {f.target}: {f.amount_usd != null ? formatAmount(f.amount_usd) : '—'}</li>
                  ))}
                  {detail.money_flows.length > 15 && <li className="entity-detail-more">+{detail.money_flows.length - 15} more</li>}
                </ul>
              </section>
            )}
            {detail.materials_flows && detail.materials_flows.length > 0 && (
              <section className="entity-detail-section">
                <h4>Materials flows</h4>
                <ul className="entity-detail-flows">
                  {detail.materials_flows.slice(0, 10).map((f, i) => (
                    <li key={i}>{f.source} → {f.target}{f.material_type ? ` (${f.material_type})` : ''}</li>
                  ))}
                  {detail.materials_flows.length > 10 && <li className="entity-detail-more">+{detail.materials_flows.length - 10} more</li>}
                </ul>
              </section>
            )}
            <section className="entity-detail-section entity-detail-actions">
              <Link to={`/analysis/network?entity=${encodeURIComponent(detail.display_name)}`} className="entity-detail-link">View in Network Graph</Link>
              <Link to={`/browse?q=${encodeURIComponent(detail.display_name)}`} className="entity-detail-link">View in Browse</Link>
            </section>
          </div>
        )}
      </div>
  );

  if (inline) return panelContent;
  return (
    <div className="entity-detail-panel-overlay" onClick={onClose} role="presentation">
      <div onClick={(e) => e.stopPropagation()}>
        {panelContent}
      </div>
    </div>
  );
}
