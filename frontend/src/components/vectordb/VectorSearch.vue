// VectorSearch.vue
<template>
  <div class="bg-[var(--prompt-bg)] text-[var(--text-color)] w-full p-6 rounded-xl shadow-sm transition-all duration-200 border border-[var(--border-color)] mb-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-sm font-semibold">Search & Exploration</h2>
      <div class="relative">
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search collections..."
          class="w-full pl-8 pr-3 py-1.5 text-xs border border-[var(--border-color)] rounded-lg bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[#55B867] focus:ring-1 focus:ring-[#55B867] transition-colors duration-200"
        />
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </div>
    </div>
    
    <div v-if="collections.length === 0" class="flex flex-col items-center justify-center py-8">
      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-gray-400 mb-2">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
        <rect x="3" y="8" width="4" height="4"></rect>
        <rect x="13" y="8" width="4" height="4"></rect>
        <rect x="8" y="14" width="4" height="4"></rect>
      </svg>
      <p class="text-xs text-center">No collections found. Create your first collection.</p>
    </div>
    
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <div 
        v-for="collection in filteredCollections" 
        :key="collection.id"
        class="border border-[var(--border-color)] rounded-lg p-3 hover:shadow-sm transition-shadow cursor-pointer"
        @click="selectCollection(collection)"
      >
        <div class="flex items-start justify-between">
          <div>
            <h3 class="text-xs font-medium">{{ collection.name }}</h3>
            <p class="text-xs text-gray-500 mt-1">{{ collection.description || 'No description' }}</p>
          </div>
          <div class="bg-[#55B867] bg-opacity-10 text-[#55B867] text-[10px] px-2 py-0.5 rounded-full">
            {{ collection.count }} vectors
          </div>
        </div>
        <div class="flex items-center justify-between mt-3 text-[10px] text-gray-500">
          <span>Created: {{ formatDate(collection.created_at) }}</span>
          <button 
            @click.stop="deleteCollection(collection.id)"
            class="text-red-500 hover:text-red-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// Props
const props = defineProps({
  collections: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Emits
const emit = defineEmits(['selectCollection', 'deleteCollection']);

// Search state
const searchQuery = ref('');

// Computed properties
const filteredCollections = computed(() => {
  if (!searchQuery.value) {
    return props.collections;
  }
  
  const query = searchQuery.value.toLowerCase();
  return props.collections.filter(collection => 
    collection.name.toLowerCase().includes(query) || 
    (collection.description && collection.description.toLowerCase().includes(query))
  );
});

// Functions
const selectCollection = (collection) => {
  emit('selectCollection', collection);
};

const deleteCollection = (collectionId) => {
  emit('deleteCollection', collectionId);
};

// Format date
const formatDate = (dateString) => new Date(dateString).toLocaleDateString();
</script>