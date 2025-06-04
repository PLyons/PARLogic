import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid as MuiGrid,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { analyzeUsage } from '../../services/api';
import type { UsagePattern } from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Analysis: React.FC = () => {
  const [startDate, setStartDate] = useState<Date | null>(
    new Date(new Date().setMonth(new Date().getMonth() - 1))
  );
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [itemId, setItemId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<UsagePattern | null>(null);

  const handleAnalyze = async () => {
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await analyzeUsage(
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0],
        itemId || undefined
      );
      setAnalysisData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze usage');
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: ['Average', 'Peak'],
    datasets: [
      {
        label: 'Usage Patterns',
        data: analysisData
          ? [analysisData.average_daily_usage, analysisData.peak_usage]
          : [],
        backgroundColor: 'rgba(25, 118, 210, 0.5)',
        borderColor: 'rgba(25, 118, 210, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Usage Analysis',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Usage Analysis
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Analyze inventory usage patterns and trends
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <MuiGrid container component="div" spacing={3}>
            <MuiGrid component="div" item xs={12} md={4}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Start Date"
                  value={startDate}
                  onChange={(newValue: Date | null) => setStartDate(newValue)}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: 'outlined',
                    },
                  }}
                />
              </LocalizationProvider>
            </MuiGrid>
            <MuiGrid component="div" item xs={12} md={4}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="End Date"
                  value={endDate}
                  onChange={(newValue: Date | null) => setEndDate(newValue)}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: 'outlined',
                    },
                  }}
                />
              </LocalizationProvider>
            </MuiGrid>
            <MuiGrid component="div" item xs={12} md={4}>
              <TextField
                fullWidth
                label="Item ID (optional)"
                value={itemId}
                onChange={(e) => setItemId(e.target.value)}
                variant="outlined"
              />
            </MuiGrid>
            <MuiGrid component="div" item xs={12}>
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={loading}
              >
                Analyze Usage
              </Button>
            </MuiGrid>
          </MuiGrid>
        </CardContent>
      </Card>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {analysisData && (
        <MuiGrid container component="div" spacing={3}>
          <MuiGrid component="div" item xs={12} md={8}>
            <Card>
              <CardContent>
                <Line data={chartData} options={chartOptions} />
              </CardContent>
            </Card>
          </MuiGrid>
          <MuiGrid component="div" item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Results
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Item ID
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {analysisData.item_id}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Average Daily Usage
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {analysisData.average_daily_usage.toFixed(2)} units
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Peak Usage
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {analysisData.peak_usage.toFixed(2)} units
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Seasonality Factor
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {analysisData.seasonality_factor?.toFixed(2) || 'N/A'}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Trend
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {analysisData.trend.charAt(0).toUpperCase() +
                      analysisData.trend.slice(1)}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Confidence Level
                  </Typography>
                  <Typography variant="body1">
                    {(analysisData.confidence_level * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </MuiGrid>
        </MuiGrid>
      )}
    </Box>
  );
};

export default Analysis; 