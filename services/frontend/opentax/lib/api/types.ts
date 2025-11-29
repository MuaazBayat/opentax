// API Response Types

export interface DailyBreakdown {
  date: string;
  transaction_count: number;
  transaction_value: number;
  invoice_count: number;
  invoice_value: number;
}

export interface SummaryResponse {
  filters: {
    start_date: string;
    end_date: string;
    target_currency: string;
  };
  transactions: {
    total_count: number;
    total_amount: number;
    average_amount: number;
    by_status: Array<{
      status: string;
      count: number;
      total_amount: number;
    }>;
    by_currency: Array<{
      currency: string;
      count: number;
      total_amount: number;
      average_amount: number;
    }>;
  };
  invoices: {
    total_count: number;
    total_amount: number;
    average_amount: number;
    unpaid_count: number;
    unpaid_amount: number;
    by_status: Array<{
      status: string;
      count: number;
      total_amount: number;
    }>;
  };
  daily_breakdown: DailyBreakdown[];
}

export interface Transaction {
  id: number;
  sender_id: number;
  receiver_id: number;
  amount: number;
  currency: string;
  status: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  sender_id: number;
  receiver_id: number;
  amount: number;
  currency: string;
  status: string;
  due_date: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}
