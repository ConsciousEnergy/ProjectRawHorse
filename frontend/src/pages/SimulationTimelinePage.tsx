import { useEffect, useMemo, useRef, useState } from 'react';
import { getSimulationTimeline } from '../services/api';
import type { SimulationTimelineResponse, SimulationFlowItem, SimulationEventItem } from '../types';
import './SimulationTimelinePage.css';

type GroupBy = 'year' | 'decade';

const confidenceColor = (tier?: string | null): string => {
  if (!tier) return '#6b7280';
  if (tier === 'confirmed') return '#10b981';
  if (tier === 'corroborated') return '#f59e0b';
  return '#ef4444';
};

function DenseFlowCanvas({ flows }: { flows: SimulationFlowItem[] }) {
  const ref = useRef<HTMLCanvasElement | null>(null);

  const yearly = useMemo(() => {
    const m = new Map<number, number>();
    for (const f of flows) {
      const y = f.year ?? 0;
      if (!y) continue;
      m.set(y, (m.get(y) ?? 0) + (f.amount_usd ?? 0));
    }
    return [...m.entries()].sort((a, b) => a[0] - b[0]);
  }, [flows]);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas || yearly.length === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    const minYear = yearly[0][0];
    const maxYear = yearly[yearly.length - 1][0];
    const maxAmount = Math.max(...yearly.map((x) => x[1]), 1);

    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = 2;
    ctx.beginPath();
    yearly.forEach(([year, amount], i) => {
      const x = ((year - minYear) / Math.max(1, maxYear - minYear)) * (width - 20) + 10;
      const y = height - ((amount / maxAmount) * (height - 20) + 10);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }, [yearly]);

  return <canvas ref={ref} width={1000} height={180} className="simulation-canvas" aria-label="Dense flow canvas rendering" />;
}

