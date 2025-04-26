<template>
  <div class="flex h-screen items-center justify-center bg-[var(--background)]">
    <div class="w-full max-w-md bg-[var(--chat-bg)] p-8 rounded-2xl shadow-lg mx-4 relative">
      <!-- Loading overlay -->
      <div v-if="isCheckingFirstUser" class="absolute inset-0 flex items-center justify-center bg-[var(--chat-bg)] bg-opacity-70 rounded-2xl z-10">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--text-color)]"></div>
          <p class="mt-3 text-[var(--text-color)]">Checking system status...</p>
        </div>
      </div>

      <!-- Header with New Logo -->
      <div class="flex items-center justify-center mb-8 gap-1">
         <div class="p-1 rounded-lg flex items-center justify-center" style="width: 32px; height: 32px;">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-color)" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
                <polyline points="7.5 19.79 7.5 14.6 3 12"/>
                <polyline points="21 12 16.5 14.6 16.5 19.79"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
            </div>
        <h1 class="font-space-grotesk tracking-wider text-2xl font-semibold text-[var(--text-color)]">Innerlink</h1>
      </div>

      <h2 class="text-xl font-medium mb-6 text-center text-[var(--text-color)]">Login</h2>

      <form @submit.prevent="login" class="space-y-5">
        <div>
          <label for="email" class="block text-sm font-medium mb-2 text-[var(--text-color)]">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            required
            class="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-[#55B867] transition-shadow duration-200"
            placeholder="Enter your email"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium mb-2 text-[var(--text-color)]">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            autocomplete="current-password"
            class="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-[#55B867] transition-shadow duration-200"
            placeholder="Enter your password"
          />
        </div>

        <button
          type="submit"
          :disabled="isCheckingFirstUser"
          class="w-full py-3 px-4 bg-[#55B867] text-white rounded-xl hover:bg-[#4da45b] transition-colors duration-200 font-medium shadow-sm mt-6 disabled:opacity-50 cursor-pointer"
        >
          Login
        </button>

        <!-- Forgot Password Link -->
        <div class="text-center mt-4">
          <router-link to="/resetpassword" class="text-sm text-[var(--secondary-text)] hover:text-[var(--text-color)] transition-colors duration-200 cursor-pointer">
            Forgot your password?
          </router-link>
        </div>
      </form>
      
      <div 
        v-if="errorMessage" 
        class="absolute bottom-0 left-0 right-0 p-4 bg-red-100 text-red-600 text-center rounded-b-2xl border-t border-red-200"
      >
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "../stores/authStore";
import { useRouter, ref, onMounted } from '@/composables';
import { firstUserService } from '../services/firstUserService';

const router = useRouter();
const email = ref("");
const password = ref("");
const errorMessage = ref<string | null>(null);
const authStore = useAuthStore();
const isCheckingFirstUser = ref(true);

// Check if this is the first user setup when the component loads
onMounted(async () => {
  isCheckingFirstUser.value = true;
  try {
    const response = await firstUserService.checkFirstUser();
    console.log('First user check response:', response);
    
    // If this is the first user setup, redirect to the start page
    if (response.is_first_user) {
      router.push('/start');
    }
  } catch (error) {
    console.error('Error checking first user:', error);
    // Continue with normal login flow on error
  } finally {
    isCheckingFirstUser.value = false;
  }
});

const login = async () => {
  try {
    errorMessage.value = null; // Clear any previous errors
    await authStore.login(email.value, password.value);
    router.push("/"); 
  } catch (error: any) {
    console.error("Login failed:", error);
    errorMessage.value = error.response?.data?.detail || "Invalid email or password";
  }
};
</script>