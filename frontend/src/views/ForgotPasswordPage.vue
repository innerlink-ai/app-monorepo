<!-- src/views/ForgotPassword.vue -->
<template>
    <div class="flex h-screen items-center justify-center bg-gray-50">
      <div class="w-full max-w-md bg-white p-8 rounded-lg shadow">
        <!-- Header -->
        <div class="flex items-center justify-center mb-6">
          <h1 class="text-2xl font-semibold text-black">Reset Your Password</h1>
        </div>
        <!-- Instruction Text -->
        <p class="text-center text-black mb-6">
          Enter your email address below and we will send you a link to reset your password.
        </p>
        <!-- Forgot Password Form -->
        <form @submit.prevent="resetPassword">
          <div class="mb-4">
            <label for="email" class="block text-sm font-medium mb-1 text-black">
              Email
            </label>
            <input
              type="email"
              id="email"
              v-model="email"
              required
              class="w-full border px-3 py-2 rounded focus:outline-none focus:ring focus:border-blue-300 text-black"
            />
          </div>
          <button
            type="submit"
            class="w-full py-2 bg-[#55B867] text-white rounded hover:bg-[#4da45b] transition-colors"
          >
            Reset Password
          </button>
        </form>
        <div v-if="message" class="mt-4 text-center text-black">
          {{ message }}
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">

  import { ref } from '../composables/index'
  const email = ref('')
  const message = ref('')
  
  const resetPassword = async () => {
    if (email.value) {
      // Dummy logic: In a real application, you'd send a request to your backend.
      console.log("Password reset requested for:", email.value)
      // The backend would generate a secure, one-time-use token (with a short expiration)
      // and send an email containing a reset link to the provided address.
      message.value = "If this email is registered, a reset link has been sent. Please check your inbox."
    } else {
      alert("Please enter a valid email address.")
    }
  }
  </script>
  
  <style scoped>
  /* Additional styling if needed */
  </style>
  