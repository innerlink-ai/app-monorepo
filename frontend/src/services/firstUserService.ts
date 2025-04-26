// firstUserService.ts
import { axios } from '../composables/index';
import { config } from '@/config';
const BASE_URL = config.apiUrl;

/**
 * Check if this is the first user setup
 * @returns Promise with first user status data
 */
export const checkFirstUser = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/check-first-user`, {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error("Error checking first user status:", error);
    throw error;
  }
};

/**
 * Create an invite for the first admin user
 * @param email The email address for the admin user
 * @returns Promise with invite data
 */
export const createFirstUserInvite = async (email: string) => {
  try {
    const response = await axios.post(`${BASE_URL}/invite`, { email }, {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error("Error creating first user invite:", error);
    throw error;
  }
};

/**
 * Check registration invite details
 * @param token The invite token
 * @returns Promise with invite details
 */
export const getInviteDetails = async (token: string) => {
  try {
    const response = await axios.get(`${BASE_URL}/admin/invite?token=${token}`, {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error("Error getting invite details:", error);
    throw error;
  }
};

// Export as a service object
export const firstUserService = {
  checkFirstUser,
  createFirstUserInvite,
  getInviteDetails
};