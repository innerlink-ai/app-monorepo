import { useAuthStore } from "../stores/authStore";
import { axios } from '../composables/index';
import { config } from '@/config';

const BASE_URL = config.apiUrl;

// Define types for API responses
interface Collection {
  id: string;
  user_id: string;
  name: string;
  type: string;
  description?: string;
  created_at: string;
  updated_at: string;
  document_count: number;
}

interface Document {
  id: string;
  collection_id: string;
  name: string;
  type: string;
  size: number;
  content_type?: string;
  is_encrypted: boolean;
  created_at: string;
  updated_at: string;
}

interface CollectionCreate {
  name: string;
  type: string;
  description?: string;
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

// Collections service with methods matching our API endpoints
export const collectionsService = {
  /**
   * Get all collections for the current user
   * @returns Promise with the collections data
   */
  async getCollections(): Promise<Collection[]> {
    return withAuth(async () => {
      try {
        const response = await axios.get(`${BASE_URL}/collections`, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Error fetching collections:', error);
        throw error;
      }
    });
  },

  /**
   * Get a specific collection by ID
   * @param collectionId - The collection's ID
   * @returns Promise with the collection data
   */
  async getCollection(collectionId: string): Promise<Collection> {
    return withAuth(async () => {
      try {
        const response = await axios.get(`${BASE_URL}/collections/${collectionId}`, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error(`Error fetching collection ${collectionId}:`, error);
        throw error;
      }
    });
  },

  /**
   * Create a new collection
   * @param collectionData - The collection data (name, type, description)
   * @returns Promise with the created collection data
   */
  async createCollection(collectionData: CollectionCreate): Promise<Collection> {
    return withAuth(async () => {
      try {
        const response = await axios.post(`${BASE_URL}/collections`, collectionData, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error('Error creating collection:', error);
        throw error;
      }
    });
  },

  /**
   * Delete a collection
   * @param collectionId - The collection's ID
   * @returns Promise with the deletion result
   */
  async deleteCollection(collectionId: string): Promise<{ message: string }> {
    return withAuth(async () => {
      try {
        const response = await axios.delete(`${BASE_URL}/collections/${collectionId}`, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error(`Error deleting collection ${collectionId}:`, error);
        throw error;
      }
    });
  },

  /**
   * Get all documents in a collection
   * @param collectionId - The collection's ID
   * @returns Promise with the documents data
   */
  async getDocuments(collectionId: string): Promise<Document[]> {
    return withAuth(async () => {
      try {
        const response = await axios.get(`${BASE_URL}/collections/${collectionId}/documents`, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error(`Error fetching documents for collection ${collectionId}:`, error);
        throw error;
      }
    });
  },

  /**
   * Upload a document to a collection
   * @param collectionId - The collection's ID
   * @param file - The file to upload
   * @returns Promise with the uploaded document data
   */
  async uploadDocument(collectionId: string, file: File): Promise<Document> {
    return withAuth(async () => {
      try {
        // Use FormData for file uploads
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(
          `${BASE_URL}/collections/${collectionId}/documents`, 
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            withCredentials: true
          }
        );
        return response.data;
      } catch (error) {
        console.error(`Error uploading document to collection ${collectionId}:`, error);
        throw error;
      }
    });
  },

  /**
   * Delete a document
   * @param documentId - The document's ID
   * @returns Promise with the deletion result
   */
  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return withAuth(async () => {
      try {
        const response = await axios.delete(`${BASE_URL}/documents/${documentId}`, {
          withCredentials: true
        });
        return response.data;
      } catch (error) {
        console.error(`Error deleting document ${documentId}:`, error);
        throw error;
      }
    });
  }
};

// Error handler middleware
export const handleApiError = (error: any) => {
  const authStore = useAuthStore();
  if (error.response?.status === 401) {
    // If token expired, user will be logged out
    authStore.checkAuth();
  }
  throw error;
};

export default collectionsService;