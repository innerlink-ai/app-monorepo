<template>
  <div class="flex h-screen items-center justify-center bg-[var(--background)]">
    <div class="w-full max-w-md bg-[var(--chat-bg)] p-6 pt-2 rounded-2xl shadow-lg mx-4 -mt-6">
      <!-- Show success message OR main content -->
      <div v-if="registrationSuccess">
        <!-- Header with New Logo (Success State) -->
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
        
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl text-center">
          <p class="font-medium">Registration Successful!</p>
          <p class="text-sm mt-1">Redirecting you to the dashboard...</p>
        </div>
        
        <div class="flex justify-center mt-4">
          <div class="animate-spin h-6 w-6 border-4 border-[#55B867] border-t-transparent rounded-full"></div>
        </div>
      </div>

      <div v-else>
        <!-- Header with New Logo (Form State) -->
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

        <!-- Error Message (Invalid Invite) -->
        <div v-if="inviteError" class="mb-4 text-red-500 text-center">
          {{ inviteError }}
        </div>

        <h2 v-else class="text-xl font-medium mb-4 text-center text-[var(--text-color)]">
          {{ isAdmin ? "Admin Registration" : "User Registration" }}
        </h2>

        <!-- Registration Form -->
        <form v-if="!inviteError" @submit.prevent="registerUser" class="space-y-5">
        <!-- Full Name Field -->
        <div>
          <label for="fullName" class="block text-sm font-medium mb-2 text-[var(--text-color)]">Your Name</label>
          <input
            type="text"
            id="fullName"
            v-model="fullName"
            required
            class="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-[#55B867] transition-shadow duration-200"
            placeholder="Enter your full name"
          />
        </div>

        <!-- Email Field -->
        <div>
          <label for="email" class="block text-sm font-medium mb-2 text-[var(--text-color)]">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            required
            readonly
            class="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--sidebar-bg)] text-[var(--text-color)] opacity-90 focus:outline-none transition-shadow duration-200"
          />
        </div>

        <!-- Password Field -->
        <div>
          <label for="password" class="block text-sm font-medium mb-2 text-[var(--text-color)]">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            autocomplete="new-password"
            pattern="(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^])[A-Za-z\d@$!%*?&#^]{12,}"
            class="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-[#55B867] transition-shadow duration-200"
            placeholder="Create a strong password"
          />
          <p class="mt-2 text-xs text-[var(--secondary-text)]">
            Password must be at least 12 characters with uppercase, lowercase, number, and special character.
          </p>
        </div>

        <!-- Error Message (User Already Exists) -->
        <div v-if="errors.general" class="text-red-500 text-sm text-center">
          {{ errors.general }}
          <div class="mt-2">
            <router-link to="/login" class="text-blue-500 underline cursor-pointer">Login</router-link>
            or
            <router-link to="/resetpassword" class="text-blue-500 underline cursor-pointer">Reset Password</router-link>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="w-full py-3 px-4 bg-[#55B867] text-white rounded-xl hover:bg-[#4da45b] transition-colors duration-200 font-medium shadow-sm mt-6 cursor-pointer"
        >
          {{ isAdmin ? "Complete Admin Registration" : "Register" }}
        </button>
      </form>
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">


import { useAuthStore } from "../stores/authStore";
import { verifyInvite, register } from "../services/userService"
import { ref, onMounted, useRoute, useRouter } from '../composables/index'
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const fullName = ref("");
const email = ref("");
const password = ref("");
const isAdmin = ref(false);
const inviteToken = ref<string | null>(null);
const inviteError = ref<string | null>(null);
const errors = ref<{ general: string | null }>({ general: null });
const registrationSuccess = ref(false);
onMounted(async () => {
  const token = route.query.token as string | undefined;

  if (!token) {
    inviteError.value = "You must be invited to register.";
    return;
  }

  inviteToken.value = token;
  await fetchInviteDetails(token);

});

const fetchInviteDetails = async (token: string) => {
  try {
    const inviteDetails = await verifyInvite(token);
    if (inviteDetails.email) {
      email.value = inviteDetails.email;
      isAdmin.value = inviteDetails.access_role === "admin";
    }
  } catch (error) {
    console.error("Error fetching invite details:", error);
    inviteError.value = "Invalid or expired invite. Please request a new one.";
  }


};

// Update your registerUser function
const registerUser = async () => {
  if (!fullName.value || !email.value || !password.value) {
    errors.value.general = "Please fill out all fields.";
    return;
  }

  try {
    await register({
      full_name: fullName.value,
      email: email.value,
      password: password.value,
      token: inviteToken.value,
    });
    
    // Update authentication state
    await authStore.checkAuth();
    
    // Show success message
    registrationSuccess.value = true;
    
    // Set timeout for redirect
    setTimeout(() => {
      router.push("/");
    }, 2000); // 2 second delay before redirect

  } catch (error: any) {
    console.error("Error registering:", error);
    
    if (error.response?.data?.detail === "User with this email already exists.") {
      errors.value.general = "An account with this email already exists.";
    } else {
      errors.value.general = "Registration failed. Please try again.";
    }
  }
};
</script>
