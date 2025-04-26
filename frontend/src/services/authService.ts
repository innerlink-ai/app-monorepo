// authService.ts
import { useAuthStore } from "../stores/authStore";
import { axios,  } from '../composables/index'
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

export const logout = async (): Promise<void> => {
  return withAuth(async () => {
    try {
      await axios.post(`${BASE_URL}/logout`, {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error("Logout failed:", error);
      throw error;
    }
  });
};