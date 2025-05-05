<template>
  <div 
    v-if="isAuthenticated" 
    class="flex flex-col h-screen overflow-hidden"
    :style="contentStyle"
  >
    <!-- Header Section -->
    <div class="pt-3 pb-4 px-6 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Settings class="h-5 w-5 text-[var(--secondary-text)] stroke-[1]" />
          <h2 class="text-lg font-light text-[var(--secondary-text)]">User Settings</h2>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden bg-[var(--bg-color)]">
      <div class="max-w-7xl w-full mx-auto p-6 overflow-y-auto custom-scrollbar">
        <!-- Settings Form -->
        <div class="mb-8 border border-[var(--border-color)] rounded-lg p-6 bg-[var(--bg-color)]">
          <h2 class="text-sm font-semibold mb-4">Account Information</h2>
          <form @submit.prevent="updateSettings" class="flex flex-col gap-6">              
            <!-- Email Field (Read-only) -->
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-[var(--text-color)]">Email</label>
              <input
                v-model="formData.email"
                type="email"
                class="w-full p-3 rounded-lg border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[var(--border-color-lighter)] disabled:opacity-70 disabled:cursor-not-allowed"
                placeholder="Your email"
                disabled
                autocomplete="email"
              />
            </div>

            <!-- Password Change Section -->
            <div class="mt-4 pt-4 border-t border-[var(--border-color)]">
              <h3 class="text-sm font-semibold mb-4">Change Password</h3>
              
              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-[var(--text-color)]">Current Password</label>
                <input
                  v-model="formData.currentPassword"
                  type="password"
                  class="w-full p-3 rounded-lg border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[var(--border-color-lighter)]"
                  placeholder="Required for password change"
                  autocomplete="off"
                />
                <div v-if="currentPasswordRequired" class="text-red-500 text-sm mt-1">
                  Current password is required for password change
                </div>
              </div>
              
              <!-- New Password Field -->
              <div class="flex flex-col gap-2 mt-3">
                <label class="text-sm font-medium text-[var(--text-color)]">New Password</label>
                <input
                  v-model="formData.newPassword"
                  type="password"
                  class="w-full p-3 rounded-lg border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[var(--border-color-lighter)]"
                  placeholder="New password"
                  autocomplete="new-password"
                  @input="checkPasswordStrength"
                />
                
                <!-- Password Strength Indicator -->
                <div v-if="formData.newPassword" class="mt-2">
                  <div class="text-sm mb-1">Password Strength: {{ passwordStrengthText }}</div>
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      class="h-full" 
                      :class="passwordStrengthClass"
                      :style="{ width: `${passwordStrengthPercent}%` }"
                    ></div>
                  </div>
                  <div class="text-xs mt-1 text-gray-500">
                    * Password should be at least 12 characters with uppercase, lowercase, numbers, and special characters
                  </div>
                </div>
              </div>

              <!-- Confirm New Password Field -->
              <div class="flex flex-col gap-2 mt-3">
                <label class="text-sm font-medium text-[var(--text-color)]">Confirm New Password</label>
                <input
                  v-model="formData.confirmPassword"
                  type="password"
                  class="w-full p-3 rounded-lg border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[var(--border-color-lighter)]"
                  placeholder="Confirm new password"
                  autocomplete="new-password"
                />
                <div v-if="passwordMismatch" class="text-red-500 text-sm mt-1">
                  Passwords do not match
                </div>
              </div>
            </div>

            <!-- Confirmation Section for Password Change -->
            <div v-if="showConfirmation" class="bg-blue-100 dark:bg-blue-900 p-4 rounded-lg">
              <h4 class="font-medium mb-2">Confirm Password Change</h4>
              <p class="text-sm mb-3">For security reasons, please confirm that you want to change your password.</p>
              <div class="flex gap-3">
                <button 
                  type="button" 
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500"
                  @click="confirmPasswordChange"
                >
                  Confirm
                </button>
                <button 
                  type="button"
                  class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
                  @click="cancelPasswordChange"
                >
                  Cancel
                </button>
              </div>
            </div>

            <!-- Submit Button -->
            <button
              v-if="!showConfirmation"
              type="submit"
              class="mt-2 py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center justify-center w-auto self-start"
              :disabled="isLoading || !isFormValid || passwordBeingChanged"
            >
              {{ isLoading ? 'Updating...' : 'Update Settings' }}
            </button>

            <!-- Error Message -->
            <div v-if="error" class="text-red-500 text-sm p-3 border border-red-300 bg-red-50 dark:bg-red-900/30 dark:border-red-800 rounded">
              {{ error }}
            </div>

            <!-- Success Message -->
            <div v-if="success" class="text-green-500 text-sm p-3 border border-green-300 bg-green-50 dark:bg-green-900/30 dark:border-green-800 rounded">
              {{ success }}
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useSidebarStore } from '../stores/sidebarStore';
import { useAuthStore } from '../stores/authStore';
import { useRouter } from '../composables/index';
import { Settings } from 'lucide-vue-next';
import { getUserInfo, updateUserInfo, checkPasswordStrength as serviceCheckPasswordStrength } from '../services/userService';

