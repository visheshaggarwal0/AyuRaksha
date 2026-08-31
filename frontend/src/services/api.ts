import axios from 'axios';
import {
  ProductClassificationRequest,
  ProductClassificationResponse,
  ABSAssessmentRequest,
  ABSAssessmentResponse,
  StructuredAnswer,
  Jurisdiction
} from '../types';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Classification
  evaluateClassification: async (data: ProductClassificationRequest): Promise<ProductClassificationResponse> => {
    const response = await apiClient.post<ProductClassificationResponse>('/classification/evaluate', data);
    return response.data;
  },

  // ABS
  evaluateABS: async (data: ABSAssessmentRequest): Promise<ABSAssessmentResponse> => {
    const response = await apiClient.post<ABSAssessmentResponse>('/abs/evaluate', data);
    return response.data;
  },

  // Chat RAG
  askAyuRaksha: async (query: string, jurisdiction: Jurisdiction = 'IN', language: string = 'en'): Promise<StructuredAnswer> => {
    const response = await apiClient.post<StructuredAnswer>('/chat/query', {
      query,
      jurisdiction,
      language,
    });
    return response.data;
  },

  // Health check
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  }
};
