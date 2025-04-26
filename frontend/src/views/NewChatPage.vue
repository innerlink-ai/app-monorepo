<template>
  <div 
    class="flex h-full w-full justify-center items-center px-32"
    :style="chatWindowStyle"
  >
    <div 
      class="flex flex-col items-center w-full space-y-8 min-w-0"
      :class="sidebarStore.isCollapsed ? 'max-w-[90%]' : 'max-w-[85%]'"
    >
      <!-- Greeting with image -->
      <div class="flex items-center bg-[var(--chat-bg)] text-[var(--text-color)] rounded-2xl shadow-sm transition-all duration-200">
        <div class="mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-color)" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
            <polyline points="7.5 19.79 7.5 14.6 3 12"/>
            <polyline points="21 12 16.5 14.6 16.5 19.79"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>
        </div>
        <span class="whitespace-pre-wrap break-words anywhere text-4xl font-medium">
          How can I help you today?
        </span>
      </div>

      <!-- Input Area - Replaced with Component -->
      <div class="flex items-center w-full min-w-0 overflow-hidden">
        <ChatInputArea 
          v-model="message" 
          v-model:files="attachedFiles" 
          @send="sendMessage"
        />
      </div>

      <!-- Collections Modal remains here as it's related to parent logic -->
      <Transition
        v-if="showCollectionsModal"
        enter-active-class="transition-opacity duration-300"
        leave-active-class="transition-opacity duration-300"
        mode="out-in"
      >
        <div v-if="showCollectionsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div class="bg-white p-8 rounded-lg">
            <h2 class="text-2xl font-bold mb-4">Select a Collection</h2>
            <input
              v-model="collectionSearch"
              placeholder="Search collections..."
              class="w-full p-2 border rounded-md mb-4"
            />
            <div class="space-y-2">
              <div
                v-for="collection in filteredCollections"
                :key="collection.id"
                class="flex items-center justify-between p-2 border rounded-md cursor-pointer hover:bg-gray-100"
                @click="selectCollectionFromModal(collection)"
              >
                <span>{{ collection.name }}</span>
              </div>
            </div>
            <button
              @click="showCollectionsModal = false"
              class="mt-4 w-full bg-blue-500 text-white p-2 rounded-md"
            >
              Close
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Send, Layers } from 'lucide-vue-next';
import { useSidebarStore } from '../stores/sidebarStore';
import { collectionsService } from '../services/collectionService';
import { createChat } from '../services/chatService';
import { useChatStore } from '../stores/chatStore';
import ChatInputArea from '../components/ChatInputArea.vue';

// Types
interface Collection {
  id: string;
  name: string;
  description?: string;
}

interface FileAttachment {
  name: string;
  size?: number;
  type?: string;
  file?: File;
  content?: string | null;
}

// Add a new interface for the API file format
interface FileForAPI {
  name: string;
  content: string;
}

const router = useRouter();
const sidebarStore = useSidebarStore();
const message = ref('');
const chatStore = useChatStore();

// Context options state
const showContextOptions = ref(false);
const toggleContextOptions = () => {
  showContextOptions.value = !showContextOptions.value;
  // Close dropdowns when collapsing options
  if (!showContextOptions.value) {
    showCollectionsModal.value = false;
  }
};

// File upload state
const attachedFiles = ref<FileAttachment[]>([]);

// Collections state
const collections = ref<Collection[]>([]);
const selectedCollection = ref<Collection | null>(null);
const isLoadingCollections = ref(false);
const collectionsError = ref<string | null>(null);
const collectionSearch = ref('');
const showCollectionsModal = ref(false);

const filteredCollections = computed(() => {
  if (!collectionSearch.value) return collections.value;
  const searchTerm = collectionSearch.value.toLowerCase();
  return collections.value.filter(c => c.name.toLowerCase().includes(searchTerm));
});

const fetchCollections = async () => {
  isLoadingCollections.value = true;
  collectionsError.value = null;
  
  try {
    const data = await collectionsService.getCollections();
    collections.value = data;
  } catch (error) {
    collectionsError.value = 'Failed to load collections';
    console.error('Error fetching collections:', error);
  } finally {
    isLoadingCollections.value = false;
  }
};

const openCollectionsModal = () => {
  showCollectionsModal.value = true;
  if (collections.value.length === 0 && !isLoadingCollections.value && !collectionsError.value) {
    fetchCollections();
  }
};

const selectCollectionFromModal = (collection: Collection) => {
  selectedCollection.value = collection;
  showCollectionsModal.value = false;
};

const removeCollection = () => {
  selectedCollection.value = null;
};

const removeCollectionInModal = () => {
  selectedCollection.value = null;
};

