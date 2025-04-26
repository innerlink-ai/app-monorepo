<template>
  <div 
    class="flex flex-col h-screen overflow-hidden"
    :style="contentStyle"
  >
    <!-- Header with Project Name Input -->
    <div class="pt-3 pb-4 px-6 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Layers class="h-5 w-5 text-[var(--secondary-text)] stroke-[1]" />
          <h2 class="text-lg font-light text-[var(--secondary-text)]">New Project</h2>
        </div>
        
        <div class="flex items-center gap-4">
          <div class="w-[300px]">
            <input 
              id="project-name"
              v-model="projectName"
              type="text"
              placeholder="Enter project name"
              required
              class="w-full p-2.5 border border-[var(--border-color)] rounded-lg text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-[var(--input-bg)]"
              aria-required="true"
            />
          </div>
          
        <button 
          @click="saveProject"
          class="py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg transition-all duration-200 flex items-center gap-2 text-sm"
          :disabled="!projectName.trim() || isSaving"
          :class="{
            'opacity-50 cursor-not-allowed': !projectName.trim() || isSaving,
            'hover:opacity-90 cursor-pointer': projectName.trim() && !isSaving
          }"
        >
          <template v-if="isSaving"> 
            <div class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            <span>Creating...</span>
          </template>
          <template v-else>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/>
              <polyline points="7 3 7 8 15 8"/>
            </svg>
            <span>Create Project</span>
          </template>
        </button>
      </div>
        </div>
        </div>

    <!-- Two Columns Section -->
    <div class="flex-1 flex overflow-hidden bg-[var(--bg-color)]">
      <div class="max-w-7xl w-full mx-auto p-6 flex gap-6 overflow-y-auto">
        <!-- Left Column - Project Knowledge -->
        <div class="flex-1 min-w-0">
          <div 
            class="bg-[var(--sidebar-bg)] rounded-xl border border-[var(--border-color)] overflow-hidden h-full flex flex-col transition-colors duration-200 cursor-pointer"
            :class="{'drop-zone-active': isDraggingOver}"
            @dragenter.prevent="handleDragEnter"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
            @click="openFileUpload"
          >
            <div class="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
              <h2 class="text-[var(--text-color)] font-medium">Project Knowledge</h2>
              <div class="flex items-center gap-2">
                <!-- Add More Documents Button -->
                <button 
                  v-if="attachedFiles.length > 0" 
                  @click.stop="openFileUpload"
                  class="inline-flex items-center gap-1.5 text-xs text-[var(--secondary-text)] hover:text-[var(--text-color)] py-1 px-2 rounded-lg transition-colors duration-200 hover:bg-[var(--button-hover-lighter)]"
                  title="Upload More Documents"
                >
                  <Upload class="h-3.5 w-3.5" />
                  <span>Upload More</span>
                </button>
                
                <!-- Add Collection Button - COMMENTED OUT -->
                <!--
                <button 
                  @click="openCollectionsModal"
                  class="inline-flex items-center gap-1.5 text-xs text-[var(--secondary-text)] hover:text-[var(--text-color)] py-1 px-2 rounded-lg transition-colors duration-200 hover:bg-[var(--button-hover-lighter)]"
                  title="Add Collection"
                >
                  <Layers class="w-4 h-4 stroke-[1.5]" />
                  <span>Add Collection</span>
                </button>
                -->
                
                <!-- Upload Document Button - REMOVED -->
              </div>
            </div>

            <div class="flex-1 p-4 overflow-y-auto pointer-events-none">
          <!-- Collections List -->
              <div v-if="selectedCollections.length > 0" class="mb-6">
                <h3 class="text-sm font-medium text-[var(--secondary-text)] mb-2">Collections</h3>
          <div class="space-y-2">
            <div 
              v-for="(collection, index) in selectedCollections" 
              :key="index"
              class="flex items-center justify-between p-2 border border-[var(--border-color)] rounded-lg bg-[var(--input-bg)]"
            >
              <div class="flex items-center gap-2">
                <Layers class="h-4 w-4 text-[var(--secondary-text)]" />
                      <span class="text-sm text-[var(--text-color)]">{{ collection.name }}</span>
              </div>
              <button 
                @click="removeCollection(index)"
                class="text-[var(--secondary-text)] hover:text-[var(--text-color)]"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
                  </div>
                </div>
              </div>
              
              <!-- Attached Files List -->
              <div v-if="attachedFiles.length > 0">
                <h3 class="text-sm font-medium text-[var(--secondary-text)] mb-2">Attached Documents</h3>
                <div class="space-y-2">
                  <div 
                    v-for="(file, index) in attachedFiles" 
                    :key="index"
                    class="flex items-center justify-between p-2 border border-[var(--border-color)] rounded-lg bg-[var(--input-bg)]"
                  >
                    <div class="flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                        <polyline points="14 2 14 8 20 8"/>
                      </svg>
                      <span class="text-sm text-[var(--text-color)]">{{ file.name }}</span>
                    </div>
                    <button 
                      @click="removeFile(index)"
                      class="text-[var(--secondary-text)] hover:text-[var(--text-color)]"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M18 6L6 18M6 6l12 12"/>
                      </svg>
                    </button>
                  </div>
                </div>
            </div>

            <!-- Empty State / Upload Instruction -->
            <div 
                v-if="selectedCollections.length === 0 && attachedFiles.length === 0"
                class="h-full flex flex-col items-center justify-center text-center p-6 text-[var(--secondary-text)] pointer-events-none"
              >
                <UploadCloud class="h-10 w-10 mb-3" />
                <h3 class="text-[var(--text-color)] font-medium mb-1">Upload Knowledge</h3>
                <p class="text-sm">
                  Drag and drop files here or click to upload.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column - Custom Instructions -->
        <div class="flex-1 min-w-0">
          <div class="bg-[var(--sidebar-bg)] rounded-xl border border-[var(--border-color)] overflow-hidden h-full flex flex-col">
            <div class="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
              <h2 class="text-[var(--text-color)] font-medium">Custom Instructions</h2>
            </div>
            
            <div class="flex-1 p-4">
              <textarea 
                v-model="customInstructions"
                placeholder="Add custom instructions for the AI to better assist you with this project. For example:
