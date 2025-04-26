<template>
  <div v-if="authStore.isLoading" class="flex h-screen justify-center items-center">
    <p>Loading...</p>
  </div>

  <div v-else class="flex h-screen overflow-hidden">
    <Sidebar 
      v-if="showSidebar" 
      :is-collapsed="sidebarStore.isCollapsed" 
      :is-admin="authStore.isAdmin"
      @toggle="sidebarStore.toggleSidebar"
    />
    <router-view class="flex-1 min-w-0" />
  </div>
</template>

<script setup lang="ts">

import { computed, onMounted, watch, useRoute, useRouter, nextTick } from '@/composables'

import Sidebar from "./components/Sidebar.vue";
import { useAuthStore } from "./stores/authStore";
import { useSidebarStore } from "./stores/sidebarStore";
import { config } from './config';
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const sidebarStore = useSidebarStore(); // ✅ Use the store

const showSidebar = computed(() => !route.meta.hideSidebar && authStore.isAuthenticated);
const publicRoutes = ["Login", "Register", "ResetPasswordPage"];

onMounted(async () => {

  //console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
  //console.log('config.apiUrl:', config.apiUrl);

  await nextTick();
  // Check if route is available
  if (route.name) {
    await checkAuthAndRedirect();
  }
});

watch(
  () => route.fullPath,
  async () => {
    await checkAuthAndRedirect();
  }
);

async function checkAuthAndRedirect(toRoute = route) {

  /*if (!publicRoutes.includes(String(toRoute.name))) {

    await authStore.checkAuth();
    if (!authStore.isAuthenticated) {
      router.push("/login");
    }
  } else {
    authStore.isLoading = false;
  }*/
}


</script>
