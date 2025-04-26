<!-- NewCollectionForm.vue -->
<template>
  <div 
    class="flex flex-col h-screen overflow-hidden"
    :style="contentStyle"
  >
    <!-- Header with Title -->
    <div class="pt-3 pb-4 px-6 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Layers class="h-5 w-5 text-[var(--secondary-text)] stroke-[1]" />
          <h2 class="text-lg font-light text-[var(--secondary-text)]">New Collection</h2>
        </div>
        <button @click="goBack" class="flex items-center text-sm font-medium gap-1 text-[var(--secondary-text)] hover:text-[var(--text-color)]">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span>Back to Collections</span>
        </button>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden bg-[var(--bg-color)]">
      <div class="max-w-7xl w-full mx-auto p-6 overflow-y-auto">
        <!-- Form -->
        <form @submit.prevent="validateAndCreate">
          <!-- Name and Type fields -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
            <div>
              <label class="block text-sm font-medium mb-2 text-[var(--secondary-text)]">Name <span class="text-red-400">*</span></label>
              <input v-model="newCollection.name" type="text" required placeholder="Enter collection name"
                class="w-full p-2.5 border border-[var(--border-color)] rounded-lg text-[var(--text-color)] placeholder-[var(--secondary-text)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-2 text-[var(--secondary-text)]">Type</label>
              <div class="relative">
                <select v-model="newCollection.type" required
                  class="appearance-none w-full p-2.5 border border-[var(--border-color)] rounded-lg text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm pr-8">
                  <option value="Document">Document</option>
                  <option value="Text">Text</option>
                  <option value="Image">Image</option>
                  <option value="Hybrid">Hybrid</option>
                </select>
                <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                  <svg class="w-4 h-4 text-[var(--secondary-text)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Description field -->
          <div class="mb-6">
            <label class="block text-sm font-medium mb-2 text-[var(--secondary-text)]">Description <span class="text-xs text-[var(--secondary-text)] font-normal">(optional)</span></label>
            <textarea v-model="newCollection.description" rows="3" placeholder="Description of the collection"
              class="w-full p-2.5 border border-[var(--border-color)] rounded-lg text-[var(--text-color)] placeholder-[var(--secondary-text)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"></textarea>
          </div>

          <!-- Encrypt toggle -->
          <div class="mb-6 p-4 border border-[var(--border-color)] rounded-lg">
            <div class="flex flex-col gap-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <h3 class="text-sm font-medium text-[var(--text-color)]">Security Settings</h3>
                  <span class="text-xs px-2 py-0.5 bg-blue-600 text-white border border-blue-700 rounded-full dark:bg-blue-500 dark:text-white dark:border-blue-600">Recommended</span>
                </div>
                <label class="inline-flex items-center cursor-pointer">
                  <span class="me-3 text-sm font-medium text-[var(--text-color)]">Encrypt documents</span>
                  <input type="checkbox" v-model="newCollection.is_encrypted" class="sr-only peer">
                  <div class="relative w-11 h-6 bg-[var(--border-color)] peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                </label>
              </div>
              <p class="text-xs text-[var(--secondary-text)]">Keep your documents secure with industry-standard encryption. This ensures your data remains private and protected from unauthorized access. Documents are encrypted at rest and during transmission, with secure key management and access controls. This is essential for protecting sensitive information and maintaining data privacy.</p>
            </div>
          </div>
          
          <!-- Vector Embeddings toggle -->
          <div class="mb-6 p-4 border border-[var(--border-color)] rounded-lg">
            <div class="flex flex-col gap-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <h3 class="text-sm font-medium text-[var(--text-color)]">Vector Embeddings</h3>
                  <span class="text-xs px-2 py-0.5 bg-blue-600 text-white border border-blue-700 rounded-full dark:bg-blue-500 dark:text-white dark:border-blue-600">Recommended</span>
                </div>
                <label class="inline-flex items-center cursor-pointer">
                  <span class="me-3 text-sm font-medium text-[var(--text-color)]">Generate Embeddings</span>
                  <input type="checkbox" v-model="generateEmbeddings" class="sr-only peer">
                  <div class="relative w-11 h-6 bg-[var(--border-color)] peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                </label>
              </div>
              <p class="text-xs text-[var(--secondary-text)]">Enable powerful semantic search capabilities. This allows you to find documents based on their meaning, not just keywords, making it easier to find exactly what you're looking for. The system analyzes document content to understand context and relationships, enabling natural language queries and finding relevant information even when exact words don't match.</p>
            </div>
          </div>
          
          <div class="border-t border-[var(--border-color)] my-6"></div>
          
          <!-- Upload Files Section -->
          <div class="mb-4">
            <h3 class="text-sm font-medium text-[var(--text-color)]">Upload Files <span class="text-red-400">*</span></h3>
            <p class="text-xs text-[var(--secondary-text)] mt-1">Select files to include in this collection</p>
          </div>
          
          <!-- Drag & Drop area -->
          <div @dragover.prevent="dragover = true" @dragleave.prevent="dragover = false" @drop.prevent="handleFileDrop"
            @click="$refs.fileInput.click()"
            class="border-2 border-dashed rounded-lg p-6 cursor-pointer text-center mb-6 transition-all duration-200"
            :class="[fileError ? 'border-red-400 bg-red-400 bg-opacity-5' : dragover ? 'border-blue-500 bg-blue-500 bg-opacity-5' : 'border-[var(--border-color)] hover:border-[var(--primary-color)]']">
            
            <div v-if="selectedFiles.length === 0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="mt-2 text-sm font-medium text-[var(--text-color)]">Drag and drop files here or click to browse</p>
              
              <!-- Upload sources -->
              <div class="flex flex-wrap justify-center gap-2 mt-3">
                <div class="px-2 py-1 border border-[var(--border-color)] rounded text-xs text-[var(--secondary-text)] hover:border-[var(--primary-color)]">Local Files</div>
                <div class="px-2 py-1 border border-[var(--border-color)] rounded text-xs text-[var(--secondary-text)] hover:border-[var(--primary-color)]">Google Drive</div>
                <div class="px-2 py-1 border border-[var(--border-color)] rounded text-xs text-[var(--secondary-text)] hover:border-[var(--primary-color)]">OneDrive</div>
                <div class="px-2 py-1 border border-[var(--border-color)] rounded text-xs text-[var(--secondary-text)] hover:border-[var(--primary-color)]">Dropbox</div>
              </div>
              
              <p class="text-xs text-[var(--secondary-text)] mt-3">Upload at least one file to create this collection</p>
            </div>
            
            <div v-else class="flex flex-col items-center w-full">
              <div class="text-sm font-medium text-[var(--text-color)] flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ selectedFiles.length }} files selected
              </div>
              
              <!-- File list -->
              <div class="w-full max-h-40 overflow-y-auto mt-3 border border-[var(--border-color)] rounded-lg p-2">
                <div v-for="(file, index) in selectedFiles" :key="index" 
                     class="flex items-center justify-between py-1 px-2 text-sm border-b last:border-b-0 border-[var(--border-color)]">
                  <div class="flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span class="truncate max-w-xs text-[var(--text-color)]">{{ file.name }}</span>
                  </div>
                  <span class="text-xs text-[var(--secondary-text)]">{{ formatFileSize(file.size) }}</span>
                </div>
              </div>
              
              <div class="flex mt-3 gap-2">
                <button type="button" @click.stop="$refs.fileInput.click()" 
                  class="text-sm text-[var(--text-color)] border border-[var(--border-color)] px-3 py-1 rounded-lg hover:border-[var(--primary-color)] transition-colors duration-200">
                  Add more files
                </button>
                <button type="button" @click.stop="selectedFiles = []"
                  class="text-sm text-[var(--text-color)] border border-[var(--border-color)] px-3 py-1 rounded-lg hover:border-[var(--primary-color)] transition-colors duration-200">
                  Clear all
                </button>
              </div>
            </div>
            
            <input type="file" ref="fileInput" @change="handleFileSelect" multiple class="hidden" />
          </div>
          
          <div v-if="fileError" class="flex items-center text-sm text-red-400 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            {{ fileError }}
          </div>
          
          <!-- Error message -->
          <div v-if="error" class="bg-red-900 bg-opacity-20 border border-red-800 text-red-400 px-4 py-3 rounded-lg mb-6 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>{{ error }}</p>
          </div>
          
          <!-- Form actions -->
          <div class="flex justify-end pt-4 border-t border-[var(--border-color)]">
            <button type="submit" :disabled="isLoading"
              class="py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:opacity-90 cursor-pointer transition-all duration-200 flex items-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed">
              <span v-if="isLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              <span>{{ isLoading ? 'Creating...' : 'Create Collection' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useSidebarStore } from "../stores/sidebarStore";
