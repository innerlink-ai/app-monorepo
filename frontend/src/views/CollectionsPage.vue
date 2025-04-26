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
          <h2 class="text-lg font-light text-[var(--secondary-text)]">Collections</h2>
        </div>
        <button 
          @click="navigateToNewCollection"
          class="py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:opacity-90 cursor-pointer transition-all duration-200 flex items-center gap-2 text-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>New Collection</span>
        </button>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden bg-[var(--bg-color)]">
      <div class="max-w-7xl w-full mx-auto p-6 overflow-y-auto">
        <!-- Search Bar -->
        <div class="mb-6">
          <div class="relative">
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="Search collections..." 
              class="w-full p-2.5 pl-10 border border-[var(--border-color)] rounded-lg text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3 top-3 text-[var(--secondary-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <button 
              v-if="searchQuery" 
              @click="searchQuery = ''" 
              class="absolute right-3 top-3 text-[var(--secondary-text)] hover:text-[var(--text-color)]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Collections Content -->
        <div class="bg-[var(--bg-color)] transition-all duration-200">
          <!-- Loading state -->
          <div v-if="isLoading" class="p-8 text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-500 mx-auto"></div>
            <p class="text-sm mt-3">Loading collections...</p>
          </div>

          <!-- Error state -->
          <div v-else-if="error" class="p-8 text-center text-[var(--secondary-text)]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm">{{ error }}</p>
            <button @click="fetchCollections" class="text-sm text-[var(--primary-color)] hover:text-[var(--primary-hover)] mt-2">Try again</button>
          </div>

          <!-- Empty state -->
          <div v-else-if="filteredCollections.length === 0" class="p-8 text-center text-[var(--secondary-text)]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p class="text-sm">No collections found</p>
            <p class="text-xs mt-1">Create your first collection to get started</p>
          </div>

          <!-- Collections Grid -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="collection in filteredCollections" 
              :key="collection.id"
              class="border border-[var(--border-color)] rounded-xl p-4 hover:border-[var(--primary-color)] transition-colors duration-200"
            >
              <div class="flex justify-between items-start">
                <div 
                  @click="navigateToCollection(collection.id)"
                  class="flex-1 cursor-pointer"
                >
                  <h3 class="font-medium text-sm mb-1.5">{{ collection.name }}</h3>
                  <span class="text-xs px-2 py-1 rounded-full bg-[var(--border-color)] text-[var(--secondary-text)]">
                    {{ collection.type }}
                  </span>
                </div>
              </div>
              <div 
                @click="navigateToCollection(collection.id)"
                class="cursor-pointer"
              >
                <p class="text-xs mt-2 text-[var(--secondary-text)] line-clamp-2">
                  {{ collection.description || 'No description' }}
                </p>
                <div class="flex justify-between items-center mt-3">
                  <div class="flex items-center gap-4">
                    <span class="text-xs text-[var(--secondary-text)]">{{ collection.document_count }} documents</span>
                    <span class="text-xs text-[var(--secondary-text)]">Created {{ formatDate(new Date(collection.created_at)) }}</span>
                  </div>
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
import { ref, computed, onMounted } from 'vue';
import { useSidebarStore } from "../stores/sidebarStore";
import { useRouter } from 'vue-router';
import { collectionsService } from '../services/collectionService';
import { Layers } from 'lucide-vue-next';

const sidebarStore = useSidebarStore();
const router = useRouter();

// State
const collections = ref([]);
const isLoading = ref(false);
const error = ref(null);
const searchQuery = ref('');

// Computed filtered collections
const filteredCollections = computed(() => {
  if (!searchQuery.value) return collections.value;
  
  const query = searchQuery.value.toLowerCase();
  return collections.value.filter(collection => 
    collection.name.toLowerCase().includes(query) ||
    collection.description?.toLowerCase().includes(query)
  );
});

// Fetch collections function
const fetchCollections = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    collections.value = await collectionsService.getCollections();
  } catch (err) {
    error.value = err.message || 'Failed to fetch collections';
    console.error(error.value);
  } finally {
    isLoading.value = false;
  }
};

// Fetch collections when component mounts
onMounted(fetchCollections);

// Navigation functions
const navigateToCollection = (collectionId) => {
  router.push(`/collections/${collectionId}`);
};

const navigateToNewCollection = () => {
  router.push('/collections/new');
};

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

// Format date helper
const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  }).format(date);
};
</script>