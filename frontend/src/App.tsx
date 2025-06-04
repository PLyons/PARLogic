import { ThemeProvider } from '@mui/material';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardLayout from './components/Layout/DashboardLayout';
import Dashboard from './pages/Dashboard/Dashboard';
import UploadData from './pages/Upload/UploadData';
import Analysis from './pages/Analysis/Analysis';
import PARLevels from './pages/PARLevels/PARLevels';
import theme from './assets/styles/theme';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <DashboardLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadData />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/par-levels" element={<PARLevels />} />
          </Routes>
        </DashboardLayout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
