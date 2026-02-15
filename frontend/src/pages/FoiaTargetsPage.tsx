import { useEffect, useState, useMemo, Fragment } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { getFOIATargets } from '../services/api';
import type { FOIATarget } from '../types';
import ScoreBadge from '../components/ScoreBadge';
import TableSkeleton from '../components/TableSkeleton';
import EmptyState from '../components/EmptyState';
import './FoiaTargetsPage.css';

type SortKey = 'agency' | 'record_request' | 'timeframe' | 'priority_score' | 'specificity_score' | 'likelihood_score';
type SortDirection = 'asc' | 'desc';

function FoiaTargetsPage() {
  const [data, setData] = useState<FOIATarget[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
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
  }, [searchTerm, agencyFilter]);

  const handleSort = (key: SortKey) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
    setCurrentPage(1);
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
          <p>Browse and prioritize FOIA targets with quality scoring</p>
        </div>
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
                    <th onClick={() => handleSort('timeframe')} className="sortable">
                      Timeframe <SortIcon column="timeframe" />
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
                        <td>{foia.timeframe || 'N/A'}</td>
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
                      {expandedRow === foia.id && foia.quality_notes && (
                        <tr className="foia-notes-row">
                          <td colSpan={6}>
                            <div className="foia-quality-notes">
                              <strong>Quality Notes:</strong> {foia.quality_notes}
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
