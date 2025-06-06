import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface UploadResponse {
  message: string;
  rows: number;
  items: number;
  date_range: string;
}

export interface UsagePattern {
  item_id: string;
  average_daily_usage: number;
  peak_usage: number;
  seasonality_factor?: number;
  trend: string;
  confidence_level: number;
}

export interface PARLevels {
  item_id: string;
  min_par: number;
  max_par: number;
  reorder_point: number;
  safety_stock: number;
}

export interface StockRecommendation {
  item_id: string;
  current_stock: number;
  recommended_order: number;
  urgency: 'low' | 'medium' | 'high';
  next_review_date: string;
}

export interface RecommendationResponse {
  recommendations: StockRecommendation[];
  timestamp: string;
}

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Error uploading file');
    }
    throw error;
  }
};

export const analyzeUsage = async (
  startDate: string,
  endDate: string,
  itemId?: string
): Promise<UsagePattern> => {
  try {
    const response = await api.get('/analyze/usage/', {
      params: {
        start_date: startDate,
        end_date: endDate,
        item_id: itemId,
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Error analyzing usage');
    }
    throw error;
  }
};

export const calculatePAR = async (itemId: string): Promise<PARLevels> => {
  try {
    const response = await api.get(`/par/${itemId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Error calculating PAR levels');
    }
    throw error;
  }
};

export const getRecommendations = async (): Promise<StockRecommendation[]> => {
  try {
    const response = await api.get('/recommendations');
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Error getting recommendations');
    }
    throw error;
  }
};

export default api; 