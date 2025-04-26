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
          <MessagesSquare class="h-5 w-5 text-[var(--secondary-text)] stroke-[1]" />
          <h2 class="text-lg font-light text-[var(--secondary-text)]">Chat History</h2>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden bg-[var(--bg-color)]">
      <div class="max-w-7xl w-full mx-auto p-6 overflow-y-auto custom-scrollbar">
        <!-- Search and New Chat -->
        <div class="mb-8">
          <div class="flex gap-4">
            <!-- Search Bar -->
            <div class="flex-1 relative">
              <input 
                v-model="searchQuery"
                type="text"
                placeholder="Search chats..."
                class="w-full p-2.5 pl-10 border border-[var(--border-color)] rounded-lg text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                @input="handleSearch"
              />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3 top-2.5 text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <button 
                v-if="searchQuery" 
                @click="searchQuery = ''" 
                class="absolute right-3 top-2.5 text-[var(--secondary-text)] hover:text-[var(--text-color)]"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-[var(--chat-bg)] rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div class="flex items-center gap-3 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h3 class="text-lg font-medium">Delete Chat</h3>
            </div>
            <p class="text-sm text-[var(--secondary-text)] mb-6">
              Are you sure you want to delete this chat? This action cannot be undone.
            </p>
            <div class="flex justify-end gap-3">
              <button 
                @click="showDeleteModal = false"
                class="px-4 py-2 text-sm font-medium text-[var(--secondary-text)] hover:text-[var(--text-color)] transition-colors duration-200"
              >
                Cancel
              </button>
              <button 
                @click="confirmDelete"
                class="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors duration-200"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-500 mx-auto"></div>
          <p class="text-sm mt-3">Loading chats...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredChats.length === 0" class="p-8 text-center text-[var(--secondary-text)]">
          <History class="h-12 w-12 mx-auto mb-3 stroke-[1]" />
          <p class="text-sm">{{ searchQuery ? 'No chats match your search' : 'No chat history found' }}</p>
          <p class="text-xs mt-1">{{ searchQuery ? 'Try a different search term' : 'Start a new conversation to begin chatting' }}</p>
        </div>

        <!-- Chat List -->
        <div v-else>
          <div class="border border-[var(--border-color)] rounded-lg overflow-hidden">
            <!-- Table header -->
            <div class="grid grid-cols-13 p-4 text-sm font-medium border-b border-[var(--border-color)]">
              <div class="col-span-5 text-left">Chat Name</div>
              <div class="col-span-3 text-center">Messages</div>
              <div class="col-span-3 text-center">Last Activity</div>
              <div class="col-span-1 text-center">Rename</div>
              <div class="col-span-1 text-center">Delete</div>
            </div>

            <!-- Chat items -->
            <div>
              <div 
                v-for="chat in filteredChats" 
                :key="chat.chat_id" 
                class="grid grid-cols-13 p-4 text-sm border-t border-[var(--border-color)] hover:bg-[var(--border-color)] hover:bg-opacity-5 transition-colors duration-150 items-center" 
                :class="{'cursor-pointer': editingChatId !== chat.chat_id}" 
                @click="editingChatId !== chat.chat_id ? handleChatClick(chat.chat_id) : null" 
              >
                <div class="col-span-5 flex items-center gap-3 min-w-0">
                  <div class="flex items-center gap-3 min-w-0 flex-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[#4a86e8] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <!-- Conditional Rendering for Edit/Display -->
                    <div v-if="editingChatId === chat.chat_id" class="flex items-center gap-2 flex-1 min-w-0">
                      <input 
                        ref="editInputRef"
                        v-model="editingChatName"
                        type="text"
                        class="flex-grow p-1 border border-[var(--border-color)] rounded bg-[var(--input-bg)] text-[var(--text-color)] text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 min-w-0"
                        placeholder="Enter new name"
                        @keydown.enter.prevent="saveChatName"
                        @keydown.esc.prevent="cancelEditing"
                        @click.stop 
                      />
                      <button 
                        @click.stop="saveChatName"
                        :disabled="isSaving || !editingChatName.trim() || editingChatName.trim() === chat.name"
                        class="p-1 rounded text-green-500 hover:bg-[var(--button-hover-lighter)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        title="Save changes"
                      >
                        <Check class="h-4 w-4" />
                      </button>
                      <button 
                        @click.stop="cancelEditing"
                        :disabled="isSaving"
                        class="p-1 rounded text-red-500 hover:bg-[var(--button-hover-lighter)] disabled:opacity-50 transition-colors"
                        title="Cancel edit"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </div>
                    <span v-else class="truncate">{{ chat.name }}</span>
                  </div>
                </div>
                <div class="col-span-3 flex items-center justify-center">{{ chat.message_count }}</div>
                <div class="col-span-3 flex items-center justify-center">{{ chat.updated_at }}</div>
                <!-- Rename Button Column -->
                <div class="col-span-1 flex items-center justify-center">
                  <button 
                    v-if="editingChatId !== chat.chat_id"
                    @click.stop="startEditing(chat)"
                    class="p-1 rounded text-[var(--secondary-text)] hover:text-[var(--text-color)] hover:bg-[var(--button-hover-lighter)] transition-colors"
                    title="Rename chat"
                  >
                    <Pencil class="h-3.5 w-3.5" />
                  </button>
                </div>
                <!-- Delete Button Column -->
                <div class="col-span-1 flex items-center justify-center">
                  <button 
                    @click.stop="handleDeleteChat(chat.chat_id)"
                    class="text-[var(--secondary-text)] hover:text-red-500 transition-colors duration-200"
                    title="Delete chat"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from "../stores/authStore";
