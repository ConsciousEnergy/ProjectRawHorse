export interface Entity {
  entity_id: string;
  display_name: string;
  normalized_name: string;
  entity_type?: string;
  intel_stack_level?: number; // 1-6 hierarchy level
}

// Intelligence Stack Levels for filtering
export const INTEL_STACK_LEVELS = {
  1: 'Control Group',      // MITRE/JASON, NSC, Executive Branch
  2: 'Administrators',     // NRO, NGA, CIA DS&T, DIA, NSA, OUSD
  3: 'FFRDCs',            // MITRE, Battelle, Sandia, LANL, LLNL, Oak Ridge
  4: 'Prime Contractors', // Lockheed Martin, Northrop Grumman, Raytheon
  5: 'Facilities',        // Area 51, S4, Edwards AFB, Tonopah, Dugway
  6: 'Programs',          // Immaculate Constellation, Kona Blue, etc.
} as const;

export interface MoneyFlow {
  id: number;
  source: string;
  target: string;
  relationship?: string;
  amount_usd?: number;
  start_date?: string;
  source_citation?: string;
}

export interface Award {
  id: number;
  piid?: string;
  recipient_name?: string;
  recipient_uei?: string;
  awarding_agency?: string;
  award_amount?: number;
  action_date?: string;
  description?: string;
  naics_code?: string;
}

export interface FOIATarget {
  id: number;
  agency: string;
  record_request: string;
  timeframe?: string;
  relevance?: string;
  notes?: string;
  specificity_score?: number;
  likelihood_score?: number;
  priority_score?: number;
  quality_notes?: string;
}

export interface Stats {
  total_entities: number;
  total_money_flows: number;
  total_awards: number;
  total_foia_targets: number;
  total_money_amount: number;
  date_range_start?: string;
  date_range_end?: string;
}

export interface GraphNode {
  id: string;
  name: string;
  type: string;
  value?: number;
  full_name?: string;  // Expanded name for acronyms
  intel_stack_level?: number;  // Intelligence stack hierarchy level (1-6)
}

export interface GraphEdge {
  source: string;
  target: string;
  value?: number;
  label?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SearchResult {
  type: 'entity' | 'award' | 'money_flow' | 'foia_target';
  id: string | number;
  title: string;
  description: string;
  matched_field: string;
  matched_text: string;
  relevance: number;
  metadata: any;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
}

export interface SankeyNode {
  name: string;
  value: number;
  category: string;
}

export interface SankeyLink {
  source: string;
  target: string;
  value: number;
  label?: string;
  type?: 'money_flow' | 'relationship';
}

export interface SankeyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

export interface DataVersion {
  version: number;
  last_updated: string | null;
  last_modified_by?: string | null;
}
