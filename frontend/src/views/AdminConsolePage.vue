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
          <Wrench class="h-5 w-5 text-[var(--secondary-text)] stroke-[1]" />
          <h2 class="text-lg font-light text-[var(--secondary-text)]">Admin Console</h2>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden bg-[var(--bg-color)]">
      <div class="max-w-7xl w-full mx-auto p-6 overflow-y-auto">
        <!-- Unauthorized Access Message -->
        <div v-if="!isAdmin" class="mb-8 border border-red-500 rounded-lg p-6 bg-red-50 dark:bg-red-900/30">
          <div class="flex items-center gap-3 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 class="text-lg font-medium text-red-600 dark:text-red-400">Access Denied</h3>
          </div>
          <p class="text-sm text-red-600 dark:text-red-400 mb-4">
            You do not have permission to access the Admin Console. This area is restricted to administrators only.
          </p>
          <button 
            @click="router.push('/')" 
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
          >
            Return to Home
          </button>
        </div>

        <!-- Admin Content -->
        <div v-else>
          <!-- Generate Registration Link Form -->
          <div class="mb-8 border border-[var(--border-color)] rounded-lg p-6 bg-[var(--bg-color)]">
            <h2 class="text-sm font-semibold mb-4">Generate Registration Link</h2>

            <!-- Fields (Side by Side on md+, stacked on small screens) -->
            <div class="flex flex-col md:flex-row gap-4">
              <div class="flex-1">
                <label for="regEmail" class="block text-xs font-medium mb-1 text-[var(--secondary-text)]">Email Address</label>
                <input 
                  id="regEmail"
                  v-model="regEmail"
                  type="email"
                  placeholder="Enter user email"
                  class="w-full px-4 py-2 border border-[var(--border-color)] rounded-lg bg-[var(--bg-color)] text-[var(--text-color)] focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                  :class="{ 'border-red-500': regEmailError }"
                />
                <p v-if="regEmailError" class="text-red-500 text-xs mt-1">{{ regEmailError }}</p>
              </div>
              <div class="w-full md:w-auto">
                <label for="regRole" class="block text-xs font-medium mb-1 text-[var(--secondary-text)]">Access Role</label>
                <select 
                  id="regRole"
                  v-model="regRole"
                  class="w-full px-4 py-2 border border-[var(--border-color)] rounded-lg bg-[var(--bg-color)] text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow duration-200"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>

            <!-- Generate Link Button & Error/Success Messages -->
            <div class="mt-6 flex flex-col md:flex-row items-center justify-between">
              <button 
                @click="handleGenerateLink" 
                class="py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 cursor-pointer transition-all duration-200 flex items-center gap-2 text-sm"
              >
                Generate Link
              </button>
              <div class="mt-2 md:mt-0 text-right">
                <p v-if="regServerError" class="text-red-500 text-xs">{{ regServerError }}</p>
                <p v-if="regLinkMessage" class="text-xs text-green-600">{{ regLinkMessage }}</p>
              </div>
            </div>

            <!-- Registration Link Display -->
            <div v-if="registrationLink" class="mt-4 p-4 bg-[var(--button-hover-lighter)] rounded-lg border border-[var(--border-color)]">
              <h3 class="text-sm font-medium mb-2 text-[var(--text-color)]">Registration Link</h3>
              <div class="flex items-center gap-2">
                <input 
                  type="text" 
                  :value="registrationLink" 
                  readonly 
                  class="flex-1 px-3 py-2 bg-[var(--background)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-color)]"
                />
                <button 
                  @click="copyRegistrationLink(registrationLink)" 
                  class="px-3 py-2 bg-[var(--button-hover)] text-[var(--text-color)] rounded-lg hover:bg-[var(--button-hover-lighter)] transition-colors duration-200"
                >
                  Copy
                </button>
              </div>
              <p class="text-xs text-[var(--secondary-text)] mt-2">
                This link will expire in 48 hours.
              </p>
            </div>
          </div>

          <!-- User List -->
          <div class="mb-8 border border-[var(--border-color)] rounded-lg overflow-hidden">
            <div class="p-4 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
              <h2 class="text-sm font-semibold">User List</h2>
            </div>
            <div class="overflow-auto max-h-[250px] bg-[var(--bg-color)]">
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-[var(--border-color)]">
                    <th class="py-3 px-4 font-medium text-[var(--secondary-text)]">Email</th>
                    <th class="py-3 px-4 font-medium text-[var(--secondary-text)]">Role</th>
                    <th class="py-3 px-4 font-medium text-[var(--secondary-text)]">Created Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id" class="border-b border-[var(--border-color)] hover:bg-[var(--border-color)] hover:bg-opacity-5 transition-colors duration-150">
                    <td class="py-3 px-4">{{ user.email }}</td>
                    <td class="py-3 px-4">{{ user.is_admin ? "Admin" : "User" }}</td>
                    <td class="py-3 px-4">{{ formatDate(user.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Pending Invites -->
          <div class="border border-[var(--border-color)] rounded-lg overflow-hidden">
            <div class="p-4 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
              <h2 class="text-sm font-semibold">Pending Registration Links</h2>
            </div>
            <div class="overflow-auto max-h-[250px] bg-[var(--bg-color)]">
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-[var(--border-color)]">
                    <th class="py-3 px-4 font-medium text-[var(--secondary-text)]">Email</th>
                    <th class="py-3 px-4 font-medium text-[var(--secondary-text)]">Role</th>
                    <th class="py-3 px-4 font-medium text-[var(--secondary-text)]">Registration Link</th>
                    <th class="py-3 px-4 font-medium text-[var(--secondary-text)]">Expires At</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="invite in pendingInvites" :key="invite.id" class="border-b border-[var(--border-color)] hover:bg-[var(--border-color)] hover:bg-opacity-5 transition-colors duration-150">
                    <td class="py-3 px-4">{{ invite.email }}</td>
                    <td class="py-3 px-4">{{ invite.access_role === "admin" ? "Admin" : "User" }}</td>
                    <td class="py-3 px-4">
                      <div class="flex items-center gap-2">
                        <input 
                          type="text" 
                          :value="getRegistrationUrl(invite.token)" 
                          readonly 
                          class="flex-1 px-3 py-1 bg-[var(--background)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-color)]"
                        />
                        <div class="flex flex-col items-end gap-1">
                          <button 
                            @click="copyRegistrationLink(getRegistrationUrl(invite.token))" 
                            class="px-2 py-1 bg-[var(--button-hover)] text-[var(--text-color)] rounded-lg hover:bg-[var(--button-hover-lighter)] transition-colors duration-200 text-xs"
                          >
                            Copy
                          </button>
                          <span v-if="copyMessages[getRegistrationUrl(invite.token)]" class="text-xs text-green-600">
                            {{ copyMessages[getRegistrationUrl(invite.token)] }}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td class="py-3 px-4">{{ formatDate(invite.expires_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- Danger Zone -->
          <div class="mt-12 p-6 border border-red-500 rounded-lg bg-[var(--bg-color)]">
            <h2 class="text-lg font-semibold text-red-600 mb-4">Danger Zone</h2>
            <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h3 class="font-medium text-[var(--text-color)]">Reset System</h3>
                <p class="text-sm text-[var(--secondary-text)] mt-1 max-w-xl">
                  This action will permanently delete all users, chats, messages, invites, keys, and audit logs.
                  The system will be reset to its initial state, requiring a new admin registration.
                  <strong class="text-red-600">This cannot be undone.</strong>
                </p>
              </div>
              <button 
                @click="showResetConfirmModal = true"
                class="py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 cursor-pointer transition-colors duration-200 flex items-center gap-2 text-sm flex-shrink-0"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                Reset System
              </button>
            </div>
            <p v-if="resetError" class="text-red-600 text-sm mt-4">{{ resetError }}</p>
            <p v-if="resetSuccessMessage" class="text-green-600 text-sm mt-4">{{ resetSuccessMessage }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Reset Confirmation Modal -->
    <div v-if="showResetConfirmModal" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div class="bg-[var(--chat-bg)] rounded-lg p-6 max-w-md w-full mx-auto shadow-xl border border-[var(--border-color)]">
        <div class="flex items-center gap-3 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 class="text-lg font-medium text-[var(--text-color)]">Confirm System Reset</h3>
        </div>
        <p class="text-sm text-[var(--secondary-text)] mb-6">
          Are you absolutely sure you want to reset the entire system? 
          <strong class="text-red-500">All data (users, chats, etc.) will be permanently deleted.</strong> 
          This action cannot be undone.
        </p>
        <div class="flex justify-end gap-3">
          <button 
            @click="showResetConfirmModal = false"
            class="px-4 py-2 text-sm font-medium text-[var(--secondary-text)] hover:text-[var(--text-color)] rounded-lg transition-colors duration-200 hover:bg-[var(--button-hover)]"
            :disabled="isResetting"
          >
            Cancel
          </button>
          <button 
            @click="handleResetSystem"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            :disabled="isResetting"
          >
            <svg v-if="isResetting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isResetting ? 'Resetting...' : 'Confirm Reset' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from "../stores/authStore";
import { useSidebarStore } from "../stores/sidebarStore";
import { Wrench } from 'lucide-vue-next';
import { 
  checkAdminAuth,
  validateEmail,
  inviteUser,
  fetchUsers,
  fetchPendingInvites,
  resetSystem,
  generateRegistrationLink,
  type User,
  type Invite,
  type InvitePayload,
  type RegistrationLinkResponse
} from "../services/adminService";
import axios from 'axios';

const email = ref("");
const role = ref("user");
const inviteMessage = ref("");
const emailError = ref("");
const serverError = ref("");
const users = ref<User[]>([]);
const pendingInvites = ref<Invite[]>([]);
const isAuthenticated = ref(false);
const router = useRouter();
const authStore = useAuthStore();
const sidebarStore = useSidebarStore();

// State for Reset functionality
const showResetConfirmModal = ref(false);
const isResetting = ref(false);
const resetError = ref<string | null>(null);
const resetSuccessMessage = ref<string | null>(null);

// New refs for registration link
const regEmail = ref("");
const regRole = ref("user");
const regEmailError = ref("");
const regServerError = ref("");
const regLinkMessage = ref("");
const registrationLink = ref("");
const copyMessages = ref<{ [key: string]: string }>({});

const isAdmin = ref(false);

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

// Validate JWT & Check Authentication
const checkAuth = async () => {
  try {
    isAuthenticated.value = await checkAdminAuth();
    isAdmin.value = authStore.isAdmin;
    
    if (isAuthenticated.value && isAdmin.value) {
      await fetchAllData();
    }
  } catch (error) {
    isAuthenticated.value = false;
    isAdmin.value = false;
    console.error("Admin auth check failed:", error);
  }
};

// Validate Inputs
const validateInputs = () => {
  emailError.value = "";
  serverError.value = "";

  if (!email.value.trim()) {
    emailError.value = "Email is required.";
    return false;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    emailError.value = "Invalid email format.";
    return false;
  }

  return true;
};

const fetchAllData = async () => {
  try {
    users.value = await fetchUsers();
    pendingInvites.value = await fetchPendingInvites();
  } catch (error) {
    console.error("Error fetching data:", error);
    serverError.value = "Failed to load admin data."; // Show error fetching data
  }
};



// Handle System Reset
const handleResetSystem = async () => {
  isResetting.value = true;
  resetError.value = null;
  resetSuccessMessage.value = null;

  try {
    // Call the service function
    const response = await resetSystem(); 
    
    resetSuccessMessage.value = response.message || "System reset successful. Redirecting...";
    showResetConfirmModal.value = false;
    
    // Wait a moment for user to see message, then logout and redirect
    setTimeout(async () => {
      await authStore.logout(); // Ensure this clears cookies/local auth state
      router.push('/start');
    }, 2000);

  } catch (error: any) {
    console.error("System reset failed:", error);
    // Use the error message thrown by the service function
    resetError.value = error.message || "An error occurred during system reset."; 
    showResetConfirmModal.value = false; // Close modal on error too
  } finally {
    isResetting.value = false;
  }
};

// Format Date
const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return 'Invalid Date';
  }
};

const handleGenerateLink = async () => {
  regEmailError.value = "";
  regServerError.value = "";
  regLinkMessage.value = "";
  registrationLink.value = "";

  const emailError = validateEmail(regEmail.value);
  if (emailError) {
    regEmailError.value = emailError;
    return;
  }

  try {
    const response = await generateRegistrationLink(regEmail.value, regRole.value === 'admin');
    registrationLink.value = response.registrationUrl;
    regLinkMessage.value = "Registration link generated successfully";
    regEmail.value = ""; // Clear the email field
    await fetchAllData(); // Refresh the pending invites list
  } catch (error: any) {
    regServerError.value = error.message;
  }
};

const copyRegistrationLink = (url: string) => {
  navigator.clipboard.writeText(url);
  // Show copy message in the appropriate section
  if (url === registrationLink.value) {
    regLinkMessage.value = "Link copied to clipboard";
    setTimeout(() => {
      regLinkMessage.value = "";
    }, 2000);
  } else {
    // For pending invites section
    copyMessages.value[url] = "Link copied to clipboard";
    setTimeout(() => {
      delete copyMessages.value[url];
    }, 2000);
  }
};

const getRegistrationUrl = (token: string): string => {
  const baseUrl = window.location.origin;
  return `${baseUrl}/register?token=${token}`;
};

onMounted(checkAuth);
</script>
