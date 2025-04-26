<template>
  <div 
    class="flex flex-col h-screen overflow-hidden"
    :style="contentStyle"
  >
    <!-- Header Section -->
    <div class="pt-3 pb-4 px-6 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Layers class="h-5 w-5 text-[var(--secondary-text)] stroke-[1]" />
          <h2 class="text-lg font-light text-[var(--secondary-text)]">{{ collectionName || 'Collection Details' }}</h2>
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
        <!-- Collection Stats -->
        <div class="mb-8">
          <div class="flex gap-6">
            <div class="flex-1 rounded-lg p-5 border border-[var(--border-color)]">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span class="text-sm font-medium text-[var(--secondary-text)]">Files</span>
                </div>
                <span class="text-lg font-semibold">{{ documents.length }}</span>
              </div>
            </div>
            <div class="flex-1 rounded-lg p-5 border border-[var(--border-color)]">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                  <span class="text-sm font-medium text-[var(--secondary-text)]">Embeddings</span>
                </div>
                <span class="text-lg font-semibold">{{ Object.values(documentChunks).reduce((a, b) => a + b, 0) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Upload Section -->
        <div class="mb-8">
          <button 
            @click="$refs.fileInput.click()"
            class="w-full border-2 border-dashed border-[var(--border-color)] rounded-lg p-6 hover:border-blue-500 transition-colors duration-200 flex items-center justify-center gap-3"
          >
            <input 
              type="file" 
              multiple 
              class="hidden" 
              @change="handleFileSelect"
              ref="fileInput"
              accept=".txt,.pdf,.doc,.docx,.rtf,.md,.json,.csv,.py,.js,.html,.css"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span class="text-sm font-medium">Add Documents</span>
          </button>
        </div>

        <!-- Search Filter -->
        <div class="mb-8">
          <div class="relative">
            <input 
              type="text" 
              v-model="searchFilter" 
              placeholder="Search documents..." 
              class="w-full p-4 pl-12 border border-[var(--border-color)] rounded-lg text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute left-4 top-4.5 text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <button 
              v-if="searchFilter" 
              @click="searchFilter = ''" 
              class="absolute right-4 top-4.5 text-[var(--secondary-text)] hover:text-[var(--text-color)]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Status Key -->
        <div class="mb-2">
          <div class="flex justify-end gap-4">
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-green-500 bg-opacity-20"></span>
              <span class="text-xs text-green-700">Completed</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-yellow-500 bg-opacity-20"></span>
              <span class="text-xs text-yellow-700">Processing</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-red-500 bg-opacity-20"></span>
              <span class="text-xs text-red-700">Cannot Process</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-gray-500 bg-opacity-20"></span>
              <span class="text-xs text-gray-700">Pending</span>
            </div>
          </div>
        </div>

        <!-- Document list with headers -->
        <div>
          <div class="border border-[var(--border-color)] rounded-lg overflow-hidden">
            <!-- Table header -->
            <div class="grid grid-cols-12 p-4 text-sm font-medium border-b border-[var(--border-color)]">
              <div class="col-span-4 text-left">Document Name</div>
              <div class="col-span-2 text-center">Type</div>
              <div class="col-span-2 text-center">Size</div>
              <div class="col-span-1 text-center">Date</div>
              <div class="col-span-2 text-center">Embeddings</div>
              <div class="col-span-1 text-center">Status</div>
            </div>

            <!-- Loading documents state -->
            <div v-if="isLoading" class="p-8 text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-500 mx-auto"></div>
              <p class="text-sm mt-3">Loading documents...</p>
            </div>

            <!-- Empty state -->
            <div v-else-if="documents.length === 0" class="p-8 text-center text-[var(--secondary-text)]">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="text-sm">No documents in this collection yet</p>
              <p class="text-xs mt-1">Drag and drop files above to add documents</p>
            </div>
            
            <!-- No results from filter -->
            <div v-else-if="filteredDocuments.length === 0" class="p-8 text-center text-[var(--secondary-text)]">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <p class="text-sm">No documents match your search</p>
              <p class="text-xs mt-1">Try a different search term or clear the filter</p>
            </div>

            <!-- Document items -->
            <div v-else>
              <div 
                v-for="(doc, index) in filteredDocuments" 
                :key="index"
                class="grid grid-cols-12 p-4 text-sm border-t border-[var(--border-color)] hover:bg-[var(--border-color)] hover:bg-opacity-5 transition-colors duration-150"
              >
                <div class="col-span-4 flex items-center justify-between gap-3 min-w-0">
                  <div class="flex items-center gap-3 min-w-0">
                    <!-- Document icon based on type -->
                    <svg v-if="doc.type === 'pdf'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <svg v-else-if="['jpg', 'jpeg', 'png', 'gif', 'image'].includes(doc.type)" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <svg v-else-if="['doc', 'docx'].includes(doc.type)" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    
                    <span class="truncate" :title="doc.name">{{ doc.name }}</span>
                  </div>
                  <button 
                    @click="removeDocument(doc.id)"
                    class="text-[var(--secondary-text)] hover:text-red-500 transition-colors duration-200 flex-shrink-0"
                    title="Remove document"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
                <div class="col-span-2 flex items-center justify-center">{{ doc.type ? doc.type.toUpperCase() : 'N/A' }}</div>
                <div class="col-span-2 flex items-center justify-center">{{ formatFileSize(doc.size || 0) }}</div>
                <div class="col-span-1 flex items-center justify-center">{{ formatDate(new Date(doc.created_at || Date.now())) }}</div>
                <div class="col-span-2 flex items-center justify-center">
                  <span 
                    class="text-xs"
                    :class="{
                      'text-green-600': documentStatus[doc.id] === 'completed',
                      'text-yellow-600': documentStatus[doc.id] === 'processing',
                      'text-[var(--secondary-text)]': !documentStatus[doc.id] || documentStatus[doc.id] === 'not_processed'
                    }"
                    :title="getChunkProgressTitle(doc.id)"
                  >
                    {{ getChunkProgress(doc.id) }}
                  </span>
                </div>
                <div class="col-span-1 flex items-center justify-center">
                  <span 
                    class="w-2 h-2 rounded-full"
                    :class="{
                      'bg-green-500': documentStatus[doc.id] === 'completed',
                      'bg-yellow-500 animate-pulse': documentStatus[doc.id] === 'processing',
                      'bg-red-500': documentStatus[doc.id] === 'unprocessable',
                      'bg-gray-500': !documentStatus[doc.id] || documentStatus[doc.id] === 'not_processed'
                    }"
                    :title="formatStatus(documentStatus[doc.id])"
                  ></span>
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
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useSidebarStore } from "../stores/sidebarStore";
import { useRouter, useRoute } from 'vue-router';
import { collectionsService } from '../services/collectionService';
import embeddingsService from '../services/embeddingsService';
import { Layers } from 'lucide-vue-next';

