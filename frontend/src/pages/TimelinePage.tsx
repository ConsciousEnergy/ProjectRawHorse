import { useEffect, useState, useCallback } from 'react';
import { getTimelineEvents, getTimelineBuckets } from '../services/api';
import type { TimelineEvent, TimelineBucket } from '../types';
import SkeletonLoader from '../components/SkeletonLoader';
import './TimelinePage.css';

const CONFIDENCE_COLORS: Record<string, string> = {
  confirmed: '#10b981',
  corroborated: '#f59e0b',
  contested: '#ef4444',
};

const CATEGORIES = [
  'crash_retrieval', 'legislation', 'disclosure', 'military',
  'scientific', 'whistleblower', 'organizational', 'sighting',
];

function TimelinePage() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [buckets, setBuckets] = useState<TimelineBucket[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);

  const [filterCategory, setFilterCategory] = useState('');
  const [filterConfidence, setFilterConfidence] = useState('');
  const [filterSearch, setFilterSearch] = useState('');
  const [startYear, setStartYear] = useState<number | undefined>(undefined);
  const [endYear, setEndYear] = useState<number | undefined>(undefined);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [eventData, bucketData] = await Promise.all([
        getTimelineEvents({
          category: filterCategory || undefined,
          confidence: filterConfidence || undefined,
          search: filterSearch || undefined,
          start_year: startYear,
          end_year: endYear,
          page,
          page_size: 50,
        }),
        getTimelineBuckets('decade'),
      ]);
      setEvents(eventData.events);
      setTotal(eventData.total);
      setBuckets(bucketData);
    } catch {
      setError('Failed to load timeline data.');
    } finally {
      setLoading(false);
    }
  }, [filterCategory, filterConfidence, filterSearch, startYear, endYear, page]);

  useEffect(() => { loadData(); }, [loadData]);

  const totalPages = Math.ceil(total / 50);

  return (
    <div className="timeline-page fade-in" role="main" aria-label="Historical Timeline">
      <div className="page-header">
        <h1>Historical UAP Timeline</h1>
        <p>1933 Magenta Crash to Present Day — {total} documented events</p>
      </div>

      {/* Decade bucket chart */}
      {buckets.length > 0 && (
        <div className="card timeline-chart-card">
          <h3>Events by Decade</h3>
          <div className="bucket-chart">
            {buckets.map((b) => {
              const maxCount = Math.max(...buckets.map((x) => x.count), 1);
              const height = Math.max((b.count / maxCount) * 120, 8);
              return (
                <div key={b.period} className="bucket-bar-wrapper">
                  <div
                    className="bucket-bar"
                    style={{ height: `${height}px` }}
                    title={`${b.period}: ${b.count} events`}
                  >
                    <span className="bucket-count">{b.count}</span>
                  </div>
                  <span className="bucket-label">{b.period}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card timeline-filters">
        <div className="filter-row">
          <select
            value={filterCategory}
            onChange={(e) => { setFilterCategory(e.target.value); setPage(1); }}
            aria-label="Filter by category"
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c.replace('_', ' ')}</option>
            ))}
          </select>
          <select
            value={filterConfidence}
            onChange={(e) => { setFilterConfidence(e.target.value); setPage(1); }}
            aria-label="Filter by confidence"
          >
            <option value="">All Confidence</option>
            <option value="confirmed">Confirmed</option>
            <option value="corroborated">Corroborated</option>
            <option value="contested">Contested</option>
          </select>
          <input
            type="number"
            placeholder="From year"
            min={1900}
            max={2100}
            value={startYear ?? ''}
            onChange={(e) => { setStartYear(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
            aria-label="Start year"
          />
          <input
            type="number"
            placeholder="To year"
            min={1900}
            max={2100}
            value={endYear ?? ''}
            onChange={(e) => { setEndYear(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
            aria-label="End year"
          />
          <input
            type="text"
            placeholder="Search events..."
            value={filterSearch}
            onChange={(e) => { setFilterSearch(e.target.value); setPage(1); }}
            aria-label="Search events"
          />
        </div>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
          <button onClick={loadData} className="btn btn-secondary" style={{ marginLeft: 12 }}>Retry</button>
        </div>
      )}

      {loading ? (
        <div className="card"><SkeletonLoader type="table" /></div>
      ) : (
        <div className="timeline-events-list">
          {events.map((evt) => (
            <div
              key={evt.event_id}
              className={`timeline-event-card ${selectedEvent?.event_id === evt.event_id ? 'selected' : ''}`}
              onClick={() => setSelectedEvent(selectedEvent?.event_id === evt.event_id ? null : evt)}
              role="button"
              tabIndex={0}
              aria-expanded={selectedEvent?.event_id === evt.event_id}
            >
              <div className="event-header">
                <span className="event-date">{evt.event_date}</span>
                <span
                  className="confidence-badge"
                  style={{ background: CONFIDENCE_COLORS[evt.confidence_tier] || '#666' }}
                >
                  {evt.confidence_tier}
                </span>
                {evt.category && <span className="category-tag">{evt.category.replace('_', ' ')}</span>}
              </div>
              <h4 className="event-title">{evt.title}</h4>
              {evt.summary && <p className="event-summary">{evt.summary}</p>}
              {evt.region && <span className="event-region">{evt.region}</span>}

              {selectedEvent?.event_id === evt.event_id && evt.sources.length > 0 && (
                <div className="event-sources">
                  <h5>Sources ({evt.sources.length})</h5>
                  <ul>
                    {evt.sources.map((src, i) => (
                      <li key={i}>
                        <span className="source-type">{src.source_type}</span>
                        {src.source_url ? (
                          <a href={src.source_url} target="_blank" rel="noopener noreferrer">
                            {src.source_title || src.source_url}
                          </a>
                        ) : (
                          <span>{src.source_title}</span>
                        )}
                        {src.notes && <span className="source-notes"> — {src.notes}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page} of {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </div>
  );
}

export default TimelinePage;
