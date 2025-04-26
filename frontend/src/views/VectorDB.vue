// VectorDB.vue (Main Component)
<template>
  <div v-if="authStore.isLoading" class="flex h-screen justify-center items-center">
    <p>Loading...</p>
  </div>
  
  <div v-else-if="isAuthenticated" class="flex flex-col h-screen overflow-hidden transition-all duration-300" :style="contentStyle">
    <!-- Main content that adjusts to sidebar -->
    <div class="h-full overflow-auto">
      <div class="p-4 md:p-6">
        <!-- Header Section -->
        <div class="bg-[var(--chat-bg)] text-[var(--text-color)] p-4 rounded-xl shadow-sm transition-all duration-200 w-full text-center mb-4">
          <span class="text-lg font-medium">Vector Database</span>
        </div>

        <!-- Tab Navigation - Full Width -->
<!-- Tab Navigation - Full Width -->
<div class="bg-[var(--prompt-bg)] text-[var(--text-color)] w-full px-4 py-3 rounded-xl shadow-sm transition-all duration-200 border border-[var(--border-color)] mb-4">
  <div class="flex w-full">
    <button 
      v-for="tab in tabs" 
      :key="tab.id"
      @click="activeTab = tab.id"
      :class="[
        'flex-1 text-xs font-medium py-1.5 rounded-lg transition-all duration-200 flex justify-center',
        activeTab === tab.id 
          ? 'bg-[#2563eb] text-white' 
          : 'hover:bg-[var(--hover-color)] hover:text-[#2563eb] hover:shadow-sm cursor-pointer'
      ]"
    >
      <div class="flex items-center space-x-1.5">
        <svg v-if="tab.id === 'collections'" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <svg v-if="tab.id === 'create'" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        <svg v-if="tab.id === 'dashboard'" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
        <span>{{ tab.name }}</span>
      </div>
    </button>
  </div>
</div>

        <!-- Search & Query Tab -->
        <div v-if="activeTab === 'collections'">
          <VectorSearch 
            :collections="collections" 
            @selectCollection="selectCollection" 
            @deleteCollection="deleteCollection" 
          />
        </div>

        <!-- Collections Management Tab -->
        <div v-if="activeTab === 'create'">
          <CollectionsManagement @createCollection="handleCreateCollection" ref="managementComponent" />
        </div>

        <!-- Dashboard Tab -->
        <div v-if="activeTab === 'dashboard'">
          <Dashboard :collections="collections" />
        </div>
      </div>
    </div>
  </div>
  <div v-else class="flex justify-center items-center h-screen">
    <p>Please log in to access VectorDB.</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from "../stores/authStore";
import { useSidebarStore } from "../stores/sidebarStore";
import { fetchCollections, createCollection as apiCreateCollection, deleteCollection as apiDeleteCollection } from "../services/vectorDbService";
import Dashboard from "../components/vectordb/VectorDashboard.vue";
import VectorSearch from "../components/vectordb/VectorSearch.vue";
import CollectionsManagement from "../components/vectordb/CollectionsManagement.vue";

const authStore = useAuthStore();
const sidebarStore = useSidebarStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const error = ref(null);

// Responsive layout adjustment based on sidebar state
const contentStyle = computed(() => {
  // Adjust margins based on sidebar state
  return {
    marginLeft: sidebarStore.isCollapsed ? '56px' : '224px', // 14rem = 224px, 3.5rem = 56px
    width: `calc(100% - ${sidebarStore.isCollapsed ? '56px' : '224px'})`,
  };
});

// Collections state
const collections = ref([]);
const selectedCollection = ref(null);

// Create collection form
const createError = ref('');
const createSuccess = ref('');

// Tab management
const tabs = [
  { id: 'dashboard', name: 'Dashboard' },
  { id: 'collections', name: 'Search & Exploration' },
  { id: 'create', name: 'Collections Management' },
];
const activeTab = ref('dashboard');





// Check authentication status
const checkAuth = async () => {
  if (isAuthenticated.value) {
    await loadCollections();
  }
};

// Load collections
const loadCollections = async () => {
  try {
    error.value = null;
    collections.value = await fetchCollections();
  } catch (err) {
    console.error('Failed to fetch collections:', err);
    error.value = 'Failed to load collections. Please try again later.';
  }
};

// Select collection
const selectCollection = (collection) => {
  selectedCollection.value = collection;
  // Here you could navigate to a collection detail view
  // router.push(`/collections/${collection.id}`);
};

// Create collection
const handleCreateCollection = async (collectionData) => {
  try {
    await apiCreateCollection(collectionData);
    
    if (this.$refs.managementComponent) {
      this.$refs.managementComponent.setSuccess('Collection created successfully!');
      this.$refs.managementComponent.resetForm();
    }
    
    await loadCollections();
    activeTab.value = 'collections';
  } catch (err) {
    console.error('Failed to create collection:', err);
    if (this.$refs.managementComponent) {
      this.$refs.managementComponent.setError(err.message || 'Failed to create collection');
    }
  }
};

// Delete collection
const deleteCollection = async (collectionId) => {
  if (!confirm('Are you sure you want to delete this collection? This action cannot be undone.')) {
    return;
  }
  
  try {
    await apiDeleteCollection(collectionId);
    await loadCollections();
  } catch (err) {
    console.error('Failed to delete collection:', err);
    error.value = 'Failed to delete collection. Please try again later.';
  }
};

// Format date
const formatDate = (dateString) => new Date(dateString).toLocaleDateString();

// Watch for sidebar changes to update layout
watch(() => sidebarStore.isCollapsed, () => {
  // This will trigger a re-render when sidebar state changes
  // The contentStyle computed property will handle the adjustment
});

// On component mount
onMounted(() => {
  checkAuth();
});
</script>