// Ensure the interface for the update payload is defined
interface UserUpdatePayload {
  name: string;
  newPassword?: string;
  currentPassword?: string;
  passwordStrength?: number; // Added passwordStrength as optional
}

const router = useRouter();
const authStore = useAuthStore();
const sidebarStore = useSidebarStore();
const isAuthenticated = ref(true);
const isLoading = ref(false);
const error = ref('');
const success = ref('');
const passwordMismatch = ref(false);
const currentPasswordRequired = ref(false);
const passwordStrength = ref(0);
const passwordBeingChanged = ref(false);
const showConfirmation = ref(false);
const lastActivity = ref(Date.now());
const sessionTimeout = 1000 * 60 * 15; // 15 minutes

// Track user activity to prevent session timeout
const updateLastActivity = () => {
  lastActivity.value = Date.now();
};

// Set up activity tracking
onMounted(() => {
  document.addEventListener('mousemove', updateLastActivity);
  document.addEventListener('keypress', updateLastActivity);
  
  // Check for session timeout every minute
  const interval = setInterval(() => {
    if (Date.now() - lastActivity.value > sessionTimeout) {
      clearInterval(interval);
      // Handle session timeout
      error.value = 'Your session has timed out. Please refresh the page and try again.';
      document.removeEventListener('mousemove', updateLastActivity);
      document.removeEventListener('keypress', updateLastActivity);
    }
  }, 60000);
  
  // Clean up on component unmount
  onUnmounted(() => {
    clearInterval(interval);
    document.removeEventListener('mousemove', updateLastActivity);
    document.removeEventListener('keypress', updateLastActivity);
  });
});

const formData = ref({
  email: '',
  newPassword: '',
  confirmPassword: '',
  currentPassword: ''
});

// Calculate password strength text and color
const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value;
  if (strength === 0) return 'Very Weak';
  if (strength === 1) return 'Weak';
  if (strength === 2) return 'Fair';
  if (strength === 3) return 'Good';
  if (strength === 4) return 'Strong';
  return 'Very Strong';
});

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value;
  if (strength <= 1) return 'bg-red-500';
  if (strength === 2) return 'bg-orange-500';
  if (strength === 3) return 'bg-yellow-500';
  if (strength >= 4) return 'bg-green-500';
  return 'bg-gray-200';
});

const passwordStrengthPercent = computed(() => {
  return Math.min(100, Math.max(0, passwordStrength.value * 20));
});

// Validate password strength when it changes
const checkPasswordStrength = () => {
  if (!formData.value.newPassword) {
    passwordStrength.value = 0;
    return;
  }
  
  passwordStrength.value = serviceCheckPasswordStrength(formData.value.newPassword);
};

