<template>
  <aside :class="sidebarClasses">
    <!-- Main container with flex to push footer to bottom -->
    <div class="flex flex-col h-full">
      <!-- Header Section - Fixed at top -->
      <div class="flex items-center justify-between h-12 px-4 border-b border-[var(--border-color)] bg-[var(--sidebar-bg)]">
        <div v-if="!isCollapsed" class="flex items-center">
          <!-- Logo -->
          <button @click="startNewChat" class="flex items-center gap-1 transition-colors duration-200 rounded-md cursor-pointer">
            <div class="p-1 rounded-lg flex items-center justify-center" style="width: 32px; height: 32px;">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-color)" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
                <polyline points="7.5 19.79 7.5 14.6 3 12"/>
                <polyline points="21 12 16.5 14.6 16.5 19.79"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
            </div>
            <h1 class="font-space-grotesk tracking-wider text-lg">
              Innerlink
            </h1>
          </button>
        </div>
        <button @click="toggleSidebar" class="p-1.5 rounded-md hover:bg-[var(--button-hover)] transition-colors duration-200 focus:outline-none cursor-pointer">
          <component :is="isCollapsed ? ChevronRightIcon : ChevronLeftIcon" class="w-4 h-4" />
        </button>
      </div>

      <!-- Navigation Buttons - Fixed below header -->
      <div class="px-2 mt-2">
        <div class="flex flex-col gap-1">
          <!-- New Chat Button -->
          <button
            @click="startNewChat"
            :class="[
              'flex items-center hover:bg-[var(--button-hover)] transition-all duration-200 cursor-pointer rounded-md',
              isCollapsed 
                ? 'p-2 mx-auto justify-center' 
                : 'px-3 py-2 gap-2 w-[calc(100%-8px)]'
            ]"
          >
            <SquarePen class="w-5 h-5 stroke-[1]" />
            <span v-if="!isCollapsed" class="text-sm font-light">New Chat</span>
          </button>

          <!-- Chats Button -->
          <button
            @click="goToHistory"
            :class="[
              'flex items-center hover:bg-[var(--button-hover)] transition-all duration-200 cursor-pointer rounded-md',
              isCollapsed 
                ? 'p-2 mx-auto justify-center' 
                : 'px-3 py-2 gap-2 w-[calc(100%-8px)]'
            ]"
          >
            <MessagesSquare class="w-5 h-5 stroke-[1]" />
            <span v-if="!isCollapsed" class="text-sm font-light">Chats</span>
          </button>

          <!-- Projects Button 
          <button
            @click="openProjects"
            :class="[
              'flex items-center hover:bg-[var(--button-hover)] transition-all duration-200 cursor-pointer rounded-md',
              isCollapsed 
                ? 'p-2 mx-auto justify-center' 
                : 'px-3 py-2 gap-2 w-[calc(100%-8px)]'
            ]"
          >
            <Layers class="w-5 h-5 stroke-[1]" />
            <span v-if="!isCollapsed" class="text-sm font-light">Projects</span>
          </button>-->
        </div>
      </div>

      <!-- Scrollable History Section -->
      <div class="flex-1 overflow-y-auto mt-2 custom-scrollbar">
        <!-- Recents Section -->
        <div v-if="!isCollapsed" class="border-t border-[var(--border-color)] px-2">
          <div class="px-3 mb-2 pt-2">
            <h2 class="text-xs font-medium tracking-wider text-[var(--secondary-text)]">Recents</h2>
          </div>
          <ul class="space-y-0.5">
            <li
              v-for="chat in chatStore.recentChats"
              :key="chat.chat_id"
              @click="navigateToChat(chat.chat_id)"
              @keydown.enter="navigateToChat(chat.chat_id)"
              class="cursor-pointer w-full text-sm py-1.5 px-3 hover:bg-[var(--button-hover)] active:bg-[var(--button-active)] rounded-md transition-colors duration-200 truncate flex items-center"
              tabindex="0"
              role="button"
              :aria-label="`Open chat: ${chat.name}`"
            >
              <span class="truncate">{{ chat.name }}</span>
            </li>
          </ul>
          <div v-if="chatStore.recentChats.length === 0" class="text-xs text-center py-2 text-[var(--secondary-text)]">
            No recent chats
          </div>
          <div class="text-center mt-2 mb-3">
            <button 
              @click="goToHistory" 
              class="text-xs text-[var(--primary-color)] hover:underline py-1"
              aria-label="View all chats"
            >
              View all
            </button>
          </div>
        </div>

        <!-- Chat History (conditionally shown) -->
        <div v-if="!isCollapsed && showHistory" class="py-4 px-2">
          <h2 class="text-xs font-medium tracking-wider text-[var(--secondary-text)] mb-1 px-2 py-1">Today</h2>
          <ul class="space-y-0.5">
            <li
              v-for="(chat, index) in todayChats"
              :key="'today-' + index"
              @click="selectChat(chat.name)"
              class="cursor-pointer w-full text-sm py-1.5 px-2 hover:bg-[var(--button-hover)] rounded-md transition-colors duration-200 truncate"
            >
              {{ chat.name }}
            </li>
          </ul>

          <h2 class="text-xs font-medium tracking-wider text-[var(--secondary-text)] mb-1 px-2 py-1 mt-4">
            Yesterday
          </h2>
          <ul class="space-y-0.5">
            <li
              v-for="(chat, index) in yesterdayChats"
              :key="'yesterday-' + index"
              @click="selectChat(chat.name)"
              class="cursor-pointer w-full text-sm py-1.5 px-2 hover:bg-[var(--button-hover)] rounded-md transition-colors duration-200 truncate"
            >
              {{ chat.name }}
            </li>
          </ul>

          <h2 class="text-xs font-medium tracking-wider text-[var(--secondary-text)] mb-1 px-2 py-1 mt-4">
            Previous 7 Days
          </h2>
          <ul class="space-y-0.5">
            <li
              v-for="(chat, index) in previous7Chats"
              :key="'previous7-' + index"
              @click="selectChat(chat.name)"
              class="cursor-pointer w-full text-sm py-1.5 px-2 hover:bg-[var(--button-hover)] rounded-md transition-colors duration-200 truncate"
            >
              {{ chat.name }}
            </li>
          </ul>

          <h2 class="text-xs font-medium tracking-wider text-[var(--secondary-text)] mb-1 px-2 py-1 mt-4">
            Previous 30 Days
          </h2>
          <ul class="space-y-0.5">
            <li
              v-for="(chat, index) in previous30Chats"
              :key="'previous30-' + index"
              @click="selectChat(chat.name)"
              class="cursor-pointer w-full text-sm py-1.5 px-2 hover:bg-[var(--button-hover)] rounded-md transition-colors duration-200 truncate"
            >
              {{ chat.name }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Footer: Admin & Profile Buttons - Fixed at bottom -->
      <div class="border-t border-[var(--border-color)] p-2 flex flex-col gap-1 relative">
        <!-- Settings Button (renamed from Profile) -->
        <button
          ref="settingsButtonRef"
          @click.stop="toggleDropup"
          :class="[
            'flex items-center hover:bg-[var(--button-hover)] transition-all duration-200 cursor-pointer rounded-md',
            isCollapsed ? 'p-2 mx-auto justify-center' : 'px-3 py-2 gap-2'
          ]"
        >
          <Settings class="w-5 h-5 stroke-[1]" />
          <span v-if="!isCollapsed" class="text-sm font-light">Account</span>
        </button>
      </div>
    </div>
  </aside>

  <!-- Account Menu Overlay - Completely separate from sidebar -->
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="dropUpVisible" class="fixed inset-0 bg-transparent z-[999998]" @click="dropUpVisible = false">
      <!-- This transparent overlay covers the entire screen to capture clicks outside the dropdown -->
    </div>
  </Transition>

  <!-- Account Menu Dropdown - Positioned relative to viewport -->
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="transform scale-95 opacity-0"
    enter-to-class="transform scale-100 opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="transform scale-100 opacity-100"
    leave-to-class="transform scale-95 opacity-0"
  >
    <div
      v-if="dropUpVisible"
      ref="profileRef"
      @click.stop
      class="fixed bg-[var(--dropdown-bg)] w-56 p-2 rounded-lg shadow-2xl text-sm flex flex-col gap-1 z-[999999] border border-[var(--border-color)]"
      :style="dropdownPosition"
    >
      <button @click="toggleTheme" class="w-full text-left hover:bg-[var(--button-hover)] transition-colors duration-200 px-3 py-2 cursor-pointer rounded-md">
        🎨 {{ isDarkMode ? "Light Mode" : "Dark Mode" }}
      </button>
      <button @click="openSettings" class="w-full text-left hover:bg-[var(--button-hover)] transition-colors duration-200 px-3 py-2 cursor-pointer rounded-md">
        ⚙️ User Settings
      </button>
      <button 
        v-if="isAdmin" 
        @click="goToAdminConsole" 
        class="w-full text-left hover:bg-[var(--button-hover)] transition-colors duration-200 px-3 py-2 cursor-pointer rounded-md"
      >
        🔧 Admin Console
      </button>
      <button @click="logOut" class="w-full text-left hover:bg-[var(--button-hover)] transition-colors duration-200 px-3 py-2 cursor-pointer rounded-md">
        🚪 Log Out
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { logout } from '../services/authService';

