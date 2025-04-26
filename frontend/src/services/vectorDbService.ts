// src/services/vectorDbService.ts
import axios from 'axios';
import type { AxiosInstance } from 'axios';

// Type definitions
interface Collection {
  id: string;
  name: string;
  description?: string;
  vector_count?: number;
  created_at?: string;
  updated_at?: string;
}

interface Vector {
  id: string;
  content?: string;
  metadata?: Record<string, any>;
  embedding?: number[];
  score?: number;
}

interface SearchResult extends Vector {
  score: number;
}

interface MetadataFilter {
  key: string;
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte';
  value: string | number | boolean;
}

interface SearchParams {
  collection_id: string;
  query_text?: string;
  vector_id?: string;
  metadata_filters?: MetadataFilter[];
  top_k?: number;
  threshold?: number;
}

interface CollectionStats {
  vector_count: number;
  avg_vector_size?: number;
  storage_size?: string;
  created_at: string;
  updated_at: string;
}

// Replace with your actual API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Create axios instance with auth headers
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  config => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

/**
 * Fetch all available collections
 */
export const fetchCollections = async (): Promise<Collection[]> => {
  try {
    const response = await apiClient.get('/collections');
    return response.data.collections;
  } catch (error) {
    console.error('Error fetching collections:', error);
    throw error;
  }
};

/**
 * Create a new collection
 */
export const createCollection = async (name: string, description: string = ''): Promise<Collection> => {
  try {
    const response = await apiClient.post('/collections', {
      name,
      description
    });
    return response.data;
  } catch (error) {
    console.error('Error creating collection:', error);
    throw error;
  }
};

/**
 * Delete a collection
 */
export const deleteCollection = async (collectionId: string): Promise<{ success: boolean }> => {
  try {
    const response = await apiClient.delete(`/collections/${collectionId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting collection:', error);
    throw error;
  }
};

/**
 * Search vectors in a collection
 */
export const searchVectors = async (params: SearchParams): Promise<SearchResult[]> => {
  try {
    const response = await apiClient.post('/search', params);
    return response.data.results;
  } catch (error) {
    console.error('Error searching vectors:', error);
    throw error;
  }
};

/**
 * Get vector by ID
 */
export const getVectorById = async (collectionId: string, vectorId: string): Promise<Vector> => {
  try {
    const response = await apiClient.get(`/collections/${collectionId}/vectors/${vectorId}`);
    return response.data.vector;
  } catch (error) {
    console.error('Error fetching vector:', error);
    throw error;
  }
};

/**
 * Delete a vector
 */
export const deleteVector = async (collectionId: string, vectorId: string): Promise<{ success: boolean }> => {
  try {
    const response = await apiClient.delete(`/collections/${collectionId}/vectors/${vectorId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting vector:', error);
    throw error;
  }
};

/**
 * Upload a document to be vectorized
 */
export const uploadDocument = async (formData: FormData): Promise<{ success: boolean; vector_id?: string }> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};

/**
 * Get collection statistics
 */
export const getCollectionStats = async (collectionId: string): Promise<CollectionStats> => {
  try {
    const response = await apiClient.get(`/collections/${collectionId}/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching collection stats:', error);
    throw error;
  }
};

/**
 * Update vector metadata
 */
export const updateVectorMetadata = async (
  collectionId: string, 
  vectorId: string, 
  metadata: Record<string, any>
): Promise<{ success: boolean }> => {
  try {
    const response = await apiClient.patch(`/collections/${collectionId}/vectors/${vectorId}`, {
      metadata
    });
    return response.data;
  } catch (error) {
    console.error('Error updating vector metadata:', error);
    throw error;
  }
};

/**
 * Batch upload vectors
 */
export const batchUploadVectors = async (
  collectionId: string, 
  vectors: Array<{ content: string; metadata?: Record<string, any> }>
): Promise<{ success: boolean; vector_ids?: string[] }> => {
  try {
    const response = await apiClient.post(`/collections/${collectionId}/vectors/batch`, {
      vectors
    });
    return response.data;
  } catch (error) {
    console.error('Error batch uploading vectors:', error);
    throw error;
  }
};

export default {
  fetchCollections,
  createCollection,
  deleteCollection,
  searchVectors,
  getVectorById,
  deleteVector,
  uploadDocument,
  getCollectionStats,
  updateVectorMetadata,
  batchUploadVectors
};