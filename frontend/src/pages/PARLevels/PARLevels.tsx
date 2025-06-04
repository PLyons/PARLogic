import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Slider,
  Grid as MuiGrid,
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { calculatePAR, getRecommendations } from '../../services/api';
import type { PARLevels as PARLevelsType, StockRecommendation } from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const PARLevels: React.FC = () => {
  const [itemId, setItemId] = useState('');
  const [serviceLevel, setServiceLevel] = useState(0.95);
  const [leadTimeDays, setLeadTimeDays] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [parLevels, setPARLevels] = useState<PARLevelsType | null>(null);
  const [recommendations, setRecommendations] = useState<StockRecommendation[]>([]);

  const handleCalculate = async () => {
    if (!itemId) {
      setError('Please enter an Item ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [parData, recsData] = await Promise.all([
        calculatePAR(itemId, serviceLevel, leadTimeDays),
        getRecommendations(itemId),
      ]);
      setPARLevels(parData);
      setRecommendations(recsData.recommendations);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate PAR levels');
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: ['Min PAR', 'Reorder Point', 'Safety Stock', 'Max PAR'],
    datasets: [
      {
        label: 'Stock Levels',
        data: parLevels
          ? [
              parLevels.min_par,
              parLevels.reorder_point,
              parLevels.safety_stock,
              parLevels.max_par,
            ]
          : [],
        backgroundColor: [
          'rgba(25, 118, 210, 0.5)',
          'rgba(237, 108, 2, 0.5)',
          'rgba(46, 125, 50, 0.5)',
          'rgba(25, 118, 210, 0.5)',
        ],
        borderColor: [
          'rgba(25, 118, 210, 1)',
          'rgba(237, 108, 2, 1)',
          'rgba(46, 125, 50, 1)',
          'rgba(25, 118, 210, 1)',
        ],
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
        text: 'PAR Level Analysis',
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
        PAR Level Calculator
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Calculate optimal PAR levels and get inventory recommendations
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <MuiGrid container spacing={3}>
            <MuiGrid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Item ID"
                value={itemId}
                onChange={(e) => setItemId(e.target.value)}
                variant="outlined"
              />
            </MuiGrid>
            <MuiGrid item xs={12} md={4}>
              <Typography gutterBottom>Service Level: {serviceLevel * 100}%</Typography>
              <Slider
                value={serviceLevel}
                onChange={(_, value) => setServiceLevel(value as number)}
                min={0.8}
                max={0.99}
                step={0.01}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
              />
            </MuiGrid>
            <MuiGrid item xs={12} md={4}>
              <Typography gutterBottom>Lead Time (Days): {leadTimeDays}</Typography>
              <Slider
                value={leadTimeDays}
                onChange={(_, value) => setLeadTimeDays(value as number)}
                min={1}
                max={14}
                step={1}
                valueLabelDisplay="auto"
              />
            </MuiGrid>
            <MuiGrid item xs={12}>
              <Button
                variant="contained"
                onClick={handleCalculate}
                disabled={loading}
              >
                Calculate PAR Levels
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

      {parLevels && (
        <MuiGrid container spacing={3}>
          <MuiGrid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Bar data={chartData} options={chartOptions} />
              </CardContent>
            </Card>
          </MuiGrid>
          <MuiGrid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Calculated Levels
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Item ID
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {parLevels.item_id}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Minimum PAR
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {parLevels.min_par} units
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Maximum PAR
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {parLevels.max_par} units
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Reorder Point
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {parLevels.reorder_point} units
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Safety Stock
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {parLevels.safety_stock} units
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </MuiGrid>
        </MuiGrid>
      )}

      {recommendations.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            {recommendations.map((rec, index) => (
              <Alert
                key={index}
                severity={
                  rec.urgency === 'high'
                    ? 'error'
                    : rec.urgency === 'medium'
                    ? 'warning'
                    : 'info'
                }
                sx={{ mb: 2 }}
              >
                <Typography variant="subtitle1">
                  {rec.recommended_action}
                </Typography>
                <Typography variant="body2">
                  Current Stock: {rec.current_stock} units
                </Typography>
                <Typography variant="body2">{rec.details}</Typography>
              </Alert>
            ))}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default PARLevels; 