import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { SummaryResponse } from '../lib/api/types';
import { getSummary } from '../lib/api/dashboard';
import dayjs, { Dayjs } from 'dayjs';

interface DashboardState {
  // State
  summaryData: SummaryResponse | null;
  startDate: Dayjs;
  endDate: Dayjs;
  currency: string;
  viewMode: 'count' | 'value';
  loading: boolean;
  error: string | null;
  lastFetchKey: string | null;

  // Actions
  setStartDate: (date: Dayjs) => void;
  setEndDate: (date: Dayjs) => void;
  setCurrency: (currency: string) => void;
  setViewMode: (mode: 'count' | 'value') => void;
  fetchSummary: () => Promise<void>;
  clearCache: () => void;
}

// Generate cache key from current filters
const getCacheKey = (startDate: Dayjs, endDate: Dayjs, currency: string) => {
  return `${startDate.toISOString()}_${endDate.toISOString()}_${currency}`;
};

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set, get) => ({
      // Initial state
      summaryData: null,
      startDate: dayjs('2025-10-01'),
      endDate: dayjs('2025-10-15'),
      currency: 'USD',
      viewMode: 'count',
      loading: false,
      error: null,
      lastFetchKey: null,

      // Setters
      setStartDate: (date: Dayjs) => {
        set({ startDate: date });
        get().fetchSummary();
      },

      setEndDate: (date: Dayjs) => {
        set({ endDate: date });
        get().fetchSummary();
      },

      setCurrency: (currency: string) => {
        set({ currency });
        get().fetchSummary();
      },

      setViewMode: (mode: 'count' | 'value') => {
        set({ viewMode: mode });
      },

      // Fetch summary with caching
      fetchSummary: async () => {
        const { startDate, endDate, currency, lastFetchKey } = get();
        const currentKey = getCacheKey(startDate, endDate, currency);

        // If data is already cached for these filters, skip fetch
        if (lastFetchKey === currentKey && get().summaryData) {
          console.log('Dashboard: Using cached data');
          return;
        }

        console.log('Dashboard: Fetching fresh data', {
          startDate: startDate.toISOString(),
          endDate: endDate.toISOString(),
          currency,
        });

        set({ loading: true, error: null });

        try {
          const summary = await getSummary(
            startDate.toDate(),
            endDate.toDate(),
            currency
          );

          set({
            summaryData: summary,
            loading: false,
            lastFetchKey: currentKey,
          });

          console.log('Dashboard: Data fetched and cached', {
            dailyBreakdownCount: summary.daily_breakdown?.length || 0,
            transactionCount: summary.transactions.total_count,
            invoiceCount: summary.invoices.total_count,
          });
        } catch (err) {
          set({
            error: err instanceof Error ? err.message : 'Failed to fetch data',
            loading: false,
          });
        }
      },

      // Clear cache and refetch
      clearCache: () => {
        set({
          summaryData: null,
          lastFetchKey: null,
        });
        get().fetchSummary();
      },
    }),
    {
      name: 'dashboard-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist filters, not the data itself
      partialize: (state) => ({
        startDate: state.startDate.toISOString(),
        endDate: state.endDate.toISOString(),
        currency: state.currency,
        viewMode: state.viewMode,
      }),
    }
  )
);
