export type HealthStatus = 'healthy' | 'degraded' | 'unavailable' | 'ready';

export interface DependencyHealth {
  status: HealthStatus;
  latency_ms?: number | null;
  message?: string | null;
  details?: Record<string, any> | null;
}

export interface SystemHealthResponse {
  api: DependencyHealth;
  postgresql: DependencyHealth;
  vector_search: DependencyHealth;
  knowledge_graph: DependencyHealth;
  llm_provider: DependencyHealth;
  fallback_engine: DependencyHealth;
  timestamp: string;
}

export interface ProviderHealth {
  provider_name: string;
  model: string;
  status: HealthStatus | 'circuit_open';
  circuit_breaker_status: 'closed' | 'open' | 'unavailable' | 'ready';
  circuit_cooldown_remaining_sec?: number;
  request_count: number;
  success_count: number;
  failure_count: number;
  avg_latency_ms?: number | null;
  fallback_count: number;
}

export interface TokenUsage {
  input_tokens?: number | null;
  output_tokens?: number | null;
  total_tokens?: number | null;
}

export interface RequestTelemetryRecord {
  request_id: string;
  trace_id: string;
  timestamp: string;
  jurisdiction: string;
  provider: string;
  model: string;
  latency_ms: number;
  latency_breakdown?: Record<string, number>;
  retrieval_count: number;
  reranked_count: number;
  citation_count: number;
  grounding_rate?: number | null;
  abstained: boolean;
  failure_reason?: string | null;
  token_usage?: TokenUsage | null;
  success: boolean;
  query_hash: string;
}

export interface AggregatedMetrics {
  queries_today: number;
  avg_latency_ms?: number | null;
  p95_latency_ms?: number | null;
  citation_grounding?: number | null;
  abstention_rate?: number | null;
  jurisdiction_leakage: number;
  total_requests_recorded: number;
  provider_statistics: Record<string, any>;
  retrieval_statistics: {
    avg_retrieved?: number | null;
    avg_reranked?: number | null;
    avg_citations?: number | null;
  };
  failure_statistics: {
    total_failures: number;
    failure_rate: number;
    reasons: Record<string, number>;
  };
}
