// userService.ts
import { useAuthStore } from "../stores/authStore";
import { axios } from '../composables/index';
import { config } from '@/config';
const BASE_URL = config.apiUrl;

interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  token: string | null;
}

interface InviteDetails {
  email: string;
  access_role: string;
}

interface UserInfo {
  email: string;
  name: string;
  is_admin: boolean;
}

interface UserUpdatePayload {
  name: string;
  newPassword?: string;
  currentPassword?: string;
  passwordStrength?: number;
}

// Password strength checker
export const checkPasswordStrength = (password: string): number => {
  let strength = 0;
  
  // Length check
  if (password.length >= 8) strength += 1;
  if (password.length >= 12) strength += 1;
  
  // Complexity checks
  if (/[A-Z]/.test(password)) strength += 1; // Has uppercase
  if (/[a-z]/.test(password)) strength += 1; // Has lowercase
  if (/[0-9]/.test(password)) strength += 1; // Has number
  if (/[^A-Za-z0-9]/.test(password)) strength += 1; // Has special char
  
  return Math.max(0, Math.min(5, strength));
};

export const verifyInvite = async (token: string): Promise<InviteDetails> => {
  try {
    const response = await axios.get(`${BASE_URL}/invite?token=${token}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching invite details:", error);
    throw error;
  }
};

export const register = async (payload: RegisterPayload): Promise<void> => {
  const authStore = useAuthStore();
  
  try {
    await axios.post(`${BASE_URL}/register`, payload, {
      withCredentials: true
    });
    
    // Update authentication state
    await authStore.checkAuth();
  } catch (error: any) {
    console.error("Error registering:", error);
    if (error.response?.data?.detail === "User with this email already exists.") {
      throw new Error("An account with this email already exists.");
    }
    throw new Error("Registration failed. Please try again.");
  }
};

/**
 * Fetch current user information
 */
export const getUserInfo = async (): Promise<UserInfo> => {
  try {
    const response = await axios.get(`${BASE_URL}/user-info`, {
      withCredentials: true
    });
    return response.data;
  } catch (error: any) {
    console.error("Error fetching user info:", error);
    throw new Error(error.response?.data?.detail || "Failed to fetch user information");
  }
};

/**
 * Update user information including name and optionally password
 */
export const updateUserInfo = async (payload: UserUpdatePayload): Promise<void> => {
  try {
    // Validate password strength client-side
    if (payload.newPassword && payload.passwordStrength && payload.passwordStrength < 3) {
      throw new Error("Password is not strong enough. Please choose a stronger password.");
    }
    
    await axios.put(`${BASE_URL}/user`, payload, {
      withCredentials: true
    });
    
    // Clear sensitive data from memory
    if (payload.newPassword) {
      payload.newPassword = '';
      payload.currentPassword = '';
    }
  } catch (error: any) {
    console.error("Error updating user info:", error);
    throw new Error(error.response?.data?.detail || "Failed to update user information");
  }
};

/**
 * Request a password reset link for the given email
 */
export const requestPasswordReset = async (email: string): Promise<{ message: string }> => {
  try {
    const response = await axios.post(`${BASE_URL}/password-reset-request`, { email });
    return response.data; // Should contain the success message
  } catch (error: any) {
    console.error("Error requesting password reset:", error);
    // Even on backend error, often better to show generic message to avoid enumeration
    // throw new Error(error.response?.data?.detail || "Failed to request password reset");
    return { message: "If an account with that email exists, a password reset link has been sent." }; 
  }
};

interface ResetPasswordPayload {
  token: string;
  new_password: string;
}

/**
 * Reset the user's password using a valid token
 */
export const resetPassword = async (payload: ResetPasswordPayload): Promise<{ message: string }> => {
  try {
    const response = await axios.post(`${BASE_URL}/reset-password`, payload);
    return response.data; // Success message
  } catch (error: any) {
    console.error("Error resetting password:", error);
    throw new Error(error.response?.data?.detail || "Failed to reset password");
  }
};