import { useRouter } from 'vue-router';
import { collectionsService } from '../services/collectionService';
import { embeddingsService } from '../services/embeddingsService';
import { Layers } from 'lucide-vue-next';

const sidebarStore = useSidebarStore();
const router = useRouter();

// Form state
const newCollection = ref({
  name: '',
  type: 'Document',
  description: '',
  is_encrypted: true
});

const generateEmbeddings = ref(true);
const isLoading = ref(false);
const error = ref(null);
const fileError = ref(null);
const dragover = ref(false);
const selectedFiles = ref([]);

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

// File handlers
const handleFileSelect = (event) => {
  fileError.value = null;
  const files = Array.from(event.target.files);
  if (files.length > 0) {
    selectedFiles.value = files;
  }
};

const handleFileDrop = (event) => {
  dragover.value = false;
  fileError.value = null;
  const files = Array.from(event.dataTransfer.files);
  if (files.length > 0) {
    selectedFiles.value = files;
  }
};

// Form validation
const validateAndCreate = () => {
  fileError.value = null;
  error.value = null;
  
  if (!newCollection.value.name.trim()) {
    error.value = "Collection name is required";
    return;
  }
  
  if (selectedFiles.value.length === 0) {
    fileError.value = "At least one file is required to create a collection";
    return;
  }
  
  createCollection();
};

// Navigation
const goBack = () => {
  router.push('/collections');
};

// Format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Create collection
const createCollection = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    
    // Create the collection
    const collection = await collectionsService.createCollection(newCollection.value);
    
    // Upload files
    const uploadPromises = selectedFiles.value.map(file => 
      collectionsService.uploadDocument(collection.id, file)
    );
    
    try {
      const uploadedDocuments = await Promise.all(uploadPromises);
      
      // Generate embeddings if user selected the option
      if (generateEmbeddings.value) {
        try {
          // Start generating embeddings for the collection
          embeddingsService.generateEmbeddings({
            collection_id: collection.id
          });
        } catch (embeddingError) {
          console.error('Error initiating embeddings:', embeddingError);
          // We don't want to interrupt navigation if embeddings fail
        }
      }
      // Navigate to collection details page
      router.push(`/collections/${collection.id}`);
      
    } catch (uploadError) {
      error.value = "Some files failed to upload. Please try again.";
      console.error('Upload error:', uploadError);
    }
  } catch (err) {
    error.value = err.message || 'Failed to create collection';
    console.error(error.value);
  } finally {
    isLoading.value = false;
  }
};
</script>