const sidebarStore = useSidebarStore();
const router = useRouter();
const route = useRoute();

// State
const collectionId = ref(route.params.id);
const collectionName = ref('');
const documents = ref([]);
const isLoading = ref(true);
const documentStatus = ref({});
const documentChunks = ref({});
const searchFilter = ref('');
const currentTaskId = ref(null);
let statusPollingInterval = null;
const fileInput = ref(null);

// Computed values
const filteredDocuments = computed(() => {
  if (!searchFilter.value) return documents.value;
  
  const filter = searchFilter.value.toLowerCase();
  return documents.value.filter(doc => 
    doc.name.toLowerCase().includes(filter)
  );
});

// Get document status for a specific ID
const getDocStatus = async (docId) => {
  const doc = documents.value.find(d => d.id === docId);
  if (doc && documentStatus.value[docId] === 'completed') {
    return 'completed';
  }
  
  try {
    const status = await embeddingsService.getDocumentEmbeddingStatus(docId);
    if (status) {
      documentStatus.value[docId] = status.status;
      
      // Store the chunk counts directly on the document object
      if (doc) {
        doc.chunks_processed = status.chunks_processed || 0;
        doc.total_chunks = status.total_chunks || 0;
        
        // Also store the metadata for compatibility
        if (status.metadata) {
          doc.metadata = status.metadata;
        }
      }
      
      return status.status;
    }
    documentStatus.value[docId] = 'not_processed';
    return 'not_processed';
  } catch (error) {
    console.error(`Error getting status for document ${docId}:`, error);
    documentStatus.value[docId] = 'not_processed';
    return 'not_processed';
  }
};

// Update status for all documents
const updateDocumentStatuses = async () => {
  for (const doc of documents.value) {
    await getDocStatus(doc.id);
  }
};

// Start periodic status updates
const startPeriodicUpdates = () => {
  // Update immediately
  updateDocumentStatuses();
  
  // Then update every 2 seconds
  statusPollingInterval = setInterval(updateDocumentStatuses, 2000);
};

// Stop periodic updates
const stopPeriodicUpdates = () => {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval);
    statusPollingInterval = null;
  }
};

// Clean up on component unmount
onUnmounted(() => {
  stopPeriodicUpdates();
});

