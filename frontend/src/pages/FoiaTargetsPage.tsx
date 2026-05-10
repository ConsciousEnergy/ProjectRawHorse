import { useEffect, useState, useMemo, Fragment } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { getFOIATargets } from '../services/api';
import type { FOIATarget } from '../types';
import ScoreBadge from '../components/ScoreBadge';
import TableSkeleton from '../components/TableSkeleton';
import EmptyState from '../components/EmptyState';
import './FoiaTargetsPage.css';

type SortKey =
  | 'agency'
  | 'record_request'
  | 'status'
  | 'response_due_at'
  | 'estimated_cost'
  | 'actual_cost'
  | 'priority_score'
  | 'specificity_score'
  | 'likelihood_score';
type SortDirection = 'asc' | 'desc';

function FoiaTargetsPage() {
  const [data, setData] = useState<FOIATarget[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; direction: SortDirection }>({
    key: 'priority_score',
    direction: 'desc',
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const params: Record<string, unknown> = { limit: 500 };
        if (searchTerm.trim()) params.search = searchTerm.trim();
        if (agencyFilter.trim()) params.agency = agencyFilter.trim();
        if (statusFilter) params.status = statusFilter;
        if (overdueOnly) params.overdue_only = true;
        const result = await getFOIATargets(params);
        setData(result);
      } catch (error) {
        console.error('Error loading FOIA targets:', error);
        setData([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [searchTerm, agencyFilter, statusFilter, overdueOnly]);

  const handleSort = (key: SortKey) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
    setCurrentPage(1);
  };

  const formatDate = (value?: string | null) => (value ? value : 'N/A');
  const formatCurrency = (value?: number | null) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
  };
  const displayStatus = (status?: string) => {
    const raw = (status || 'draft').toLowerCase();
    return raw.charAt(0).toUpperCase() + raw.slice(1);
  };

  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data;
    return [...data].sort((a, b) => {
      const aVal = (a as unknown as Record<string, unknown>)[sortConfig.key];
      const bVal = (b as unknown as Record<string, unknown>)[sortConfig.key];
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      return sortConfig.direction === 'asc'
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr);
    });
  }, [data, sortConfig]);

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return sortedData.slice(start, start + itemsPerPage);
  }, [sortedData, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(sortedData.length / itemsPerPage);
  const SortIcon = ({ column }: { column: SortKey }) =>
    sortConfig.key === column ? (
      sortConfig.direction === 'asc' ? (
        <ChevronUp size={14} style={{ marginLeft: 4 }} />
      ) : (
        <ChevronDown size={14} style={{ marginLeft: 4 }} />
      )
    ) : null;

  return (
    <div className="foia-targets-page fade-in" role="main" aria-label="FOIA Targets">
      <div className="foia-page-header">
        <Link to="/analysis" className="back-link">
          <ChevronLeft size={20} />
          <span>Back to Analysis</span>
        </Link>
        <div className="foia-page-title">
          <h1>FOIA Targets</h1>
          <p>Track FOIA targets from draft through response with due dates, costs, and source links.</p>
        </div>
      </div>

      <div className="foia-purpose-note">
        <strong>What this is for:</strong> Maintain a research FOIA pipeline, monitor response deadlines,
        and keep reference/archive links for each request target.
      </div>

      <div className="foia-filters">
        <input
          type="text"
          placeholder="Search records, agency, notes..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="foia-search-input"
          aria-label="Search FOIA targets"
        />
        <input
          type="text"
          placeholder="Filter by agency"
          value={agencyFilter}
          onChange={(e) => {
            setAgencyFilter(e.target.value);
            setCurrentPage(1);
          }}
          className="foia-agency-input"
          aria-label="Filter by agency"
        />
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setCurrentPage(1);
          }}
          className="foia-status-input"
          aria-label="Filter by status"
        >
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="submitted">Submitted</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="responded">Responded</option>
          <option value="closed">Closed</option>
        </select>
        <label className="foia-overdue-toggle">
          <input
            type="checkbox"
            checked={overdueOnly}
            onChange={(e) => {
              setOverdueOnly(e.target.checked);
              setCurrentPage(1);
            }}
          />
          Overdue only
        </label>
      </div>

      <div className="foia-content card">
        {loading ? (
          <TableSkeleton />
        ) : sortedData.length === 0 ? (
          <EmptyState
            icon="📋"
            title="No FOIA targets found"
            description="Try adjusting your search or agency filter."
          />
        ) : (
          <>
            <div className="foia-pagination-top">
              <span className="foia-result-count">
                Showing {paginatedData.length} of {sortedData.length} targets
              </span>
              <label className="foia-page-size">
                Show:
                <select
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  aria-label="Items per page"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </label>
            </div>
            <div className="foia-table-wrapper">
              <table className="foia-table data-table" role="table" aria-label="FOIA targets table">
                <thead>
                  <tr>
                    <th onClick={() => handleSort('agency')} className="sortable">
                      Agency <SortIcon column="agency" />
                    </th>
                    <th onClick={() => handleSort('record_request')} className="sortable">
                      Record Request <SortIcon column="record_request" />
                    </th>
                    <th onClick={() => handleSort('status')} className="sortable">
                      Status <SortIcon column="status" />
                    </th>
                    <th onClick={() => handleSort('response_due_at')} className="sortable">
                      Response Due <SortIcon column="response_due_at" />
                    </th>
                    <th onClick={() => handleSort('estimated_cost')} className="sortable">
                      Est. Cost <SortIcon column="estimated_cost" />
                    </th>
                    <th onClick={() => handleSort('actual_cost')} className="sortable">
                      Actual Cost <SortIcon column="actual_cost" />
                    </th>
                    <th onClick={() => handleSort('priority_score')} className="sortable">
                      Priority <SortIcon column="priority_score" />
                    </th>
                    <th onClick={() => handleSort('specificity_score')} className="sortable">
                      Specificity <SortIcon column="specificity_score" />
                    </th>
                    <th onClick={() => handleSort('likelihood_score')} className="sortable">
                      Likelihood <SortIcon column="likelihood_score" />
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((foia) => (
                    <Fragment key={foia.id}>
                      <tr
                        className={expandedRow === foia.id ? 'expanded' : ''}
                        onClick={() => setExpandedRow(expandedRow === foia.id ? null : foia.id)}
                      >
                        <td className="foia-agency-cell" title={foia.agency}>
                          {foia.agency}
                        </td>
                        <td className="foia-record-cell" title={foia.record_request}>
                          {foia.record_request}
                        </td>
                        <td>
                          <span className={`foia-status foia-status-${(foia.status || 'draft').toLowerCase()}`}>
                            {displayStatus(foia.status)}
                          </span>
                          {foia.is_overdue && <span className="foia-overdue-chip">Overdue</span>}
                        </td>
                        <td>{formatDate(foia.response_due_at)}</td>
                        <td>{formatCurrency(foia.estimated_cost)}</td>
                        <td>{formatCurrency(foia.actual_cost)}</td>
                        <td>
                          <ScoreBadge score={foia.priority_score} type="priority" />
                        </td>
                        <td>
                          <ScoreBadge score={foia.specificity_score} type="specificity" />
                        </td>
                        <td>
                          <ScoreBadge score={foia.likelihood_score} type="likelihood" />
                        </td>
                      </tr>
                      {expandedRow === foia.id && (
                        <tr className="foia-notes-row">
                          <td colSpan={9}>
                            <div className="foia-quality-notes">
                              <div><strong>Quality Notes:</strong> {foia.quality_notes}</div>
                              <div><strong>Timeframe:</strong> {foia.timeframe || 'N/A'}</div>
                              <div><strong>Submitted:</strong> {formatDate(foia.submitted_at)}</div>
                              <div><strong>Responded:</strong> {formatDate(foia.responded_at)}</div>
                              {(foia.reference_url || foia.archive_url) && (
                                <div className="foia-links-row">
                                  {foia.reference_url && (
                                    <a href={foia.reference_url} target="_blank" rel="noreferrer noopener">Reference</a>
                                  )}
                                  {foia.archive_url && (
                                    <a href={foia.archive_url} target="_blank" rel="noreferrer noopener">Archive</a>
                                  )}
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  ))}
                </tbody>
              </table>
            </div>
            {totalPages > 1 && (
              <div className="foia-pagination">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((p) => p - 1)}
                  className="btn btn-sm"
                >
                  ← Prev
                </button>
                <span className="page-info">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage((p) => p + 1)}
                  className="btn btn-sm"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default FoiaTargetsPage;