import { useSidebarStore } from "../stores/sidebarStore";
import { MessagesSquare, History, Pencil, Check, X } from 'lucide-vue-next';
import { 
  fetchChats, 
  createChat, 
  deleteChat, 
  updateChat,
  searchChats 
} from '../services/chatHistoryService';

const router = useRouter();
const authStore = useAuthStore();
const sidebarStore = useSidebarStore();
const isAuthenticated = ref(false);
const chats = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const searchTimeout = ref(null);
const showDeleteModal = ref(false);
const chatToDelete = ref(null);

// --- State for Editing Chat Name ---
const editingChatId = ref(null); // Store the ID of the chat being edited
const editingChatName = ref(''); // Store the new name being typed
const editInputRef = ref(null); // Ref for the input element
const isSaving = ref(false);

// Computed style for the content window that adjusts with sidebar
const contentStyle = computed(() => ({
  marginLeft: sidebarStore.isCollapsed ? "3.5rem" : "14rem",
  transition: "margin-left 0.3s ease",
  width: `calc(100% - ${sidebarStore.isCollapsed ? "3.5rem" : "14rem"})`,
  position: "fixed",
  top: 0,
  right: 0,
  bottom: 0,
}));

// Computed property for filtered chats
const filteredChats = computed(() => {
  if (!searchQuery.value.trim()) return chats.value;
  
  const query = searchQuery.value.toLowerCase();
  return chats.value.filter(chat => 
    chat.name.toLowerCase().includes(query) || 
    (chat.preview && chat.preview.toLowerCase().includes(query))
  );
});

// Check authentication status
const checkAuth = async () => {
  await authStore.checkAuth();
  isAuthenticated.value = authStore.isAuthenticated;
  
  if (isAuthenticated.value) {
    await loadChats();
  } else {
    router.push('/login');
  }
};

// Load all chats
const loadChats = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // Get original data from API
    const apiChats = await fetchChats();
    
    // Process each chat to convert the date
    chats.value = apiChats.map(chat => {
      // Make a copy of the chat object
      const processedChat = { ...chat };
      
      // Convert the updated_at timestamp from UTC to local time
      if (processedChat.updated_at) {
        try {
          // Store the original date for sorting
          processedChat._original_updated_at = processedChat.updated_at;
          
          // The key fix: Add the "Z" to explicitly mark as UTC time
          // This tells JavaScript to treat this as UTC, not local time
          const dateString = processedChat.updated_at.endsWith('Z') 
            ? processedChat.updated_at 
            : processedChat.updated_at + 'Z';
            
          // Create a date object from the UTC string
          const utcDate = new Date(dateString);
          
          // Format using toLocaleString to convert to local timezone
          processedChat.updated_at = utcDate.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
          });
        } catch (e) {
          console.error("Error converting date:", e);
        }
      }
      
      return processedChat;
    });
    
    // Sort chats by the original date (newest first)
    chats.value.sort((a, b) => {
      const dateA = a._original_updated_at ? new Date(a._original_updated_at) : new Date(0);
      const dateB = b._original_updated_at ? new Date(b._original_updated_at) : new Date(0);
      return dateB - dateA;
    });
    
  } catch (err) {
    console.error('Failed to fetch chat history:', err);
    error.value = 'Failed to load chat history. Please try again later.';
  } finally {
    loading.value = false;
  }
};