// Regenerate embeddings for the collection
const regenerateEmbeddings = async () => {
  try {
    // Reset all statuses to processing
    documents.value.forEach(doc => {
      documentStatus.value[doc.id] = 'processing';
      documentChunks.value[doc.id] = 0;
    });
    
    // Start the embedding generation process
    const response = await embeddingsService.generateEmbeddings({
      collection_id: collectionId.value
    });
    
    // Start polling for status updates
    startPeriodicUpdates();
    
  } catch (err) {
    console.error('Error generating embeddings:', err);
    // Reset statuses on error
    documents.value.forEach(doc => {
      documentStatus.value[doc.id] = 'not_processed';
      documentChunks.value[doc.id] = 0;
    });
  }
};

// Refresh data with real status updates
const refreshData = async () => {
  try {
    isLoading.value = true;
    
    // Fetch collection info
    try {
      const collection = await collectionsService.getCollection(collectionId.value);
      collectionName.value = collection.name;
    } catch (err) {
      console.error('Error fetching collection:', err);
      collectionName.value = 'Collection Details';
    }
    
    // Fetch documents
    let fetchedDocs = await collectionsService.getDocuments(collectionId.value);
    documents.value = fetchedDocs;
    
    // Get real status for each document
    await updateDocumentStatuses();
    
    // Start periodic updates
    startPeriodicUpdates();
    
  } catch (error) {
    console.error('Error fetching documents:', error);
  } finally {
    isLoading.value = false;
  }
};

// Navigation
const goBack = () => {
  router.push('/collections');
};

// Format helpers
const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US', { 
    month: 'numeric',
    day: 'numeric',
    year: '2-digit'
  }).format(date);
};

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  else if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
  else return (bytes / 1073741824).toFixed(1) + ' GB';
};

// Add helper functions for progress calculation
const getProcessedCount = () => {
  return Object.values(documentStatus.value).filter(status => status === 'completed').length;
};

const getProgress = () => {
  if (documents.value.length === 0) return 0;
  return (getProcessedCount() / documents.value.length) * 100;
};

// Update the computed style property to match other pages
const contentStyle = computed(() => ({
  marginLeft: sidebarStore.isCollapsed ? "3.5rem" : "14rem",
  transition: "margin-left 0.3s ease",
  width: `calc(100% - ${sidebarStore.isCollapsed ? "3.5rem" : "14rem"})`,
  position: "fixed",
  top: 0,
  right: 0,
  bottom: 0,
}));

// Add this new function before the onMounted line
const formatStatus = (status) => {
  if (!status) return 'Pending';
  
  const statusMap = {
    'completed': 'Completed',
    'processing': 'Processing',
    'not_processed': 'Pending',
    'unprocessable': 'Cannot Process'
  };
  
  return statusMap[status] || status;
};

// Add remove document function
const removeDocument = async (docId) => {
  try {
    await collectionsService.deleteDocument(docId);
    // Remove document from local state
    documents.value = documents.value.filter(doc => doc.id !== docId);
    // Remove from status tracking
    delete documentStatus.value[docId];
    delete documentChunks.value[docId];
  } catch (error) {
    console.error('Error removing document:', error);
    // You might want to show an error message to the user here
  }
};

const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files);
  await uploadFiles(files);
};

const handleFileDrop = async (event) => {
  const files = Array.from(event.dataTransfer.files);
  await uploadFiles(files);
};

const uploadFiles = async (files) => {
  try {
    const formData = new FormData();
    for (let file of files) {
      formData.append('files', file);
    }
    
    await collectionsService.uploadDocuments(collectionId.value, formData);
    await refreshData(); // Refresh the document list
  } catch (error) {
    console.error('Error uploading files:', error);
    // You might want to show an error message to the user here
  }
};

// Load data on mount
onMounted(refreshData);

// Add these new functions before the onMounted line:
const getChunkProgress = (docId) => {
  const doc = documents.value.find(d => d.id === docId);
  if (!doc) return '0/0';
  
  // Check if we have status data from the server
  const status = documentStatus.value[docId];
  if (status === 'completed' || status === 'processing') {
    // Try to get from API response metadata 
    const processedChunks = doc.chunks_processed || 0;
    const totalChunks = doc.total_chunks || 0;
    
    if (totalChunks > 0) {
      return `${processedChunks}/${totalChunks}`;
    }
  }
  
  // Fallback for unknown or not processed
  return '0/0';
};

const getChunkProgressTitle = (docId) => {
  const doc = documents.value.find(d => d.id === docId);
  if (!doc) return 'No chunks processed';
  
  const status = documentStatus.value[docId];
  
  // Try to get from API response
  const processedChunks = doc.chunks_processed || 0;
  const totalChunks = doc.total_chunks || 0;
  
  if (status === 'completed' && totalChunks > 0) {
    return `All ${totalChunks} chunks processed`;
  } else if (status === 'processing' && totalChunks > 0) {
    return `Processing chunks: ${processedChunks} of ${totalChunks} complete`;
  } else if (status === 'unprocessable') {
    return 'Document cannot be processed';
  }
  return 'Pending processing';
};
</script>