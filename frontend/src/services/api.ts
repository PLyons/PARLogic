import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'test-key'; // In production, this should be loaded from environment variables

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
  },
});

export interface UploadResponse {
  message: string;
  rows: number;
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
  service_level: number;
  lead_time_days: number;
}

export interface StockRecommendation {
  item_id: string;
  current_stock: number;
  recommended_action: string;
  urgency: string;
  details: string;
}

export interface RecommendationResponse {
  recommendations: StockRecommendation[];
  timestamp: string;
}

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<UploadResponse>('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeUsage = async (
  startDate: string,
  endDate: string,
  itemId?: string
): Promise<UsagePattern> => {
  const response = await api.get<UsagePattern>('/analyze/usage/', {
    params: {
      start_date: startDate,
      end_date: endDate,
      item_id: itemId,
    },
  });
  return response.data;
};

export const calculatePAR = async (
  itemId: string,
  serviceLevel: number = 0.95,
  leadTimeDays: number
): Promise<PARLevels> => {
  const response = await api.get<PARLevels>('/calculate/par/', {
    params: {
      item_id: itemId,
      service_level: serviceLevel,
      lead_time_days: leadTimeDays,
    },
  });
  return response.data;
};

export const getRecommendations = async (
  itemId?: string
): Promise<RecommendationResponse> => {
  const response = await api.get<RecommendationResponse>('/recommendations/', {
    params: {
      item_id: itemId,
    },
  });
  return response.data;
};

export default api; 