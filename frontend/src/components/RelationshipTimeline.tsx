import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import './RelationshipTimeline.css';

interface TimelineLink {
  source: string;
  target: string;
  label?: string;
  value?: number;
  count?: number;
}

interface RelationshipTimelineProps {
  actorName: string;
  /** All links from the current graph data */
  links: TimelineLink[];
  /** Total relationships before filters */
  totalLinks: number;
  onClose: () => void;
  onSelectActor: (name: string) => void;
}

function classifyRelationType(label: string): { cls: string; text: string } {
  if (!label) return { cls: 'relationship', text: 'RELATED' };
  const l = label.toLowerCase();
  if (l.includes('money flow') || l.includes('$') || l.includes('financial')) {
    return { cls: 'financial', text: 'FINANCIAL' };
  }
  if (l.includes('award') || l.includes('contract')) {
    return { cls: 'award', text: 'AWARD' };
  }
  if (l.includes('co-recipient') || l.includes('same industry') || l.includes('inferred')) {
    return { cls: 'inferred', text: 'INFERRED' };
  }
  return { cls: 'relationship', text: 'RELATED' };
}

function formatAmount(val: number | undefined | null): string | null {
  if (!val || val <= 0) return null;
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(2)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(1)}K`;
  return `$${val.toLocaleString()}`;
}

export default function RelationshipTimeline({
  actorName,
  links,
  totalLinks,
  onClose,
  onSelectActor,
}: RelationshipTimelineProps) {
  const [entityFilter, setEntityFilter] = useState('');

  // Get connections for this actor
  const actorLinks = useMemo(() => {
    return links.filter(l => {
      const src = typeof l.source === 'string' ? l.source : (l.source as any)?.id || '';
      const tgt = typeof l.target === 'string' ? l.target : (l.target as any)?.id || '';
      return src === actorName || tgt === actorName;
    });
  }, [links, actorName]);

  // Apply entity filter
  const filteredLinks = useMemo(() => {
    if (!entityFilter.trim()) return actorLinks;
    const q = entityFilter.toLowerCase();
    return actorLinks.filter(l => {
      const src = typeof l.source === 'string' ? l.source : (l.source as any)?.id || '';
      const tgt = typeof l.target === 'string' ? l.target : (l.target as any)?.id || '';
      const other = src === actorName ? tgt : src;
      return other.toLowerCase().includes(q);
    });
  }, [actorLinks, entityFilter, actorName]);

  return (
    <div className="relationship-timeline">
      {/* Header */}
      <div className="timeline-header">
        <div className="timeline-header-top">
          <h3>Timeline</h3>
          <button className="timeline-close-btn" onClick={onClose} title="Close panel">
            ✕
          </button>
        </div>
        <div className="timeline-actor-name">{actorName}</div>
        <div className="timeline-subtitle">
          Showing {filteredLinks.length} of {totalLinks} relationships
        </div>
      </div>

      {/* Filter */}
      <div className="timeline-filter">
        <label>Filter by entity:</label>
        <input
          className="timeline-filter-input"
          type="text"
          placeholder="e.g., Boeing"
          value={entityFilter}
          onChange={(e) => setEntityFilter(e.target.value)}
        />
      </div>

      {/* Entries */}
      <div className="timeline-entries">
        {filteredLinks.length === 0 ? (
          <div className="timeline-empty">No interactions found</div>
        ) : (
          filteredLinks.map((link, idx) => {
            const src = typeof link.source === 'string' ? link.source : (link.source as any)?.id || '';
            const tgt = typeof link.target === 'string' ? link.target : (link.target as any)?.id || '';
            const otherActor = src === actorName ? tgt : src;
            const isSource = src === actorName;
            const relType = classifyRelationType(link.label || '');
            const amount = formatAmount(link.value);

            return (
              <div key={`${src}-${tgt}-${idx}`} className="timeline-entry">
                <span className={`timeline-entry-type ${relType.cls}`}>{relType.text}</span>
                {link.count && link.count > 1 && (
                  <span style={{ fontSize: '0.68rem', color: '#64748b', marginLeft: 6 }}>
                    x{link.count}
                  </span>
                )}
                <div className="timeline-entry-actors">
                  <span
                    className="actor-source"
                    onClick={() => onSelectActor(isSource ? actorName : otherActor)}
                  >
                    {isSource ? actorName : otherActor}
                  </span>
                  <span className="actor-action"> {link.label || 'related to'} </span>
                  <span
                    className="actor-target"
                    onClick={() => onSelectActor(isSource ? otherActor : actorName)}
                  >
                    {isSource ? otherActor : actorName}
                  </span>
                </div>
                {amount && <div className="timeline-entry-amount">{amount}</div>}
              </div>
            );
          })
        )}
      </div>

      {/* Browse Link */}
      <Link
        to={`/browse?search=${encodeURIComponent(actorName)}&highlight=${encodeURIComponent(actorName)}`}
        className="timeline-browse-link"
      >
        View {actorName} in Browse
      </Link>
    </div>
  );
}
