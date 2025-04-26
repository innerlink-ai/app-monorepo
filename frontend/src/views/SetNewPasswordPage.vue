<template>
  <div class="flex h-screen items-center justify-center bg-[var(--background)]">
    <div class="w-full max-w-md bg-[var(--chat-bg)] p-8 rounded-2xl shadow-lg mx-4">
      <!-- Header -->
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
      
      <h2 class="text-xl font-medium mb-6 text-center text-[var(--text-color)]">
        Set New Password
      </h2>

      <!-- Loading or Error State -->
      <div v-if="loadingToken || tokenError" class="text-center p-4 bg-[var(--sidebar-bg)] rounded-xl text-[var(--text-color)] border border-[var(--border-color)]">
        <p v-if="loadingToken">Verifying token...</p>
        <p v-if="tokenError" class="text-red-500">{{ tokenError }}</p>
        <router-link v-if="tokenError" to="/resetpassword" class="text-blue-500 underline mt-2 inline-block">Request a new link</router-link>
      </div>

      <!-- Password Form -->
      <form v-else @submit.prevent="setNewPassword" class="space-y-5">
        <div>
          <label for="newPassword" class="block text-sm font-medium mb-2 text-[var(--text-color)]">New Password</label>
          <input
            type="password"
            id="newPassword"
            v-model="newPassword"
            required
            autocomplete="new-password"
            class="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-[#55B867] transition-shadow duration-200"
            placeholder="Enter your new password"
            @input="validatePassword"
          />
           <p class="mt-2 text-xs text-[var(--secondary-text)]">
            Password must be at least 12 characters with uppercase, lowercase, number, and special character.
          </p>
        </div>

        <div>
          <label for="confirmPassword" class="block text-sm font-medium mb-2 text-[var(--text-color)]">Confirm New Password</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            required
            autocomplete="new-password"
            class="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-[#55B867] transition-shadow duration-200"
            placeholder="Confirm your new password"
            @input="validatePassword"
          />
        </div>
        
        <!-- Password Mismatch Error -->
        <div v-if="passwordMismatch" class="text-red-500 text-sm">
          Passwords do not match.
        </div>
        <!-- Password Strength Error -->
        <div v-if="passwordStrengthError" class="text-red-500 text-sm">
          Password does not meet complexity requirements.
        </div>

        <button
          type="submit"
          class="w-full py-3 px-4 bg-[#55B867] text-white rounded-xl hover:bg-[#4da45b] transition-colors duration-200 font-medium shadow-sm mt-6 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isLoading || passwordMismatch || passwordStrengthError || !newPassword || !confirmPassword"
        >
           <span v-if="isLoading" class="flex items-center justify-center">
             <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
               <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
               <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
             </svg>
             Setting Password...
           </span>
           <span v-else>Set New Password</span>
        </button>

        <!-- General Error/Success Message -->
        <div 
          v-if="message" 
          :class="[
            'mt-6 text-center p-4 rounded-xl border',
            isError ? 'bg-red-100 border-red-300 text-red-700' : 'bg-green-100 border-green-300 text-green-700'
          ]"
        >
          {{ message }}
          <router-link v-if="isSuccess" to="/login" class="text-blue-500 underline ml-1">Login Now</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { resetPassword, checkPasswordStrength } from '../services/userService'; // Assuming checkPasswordStrength is exported

const route = useRoute();
const router = useRouter();

const token = ref<string | null>(null);
const newPassword = ref('');
const confirmPassword = ref('');
const message = ref('');
const isError = ref(false);
const isSuccess = ref(false);
const isLoading = ref(false);
const loadingToken = ref(true); // State to check token validity initially
const tokenError = ref<string | null>(null);

const passwordMismatch = ref(false);
const passwordStrengthError = ref(false);

onMounted(() => {
  const queryToken = route.query.token;
  if (typeof queryToken === 'string') {
    token.value = queryToken;
    // Optional: Add a quick backend check here to see if the token is initially valid/not expired
    // This prevents showing the form for an immediately invalid token.
    // For now, we assume it might be valid and let the final submission check.
    loadingToken.value = false; 
  } else {
    tokenError.value = 'Invalid or missing password reset token.';
    loadingToken.value = false;
  }
});

const validatePassword = () => {
  passwordMismatch.value = newPassword.value !== '' && confirmPassword.value !== '' && newPassword.value !== confirmPassword.value;
  
  // Check strength (assuming checkPasswordStrength returns a score >= 3 for valid)
  if (newPassword.value) {
    const strength = checkPasswordStrength(newPassword.value);
    passwordStrengthError.value = strength < 3; 
  } else {
    passwordStrengthError.value = false;
  }
};

const setNewPassword = async () => {
  message.value = '';
  isError.value = false;
  isSuccess.value = false;
  validatePassword(); // Re-validate before submit

  if (passwordMismatch.value || passwordStrengthError.value || !token.value) {
    return; // Prevent submission if basic validation fails
  }

  isLoading.value = true;
  try {
    const response = await resetPassword({
      token: token.value,
      new_password: newPassword.value,
    });
    message.value = response.message;
    isSuccess.value = true;
    
    // Show success message for a short duration before redirecting
    setTimeout(() => {
      router.push('/login');
    }, 2000); // Delay for 2 seconds (2000 milliseconds)
    
    // Optionally clear fields (less relevant now as we navigate away)
    // newPassword.value = '';
  } catch (error) {
    message.value = error instanceof Error ? error.message : "Failed to reset password. The link may be invalid or expired.";
    isError.value = true;
    console.error("Set new password error:", error);
  } finally {
    isLoading.value = false;
  }
};
</script> 