// Watch for password changes to clear validation errors
watch(() => formData.value.newPassword, () => {
  passwordMismatch.value = false;
  checkPasswordStrength();
  
  if (formData.value.newPassword) {
    currentPasswordRequired.value = !formData.value.currentPassword;
  } else {
    currentPasswordRequired.value = false;
  }
});

watch(() => formData.value.confirmPassword, () => {
  if (formData.value.newPassword && formData.value.confirmPassword) {
    passwordMismatch.value = formData.value.newPassword !== formData.value.confirmPassword;
  } else {
    passwordMismatch.value = false;
  }
});

watch(() => formData.value.currentPassword, () => {
  if (formData.value.newPassword) {
    currentPasswordRequired.value = !formData.value.currentPassword;
  } else {
    currentPasswordRequired.value = false;
  }
});

const isFormValid = computed(() => {
  // Password validation
  if (formData.value.newPassword) {
    if (formData.value.newPassword !== formData.value.confirmPassword) return false;
    if (!formData.value.currentPassword) return false;
    if (passwordStrength.value < 3) return false; // Require at least "Good" strength
  }
  
  return true;
});

// Computed style for the content window that adjusts with sidebar
const contentStyle = computed(() => ({
  marginLeft: sidebarStore.isCollapsed ? "3.5rem" : "14rem",
  transition: "margin-left 0.3s ease",
  width: `calc(100% - ${sidebarStore.isCollapsed ? "3.5rem" : "14rem"})`,
  position: "fixed" as const,
  top: 0,
  right: 0,
  bottom: 0,
}));

const fetchUserData = async () => {
  try {
    isLoading.value = true;
    const userData = await getUserInfo();
    formData.value.email = userData.email || '';
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load user data';
    console.error('Error fetching user data:', err);
  } finally {
    isLoading.value = false;
  }
};

const updateSettings = async () => {
  // Clear previous messages
  error.value = '';
  success.value = '';
  
  // Validate password fields
  if (formData.value.newPassword) {
    if (formData.value.newPassword !== formData.value.confirmPassword) {
      passwordMismatch.value = true;
      return;
    }
    
    if (!formData.value.currentPassword) {
      currentPasswordRequired.value = true;
      return;
    }
    
    if (passwordStrength.value < 3) {
      error.value = 'Please choose a stronger password.';
      return;
    }
    
    // Show confirmation dialog for password changes
    showConfirmation.value = true;
    passwordBeingChanged.value = true;
    return;
  }
  
  // If we're only updating name, proceed directly
  await saveChanges();
};

const confirmPasswordChange = async () => {
  showConfirmation.value = false;
  await saveChanges();
};

const cancelPasswordChange = () => {
  showConfirmation.value = false;
  passwordBeingChanged.value = false;
  // Clear password fields for security
  formData.value.newPassword = '';
  formData.value.confirmPassword = '';
  formData.value.currentPassword = '';
};

const saveChanges = async () => {
  isLoading.value = true;
  
  try {
    // Ensure payload is correctly typed with UserUpdatePayload
    const payload: UserUpdatePayload = { name: '' };
    
    // Only include password fields if changing password
    if (formData.value.newPassword) {
      payload.newPassword = formData.value.newPassword;
      payload.currentPassword = formData.value.currentPassword;
      payload.passwordStrength = passwordStrength.value; // Assign strength
    }
    
    await updateUserInfo(payload);
    
    success.value = 'Settings updated successfully';
    
    // Reset password fields for security
    formData.value.newPassword = '';
    formData.value.confirmPassword = '';
    formData.value.currentPassword = '';
    passwordBeingChanged.value = false;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An unexpected error occurred';
    console.error('Error updating settings:', err);
    passwordBeingChanged.value = false;
  } finally {
    isLoading.value = false;
  }
};

// Fetch user data when component mounts
onMounted(() => {
  authStore.checkAuth();
  fetchUserData();
});
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: 3px;
}

.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: var(--button-hover);
}
</style>