- Specific requirements or constraints
- Preferred coding style or frameworks
- Background information
- Performance considerations"
                class="w-full h-full p-3 bg-[var(--input-bg)] border border-[var(--border-color)] rounded-lg text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Collections Modal -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showCollectionsModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center" @click.self="showCollectionsModal = false">
        <div class="bg-[var(--dropdown-bg)] w-80 rounded-lg shadow-xl border border-[var(--border-color)]">
          <div class="flex items-center justify-between p-3 border-b border-[var(--border-color)]">
            <h3 class="font-medium text-[var(--text-color)]">Collections</h3>
            <button @click="showCollectionsModal = false" class="text-[var(--secondary-text)] hover:text-[var(--text-color)]">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6 6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
          
          <div class="p-2 border-b border-[var(--border-color)]">
            <input 
              type="text" 
              v-model="collectionSearch" 
              placeholder="Search collections..." 
              class="w-full p-2 text-sm rounded-md border border-[var(--border-color)] bg-[var(--prompt-bg)] text-[var(--text-color)]"
            />
          </div>
          
          <div class="max-h-60 overflow-y-auto py-1">
            <div v-if="isLoadingCollections" class="px-3 py-6 text-sm text-center">
              <div class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-[var(--text-color)]"></div>
              <div class="mt-2">Loading collections...</div>
            </div>
            <div v-else-if="collectionsError" class="px-3 py-4 text-sm text-[var(--secondary-text)] text-center">
              <div class="text-red-500">{{ collectionsError }}</div>
              <button @click="fetchCollections" class="mt-2 text-blue-500 hover:underline">Try again</button>
            </div>
            <div v-else-if="filteredCollections.length === 0" class="px-3 py-2 text-sm text-[var(--secondary-text)] text-center">
              No collections found
            </div>
            <button 
              v-for="collection in filteredCollections" 
              :key="collection.id"
              @click="selectCollectionFromModal(collection)"
              class="w-full text-left px-3 py-2 text-sm hover:bg-[var(--button-hover)] transition-colors duration-200"
            >
              {{ collection.name }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Hidden file input -->
    <input 
      type="file" 
      ref="fileInput" 
      @change="handleFileUpload" 
      multiple 
      hidden
      accept=".txt,.md,.json,.csv,.js,.ts,.py,.html,.css,.pdf,.docx,.doc,.xls,.xlsx,.ppt,.pptx,.rtf,.xml,.yaml,.yml,.toml,.ini,.properties" 
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Layers, Database, UploadCloud, Upload } from 'lucide-vue-next';
import { useSidebarStore } from '../stores/sidebarStore';
import { collectionsService } from '../services/collectionService';
import { createChat } from '../services/chatService';
import ChatInputArea from '../components/ChatInputArea.vue';
import { createProject, linkChatToProject } from '../services/projectService';

// Router and Sidebar setup
const router = useRouter();
const sidebarStore = useSidebarStore();

// Project data
const projectName = ref('');
const customInstructions = ref('');
const isSaving = ref(false);

// File handling
const fileInput = ref<HTMLInputElement | null>(null);
const isDraggingOver = ref(false);

// Types
interface Collection {
  id: string;
  name: string;
  description?: string;
}

interface FileAttachment {
  name: string;
  content: string;
  type?: string;
}

// Project Knowledge Files
const attachedFiles = ref<FileAttachment[]>([]);