const formatDateToLocalTime = (date) => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};

// Handle search with debounce
const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
  
  searchTimeout.value = setTimeout(async () => {
    if (searchQuery.value.trim().length > 0) {
      try {
        loading.value = true;
        // Using client-side filtering through computed property
        // If you want to use server-side search, uncomment below:
        // chats.value = await searchChats(searchQuery.value);
        loading.value = false;
      } catch (err) {
        console.error('Search error:', err);
        error.value = 'Search failed. Please try again.';
        loading.value = false;
      }
    }
  }, 300);
};

// Highlight matching text in search results
const highlightMatch = (text) => {
  if (!text || !searchQuery.value.trim()) return text;
  
  const query = searchQuery.value.trim();
  if (query.length < 2) return text; // Don't highlight very short queries
  
  // Escape special characters in the query for regex
  const safeQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${safeQuery})`, 'gi');
  return text.replace(regex, '<span class="bg-yellow-200">$1</span>');
};

// Handle chat click to navigate to chat
const handleChatClick = (chatId) => {
  router.push(`/chat/${chatId}`);
};

// Create new chat
const handleNewChat = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await createChat();
    if (response && response.chat_id) {
      router.push(`/chat/${response.chat_id}`);
    }
  } catch (err) {
    console.error('Failed to create new chat:', err);
    error.value = 'Failed to create a new chat. Please try again.';
    loading.value = false;
  }
};

// Delete chat
const handleDeleteChat = (chatId) => {
  chatToDelete.value = chatId;
  showDeleteModal.value = true;
};

const confirmDelete = async () => {
  if (!chatToDelete.value) return;
  
  try {
    await deleteChat(chatToDelete.value);
    // Refresh the chat list
    await loadChats();
  } catch (err) {
    console.error('Failed to delete chat:', err);
    error.value = 'Failed to delete the chat. Please try again.';
  } finally {
    showDeleteModal.value = false;
    chatToDelete.value = null;
  }
};

// --- Functions for Editing Chat Name ---
const startEditing = (chat) => {
  editingChatId.value = chat.chat_id;
  editingChatName.value = chat.name; // Pre-fill input with current name
  // Focus the input field after it becomes visible
  nextTick(() => {
    editInputRef.value?.focus();
  });
};

const cancelEditing = () => {
  editingChatId.value = null;
  editingChatName.value = '';
};

const saveChatName = async () => {
  if (!editingChatId.value || !editingChatName.value.trim() || isSaving.value) return;

  const originalChat = chats.value.find(chat => chat.chat_id === editingChatId.value);
  if (!originalChat || originalChat.name === editingChatName.value.trim()) {
    // No change or chat not found, just cancel
    cancelEditing();
    return;
  }

  isSaving.value = true;
  const chatIdToUpdate = editingChatId.value;
  const newName = editingChatName.value.trim();

  try {
    await updateChat(chatIdToUpdate, { name: newName });
    // Update local state on success
    const index = chats.value.findIndex(chat => chat.chat_id === chatIdToUpdate);
    if (index !== -1) {
      chats.value[index].name = newName;
      
      // Create a new UTC timestamp
      const nowUTC = new Date().toISOString();
      
      // Store the original date string for sorting
      chats.value[index]._original_updated_at = nowUTC;
      
      // Create a Date object from the UTC string (which already has a Z)
      const localDate = new Date(nowUTC);
      
      // Format using toLocaleString to convert to local timezone
      chats.value[index].updated_at = localDate.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
      
      // Re-sort the chats array to put the updated chat at the top
      chats.value.sort((a, b) => {
        const dateA = a._original_updated_at ? new Date(a._original_updated_at) : new Date(0);
        const dateB = b._original_updated_at ? new Date(b._original_updated_at) : new Date(0);
        return dateB - dateA;
      });
    }
    cancelEditing(); // Exit edit mode
  } catch (err) {
    console.error('Failed to update chat name:', err);
    alert('Failed to save chat name. Please try again.'); 
  } finally {
    isSaving.value = false;
  }
};


// On component mount
onMounted(() => {
  checkAuth();
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