function SimulationTimelinePage() {
  const [data, setData] = useState<SimulationTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [confidenceMin, setConfidenceMin] = useState(0.5);
  const [groupBy, setGroupBy] = useState<GroupBy>('year');
  const [showEvents, setShowEvents] = useState(true);
  const [showFlows, setShowFlows] = useState(true);
  const [showEntities, setShowEntities] = useState(true);
  const [showConnections, setShowConnections] = useState(true);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getSimulationTimeline({
        confidence_min: confidenceMin,
        group_by: groupBy,
        page: 1,
        page_size: 250,
      });
      setData(response);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load simulation timeline';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const years = useMemo(() => {
    if (!data) return [];
    const out: number[] = [];
    data.events.forEach((e: SimulationEventItem) => {
      const y = new Date(e.event_date).getFullYear();
      if (!Number.isNaN(y)) out.push(y);
    });
    data.money_flows.forEach((f: SimulationFlowItem) => {
      if (typeof f.year === 'number') out.push(f.year);
    });
    return [...new Set(out)].sort((a, b) => a - b);
  }, [data]);

  const timelineWidth = 1200;
  const x = (year: number) => {
    if (years.length === 0) return 40;
    const min = years[0];
    const max = years[years.length - 1];
    if (max === min) return 40;
    return 40 + ((year - min) / (max - min)) * (timelineWidth - 80);
  };

  const topEntities = useMemo(() => {
    if (!data) return [];
    return [...data.entities]
      .sort((a, b) => (b.simulation_confidence ?? 0) - (a.simulation_confidence ?? 0))
      .slice(0, 14);
  }, [data]);

  if (loading) {
    return (
      <div className="simulation-page">
        <div className="page-header">
          <h1>Simulation Timeline</h1>
          <p>Loading timeline layers and confidence mappings...</p>
        </div>
        <div className="simulation-skeleton">Loading visualization...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="simulation-page">
        <div className="page-header">
          <h1>Simulation Timeline</h1>
        </div>
        <div className="simulation-error">
          <p>{error}</p>
          <button className="btn btn-primary" onClick={load}>Retry</button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="simulation-page">
      <div className="page-header">
        <h1>Simulation Timeline</h1>
        <p>Unified temporal view of events, money flows, entities, and confidence-linked connections.</p>
      </div>

      <div className="simulation-controls card">
        <div className="control-group">
          <label>Confidence Threshold</label>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={confidenceMin}
            onChange={(e) => setConfidenceMin(parseFloat(e.target.value))}
          />
          <span>{confidenceMin.toFixed(2)}</span>
        </div>

        <div className="control-group">
          <label>Group By</label>
          <select value={groupBy} onChange={(e) => setGroupBy(e.target.value as GroupBy)}>
            <option value="year">Year</option>
            <option value="decade">Decade</option>
          </select>
        </div>

        <div className="control-group toggles" aria-label="Layer toggles">
          <label><input type="checkbox" checked={showEvents} onChange={() => setShowEvents((v) => !v)} /> Events</label>
          <label><input type="checkbox" checked={showFlows} onChange={() => setShowFlows((v) => !v)} /> Flows</label>
          <label><input type="checkbox" checked={showEntities} onChange={() => setShowEntities((v) => !v)} /> Entities</label>
          <label><input type="checkbox" checked={showConnections} onChange={() => setShowConnections((v) => !v)} /> Connections</label>
        </div>

        <button className="btn btn-primary" onClick={load}>Apply Filters</button>
      </div>

      <div className="simulation-meta card">
        <span>Events: {data.meta.total_events}</span>
        <span>Flows: {data.meta.total_flows}</span>
        <span>Entities: {data.meta.total_entities}</span>
        <span>Connections: {data.meta.total_connections}</span>
        {data.meta.truncated && <span className="warn">Showing paged subset</span>}
      </div>

      <div className="timeline-surface card">
        <svg viewBox={`0 0 ${timelineWidth} 520`} role="img" aria-label="Simulation timeline lanes">
          <line x1="40" y1="42" x2={timelineWidth - 40} y2="42" className="axis-line" />
          {years.filter((_y, i) => i % Math.max(1, Math.floor(years.length / 12)) === 0).map((year) => (
            <g key={year}>
              <line x1={x(year)} y1="36" x2={x(year)} y2="48" className="tick-line" />
              <text x={x(year)} y="24" className="tick-text">{year}</text>
            </g>
          ))}

          {showEvents && data.events.map((e) => {
            const year = new Date(e.event_date).getFullYear();
            return (
              <g key={e.event_id}>
                <circle cx={x(year)} cy={105} r={6} fill={confidenceColor(e.confidence_tier)} />
                <title>{`${e.title} (${year}) - ${e.confidence_tier}`}</title>
              </g>
            );
          })}

          {showFlows && data.money_flows.slice(0, 220).map((f, idx) => {
            const year = f.year ?? years[0] ?? 1933;
            const stroke = confidenceColor(f.confidence_tier);
            const w = Math.max(1, Math.min(8, Math.log10((f.amount_usd ?? 1) + 1)));
            return (
              <line
                key={`${f.edge_id ?? idx}`}
                x1={x(year)}
                y1={150}
                x2={x(year)}
                y2={205}
                stroke={stroke}
                strokeWidth={w}
                opacity={0.75}
              >
                <title>{`${f.source} -> ${f.target} | ${f.amount_usd ?? 0}`}</title>
              </line>
            );
          })}

          {showEntities && topEntities.map((ent, idx) => {
            const rowY = 245 + idx * 16;
            const start = ent.effective_start_date ? new Date(ent.effective_start_date).getFullYear() : (years[0] ?? 1933);
            const end = ent.effective_end_date ? new Date(ent.effective_end_date).getFullYear() : (years[years.length - 1] ?? 2026);
            return (
              <g key={ent.entity_id}>
                <rect
                  x={x(start)}
                  y={rowY}
                  width={Math.max(2, x(end) - x(start))}
                  height={10}
                  fill={confidenceColor(ent.confidence_tier)}
                  opacity={0.75}
                />
                <text x={45} y={rowY + 9} className="entity-label">{ent.display_name}</text>
              </g>
            );
          })}
        </svg>
      </div>

      {showFlows && data.money_flows.length > 220 && (
        <div className="card">
          <h3>Dense Flow Layer (Canvas Fallback)</h3>
          <DenseFlowCanvas flows={data.money_flows} />
        </div>
      )}

      {showConnections && (
        <div className="card">
          <h3>Connection Trace</h3>
          <div className="simulation-list">
            {data.connections.slice(0, 30).map((c, idx) => (
              <div className="simulation-list-item" key={`${c.source}-${c.target}-${idx}`}>
                <span className="dot" style={{ backgroundColor: confidenceColor(c.confidence_tier) }} />
                <span>{c.source}</span>
                <span>→</span>
                <span>{c.target}</span>
                <span className="muted">{c.label ?? c.relationship_type ?? 'linked'}</span>
                <span className="muted">{c.simulation_confidence?.toFixed(2) ?? 'n/a'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationTimelinePage;
