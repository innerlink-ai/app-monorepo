// adminService.ts
import { useAuthStore } from "../stores/authStore";
import { axios, useRouter, } from '../composables/index'
import { config } from '@/config';
const BASE_URL = config.apiUrl;

export interface User {
  id: string;
  email: string;
  is_admin: boolean;
  created_at: string;
}

export interface Invite {
  id: string;
  email: string;
  access_role: string;
  created_at: string;
  expires_at: string;
  token: string;
}

export interface InvitePayload {
  email: string;
  is_admin: boolean;
}

export interface RegistrationLinkResponse {
  token: string;
  registrationUrl: string;
}

export const checkAdminAuth = async (): Promise<boolean> => {
  const authStore = useAuthStore();
  const router = useRouter();

  try {
    // First check if user is authenticated and is an admin
    if (!authStore.isAuthenticated || !authStore.isAdmin) {
      router.push("/");
      return false;
    }

    // Then verify admin access with the backend
    await axios.get(`${BASE_URL}/admin/users`, { withCredentials: true });
    return true;
  } catch (error) {
    console.error("Authentication failed:", error);
    router.push("/");
    return false;
  }
};

export const validateEmail = (email: string): string | null => {
  if (!email.trim()) {
    return "Email is required.";
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return "Invalid email format.";
  }
  return null;
};

export const inviteUser = async (payload: InvitePayload): Promise<void> => {
  try {
    await axios.post(
      `${BASE_URL}/admin/invite`,
      payload,
      { withCredentials: true }
    );
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || "An error occurred.");
  }
};

export const fetchUsers = async (): Promise<User[]> => {
  try {
    const response = await axios.get(`${BASE_URL}/admin/users`, { 
      withCredentials: true 
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching users:", error);
    throw error;
  }
};

export const fetchPendingInvites = async (): Promise<Invite[]> => {
  try {
    const response = await axios.get(`${BASE_URL}/admin/invites`, { 
      withCredentials: true 
    });
    console.log(response.data);
    const currentTime = new Date();
    return response.data.filter((invite: Invite) => 
      new Date(invite.expires_at) > currentTime
    );
  } catch (error) {
    console.error("Error fetching pending invites:", error);
    throw error;
  }
};

/**
 * Calls the backend endpoint to reset the entire system.
 * WARNING: This is a destructive operation.
 * @returns Promise resolving with the success message or rejecting with an error.
 */
export const resetSystem = async (): Promise<{ message: string }> => {
  try {
    const response = await axios.post(
      `${BASE_URL}/admin/reset-system`, 
      {}, // Send empty object as data if no payload needed
      { withCredentials: true } // Add this option to send cookies
    );
    return response.data;
  } catch (error: any) {
    console.error("Error calling reset system endpoint:", error);
    const message = error.response?.data?.detail || "Failed to reset system. Please check server logs.";
    throw new Error(message);
  }
};

export const generateRegistrationLink = async (email: string, isAdmin: boolean): Promise<RegistrationLinkResponse> => {
  try {
    const frontendBaseUrl = window.location.origin;
    const response = await axios.post(
      `${BASE_URL}/admin/generate-registration-link`,
      { email, is_admin: isAdmin, base_url: frontendBaseUrl },
      { withCredentials: true }
    );
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || "Failed to generate registration link");
  }
};