import { ref, computed, onMounted, onBeforeUnmount, useRouter, useRoute, ChevronLeft, ChevronRight, MessageCircle, Wrench } from '../composables/index'
import { DatabaseZap, Blocks, MessagesSquare, MessageSquarePlus, Layers, History, Settings, SquarePen } from 'lucide-vue-next';
import { useChatStore } from '../stores/chatStore';
import { useAuthStore } from '../stores/authStore';

// Define a Chat interface
interface Chat {
  chat_id: string;
  name: string;
  message_count: number;
  updated_at: string;
  preview?: string;
}

const props = defineProps({
  isCollapsed: {
    type: Boolean,
    default: false
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["toggle"]);
const router = useRouter();
const route = useRoute();
const isCollapsed = computed(() => props.isCollapsed);

// State variables
const dropUpVisible = ref(false);
const isDarkMode = ref(true); // Always start with dark mode
const profileRef = ref<HTMLElement | null>(null);
const showHistory = ref(false);
const settingsButtonRef = ref<HTMLElement | null>(null);
const dropdownPosition = ref<{
  top?: string;
  bottom?: string;
  left: string;
}>({
  top: '0px',
  left: '0px'
});

// Dummy chat data
const todayChats = ref([
  { name: "AI Model Updates" }, 
  { name: "Customer Feedback" }
]);

const yesterdayChats = ref([
  { name: "Meeting follow-up" }, 
  { name: "Customer Support" }
]);

const previous7Chats = ref([
  { name: "Weekly roundup" }, 
  { name: "Performance feedback" }
]);

const previous30Chats = ref([
  { name: "Marketing strategy" }, 
  { name: "End-of-month recap" }, 
  { name: "End-of-month recap" }, 
]);

// Use the chat store
const chatStore = useChatStore();

// Methods
const toggleSidebar = () => emit("toggle");

const toggleDropup = () => {
  dropUpVisible.value = !dropUpVisible.value;
  
  if (dropUpVisible.value) {
    updateDropdownPosition();
  }
};

const toggleHistory = () => {
  showHistory.value = !showHistory.value;
};

const openCollections = () => {
  router.push("/collections");
};

const openProjects = () => {
  router.push("/projects");
};

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (
    dropUpVisible.value && 
    profileRef.value && 
    !profileRef.value.contains(target) && 
    settingsButtonRef.value && 
    !settingsButtonRef.value.contains(target)
  ) {
    dropUpVisible.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('resize', handleResize);
  chatStore.fetchRecentChats();
  // Set initial theme to dark
  document.documentElement.setAttribute("data-theme", "dark");
  localStorage.setItem('theme', 'dark');
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('resize', handleResize);
});

const handleResize = () => {
  if (dropUpVisible.value && settingsButtonRef.value) {
    // Recalculate position when window is resized
    updateDropdownPosition();
  }
};

const updateDropdownPosition = () => {
  if (!settingsButtonRef.value) return;
  
  const rect = settingsButtonRef.value.getBoundingClientRect();
  const dropdownHeight = 180; // Approximate height of dropdown with all options
  const viewportHeight = window.innerHeight;
  const spaceBelow = viewportHeight - rect.bottom;
  const spaceAbove = rect.top;
  
  // Calculate position based on sidebar state and available space
  if (isCollapsed.value) {
    // When sidebar is collapsed, position dropdown to the right
    // Check if there's enough space below
    if (spaceBelow >= dropdownHeight) {
      // Position below the button
      dropdownPosition.value = {
        top: `${rect.top}px`,
        left: `${rect.right + 15}px`,
        bottom: 'auto' // Clear any previous bottom value
      };
    } else {
      // Not enough space below, position above bottom of screen
      dropdownPosition.value = {
        top: 'auto',
        bottom: '20px',
        left: `${rect.right + 15}px`
      };
    }
  } else {
    // When sidebar is expanded
    // Check if there's enough space below
    if (spaceBelow >= dropdownHeight) {
      // Position below the button
      dropdownPosition.value = {
        top: `${rect.bottom + 10}px`,
        left: `${rect.left}px`,
        bottom: 'auto' // Clear any previous bottom value
      };
    } else if (spaceAbove >= dropdownHeight) {
      // Not enough space below, but enough space above, position above the button
      dropdownPosition.value = {
        top: 'auto',
        bottom: `${viewportHeight - rect.top + 10}px`,
        left: `${rect.left}px`
      };
    } else {
      // Not enough space above or below, position at bottom of screen
      dropdownPosition.value = {
        top: 'auto',
        bottom: '20px',
        left: `${rect.left}px`
      };
    }
  }
};

const goToAdminConsole = () => {
  router.push("/admin-console");
  dropUpVisible.value = false;
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  const theme = isDarkMode.value ? 'dark' : 'light';
  localStorage.setItem('theme', theme);
  document.documentElement.setAttribute("data-theme", theme);
  dropUpVisible.value = false;
};

const startNewChat = () => router.push("/");
const goToHistory = () => router.push("/chat-history");
const selectChat = (chatName: string) => console.log("Selected chat:", chatName);
const openSettings = () => {
  router.push({ name: 'UserSettings' });
  dropUpVisible.value = false;
};

const logOut = async () => {
  try {
    await logout();
    router.push("/login");
  } catch (error) {
    console.error("Logout failed:", error);
  }
};

const navigateToChat = (chatId: string) => {
  // If we're already on a chat page and just changing the ID parameter
  if (route.path.startsWith('/chat/') && route.params.id !== chatId) {
    // Use the router to navigate to a loading page first, then to the new chat
    // This creates the impression of a page refresh without the screen blink
    const currentPath = route.path;
    
    // First navigate to a non-existent chat ID to force component reload
    router.replace('/loading-chat').then(() => {
      // Then navigate to the actual chat after a brief delay
      setTimeout(() => {
        router.replace(`/chat/${chatId}`);
      }, 50);
    });
  } else {
    router.push(`/chat/${chatId}`);
  }
};

// Computed classes
const sidebarClasses = computed(() => [
  "flex flex-col fixed h-full transition-all duration-300",
  props.isCollapsed ? "w-14" : "w-56",
  "bg-[var(--sidebar-bg)] text-[var(--text-color)]",
  "border-r border-[var(--border-color)]"
]);

const ChevronLeftIcon = ChevronLeft;
const ChevronRightIcon = ChevronRight;
const MessageCircleIcon = MessageCircle;
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