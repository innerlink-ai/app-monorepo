
import { axios, ref, defineStore } from '../composables/index'
import { config } from '@/config';
const BASE_URL = config.apiUrl;


export const useAuthStore = defineStore("auth", () => {
  const isAuthenticated = ref(false);
  const isAdmin = ref(false);
  const isLoading = ref(true);

  const checkAuth = async () => {
    try {
      //console.log('checkAuth called from:', new Error().stack); 
      const response = await axios.get(`${BASE_URL}/user-info`, {
        withCredentials: true,
      });
      isAuthenticated.value = true;
      isAdmin.value = response.data.is_admin;
    } catch (error: any) {
      console.error("Authentication failed:", error);

      // ✅ If token expired, attempt to refresh
      if (error.response?.status === 401) {
        try {
          await refreshToken(); 
          await checkAuth(); //
        } catch (refreshError) {
          console.error("Token refresh failed:", refreshError);
          isAuthenticated.value = false;
          isAdmin.value = false;
        }
      } else {
        isAuthenticated.value = false;
        isAdmin.value = false;
      }
    } finally {
      isLoading.value = false;
    }
  };

  // ✅ Function to refresh token
  const refreshToken = async () => {
    await axios.post(`${BASE_URL}/refresh`, {}, { withCredentials: true });
  };

  // ✅ Function to handle login
  const login = async (email: string, password: string) => {
    await axios.post(`${BASE_URL}/login`, { email, password }, { withCredentials: true });
    await checkAuth(); // ✅ Revalidate session immediately after login
  };

  // ✅ Function to handle logout
  const logout = async () => {
    await axios.post(`${BASE_URL}/logout`, {}, { withCredentials: true });
    isAuthenticated.value = false;
    isAdmin.value = false;
  };

  return { isAuthenticated, isAdmin, isLoading, checkAuth, login, logout };
});
