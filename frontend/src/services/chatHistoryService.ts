// chatHistoryService.ts
import { useAuthStore } from "../stores/authStore";
import { axios } from '../composables/index';
import { config } from '@/config';
const BASE_URL = config.apiUrl;

// Helper function to check auth before making requests
const withAuth = async (apiCall: () => Promise<any>) => {
  const authStore = useAuthStore();
  await authStore.checkAuth();
  if (!authStore.isAuthenticated) {
    throw new Error("Not authenticated");
  }
  return apiCall();
};

/**
 * Fetch all chats for the current user
 * @returns Promise with chat history data
 */
export const fetchChats = async () => {
  return withAuth(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/chats`, {
        withCredentials: true
      });
      return response.data.chats;
    } catch (error) {
      console.error("Error fetching chat history:", error);
      throw error;
    }
  });
};

/**
 * Create a new chat
 * @param name Optional name for the chat
 * @returns Promise with new chat data
 */
export const createChat = async (name?: string) => {
  return withAuth(async () => {
    try {
      const payload = name ? { name } : null;
      const response = await axios.post(`${BASE_URL}/create_chat`, payload, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error("Error creating chat:", error);
      throw error;
    }
  });
};

/**
 * Delete a chat by ID
 * @param chatId The ID of the chat to delete
 * @returns Promise with deletion confirmation
 */
export const deleteChat = async (chatId: string) => {
  return withAuth(async () => {
    try {
      const response = await axios.delete(`${BASE_URL}/chats/${chatId}`, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error("Error deleting chat:", error);
      throw error;
    }
  });
};

/**
 * Update chat details (e.g., name)
 * @param chatId The ID of the chat to update
 * @param updates Object containing fields to update
 * @returns Promise with updated chat data
 */
export const updateChat = async (chatId: string, updates: { name?: string }) => {
  return withAuth(async () => {
    try {
      const response = await axios.put(`${BASE_URL}/chats/${chatId}`, updates, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error("Error updating chat:", error);
      throw error;
    }
  });
};

/**
 * Search chats by query
 * Note: This assumes your API has a search endpoint.
 * If not, you'll need to implement client-side filtering.
 * @param query Search query text
 * @returns Promise with search results
 */
export const searchChats = async (query: string) => {
  return withAuth(async () => {
    try {
      // If your API doesn't have a search endpoint, 
      // fetch all chats and filter on the client side
      const chats = await fetchChats();
      
      if (!query.trim()) {
        return chats;
      }
      
      const lowerQuery = query.toLowerCase();
      return chats.filter((chat: any) => 
        chat.name.toLowerCase().includes(lowerQuery) || 
        (chat.preview && chat.preview.toLowerCase().includes(lowerQuery))
      );
    } catch (error) {
      console.error("Error searching chats:", error);
      throw error;
    }
  });
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