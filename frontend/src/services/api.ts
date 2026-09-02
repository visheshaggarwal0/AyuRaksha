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
  },

  // Corpus & TKDL Taxonomy
  getManifest: async () => {
    const response = await apiClient.get('/corpus/manifest');
    return response.data;
  },

  getBooks: async (query: string = '', limit: number = 50) => {
    const response = await apiClient.get('/corpus/books', { params: { query, limit } });
    return response.data;
  },

  getPlants: async (query: string = '', limit: number = 50) => {
    const response = await apiClient.get('/corpus/plants', { params: { query, limit } });
    return response.data;
  },

  getGlossary: async (query: string = '', limit: number = 50) => {
    const response = await apiClient.get('/corpus/glossary', { params: { query, limit } });
    return response.data;
  },

  getEntities: async (query: string = '', entityType: string = '', limit: number = 50) => {
    const response = await apiClient.get('/corpus/entities', { params: { query, entity_type: entityType, limit } });
    return response.data;
  },

  getCorpusStats: async () => {
    const response = await apiClient.get('/corpus/stats');
    return response.data;
  }
};
