import { getApiUrl } from '../api-config';

export interface AgentLogEntry {
  query_id: string;
  timestamp: string;
  user_query: string;
  assistant_response: string;
  tools_used: string[];
  execution_time_ms: number;
  tokens: {
    prompt: number | null;
    completion: number | null;
    total: number | null;
  };
  structured_data: Record<string, any>;
}

export interface AgentLogsResponse {
  period: {
    start_date: string;
    end_date: string;
  };
  summary: {
    total_queries: number;
    error_count: number;
    error_rate: number;
    avg_execution_time_ms: number;
    total_tokens_used: number;
    avg_tokens_per_query: number;
  };
  logs: AgentLogEntry[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export async function getAgentLogs(
  startDate?: Date,
  endDate?: Date,
  page: number = 1,
  pageSize: number = 20
): Promise<AgentLogsResponse> {
  const params = new URLSearchParams();

  if (startDate) {
    params.append('start_date', startDate.toISOString());
  }
  if (endDate) {
    params.append('end_date', endDate.toISOString());
  }
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());

  const url = getApiUrl(`/api/agent-logs?${params.toString()}`);
  console.log('Fetching agent logs from:', url);

  const response = await fetch(url);

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('Agent Logs API Error:', response.status, errorBody);
    throw new Error(`Failed to fetch agent logs: ${response.statusText}`);
  }

  return response.json();
}