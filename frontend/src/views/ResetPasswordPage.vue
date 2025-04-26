<template>
  <div class="flex h-screen items-center justify-center bg-[var(--background)]">
    <div class="w-full max-w-md bg-[var(--chat-bg)] p-8 rounded-2xl shadow-lg mx-4">
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
      
      <h2 class="text-xl font-medium mb-4 text-center text-[var(--text-color)]">
        Reset Your Password
      </h2>

      <p class="text-center text-[var(--secondary-text)] mb-8 px-4 text-sm leading-relaxed">
        Enter your email address below and we will send you a link to reset your password.
      </p>

      <form @submit.prevent="resetPassword" class="space-y-5">
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

        <button
          type="submit"
          class="w-full py-3 px-4 bg-[#55B867] text-white rounded-xl hover:bg-[#4da45b] transition-colors duration-200 font-medium shadow-sm mt-6 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Sending...
          </span>
          <span v-else>Reset Password</span>
        </button>

        <!-- Back to Login Link -->
        <div class="text-center mt-4">
          <a href="/login" class="text-sm text-[var(--secondary-text)] hover:text-[var(--text-color)] transition-colors duration-200 cursor-pointer">
            Back to Login
          </a>
        </div>
      </form>

      <!-- Success/Error Message -->
      <div 
        v-if="message" 
        class="mt-6 text-center p-4 bg-[var(--sidebar-bg)] rounded-xl text-[var(--text-color)] border border-[var(--border-color)]"
      >
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from '../composables/index'
import { requestPasswordReset } from '../services/userService'

const email = ref('')
const message = ref('')
const isLoading = ref(false)

const resetPassword = async () => {
  if (!email.value) {
    message.value = "Please enter a valid email address."
    return
  }

  isLoading.value = true
  message.value = ''

  try {
    const response = await requestPasswordReset(email.value)
    message.value = response.message
  } catch (error) {
    console.error("Reset password error:", error)
    message.value = "Failed to send reset link. Please try again."
  } finally {
    isLoading.value = false
  }
}
</script>