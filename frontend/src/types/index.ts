export interface Entity {
  entity_id: string;
  display_name: string;
  normalized_name: string;
  entity_type?: string;
}

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
