'use client';

import * as React from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LineChart } from '@mui/x-charts/LineChart';
import { PieChart } from '@mui/x-charts/PieChart';
import dayjs, { Dayjs } from 'dayjs';
import { useDashboardStore } from '../store/dashboardStore';

const SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'CAD'];

export default function Home() {
  // Use Zustand store
  const {
    summaryData,
    startDate,
    endDate,
    currency,
    viewMode,
    loading,
    error,
    setStartDate,
    setEndDate,
    setCurrency,
    setViewMode,
    fetchSummary,
  } = useDashboardStore();

  // Fetch data on mount
  React.useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  // Generate time series data from daily breakdown
  const timeSeriesData = React.useMemo(() => {
    if (!summaryData || !summaryData.daily_breakdown) {
      return { dates: [], transactions: [], invoices: [] };
    }

    const dates: string[] = [];
    const transactions: number[] = [];
    const invoices: number[] = [];

    // Filter to only include data within the selected date range
    const filteredBreakdown = summaryData.daily_breakdown.filter((day) => {
      const dayDate = dayjs(day.date);
      const start = dayjs(startDate);
      const end = dayjs(endDate);
      const isAfterStart = dayDate.isAfter(start, 'day') || dayDate.isSame(start, 'day');
      const isBeforeEnd = dayDate.isBefore(end, 'day') || dayDate.isSame(end, 'day');
      return isAfterStart && isBeforeEnd;
    });

    console.log('Filtered daily breakdown:', {
      total: summaryData.daily_breakdown.length,
      filtered: filteredBreakdown.length,
      startDate: dayjs(startDate).format('YYYY-MM-DD'),
      endDate: dayjs(endDate).format('YYYY-MM-DD'),
      dates: filteredBreakdown.map(d => d.date)
    });

    // Use actual daily breakdown data from the API
    filteredBreakdown.forEach((day) => {
      // Format date as "MMM D"
      dates.push(dayjs(day.date).format('MMM D'));

      // Use count or value based on viewMode
      if (viewMode === 'count') {
        transactions.push(day.transaction_count);
        invoices.push(day.invoice_count);
      } else {
        transactions.push(day.transaction_value);
        invoices.push(day.invoice_value);
      }
    });

    return { dates, transactions, invoices };
  }, [summaryData, viewMode, startDate, endDate]);

  // Prepare pie chart data from API
  const transactionCurrencyData = React.useMemo(() => {
    if (!summaryData) return [];
    return summaryData.transactions.by_currency.map((item, index) => ({
      id: index,
      value: item.count,
      label: item.currency,
    }));
  }, [summaryData]);

  const invoiceStatusData = React.useMemo(() => {
    if (!summaryData) return [];
    console.log('Invoice by_status data:', summaryData.invoices.by_status);
    const mapped = summaryData.invoices.by_status.map((item, index) => ({
      id: index,
      value: item.count,
      label: item.status,
    }));
    console.log('Mapped invoice status data:', mapped);
    return mapped;
  }, [summaryData]);

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <DateTimePicker
              label="Start Date & Time"
              value={dayjs(startDate)}
              onChange={(newValue) => newValue && setStartDate(newValue)}
              slotProps={{ textField: { size: 'small' } }}
            />
            <Typography>to</Typography>
            <DateTimePicker
              label="End Date & Time"
              value={dayjs(endDate)}
              onChange={(newValue) => newValue && setEndDate(newValue)}
              slotProps={{ textField: { size: 'small' } }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="view-mode-select-label">View</InputLabel>
              <Select
                labelId="view-mode-select-label"
                id="view-mode-select"
                value={viewMode}
                label="View"
                onChange={(e: SelectChangeEvent) => setViewMode(e.target.value as 'count' | 'value')}
              >
                <MenuItem value="count">Count</MenuItem>
                <MenuItem value="value">Value</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="currency-select-label">Currency</InputLabel>
              <Select
                labelId="currency-select-label"
                id="currency-select"
                value={currency}
                label="Currency"
                onChange={(e: SelectChangeEvent) => setCurrency(e.target.value)}
              >
                {SUPPORTED_CURRENCIES.map((curr) => (
                  <MenuItem key={curr} value={curr}>
                    {curr}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Paper>

        {/* Combined Line Chart */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 5 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Transactions & Invoices Over Time {viewMode === 'value' && `(${currency})`}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
              {dayjs(startDate).format('MMM D, YYYY h:mm A')} - {dayjs(endDate).format('MMM D, YYYY h:mm A')}
            </Typography>
            {timeSeriesData.dates.length > 0 ? (
              <LineChart
                xAxis={[{ scaleType: 'point', data: timeSeriesData.dates }]}
                series={[
                  {
                    data: timeSeriesData.transactions,
                    label: viewMode === 'count' ? 'Transactions' : `Transactions (${currency})`,
                    color: '#1976d2',
                  },
                  {
                    data: timeSeriesData.invoices,
                    label: viewMode === 'count' ? 'Invoices' : `Invoices (${currency})`,
                    color: '#dc004e',
                  },
                ]}
                height={300}
              />
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 5 }}>
                No data available
              </Typography>
            )}
          </Paper>
        )}

        {/* Pie Charts */}
        {!loading && (
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(50% - 12px)' } }}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Transaction Currency Split
                </Typography>
                {transactionCurrencyData.length > 0 ? (
                  <PieChart
                    series={[
                      {
                        data: transactionCurrencyData,
                        highlightScope: { fade: 'global', highlight: 'item' },
                      },
                    ]}
                    height={300}
                  />
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 5 }}>
                    No transaction currency data available
                  </Typography>
                )}
              </Paper>
            </Box>
            <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(50% - 12px)' } }}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Invoice Status
                </Typography>
                {invoiceStatusData.length > 0 ? (
                  <PieChart
                    series={[
                      {
                        data: invoiceStatusData,
                        highlightScope: { fade: 'global', highlight: 'item' },
                      },
                    ]}
                    height={300}
                  />
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 5 }}>
                    No invoice status data available
                  </Typography>
                )}
              </Paper>
            </Box>
          </Box>
        )}
      </Box>
    </LocalizationProvider>
  );
}
