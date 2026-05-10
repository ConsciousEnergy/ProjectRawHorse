import axios from 'axios';
import type {
  Entity, MoneyFlow, Award, FOIATarget, Stats, GraphData, SankeyData, DataVersion,
  PyramidData, HierarchyChain, EntityDetail, IntelStackSearchResponse,
  FinancialFlowsResponse, TimelineResponse, EntityRelationshipsResponse,
  TimelineEventListResponse, TimelineEvent, TimelineBucket, SimulationTimelineResponse, OfflineImportResult,
} from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Data endpoints
export const getEntities = async (params?: any) => {
  const response = await api.get<Entity[]>('/data/entities', { params });
  return response.data;
};

export const getMoneyFlows = async (params?: any) => {
  const response = await api.get<MoneyFlow[]>('/data/money-flows', { params });
  return response.data;
};

export const getAwards = async (params?: any) => {
  const response = await api.get<Award[]>('/data/awards', { params });
  return response.data;
};

export const getFOIATargets = async (params?: any) => {
  const response = await api.get<FOIATarget[]>('/data/foia-targets', { params });
  return response.data;
};

export const getOfflineImportTemplate = async (dataType: string) => {
  const response = await api.get<{ data_type: string; columns: string[] }>(`/import/templates/${encodeURIComponent(dataType)}`);
  return response.data;
};

