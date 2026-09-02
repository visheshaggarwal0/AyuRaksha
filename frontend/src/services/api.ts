import axios from 'axios';
import {
  ProductClassificationRequest,
  ProductClassificationResponse,
  ABSAssessmentRequest,
  ABSAssessmentResponse,
  StructuredAnswer,
  Jurisdiction
} from '../types';

const apiBase = (import.meta as any).env?.VITE_API_BASE_URL
  ? `${(import.meta as any).env.VITE_API_BASE_URL.replace(/\/$/, '')}/api/v1`
  : '/api/v1';

const apiClient = axios.create({
  baseURL: apiBase,
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

  // Streaming Chat RAG (Server-Sent Events)
  streamChatQuery: async (
    query: string,
    jurisdiction: Jurisdiction = 'IN',
    language: string = 'en',
    onStage?: (stage: { stage: string; message: string }) => void,
    onToken?: (token: string) => void,
    onResult?: (result: StructuredAnswer) => void,
    onError?: (err: any) => void
  ) => {
    try {
      const response = await fetch(`${apiBase}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, jurisdiction, language })
      });

      if (!response.ok) throw new Error(`HTTP error ${response.status}`);
      if (!response.body) throw new Error('No readable stream');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const blocks = buffer.split('\n\n');
        buffer = blocks.pop() || '';

        for (const block of blocks) {
          if (!block.trim()) continue;
          let eventType = 'message';
          let dataStr = '';

          for (const line of block.split('\n')) {
            if (line.startsWith('event: ')) {
              eventType = line.replace('event: ', '').trim();
            } else if (line.startsWith('data: ')) {
              dataStr = line.replace('data: ', '').trim();
            }
          }

          if (dataStr) {
            try {
              const parsed = JSON.parse(dataStr);
              if (eventType === 'stage' && onStage) onStage(parsed);
              if (eventType === 'token' && onToken) onToken(parsed.token);
              if (eventType === 'result' && onResult) onResult(parsed);
            } catch (e) {
              console.error('SSE JSON parse error:', e);
            }
          }
        }
      }
    } catch (err) {
      if (onError) onError(err);
      else throw err;
    }
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
  },

  getPatentForms: async (query: string = '') => {
    const response = await apiClient.get('/corpus/patent-forms', { params: { query } });
    return response.data;
  },

  getPatentProvisions: async (query: string = '', relevanceFilter?: string) => {
    const response = await apiClient.get('/corpus/patent-provisions', {
      params: { query, relevance_filter: relevanceFilter }
    });
    return response.data;
  },

  getKnowledgeGraph: async () => {
    const response = await apiClient.get('/corpus/graph');
    return response.data;
  },

  // Active Compliance Dossier (SIH 26045)
  generateDossier: async (data: any) => {
    const response = await apiClient.post('/dossier/generate', data);
    return response.data;
  },

  exportDossierMarkdown: async (data: any) => {
    const response = await apiClient.post('/dossier/export-markdown', data, {
      responseType: 'blob'
    });
    return response.data;
  },

  getSampleDossier: async () => {
    const response = await apiClient.get('/dossier/sample');
    return response.data;
  }
};