// Define allowed text MIME types (adjust as needed)
const allowedTextMimeTypes = [
  'text/plain',
  'text/markdown',
  'text/csv',
  'text/html',
  'text/css',
  'text/javascript',
  'application/json',
  'application/xml',
  'text/xml',
  'application/x-yaml',
  'text/yaml',
  'application/x-python', // Common for .py
  'application/x-sh', // Common for shell scripts
  // Add others like application/typescript, etc. if needed
];

const processFiles = async (fileList: FileList) => {
  if (!fileList) return;

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];

    // Check if the file type is allowed for reading as text
    if (!allowedTextMimeTypes.includes(file.type.toLowerCase()) && !file.type.startsWith('text/')) {
      console.warn(`Skipping file '${file.name}' due to unsupported text type: ${file.type}`);
      alert(`Skipping file '${file.name}': Cannot read content of type ${file.type} as text.`);
      continue; // Skip to the next file
    }

    // Read file content as text
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        attachedFiles.value.push({
          name: file.name,
          content: e.target.result as string,
          type: file.type
        });
      }
    };
    reader.onerror = (e) => {
      console.error("Error reading file:", file.name, e);
      // Optionally show an error to the user
    };
    reader.readAsText(file); // Read as text
  }
};

const openFileUpload = () => {
  fileInput.value?.click();
};

const handleFileUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files) {
    await processFiles(input.files);
  }
  // Reset the input value to allow selecting the same file again
  if (input) {
    input.value = ''; 
  }
};

// Collections
const collections = ref<Collection[]>([]);
const selectedCollections = ref<Collection[]>([]);
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
  // Check if the collection already exists
  if (!selectedCollections.value.some(c => c.id === collection.id)) {
    selectedCollections.value.push(collection);
  }
  showCollectionsModal.value = false;
};

const removeCollection = (index: number) => {
  selectedCollections.value.splice(index, 1);
};

// Drag and Drop Handlers
const handleDragEnter = (event: DragEvent) => {
  isDraggingOver.value = true;
};

const handleDragOver = (event: DragEvent) => {
  // This is necessary to allow dropping
  // No specific action needed here beyond preventDefault in the template
};

const handleDragLeave = (event: DragEvent) => {
  // Add a check to ensure we are leaving the intended drop zone, not just moving over a child element
  const relatedTarget = event.relatedTarget as Node;
  if (!(event.currentTarget as Node)?.contains(relatedTarget)) {
    isDraggingOver.value = false;
  }
};

const handleDrop = async (event: DragEvent) => {
  isDraggingOver.value = false;
  if (event.dataTransfer?.files) {
    await processFiles(event.dataTransfer.files);
  }
};

const removeFile = (index: number) => {
  attachedFiles.value.splice(index, 1);
};

// Add saveProject function back
const saveProject = async (): Promise<string | null> => {
  if (isSaving.value) return null;
  isSaving.value = true;

  console.log("Create Project button clicked."); 
  console.log("Project Name:", projectName.value);

  if (!projectName.value.trim()) {
    alert('Please enter a project name');
    isSaving.value = false; // Reset saving state
    return null;
  }
  
  try {
    // Prepare project data
    const projectData = {
      name: projectName.value,
      custom_instructions: customInstructions.value,
      documents: attachedFiles.value.map(f => ({ name: f.name, content: f.content, file_type: f.type })), 
    };
    
    console.log('Saving project data:', projectData);
    
    console.log('Calling createProject API service...');
    const response = await createProject(projectData);
    console.log('createProject API response:', response);
    
    if (response && response.project_id) {
      console.log(`Project saved successfully with ID: ${response.project_id}`);
      // Navigate to the new project's page
      router.push(`/projects/${response.project_id}`); 
      return response.project_id;
    } else {
      throw new Error('Project ID not found in API response');
    }

  } catch (error) {
    console.error('Failed to save project:', error);
    alert(`Failed to save project: ${error instanceof Error ? error.message : String(error)}`);
    return null;
  } finally {
    isSaving.value = false;
  }
};

// Computed styles for the content area
const contentStyle = computed(() => ({
  marginLeft: sidebarStore.isCollapsed ? "3.5rem" : "14rem",
  transition: "margin-left 0.3s ease",
  width: `calc(100% - ${sidebarStore.isCollapsed ? "3.5rem" : "14rem"})`,
  position: "fixed" as const,
  top: 0,
  right: 0,
  bottom: 0,
}));
</script> 

<style scoped>
textarea::placeholder {
  color: var(--secondary-text);
}

textarea {
  min-height: 40px;
}

/* Styles for drag-and-drop */
.drop-zone-active {
  border-style: dashed;
  border-color: var(--primary-color, #3b82f6); /* Use primary color or fallback */
  background-color: rgba(59, 130, 246, 0.1); /* Light blue background */
}
</style> 