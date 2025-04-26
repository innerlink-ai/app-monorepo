// VectorDashboard.vue
<template>
  <div class="bg-[var(--prompt-bg)] text-[var(--text-color)] w-full p-6 rounded-xl shadow-sm transition-all duration-200 border border-[var(--border-color)]">
    <h2 class="text-sm font-semibold mb-4">Dashboard</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <!-- Total Collections Card -->
      <div class="bg-[var(--chat-bg)] rounded-lg p-4 shadow-sm">
        <h3 class="text-xs font-medium text-gray-500 mb-1">Total Collections</h3>
        <p class="text-2xl font-semibold">{{ collections.length }}</p>
      </div>
      
      <!-- Total Vectors Card -->
      <div class="bg-[var(--chat-bg)] rounded-lg p-4 shadow-sm">
        <h3 class="text-xs font-medium text-gray-500 mb-1">Total Vectors</h3>
        <p class="text-2xl font-semibold">{{ totalVectors }}</p>
      </div>
      
      <!-- Average Response Time Card (placeholder) -->
      <div class="bg-[var(--chat-bg)] rounded-lg p-4 shadow-sm">
        <h3 class="text-xs font-medium text-gray-500 mb-1">Avg. Query Time</h3>
        <p class="text-2xl font-semibold">12ms</p>
      </div>
    </div>
    
    <div class="bg-[var(--chat-bg)] rounded-lg p-4 shadow-sm mb-6">
      <h3 class="text-xs font-medium mb-3">Collection Size Distribution</h3>
      <div class="h-40 flex items-end space-x-2">
        <div v-for="collection in collections" :key="collection.id" class="relative flex-1 group">
          <div 
            class="bg-[#55B867] hover:bg-[#4da45b] transition-colors rounded-t-sm" 
            :style="{ height: `${(collection.count / maxVectorCount) * 100}%` }"
          ></div>
          <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full mt-1 text-[10px] truncate w-full text-center">
            {{ collection.name.substring(0, 8) }}{{ collection.name.length > 8 ? '...' : '' }}
          </div>
          <div class="hidden group-hover:block absolute bottom-full left-1/2 transform -translate-x-1/2 bg-black bg-opacity-75 text-white text-xs rounded px-2 py-1 mb-1 whitespace-nowrap">
            {{ collection.name }}: {{ collection.count }} vectors
          </div>
        </div>
      </div>
    </div>
    
    <div class="bg-[var(--chat-bg)] rounded-lg p-4 shadow-sm">
      <h3 class="text-xs font-medium mb-3">Recent Activity</h3>
      <div class="text-xs text-center text-gray-500 py-4">
        Activity tracking will be available soon.
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Props
const props = defineProps({
  collections: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Computed properties
const totalVectors = computed(() => {
  return props.collections.reduce((sum, collection) => sum + collection.count, 0);
});

// Get the maximum vector count for the dashboard chart scaling
const maxVectorCount = computed(() => {
  if (props.collections.length === 0) return 100; // Default if no collections
  return Math.max(...props.collections.map(collection => collection.count || 0));
});
</script>