// CollectionsManagement.vue
<template>
  <div class="bg-[var(--prompt-bg)] text-[var(--text-color)] w-full p-6 rounded-xl shadow-sm transition-all duration-200 border border-[var(--border-color)]">
    <h2 class="text-sm font-semibold mb-4">Collections Management</h2>
    
    <div class="space-y-4">
      <div>
        <label for="collection-name" class="block text-xs font-medium mb-1">
          Collection Name
        </label>
        <input
          id="collection-name"
          v-model="newCollection.name"
          type="text"
          placeholder="Enter collection name"
          class="w-full px-4 py-2 border border-gray-300 rounded-md bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[#55B867] focus:ring-2 focus:ring-[#55B867] transition-colors duration-200"
        />
      </div>
      
      <div>
        <label for="collection-description" class="block text-xs font-medium mb-1">
          Description (Optional)
        </label>
        <textarea
          id="collection-description"
          v-model="newCollection.description"
          rows="3"
          placeholder="Enter collection description"
          class="w-full px-4 py-2 border border-gray-300 rounded-md bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[#55B867] focus:ring-2 focus:ring-[#55B867] transition-colors duration-200"
        ></textarea>
      </div>
      
      <div>
        <label for="collection-type" class="block text-xs font-medium mb-1">
          Collection Type
        </label>
        <select
          id="collection-type"
          v-model="newCollection.type"
          class="w-full px-4 py-2 border border-gray-300 rounded-md bg-[var(--prompt-bg)] text-[var(--text-color)] focus:outline-none focus:border-[#55B867] focus:ring-2 focus:ring-[#55B867] transition-colors duration-200"
        >
          <option value="text">Text</option>
          <option value="image">Image</option>
          <option value="hybrid">Hybrid</option>
        </select>
      </div>
      
      <div>
        <label class="block text-xs font-medium mb-1">
          Advanced Options
        </label>
        <div class="border border-[var(--border-color)] rounded-md p-3">
          <div class="flex items-center mb-2">
            <input
              id="metadata-toggle"
              v-model="newCollection.enableMetadata"
              type="checkbox"
              class="h-4 w-4 text-[#55B867] focus:ring-[#55B867] border-gray-300 rounded"
            />
            <label for="metadata-toggle" class="ml-2 text-xs">
              Enable metadata storage
            </label>
          </div>
          <div class="flex items-center">
            <input
              id="similarity-toggle"
              v-model="newCollection.useCosine"
              type="checkbox"
              class="h-4 w-4 text-[#55B867] focus:ring-[#55B867] border-gray-300 rounded"
            />
            <label for="similarity-toggle" class="ml-2 text-xs">
              Use cosine similarity (default: Euclidean)
            </label>
          </div>
        </div>
      </div>
    </div>
    
    <div class="mt-6 flex flex-col md:flex-row items-center justify-between">
      <button 
        @click="createCollection"
        class="py-2 px-6 bg-[#55B867] text-white rounded-xl hover:bg-[#4da45b] transition-colors duration-200 font-medium shadow-sm"
      >
        Create Collection
      </button>
      <div class="mt-2 md:mt-0 text-right">
        <p v-if="createError" class="text-red-500 text-xs">{{ createError }}</p>
        <p v-if="createSuccess" class="text-xs text-green-600">{{ createSuccess }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Props
const props = defineProps({
  onCollectionCreated: {
    type: Function,
    default: () => {}
  }
});

// Emits
const emit = defineEmits(['createCollection']);

// Form state
const newCollection = ref({
  name: '',
  description: '',
  type: 'text',
  enableMetadata: true,
  useCosine: false
});
const createError = ref('');
const createSuccess = ref('');

// Create collection
const createCollection = async () => {
  createError.value = '';
  createSuccess.value = '';
  
  if (!newCollection.value.name) {
    createError.value = 'Collection name is required';
    return;
  }
  
  try {
    emit('createCollection', {
      name: newCollection.value.name,
      description: newCollection.value.description,
      type: newCollection.value.type,
      metadata_enabled: newCollection.value.enableMetadata,
      similarity_metric: newCollection.value.useCosine ? 'cosine' : 'euclidean'
    });
    
    createSuccess.value = 'Collection created successfully!';
    resetForm();
  } catch (err) {
    console.error('Failed to create collection:', err);
    createError.value = err.message || 'Failed to create collection';
  }
};

const resetForm = () => {
  newCollection.value = {
    name: '',
    description: '',
    type: 'text',
    enableMetadata: true,
    useCosine: false
  };
};

// Expose methods to parent
defineExpose({
  resetForm,
  setError: (error) => {
    createError.value = error;
  },
  setSuccess: (message) => {
    createSuccess.value = message;
  }
});
</script>