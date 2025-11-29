import { getApiUrl } from '../api-config';

export interface AssistantRequest {
  query: string;
}

export interface AssistantResponse {
  query_id: string;
  natural_language: string;
  structured_data: Record<string, any>;
  metadata: {
    tools_used: string[];
    execution_time_ms: number;
    tokens: {
      prompt: number | null;
      completion: number | null;
      total: number | null;
    };
  };
}

export async function sendChatMessage(query: string): Promise<AssistantResponse> {
  const url = getApiUrl('/api/ai-assistant');

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('AI Assistant API Error:', response.status, errorBody);
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return response.json();
}