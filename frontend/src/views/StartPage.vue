<template>
  <div class="flex h-screen items-center justify-center bg-[var(--background)]">
    <!-- Main content area -->
    <div class="w-full max-w-md bg-[var(--chat-bg)] p-6 pt-2 rounded-2xl shadow-lg mx-4 -mt-6">
      <!-- Logo and Header -->
      <div class="flex items-center justify-center mb-3 gap-1">
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

      <h2 class="text-lg font-medium mb-4 text-center text-[var(--text-color)]">System Setup</h2>
      
      <div class="text-center mb-4 text-[var(--secondary-text)]">
        <p>Welcome to your secure communication platform.</p>
        <p class="mt-1">Let's set up your administrator account to get started.</p>
      </div>

      <!-- Initial Email Form -->
      <form v-if="!inviteSent && !showConfirmation" @submit.prevent="confirmEmail" class="space-y-5">
        <div>
          <label for="email" class="block text-sm font-medium mb-2 text-[var(--text-color)]">Admin Email</label>
          <div class="relative">
            <input
              type="email"
              id="email"
              v-model="email"
              required
              class="w-full px-4 py-3 rounded-lg border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:ring-1 focus:ring-[#55B867] transition-shadow duration-200 pr-10"
              placeholder="Enter your email address"
            />
            <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--secondary-text)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect width="20" height="16" x="2" y="4" rx="2"/>
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
              </svg>
            </div>
          </div>
          <p class="text-xs text-[var(--secondary-text)] mt-1">
            A secure registration link will be sent to this address.
          </p>
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-3 px-4 bg-[#55B867] text-white rounded-lg hover:bg-[#4da45b] transition-colors duration-200 font-medium shadow-sm mt-6 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer"
        >
          <span v-if="isLoading" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </span>
          <span v-else class="flex items-center">
            Continue
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ml-2">
              <path d="M5 12h14"/>
              <path d="m12 5 7 7-7 7"/>
            </svg>
          </span>
        </button>
      </form>

      <!-- Email Confirmation Dialog -->
      <div v-if="showConfirmation && !inviteSent" class="space-y-5">
        <div class="bg-[var(--button-hover-lighter)] p-4 rounded-lg border border-[var(--border-color)]">
          <h3 class="font-medium text-[var(--text-color)] mb-3">Confirm Email Address</h3>
          <p class="text-[var(--secondary-text)] mb-4">We'll send an invitation link to:</p>
          <div class="px-3 py-2 bg-[var(--background)] rounded-md border border-[var(--border-color)] text-[var(--text-color)] flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
              <path d="M22 10.5c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v7c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2v-7Z"/>
              <path d="m22 10.5-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 10.5"/>
              <path d="M2 10.5V6c0-1.1.9-2 2-2h16c1.1 0 2 .9 2 2v4.5"/>
            </svg>
            <span class="font-medium">{{ email }}</span>
          </div>
          <p class="text-xs text-[var(--secondary-text)] mt-3">
            Please verify this email address is correct and accessible to you.
          </p>
        </div>
        
        <div class="flex gap-3">
          <button 
            @click="showConfirmation = false"
            class="flex-1 py-3 px-4 bg-[var(--button-hover)] text-[var(--text-color)] rounded-lg hover:bg-[var(--button-hover-lighter)] transition-colors duration-200 font-medium cursor-pointer"
          >
            Edit Email
          </button>
          <button 
            @click="createFirstUserInvite"
            :disabled="isLoading"
            class="flex-1 py-3 px-4 bg-[#55B867] text-white rounded-lg hover:bg-[#4da45b] transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <span v-if="isLoading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            </span>
            <span v-else>Send Invite</span>
          </button>
        </div>
      </div>

      <!-- Success screen after invite sent -->
      <div v-if="inviteSent" class="space-y-4">
        <div class="flex items-center justify-center">
          <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
        </div>
        
        <h3 class="text-lg font-medium text-center text-[var(--text-color)]">Invitation Sent</h3>
        
        <div class="bg-[var(--button-hover-lighter)] p-4 rounded-lg border border-[var(--border-color)]">
          <p class="text-[var(--secondary-text)]">Check your email at <strong class="text-[var(--text-color)]">{{ email }}</strong> to complete registration.</p>
        </div>
      </div>

      <!-- Error Message Display with TypeScript Fix -->
      <div 
        v-if="errorMessage" 
        class="mt-4 p-4 bg-red-100 text-red-700 rounded-lg border border-red-300 flex items-start"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-3 mt-0.5 text-red-600">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" x2="12" y1="8" y2="12"/>
          <line x1="12" x2="12.01" y1="16" y2="16"/>
        </svg>
        <div>
          <p class="font-medium">{{ getErrorTitle }}</p>
          <p class="mt-1">{{ errorMessage }}</p>
          <div v-if="isSystemInitialized" class="mt-3 pt-3 border-t border-red-200">
            <p>The system has already been initialized. Please:</p>
            <ul class="list-disc ml-5 mt-2 text-sm">
              <li>Contact an existing administrator for an invitation</li>
              <li>Use the login page if you already have an account</li>
            </ul>
            <button 
              @click="goToLogin" 
              class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 cursor-pointer"
            >
              Go to Login
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { firstUserService } from '../services/firstUserService';

const router = useRouter();
const email = ref("");
const errorMessage = ref<string | null>(null);
const isLoading = ref(false);
const inviteSent = ref(false);
const showConfirmation = ref(false);
const isSystemInitialized = ref(false);

// Fixed the TypeScript error by using a computed property instead
const getErrorTitle = computed(() => {
  if (errorMessage.value && errorMessage.value.includes("Cannot create invite: users or invites already exist")) {
    return "System Already Initialized";
  }
  return "Error";
});

// Step 1: Show confirmation dialog
const confirmEmail = () => {
  if (!email.value || !email.value.includes('@')) {
    errorMessage.value = "Please enter a valid email address";
    return;
  }
  
  errorMessage.value = null;
  showConfirmation.value = true;
};

// Step 2: Create invite after confirmation
const createFirstUserInvite = async () => {
  isLoading.value = true;
  errorMessage.value = null;
  
  try {
    console.log("Creating first user invite for email:", email.value);
    const response = await firstUserService.createFirstUserInvite(email.value);
    
    console.log('Invite created:', response);
    showConfirmation.value = false;
    inviteSent.value = true;
  } catch (error: any) {
    console.error('Error creating invite:', error);
    errorMessage.value = error.response?.data?.detail || "Failed to create invitation. Please try again.";
    
    // Check if the error indicates the system is already initialized
    if (errorMessage.value && errorMessage.value.includes("Cannot create invite: users or invites already exist")) {
      isSystemInitialized.value = true;
    }
  } finally {
    isLoading.value = false;
  }
};

// Navigate to login page
const goToLogin = () => {
  router.push('/login');
};

// Reset form to try with a different email
const resetForm = () => {
  email.value = "";
  errorMessage.value = null;
  inviteSent.value = false;
  showConfirmation.value = false;
  isSystemInitialized.value = false;
};
</script>