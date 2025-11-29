'use client';

import * as React from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Collapse from '@mui/material/Collapse';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TokenIcon from '@mui/icons-material/Token';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs, { Dayjs } from 'dayjs';
import { getAgentLogs } from '../../lib/api/logs';
import type { AgentLogEntry } from '../../lib/api/logs';

export default function Logs() {
  const [startDate, setStartDate] = React.useState<Dayjs | null>(dayjs().subtract(1, 'day'));
  const [endDate, setEndDate] = React.useState<Dayjs | null>(dayjs());
  const [logs, setLogs] = React.useState<AgentLogEntry[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [expandedId, setExpandedId] = React.useState<string | null>(null);

  // Fetch logs
  React.useEffect(() => {
    const fetchLogs = async () => {
      if (!startDate || !endDate) return;

      setLoading(true);
      setError(null);

      try {
        const response = await getAgentLogs(startDate.toDate(), endDate.toDate(), 1, 50);
        setLogs(response.logs);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch logs');
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [startDate, endDate]);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const isError = (log: AgentLogEntry) => {
    return log.assistant_response?.toLowerCase().includes('error') ||
           log.assistant_response?.toLowerCase().includes('failed');
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box>
        <Typography variant="h4" gutterBottom>
          AI Assistant Activity Logs
        </Typography>

        {/* Date Range Picker */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <DatePicker
              label="Start Date"
              value={startDate}
              onChange={(newValue) => setStartDate(newValue)}
              slotProps={{ textField: { size: 'small' } }}
            />
            <Typography>to</Typography>
            <DatePicker
              label="End Date"
              value={endDate}
              onChange={(newValue) => setEndDate(newValue)}
              slotProps={{ textField: { size: 'small' } }}
            />
          </Box>
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 5 }}>
            <CircularProgress />
          </Box>
        ) : logs.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              No logs found for this time period
            </Typography>
          </Paper>
        ) : (
          /* Timeline */
          <Box sx={{ position: 'relative' }}>
            {/* Vertical Line */}
            <Box
              sx={{
                position: 'absolute',
                left: 20,
                top: 0,
                bottom: 0,
                width: 2,
                backgroundColor: 'divider',
              }}
            />

            {/* Log Entries */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pl: 6 }}>
              {logs.map((log) => {
                const expanded = expandedId === log.query_id;
                const hasError = isError(log);

                return (
                  <Box key={log.query_id} sx={{ position: 'relative' }}>
                    {/* Timeline Dot */}
                    <Box
                      sx={{
                        position: 'absolute',
                        left: -29,
                        top: 12,
                        width: 16,
                        height: 16,
                        borderRadius: '50%',
                        backgroundColor: hasError ? 'error.main' : 'success.main',
                        border: '3px solid',
                        borderColor: 'background.paper',
                        zIndex: 1,
                      }}
                    />

                    {/* Log Card */}
                    <Paper sx={{ p: 2.5 }}>
                      {/* Timestamp */}
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </Typography>

                      {/* Query */}
                      <Typography variant="h6" gutterBottom>
                        {log.user_query}
                      </Typography>

                      {/* Tools Used */}
                      <Box sx={{ display: 'flex', gap: 1, mb: 1.5, flexWrap: 'wrap' }}>
                        {log.tools_used.map((tool, idx) => (
                          <Chip
                            key={idx}
                            label={tool}
                            size="small"
                            variant="outlined"
                            color="primary"
                          />
                        ))}
                      </Box>

                      {/* Metrics */}
                      <Box sx={{ display: 'flex', gap: 2, mb: 1.5, flexWrap: 'wrap', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          {hasError ? (
                            <ErrorIcon fontSize="small" color="error" />
                          ) : (
                            <CheckCircleIcon fontSize="small" color="success" />
                          )}
                          <Typography variant="body2" color={hasError ? 'error' : 'success.main'}>
                            {hasError ? 'Error' : 'Success'}
                          </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AccessTimeIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {log.execution_time_ms}ms
                          </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <TokenIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {log.tokens.total || 0} tokens
                          </Typography>
                        </Box>
                      </Box>

                      {/* Response Preview */}
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: expanded ? 'unset' : 2,
                          WebkitBoxOrient: 'vertical',
                          mb: 1,
                        }}
                      >
                        {log.assistant_response}
                      </Typography>

                      {/* Expand/Collapse Button */}
                      <Button
                        size="small"
                        onClick={() => toggleExpand(log.query_id)}
                        endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      >
                        {expanded ? 'Show Less' : 'Show Details'}
                      </Button>

                      {/* Expanded Details */}
                      <Collapse in={expanded}>
                        <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Query ID
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontFamily: 'monospace' }}>
                            {log.query_id}
                          </Typography>

                          <Typography variant="subtitle2" gutterBottom>
                            Token Breakdown
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Prompt: {log.tokens.prompt || 0} • Completion: {log.tokens.completion || 0} • Total: {log.tokens.total || 0}
                          </Typography>

                          {log.structured_data && Object.keys(log.structured_data).length > 0 && (
                            <>
                              <Typography variant="subtitle2" gutterBottom>
                                Structured Data
                              </Typography>
                              <Paper
                                sx={{
                                  p: 1.5,
                                  backgroundColor: 'grey.100',
                                  overflow: 'auto',
                                  maxHeight: 300,
                                }}
                              >
                                <pre style={{ margin: 0, fontSize: '0.75rem' }}>
                                  {JSON.stringify(log.structured_data, null, 2)}
                                </pre>
                              </Paper>
                            </>
                          )}
                        </Box>
                      </Collapse>
                    </Paper>
                  </Box>
                );
              })}
            </Box>
          </Box>
        )}
      </Box>
    </LocalizationProvider>
  );
}