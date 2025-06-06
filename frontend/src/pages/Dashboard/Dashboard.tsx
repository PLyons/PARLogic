import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid as MuiGrid,
  Typography,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  LocalShipping as ShippingIcon,
} from '@mui/icons-material';

const summaryCards = [
  {
    title: 'Items Tracked',
    value: '157',
    icon: <TrendingUpIcon />,
    color: '#1976d2',
  },
  {
    title: 'Needs Attention',
    value: '12',
    icon: <WarningIcon />,
    color: '#d32f2f',
  },
  {
    title: 'Optimal Stock',
    value: '89',
    icon: <CheckCircleIcon />,
    color: '#2e7d32',
  },
  {
    title: 'Pending Orders',
    value: '8',
    icon: <ShippingIcon />,
    color: '#ed6c02',
  },
];

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to PARLogic
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Your hospital supply chain management dashboard
      </Typography>

      <MuiGrid container component="div" spacing={3} sx={{ mt: 2 }} data-testid="dashboard-summary">
        {summaryCards.map((card) => (
          <MuiGrid component="div" item xs={12} sm={6} md={3} key={card.title}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                overflow: 'hidden',
                '&:before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '4px',
                  backgroundColor: card.color,
                },
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography
                      variant="h3"
                      component="div"
                      sx={{ fontWeight: 'bold', mb: 1 }}
                    >
                      {card.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {card.title}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '48px',
                      height: '48px',
                      borderRadius: '50%',
                      backgroundColor: `${card.color}15`,
                      color: card.color,
                    }}
                  >
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </MuiGrid>
        ))}
      </MuiGrid>

      {/* Placeholder for charts */}
      <MuiGrid container component="div" spacing={3} sx={{ mt: 3 }}>
        <MuiGrid component="div" item xs={12} md={8}>
          <Card sx={{ height: '400px' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Usage Trends
              </Typography>
              {/* Add Chart.js component here */}
            </CardContent>
          </Card>
        </MuiGrid>
        <MuiGrid component="div" item xs={12} md={4}>
          <Card sx={{ height: '400px' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Stock Status
              </Typography>
              {/* Add Chart.js component here */}
            </CardContent>
          </Card>
        </MuiGrid>
      </MuiGrid>
    </Box>
  );
};

export default Dashboard;