import axios from 'axios';
import type { Entity, MoneyFlow, Award, FOIATarget, Stats, GraphData, SankeyData, DataVersion, PyramidData, HierarchyChain, EntityDetail, IntelStackSearchResponse } from '../types';

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
  const response = await api.get(`/analysis/relationships/${entityName}`);
  return response.data;
};

export const getFinancialFlows = async () => {
  const response = await api.get('/analysis/financial/flows');
  return response.data;
};

export const getTimeline = async () => {
  const response = await api.get('/analysis/timeline');
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

export const exportEntitiesJSON = () => {
  window.open(`${API_BASE_URL}/export/json/entities`, '_blank');
};

export const exportSummaryPDF = () => {
  window.open(`${API_BASE_URL}/export/pdf/summary`, '_blank');
};

// Contribution endpoints
export const contributeEntity = async (entity: any, githubToken: string) => {
  const response = await api.post('/contribute/entity', entity, {
    headers: {
      'X-GitHub-Token': githubToken,
    },
  });
  return response.data;
};

export const contributeMoneyFlow = async (moneyFlow: any, githubToken: string) => {
  const response = await api.post('/contribute/money-flow', moneyFlow, {
    headers: {
      'X-GitHub-Token': githubToken,
    },
  });
  return response.data;
};

export const contributeAward = async (award: any, githubToken: string) => {
  const response = await api.post('/contribute/award', award, {
    headers: {
      'X-GitHub-Token': githubToken,
    },
  });
  return response.data;
};

export const contributeFOIATarget = async (foiaTarget: any, githubToken: string) => {
  const response = await api.post('/contribute/foia-target', foiaTarget, {
    headers: {
      'X-GitHub-Token': githubToken,
    },
  });
  return response.data;
};

export const validateGitHubToken = async (token: string) => {
  const response = await api.get('/contribute/validate-token', {
    headers: {
      'X-GitHub-Token': token,
    },
  });
  return response.data;
};

export default api;
