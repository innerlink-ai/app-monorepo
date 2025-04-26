import { useAuthStore } from "../stores/authStore";
import { axios } from '../composables/index';
import { config } from '@/config';

const BASE_URL = config.apiUrl;

// Define types for API responses
interface EmbeddingStatus {
  task_id?: string;
  collection_id?: string;
  document_ids: string[];
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'not_processed';
  progress: number;
  document_count: number;
  processed_count: number;
  chunk_count?: number; // Added for document-specific status
}

interface DocumentStatus {
  document_id: string;
  status: 'completed' | 'not_processed' | 'processing' | 'unprocessable';
  chunks_processed: number;
  total_chunks: number;
  collection_id: string;
  metadata?: any;
}

interface EmbeddingRequest {
  collection_id?: string;
  document_ids?: string[];
}

interface SearchResult {
  document_id: string;
  document_name: string;
  collection_id: string;
  collection_name: string;
  chunk_text: string;
  chunk_index: number;
  similarity: number;
  metadata?: Record<string, any>;
}

interface SearchQuery {
  query: string;
  collection_id?: string;
  limit?: number;
  filter_metadata?: Record<string, any>;
}

// Helper function to check auth before making requests
const withAuth = async (apiCall: () => Promise<any>) => {
  const authStore = useAuthStore();
  await authStore.checkAuth();
  if (!authStore.isAuthenticated) {
    throw new Error("Not authenticated");
  }
  return apiCall();
};

// Embeddings service with methods matching our API endpoints
export const embeddingsService = {
  /**
   * Generate embeddings for documents in a collection
   * @param params - Parameters for embedding generation
   * @returns Promise with the status of the embedding generation task
   */
  async generateEmbeddings(params: EmbeddingRequest): Promise<EmbeddingStatus> {
    return withAuth(async () => {
      try {
        const response = await axios.post(`${BASE_URL}/embeddings/generate`, params, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Error generating embeddings:', error);
        throw error;
      }
    });
  },

  /**
   * Get status of an embedding generation task
   * @param taskId - Task ID to get status for
   * @returns Promise with the current status of the embedding task
   */
  async getEmbeddingStatus(taskId: string): Promise<EmbeddingStatus> {
    return withAuth(async () => {
      try {
        const response = await axios.get(`${BASE_URL}/embeddings/status/${taskId}`, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error(`Error fetching embedding status for task ${taskId}:`, error);
        throw error;
      }
    });
  },

  /**
   * Check embeddings status for a collection
   * @param collectionId - Collection ID to check status for
   * @returns Promise with the status information or null if not found
   */
  async getCollectionEmbeddingStatus(collectionId: string): Promise<EmbeddingStatus | null> {
    return withAuth(async () => {
      try {
        const response = await axios.get(`${BASE_URL}/embeddings/collection/${collectionId}/status`, {
          withCredentials: true
        });
        return response.data;
      } catch (error: any) {
        // If no status found, don't throw error, just return null
        if (error.response?.status === 404) {
          return null;
        }
        console.error(`Error fetching embedding status for collection ${collectionId}:`, error);
        throw error;
      }
    });
  },

  /**
   * Get embedding status for a specific document
   * @param documentId - Document ID to check status for
   * @returns Promise with the document embedding status
   */
  async getDocumentEmbeddingStatus(documentId: string): Promise<DocumentStatus | null> {
    return withAuth(async () => {
      try {
        const response = await axios.get(`${BASE_URL}/embeddings/document/${documentId}/status`, {
          withCredentials: true
        });
        return response.data;
      } catch (error: any) {
        // If no status found, don't throw error, just return null
        if (error.response?.status === 404) {
          return null;
        }
        console.error(`Error fetching embedding status for document ${documentId}:`, error);
        throw error;
      }
    });
  },

  /**
   * Search using vector embeddings
   * @param params - Search parameters
   * @returns Promise with search results
   */
  async search(params: SearchQuery): Promise<SearchResult[]> {
    return withAuth(async () => {
      try {
        const response = await axios.post(`${BASE_URL}/embeddings/search`, params, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Error performing vector search:', error);
        throw error;
      }
    });
  },

  /**
   * Simple search using query parameters
   * @param query - Search query text
   * @param collectionId - Optional collection ID to search within
   * @param limit - Maximum number of results to return
   * @returns Promise with search results
   */
  async simpleSearch(query: string, collectionId?: string, limit: number = 10): Promise<SearchResult[]> {
    return withAuth(async () => {
      try {
        const params: Record<string, any> = { query };
        if (collectionId) params.collection_id = collectionId;
        if (limit) params.limit = limit;
        
        const response = await axios.get(`${BASE_URL}/embeddings/search`, {
          params,
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Error performing simple search:', error);
        throw error;
      }
    });
  },

  /**
   * Poll status updates
   * @param taskId - Task ID to poll
   * @param onUpdate - Callback function for status updates
   * @param interval - Polling interval in milliseconds
   */
  async pollStatus(
    taskId: string, 
    onUpdate: (status: EmbeddingStatus) => void, 
    interval: number = 2000
  ): Promise<void> {
    const poll = async () => {
      try {
        const status = await this.getEmbeddingStatus(taskId);
        onUpdate(status);
        
        // Continue polling if still processing
        if (status.status === 'processing' || status.status === 'queued') {
          setTimeout(poll, interval);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        // Stop polling on error
      }
    };
    
    poll();
  }
};

export default embeddingsService;