export const uploadOfflineImportFile = async (params: {
  dataType: string;
  file: File;
  dryRun: boolean;
}) => {
  const formData = new FormData();
  formData.append('data_type', params.dataType);
  formData.append('dry_run', String(params.dryRun));
  formData.append('file', params.file);
  const response = await api.post<OfflineImportResult>('/import/offline', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get<Stats>('/data/stats');
  return response.data;
};

// Analysis endpoints
export const getEntityGraph = async () => {
  const response = await api.get<GraphData>('/analysis/graph/entities');
  return response.data;
};

export const getMoneyFlowGraph = async (minAmount?: number) => {
  const response = await api.get<GraphData>('/analysis/graph/money-flows', {
    params: { min_amount: minAmount },
  });
  return response.data;
};

export const getEntityRelationships = async (entityName: string) => {
  const response = await api.get<EntityRelationshipsResponse>(`/analysis/relationships/${encodeURIComponent(entityName)}`);
  return response.data;
};

export const getFinancialFlows = async () => {
  const response = await api.get<FinancialFlowsResponse>('/analysis/financial/flows');
  return response.data;
};

export const getTimeline = async () => {
  const response = await api.get<TimelineResponse>('/analysis/timeline');
  return response.data;
};

export const getSankeyData = async (params?: {
  min_amount?: number;
  include_relationships?: boolean;
  limit?: number;
}) => {
  const response = await api.get<SankeyData>('/analysis/sankey', { params });
  return response.data;
};

/** GET /analysis/intel-stack/pyramid: levels, entity counts, total money per level, cross-level flows. */
export const getPyramidData = async () => {
  const response = await api.get<PyramidData>('/analysis/intel-stack/pyramid');
  return response.data;
};

/** GET /analysis/intel-stack/hierarchy: chain of command for an entity. */
export const getPyramidHierarchy = async (entityId: string) => {
  const response = await api.get<HierarchyChain>('/analysis/intel-stack/hierarchy', {
    params: { entity_id: entityId },
  });
  return response.data;
};

/** GET /analysis/intel-stack/entity/:id/detail: full entity detail for drill-down. */
export const getPyramidEntityDetail = async (entityId: string) => {
  const response = await api.get<EntityDetail>(`/analysis/intel-stack/entity/${encodeURIComponent(entityId)}/detail`);
  return response.data;
};

/** GET /analysis/intel-stack/search: search entities with intel stack level. */
export const searchIntelStack = async (q: string, limit = 20) => {
  const response = await api.get<IntelStackSearchResponse>('/analysis/intel-stack/search', {
    params: { q, limit },
  });
  return response.data;
};

// Timeline endpoints
export const getTimelineEvents = async (params?: {
  category?: string;
  confidence?: string;
  search?: string;
  start_year?: number;
  end_year?: number;
  page?: number;
  page_size?: number;
}) => {
  const response = await api.get<TimelineEventListResponse>('/timeline/events', { params });
  return response.data;
};

export const getTimelineEvent = async (eventId: string) => {
  const response = await api.get<TimelineEvent>(`/timeline/events/${encodeURIComponent(eventId)}`);
  return response.data;
};

export const getTimelineBuckets = async (bucketSize: 'decade' | 'year' = 'decade') => {
  const response = await api.get<TimelineBucket[]>('/timeline/buckets', { params: { bucket_size: bucketSize } });
  return response.data;
};

export const getSimulationTimeline = async (params?: {
  start_year?: number;
  end_year?: number;
  confidence_min?: number;
  category?: string[];
  entity_id?: string[];
  page?: number;
  page_size?: number;
  group_by?: 'year' | 'decade';
}) => {
  const response = await api.get<SimulationTimelineResponse>('/simulation/timeline', { params });
  return response.data;
};

export const getSimulationEntities = async (params?: {
  confidence_min?: number;
  active_year?: number;
  type?: string;
  page?: number;
  page_size?: number;
}) => {
  const response = await api.get('/simulation/entities', { params });
  return response.data;
};

export const getSimulationFlows = async (params?: {
  confidence_min?: number;
  min_amount?: number;
  start_year?: number;
  end_year?: number;
  page?: number;
  page_size?: number;
}) => {
  const response = await api.get('/simulation/flows', { params });
  return response.data;
};

/**
 * Derived financial analytics — built from existing /analysis/financial/* endpoints.
 * Used by FinancialDashboard component.
 */
export const getTopRecipientsByType = async () => {
  const data = await api.get('/analysis/financial/totals');
  return {
    recipients: (data.data.top_recipients || []).map((r: { entity: string; amount: number }) => ({
      entity: r.entity,
      amount: r.amount,
    })),
  };
};

export const getAgencySpendingBreakdown = async () => {
  const data = await api.get('/analysis/financial/flows');
  const outflows: Array<{ entity: string; amount: number }> = data.data.outflows || [];
  const totalAmount = outflows.reduce((s: number, o: { amount: number }) => s + (o.amount || 0), 0);
  return {
    agencies: outflows
      .sort((a: { amount: number }, b: { amount: number }) => (b.amount || 0) - (a.amount || 0))
      .slice(0, 15)
      .map((o: { entity: string; amount: number }) => ({
        agency: o.entity,
        amount: o.amount || 0,
        percentage: totalAmount > 0 ? ((o.amount || 0) / totalAmount) * 100 : 0,
      })),
  };
};

export const getAmountDistribution = async () => {
  const flows = await api.get('/data/money-flows', { params: { limit: 1000 } });
  const amounts: number[] = (flows.data || [])
    .map((f: { amount_usd?: number }) => f.amount_usd)
    .filter((a: number | undefined): a is number => a != null && a > 0);
  if (amounts.length === 0) {
    return { count: 0, total: 0, mean: 0, median: 0, min: 0, max: 0, std_dev: 0, distribution_bins: [] };
  }
  amounts.sort((a: number, b: number) => a - b);
  const count = amounts.length;
  const total = amounts.reduce((s, v) => s + v, 0);
  const mean = total / count;
  const median = count % 2 === 0 ? (amounts[count / 2 - 1] + amounts[count / 2]) / 2 : amounts[Math.floor(count / 2)];
  const min = amounts[0];
  const max = amounts[count - 1];
  const variance = amounts.reduce((s, v) => s + (v - mean) ** 2, 0) / count;
  const std_dev = Math.sqrt(variance);
  const bins = ['<$1K', '$1K-$10K', '$10K-$100K', '$100K-$1M', '$1M-$10M', '$10M+'];
  const thresholds = [1000, 10000, 100000, 1000000, 10000000, Infinity];
  const binCounts = new Array(bins.length).fill(0);
  for (const a of amounts) {
    for (let i = 0; i < thresholds.length; i++) {
      if (a < thresholds[i]) { binCounts[i]++; break; }
    }
  }
  return { count, total, mean, median, min, max, std_dev, distribution_bins: bins.map((label, i) => ({ label, count: binCounts[i] })) };
};

export const getDataVersion = async () => {
  const response = await api.get<DataVersion>('/data/version');
  return response.data;
};

export const refreshData = async () => {
  const response = await api.post('/data/refresh');
  return response.data;
};

// Search endpoint
export const searchGlobal = async (query: string, types?: string[], limit?: number) => {
  const response = await api.get('/search', {
    params: {
      q: query,
      types: types,
      limit: limit,
    },
  });
  return response.data;
};

// Export endpoints
export const exportEntitiesCSV = () => {
  window.open(`${API_BASE_URL}/export/csv/entities`, '_blank');
};

export const exportMoneyFlowsCSV = () => {
  window.open(`${API_BASE_URL}/export/csv/money-flows`, '_blank');
};

export const exportAwardsCSV = () => {
  window.open(`${API_BASE_URL}/export/csv/awards`, '_blank');
};

export const exportFOIATargetsCSV = () => {
  window.open(`${API_BASE_URL}/export/csv/foia-targets`, '_blank');
};

export const exportEntitiesJSON = () => {
  window.open(`${API_BASE_URL}/export/json/entities`, '_blank');
};

export const exportSummaryPDF = () => {
  window.open(`${API_BASE_URL}/export/pdf/summary`, '_blank');
};

// Contribution endpoints (database-first, no GitHub token required)
export const submitContribution = async (payload: {
  contribution_type: string;
  data: Record<string, unknown>;
  contributor_name?: string;
  contributor_email?: string;
  notes?: string;
}) => {
  const response = await api.post('/contribute/submit', payload);
  return response.data;
};

export const getContributionQueue = async (params?: {
  status?: string;
  skip?: number;
  limit?: number;
}) => {
  const response = await api.get('/contribute/queue', { params });
  return response.data;
};

export const reviewContribution = async (
  contributionId: number,
  action: 'approve' | 'reject',
  review_notes?: string,
) => {
  const response = await api.post(`/contribute/${contributionId}/review`, {
    action,
    review_notes,
  });
  return response.data;
};

export default api;