// Send message functionality
const sendMessage = async () => {
  const currentTimestamp = new Date().toISOString();
  if ((!message.value.trim() && attachedFiles.value.length === 0) || isLoadingCollections.value) return;
  
  try {
    // Step 1: Create a new chat with minimal info (just gets a UUID back)
    const response = await createChat({
      message: message.value.trim() || (attachedFiles.value.length > 0 ? "File(s) attached" : "")
    });
    
    if (response.chat_id) {
      const newChatInfo = {
        chat_id: response.chat_id,
        name: message.value.trim().substring(0, 50) || (attachedFiles.value.length > 0 ? attachedFiles.value[0].name : 'New Chat'),
        updated_at: currentTimestamp,
      };
      chatStore.addChat(newChatInfo);

      // Step 2: Read file contents at this point for files that were stored by reference
      let filesForAPI: FileForAPI[] = [];
      
      if (attachedFiles.value.length > 0) {
        // Process files for API, reading content as needed
        filesForAPI = await Promise.all(attachedFiles.value.map(async (attachment) => {
          // If we have a file reference, read it now
          if (attachment.file && !attachment.content) {
            try {
              let content = await readFileAsBase64(attachment.file);
              return {
                name: attachment.name,
                content: content
              };
            } catch (error) {
              const errorMessage = error instanceof Error ? error.message : 'Unknown error';
              console.error(`Error reading file ${attachment.name}:`, errorMessage);
              return {
                name: attachment.name,
                content: `[Error reading file: ${errorMessage}]`
              };
            }
          } else {
            // Regular text content
            return {
              name: attachment.name,
              content: attachment.content || ''
            };
          }
        }));
      }
      
      // Step 3: Save the message, files and collection info to pass to chat page
      const contextData = {
        messageText: message.value.trim(),
        files: filesForAPI.length > 0 ? filesForAPI : undefined,
        collection: selectedCollection.value ? {
          id: selectedCollection.value.id,
          name: selectedCollection.value.name
        } : undefined
      };
    
      console.log('Sending to ChatWindow via router state:', {
        messageText: contextData.messageText,
        hasFiles: Array.isArray(contextData.files),
        filesCount: Array.isArray(contextData.files) ? contextData.files.length : 0,
        fileNames: Array.isArray(contextData.files) ? contextData.files.map(f => f.name) : [],
        fileContentSample: Array.isArray(contextData.files) && contextData.files.length > 0 
          ? contextData.files.map(f => `${f.name}: ${typeof f.content === 'string' ? f.content.substring(0, 30) : 'Binary data'}...`) 
          : 'none',
        hasCollection: !!contextData.collection,
        collectionInfo: contextData.collection ? `${contextData.collection.id} - ${contextData.collection.name}` : 'none'
      });
      
      try {
        // Store the contextData in localStorage with the chat ID as a key
        // Skip storing if too large
        const serializedData = JSON.stringify(contextData);
        if (serializedData.length > 4000000) { // ~4MB safety limit
          console.warn('Context data too large for localStorage, using session navigation');
          // Use sessionStorage instead for one-time transfer
          sessionStorage.setItem(`chat_context_${response.chat_id}`, serializedData);
        } else {
          localStorage.setItem(`chat_context_${response.chat_id}`, serializedData);
        }
      } catch (e) {
        console.error('Error storing context data:', e);
        // Fall back to session navigation (without storage)
        sessionStorage.setItem(`chat_context_${response.chat_id}_error`, 'Storage error occurred');
      }
      
      // Navigate to the chat page (without using state)
      router.push({
        name: 'Chat',
        params: { id: response.chat_id }
      });
    } else {
      console.error("Error: Chat ID not returned.");
    }
  } catch (error) {
    console.error('Error creating chat:', error);
  }
};

// Helper function to read file as base64
const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (reader.result) {
        resolve(reader.result as string);
      } else {
        reject(new Error('Failed to read file content'));
      }
    };
    reader.onerror = () => reject(reader.error || new Error('File read error'));
    reader.readAsDataURL(file); // Read as data URL (base64)
  });
};

onMounted(() => {
  // Reset state when component is mounted
  message.value = '';
  attachedFiles.value = [];
  selectedCollection.value = null;
  showContextOptions.value = false;
  showCollectionsModal.value = false;
  collectionSearch.value = '';
});

// Computed style for the chat window wrapper
const chatWindowStyle = computed(() => ({
  marginLeft: sidebarStore.isCollapsed ? "3.5rem" : "14rem",
  transition: "margin-left 0.3s ease",
}));

// Assign necessary icons if still used elsewhere in THIS component
const LayersIcon = Layers;
const SendIcon = Send;
</script>

<style scoped>
.anywhere {
  overflow-wrap: anywhere;
}

textarea {
  min-height: 40px;
}

textarea::placeholder {
  color: var(--secondary-text);
}

/* Input container styling */
.input-container {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background: linear-gradient(to bottom, var(--prompt-bg), var(--prompt-bg));
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.input-container:focus-within {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-color: var(--border-color);
}

/* Light theme specific styles */
html[data-theme="light"] .input-container {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background: linear-gradient(to bottom, #ffffff, #f9fafb);
  border: 1px solid #e5e7eb;
}

html[data-theme="light"] .input-container:focus-within {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-color: #d1d5db;
}

/* Dark theme specific styles */
html[data-theme="dark"] .input-container {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  background: linear-gradient(to bottom, var(--prompt-bg), var(--prompt-bg));
  border: 1px solid var(--border-color);
}

html[data-theme="dark"] .input-container:focus-within {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  border-color: var(--border-color);
}
</style>