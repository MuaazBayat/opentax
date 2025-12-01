import { getApiUrl } from '../api-config';
import { SummaryResponse, Transaction, Invoice, PaginatedResponse } from './types';

export async function getSummary(
  startDate?: Date,
  endDate?: Date,
  targetCurrency: string = 'USD'
): Promise<SummaryResponse> {
  const params = new URLSearchParams();

  if (startDate) {
    params.append('start_date', startDate.toISOString());
  }
  if (endDate) {
    params.append('end_date', endDate.toISOString());
  }
  params.append('target_currency', targetCurrency);

  const url = getApiUrl(`/api/summary?${params.toString()}`);
  console.log('Fetching summary from:', url);
  console.log('Date range:', {
    startDate: startDate?.toISOString(),
    endDate: endDate?.toISOString(),
    currency: targetCurrency
  });

  const response = await fetch(url, {
    cache: 'no-store', // Prevent caching to ensure fresh data
  });

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('API Error:', response.status, errorBody);
    throw new Error(`Failed to fetch summary: ${response.statusText}. ${errorBody}`);
  }

  const data = await response.json();
  console.log('Received daily_breakdown:', data.daily_breakdown);
  return data;
}

export async function getTransactions(
  page: number = 1,
  pageSize: number = 100
): Promise<PaginatedResponse<Transaction>> {
  const url = getApiUrl(`/transactions/?page=${page}&page_size=${pageSize}`);
  console.log('Fetching transactions from:', url);

  const response = await fetch(url);

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('API Error:', response.status, errorBody);
    throw new Error(`Failed to fetch transactions: ${response.statusText}. ${errorBody}`);
  }

  return response.json();
}

export async function getInvoices(
  page: number = 1,
  pageSize: number = 100
): Promise<PaginatedResponse<Invoice>> {
  const url = getApiUrl(`/invoices/?page=${page}&page_size=${pageSize}`);
  console.log('Fetching invoices from:', url);

  const response = await fetch(url);

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('API Err:', response.status, errorBody);
    throw new Error(`Failed to fetch invoices: ${response.statusText}. ${errorBody}`);
  }

  return response.json();
}
