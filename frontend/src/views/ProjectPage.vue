<template>
  <div 
    class="flex flex-col h-screen overflow-hidden"
    :style="contentStyle"
  >
    <!-- Header with Project Name -->
    <div class="pt-3 pb-4 px-6 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button 
            @click="router.push('/projects')"
            class="text-[var(--secondary-text)] hover:text-[var(--text-color)] transition-colors duration-150"
          >
            <ArrowLeft class="h-5 w-5" />
          </button>
          
          <div v-if="isEditing" class="flex items-center gap-2">
            <input 
              ref="nameInputRef"
              v-model="editedName" 
              type="text" 
              class="text-lg font-medium text-[var(--text-color)] bg-transparent border-b border-[var(--primary-color)] focus:outline-none px-1 min-w-[200px]"
              @keyup.enter="saveProjectName"
              @blur="saveProjectName"
            />
            <button @click="saveProjectName" class="text-[var(--secondary-text)] hover:text-[var(--text-color)] cursor-pointer">
              <Check class="h-4 w-4" />
            </button>
          </div>
          <div v-else class="flex items-center gap-2">
            <h1 class="text-lg font-medium text-[var(--text-color)]">{{ project.name || 'Untitled Project' }}</h1>
            <button 
              @click="startEditing"
              class="text-[var(--secondary-text)] hover:text-[var(--text-color)] cursor-pointer"
            >
              <Edit class="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <button 
            @click="deleteProjectConfirm"
            class="p-2 rounded-lg text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors duration-150 cursor-pointer"
            title="Delete Project"
          >
            <Trash class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Project Content -->
    <div class="flex-1 overflow-hidden bg-[var(--bg-color)]">
      <div class="h-full max-w-7xl mx-auto p-6 flex flex-col md:flex-row gap-6 overflow-y-auto">
        <!-- Loading state -->
        <div v-if="isLoading" class="w-full flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-500"></div>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="w-full flex flex-col items-center justify-center text-center p-8">
          <AlertTriangle class="h-12 w-12 text-red-500 mb-4" />
          <p class="text-[var(--text-color)] mb-2">{{ error }}</p>
          <button 
            @click="fetchProject"
            class="px-4 py-2 bg-[var(--primary-color)] text-white rounded-lg hover:bg-[var(--primary-hover)] transition-colors duration-150"
          >
            Try Again
          </button>
        </div>
        
        <!-- Project details -->
        <template v-else>
          <!-- Left Column - Chat Input & History -->
          <div class="w-full md:w-1/2 flex flex-col gap-4"> 
            
            <!-- Chat Input Area -->
            <div class="bg-[var(--sidebar-bg)] rounded-xl border border-[var(--border-color)] p-4">
              <ChatInputArea 
                v-model="message"
                v-model:files="chatAttachedFiles"
                @send="sendMessage"
                placeholder="Start a new chat about this project..." 
                :show-attachments-above="false"
              />
            </div>

            <!-- Chat History -->
            <div class="bg-[var(--sidebar-bg)] rounded-xl border border-[var(--border-color)] overflow-hidden h-full flex flex-col flex-1">
              <div class="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
                <h2 class="text-[var(--text-color)] font-medium">Chat History</h2>
                <!-- Remove New Chat Button -->
                <!-- <button 
                  @click="startNewChat"
                  class="inline-flex items-center gap-1.5 text-xs text-[var(--secondary-text)] hover:text-[var(--text-color)] py-1 px-2 rounded-lg transition-colors duration-200 hover:bg-[var(--button-hover-lighter)]"
                >
                  <MessageSquarePlus class="h-4 w-4" />
                  <span>New Chat</span>
                </button> -->
              </div>
              
              <div class="flex-1 p-4 overflow-y-auto">
                <!-- Chat List -->
                <div v-if="projectChats.length > 0" class="space-y-2">
                  <div 
                    v-for="chat in projectChats" 
                    :key="chat.id"
                    @click="openChat(chat.id)"
                    class="flex items-center justify-between p-3 border border-[var(--border-color)] rounded-lg bg-[var(--input-bg)] hover:border-[var(--primary-color)] cursor-pointer transition-colors duration-150"
                  >
                    <div class="flex items-center gap-2">
                      <MessageSquare class="h-4 w-4 text-[var(--secondary-text)]" />
                      <div class="flex flex-col">
                        <span class="text-sm text-[var(--text-color)]">{{ chat.title || 'Untitled Chat' }}</span>
                        <span class="text-xs text-[var(--secondary-text)]">{{ formatDate(new Date(chat.created_at)) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Empty State -->
                <div 
                  v-else
                  class="h-full flex flex-col items-center justify-center text-center p-6 text-[var(--secondary-text)]"
                >
                  <MessageSquare class="h-10 w-10 mb-3" />
                  <h3 class="text-[var(--text-color)] font-medium mb-1">No Chats Yet</h3>
                  <p class="text-sm">Start a new chat above to collaborate with AI on this project.</p>
                  <button 
                    @click="startNewChat"
                    class="mt-4 px-4 py-2 bg-[var(--primary-color)] text-white rounded-lg hover:bg-[var(--primary-hover)] transition-colors duration-150 flex items-center gap-2"
                  >

                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Right Column - Custom Instructions & Project Knowledge -->
          <div class="w-full md:w-1/2 flex flex-col gap-4">
            <!-- Custom Instructions (small section) -->
            <div class="bg-[var(--sidebar-bg)] rounded-xl border border-[var(--border-color)] overflow-hidden">
              <div class="p-3 flex items-center justify-between">
                <h2 class="text-[var(--text-color)] text-sm font-medium">Custom Instructions</h2>
                <button 
                  @click="toggleInstructionsPopup"
                  class="text-[var(--secondary-text)] hover:text-[var(--text-color)] p-1 cursor-pointer"
                >
                  <Edit class="h-3.5 w-3.5" />
                </button>
              </div>
              
              <div class="px-3 pb-3">
                <p class="text-xs text-[var(--secondary-text)] line-clamp-2">
                  {{ project.custom_instructions || 'No custom instructions added yet.' }}
                </p>
              </div>
            </div>
            
            <!-- Project Knowledge -->
            <div 
              class="bg-[var(--sidebar-bg)] rounded-xl border border-[var(--border-color)] overflow-hidden flex-1 flex flex-col transition-colors duration-200 cursor-pointer"
              :class="{'drop-zone-active': isDraggingOver}" 
              @dragenter.prevent="handleDragEnter"
              @dragover.prevent="handleDragOver"
              @dragleave.prevent="handleDragLeave"
              @drop.prevent="handleDrop"
              @click="openFileUpload"
            >
              <div class="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
                <h2 class="text-[var(--text-color)] font-medium">Project Knowledge</h2>
                <!-- Add More Documents Button -->
                <button 
                  v-if="project.documents && project.documents.length > 0"
                  @click.stop="openFileUpload" 
                  class="inline-flex items-center gap-1.5 text-xs text-[var(--secondary-text)] hover:text-[var(--text-color)] py-1 px-2 rounded-lg transition-colors duration-200 hover:bg-[var(--button-hover-lighter)]"
                  title="Upload More Documents"
                >
                  <Upload class="h-3.5 w-3.5" />
                  <span>Upload More</span>
                </button>
              </div>
              
              <div class="flex-1 p-4 overflow-y-auto pointer-events-none"> <!-- Added pointer-events-none to inner div -->
                <!-- Documents List -->
                <div v-if="project.documents && project.documents.length > 0">
                  <h3 class="text-sm font-medium text-[var(--secondary-text)] mb-2">Documents</h3>
                  <div class="space-y-2">
                    <div 
                      v-for="doc in project.documents" 
                      :key="doc.doc_id"
                      class="flex items-center justify-between p-2 border border-[var(--border-color)] rounded-lg bg-[var(--input-bg)]"
                    >
                      <div class="flex items-center gap-2">
                        <FileText class="h-4 w-4 text-[var(--secondary-text)]" />
                        <span class="text-sm text-[var(--text-color)]">{{ doc.name }}</span>
                      </div>
                      <div class="flex items-center">
                        <button 
                          @click="viewDocument(doc.doc_id)"
                          class="text-[var(--secondary-text)] hover:text-[var(--text-color)] p-1"
                          title="View Document"
                        >
                          <Eye class="h-4 w-4" />
                        </button>
                        <button 
                          @click="removeDocument(doc.doc_id)"
                          class="text-[var(--secondary-text)] hover:text-red-500 p-1 ml-1"
                          title="Remove Document"
                        >
                          <X class="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Collections List -->
                <div v-if="project.collections && project.collections.length > 0" class="mt-6">
                  <h3 class="text-sm font-medium text-[var(--secondary-text)] mb-2">Collections</h3>
                  <div class="space-y-2">
                    <div 
                      v-for="collection in project.collections" 
                      :key="collection.id"
                      class="flex items-center justify-between p-2 border border-[var(--border-color)] rounded-lg bg-[var(--input-bg)]"
                    >
                      <div class="flex items-center gap-2">
                        <Database class="h-4 w-4 text-[var(--secondary-text)]" />
                        <span class="text-sm text-[var(--text-color)]">{{ collection.name }}</span>
                      </div>
                      <button 
                        @click="removeCollection(collection.id)"
                        class="text-[var(--secondary-text)] hover:text-red-500"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
                
                <!-- Empty State -->
                <div 
                  v-if="(!project.documents || project.documents.length === 0) && (!project.collections || project.collections.length === 0)"
                  class="h-full flex flex-col items-center justify-center text-center p-6 text-[var(--secondary-text)]"
                >
                  <UploadCloud class="h-10 w-10 mb-3" />
                  <h3 class="text-[var(--text-color)] font-medium mb-1">No Knowledge Added</h3>
                  <p class="text-sm">Drag and drop files here or click to upload.</p>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
    
    <!-- Instructions Popup Modal -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showInstructionsPopup" 
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center"
        @click.self="closeInstructionsPopup"
      >
        <div class="bg-[var(--dropdown-bg)] w-96 rounded-lg shadow-xl overflow-hidden">
          <div class="p-4 border-b border-[var(--border-color)] flex items-center justify-between">
            <h3 class="font-medium text-[var(--text-color)]">Custom Instructions</h3>
            <button @click="closeInstructionsPopup" class="text-[var(--secondary-text)] hover:text-[var(--text-color)] cursor-pointer">
              <X class="h-5 w-5" />
            </button>
          </div>
          <div class="p-4">
            <textarea 
              v-model="editedInstructions"
              ref="instructionsTextareaRef"
              class="w-full min-h-[150px] p-3 bg-[var(--input-bg)] border border-[var(--border-color)] rounded-lg text-[var(--text-color)] focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
              placeholder="Add custom instructions for the AI to better assist you with this project..."
            ></textarea>
            <div class="flex justify-end mt-4">
              <button 
                @click="saveInstructionsAndClosePopup"
                class="px-4 py-2 bg-[var(--primary-color)] rounded-lg hover:bg-[var(--primary-hover)] transition-colors duration-150 text-sm cursor-pointer"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    
    <!-- Delete Confirmation Modal -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showDeleteModal" 
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center"
        @click.self="showDeleteModal = false"
      >
        <div class="bg-[var(--dropdown-bg)] w-96 rounded-lg shadow-xl overflow-hidden">
          <div class="p-4 border-b border-[var(--border-color)]">
            <h3 class="font-medium text-[var(--text-color)]">Delete Project</h3>
          </div>
          <div class="p-4">
            <p class="text-sm text-[var(--secondary-text)] mb-4">
              Are you sure you want to delete this project? This action cannot be undone and all associated data will be permanently removed.
            </p>
            <div class="flex justify-end gap-3">
              <button 
                @click="showDeleteModal = false"
                class="px-4 py-2 border border-[var(--border-color)] rounded-lg text-sm hover:bg-[var(--button-hover)] transition-colors duration-150"
              >
                Cancel
              </button>
              <button 
                @click="deleteProject"
                class="px-4 py-2 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 transition-colors duration-150"
              >
                Delete
              </button>
            </div>
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
      accept=".txt,.md,.json,.csv,.js,.ts,.py,.html,.css"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useSidebarStore } from '../stores/sidebarStore';
import { useChatStore } from '../stores/chatStore';
import { 
  ArrowLeft, 
  Edit, 
  Check, 
  Trash, 
  Upload, 
  Eye, 
  X, 
  Database, 
  UploadCloud,
  MessageSquare,
  MessageSquarePlus,
  FileText,
  AlertTriangle
} from 'lucide-vue-next';
import { 
  getProject, 
  updateProject, 
  deleteProject as apiDeleteProject,
  deleteDocumentFromProject,
  addDocumentToProject, 
  getProjectChats, 
  linkChatToProject
} from '../services/projectService';
import { createChat } from '../services/chatService';
import ChatInputArea from '../components/ChatInputArea.vue'; // Import ChatInputArea

const route = useRoute();
const router = useRouter();
const sidebarStore = useSidebarStore();
const chatStore = useChatStore();

// State
const project = ref({
  project_id: '',
  name: '',
  custom_instructions: '',
  documents: [],
  collections: [],
  created_at: '',
  updated_at: ''
});
const projectChats = ref([]);
const isLoading = ref(true);
const error = ref(null);

// Edit states
const isEditing = ref(false);
const editedName = ref('');
const nameInputRef = ref(null);
const editedInstructions = ref('');
const instructionsTextareaRef = ref(null);
const showInstructionsPopup = ref(false);
const showDeleteModal = ref(false);
const debounceTimer = ref(null);

// --- Chat Input State ---
const message = ref('');
const chatAttachedFiles = ref([]); // Assuming FileAttachment interface is needed/available or use basic type

// --- Drag and Drop State ---
const isDraggingOver = ref(false);
const fileInput = ref(null); // Use null initially for template refs

// Define allowed text MIME types
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
  'application/x-python',
  'application/x-sh',
  // Add others if needed
];

// Get project ID from route
const projectId = computed(() => route.params.id);

// Replace the placeholder in fetchProject function
const fetchProject = async () => {
  if (!projectId.value) return;

  isLoading.value = true;
  error.value = null;

  try {
    // Fetch project details
    const data = await getProject(projectId.value);
    project.value = data;
    
    // Fetch chats associated with this project
    try {
      projectChats.value = await getProjectChats(projectId.value);
    } catch (err) {
      console.error('Error fetching project chats:', err);
      projectChats.value = []; // Default to empty array on error
    }
  } catch (err) {
    console.error('Error fetching project:', err);
    error.value = 'Failed to load project details. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

// Editing functions
const startEditing = () => {
  editedName.value = project.value.name || '';
  isEditing.value = true;
  nextTick(() => {
    if (nameInputRef.value) {
      nameInputRef.value.focus();
    }
  });
};

const saveProjectName = async () => {
  if (editedName.value.trim() === '') {
    editedName.value = 'Untitled Project';
  }
  
  isEditing.value = false;
  
  if (editedName.value !== project.value.name) {
    try {
      await updateProject(projectId.value, { name: editedName.value });
      project.value.name = editedName.value;
    } catch (err) {
      console.error('Error updating project name:', err);
      // Show error notification
    }
  }
};

// --- Custom Instructions Handling ---

// Core logic to call the API
const updateInstructionsApiCall = async () => {
  // Avoid saving if the content hasn't actually changed from the last known saved state
  if (editedInstructions.value !== project.value.custom_instructions) {
    try {
      console.log('Attempting to save instructions...'); // Debug log
      await updateProject(projectId.value, { custom_instructions: editedInstructions.value });
      project.value.custom_instructions = editedInstructions.value; // Update local project state on successful save
      console.log('Instructions saved successfully.'); // Debug log
    } catch (err) {
      console.error('Error updating custom instructions:', err);
      // Optionally: Show an error notification to the user
      // Optionally: Revert editedInstructions.value = project.value.custom_instructions; ?
    }
  } else {
    console.log('Instructions unchanged, skipping save.'); // Debug log
  }
};

// Function called by the explicit "Save" button
const saveInstructionsAndClosePopup = () => {
  clearTimeout(debounceTimer.value); // Clear any pending auto-save
  updateInstructionsApiCall(); // Save immediately
  showInstructionsPopup.value = false; // Close the popup
};

// Function to handle closing the popup without explicit save (X button, clicking outside)
const closeInstructionsPopup = () => {
  // Optional: Decide if you want to trigger a save on manual close, or discard changes.
  // Current implementation will rely on auto-save having already triggered or changes being discarded.
  // To save on close:
  // clearTimeout(debounceTimer.value);
  // updateInstructionsApiCall(); 

  // To discard changes since last auto-save:
  editedInstructions.value = project.value.custom_instructions; // Reset to last known saved state

  showInstructionsPopup.value = false;
  clearTimeout(debounceTimer.value); // Clear timer regardless
};

const toggleInstructionsPopup = () => {
  showInstructionsPopup.value = !showInstructionsPopup.value;
  
  if (showInstructionsPopup.value) {
    editedInstructions.value = project.value.custom_instructions || ''; // Load current instructions
    nextTick(() => {
      instructionsTextareaRef.value?.focus();
    });
  } else {
    // If closing, clear any pending auto-save timer
    clearTimeout(debounceTimer.value);
    // Optional: decide whether to trigger save or discard changes when toggling closed, similar to closeInstructionsPopup
    // editedInstructions.value = project.value.custom_instructions; // Example: discard changes on toggle close
  }
};

// Watch for changes in the instructions textarea for auto-save
watch(editedInstructions, (newValue, oldValue) => {
  // Only run when the popup is open and the value has actually changed
  if (showInstructionsPopup.value && newValue !== oldValue && newValue !== project.value.custom_instructions) {
    clearTimeout(debounceTimer.value);
    debounceTimer.value = setTimeout(() => {
      console.log('Debounce timer fired, calling API save...'); // Debug log
      updateInstructionsApiCall();
    }, 1500); // Auto-save after 1.5 seconds of inactivity
  }
});

// Clear the timer when the component is unmounted
onUnmounted(() => {
  clearTimeout(debounceTimer.value);
});

// Delete functions
const deleteProjectConfirm = () => {
  showDeleteModal.value = true;
};

const deleteProject = async () => {
  try {
    await apiDeleteProject(projectId.value);
    showDeleteModal.value = false;
    router.push('/projects');
  } catch (err) {
    console.error('Error deleting project:', err);
    // Show error notification
  }
};

// --- Drag and Drop / File Upload Handlers ---

const handleDragEnter = (event) => {
  isDraggingOver.value = true;
};

const handleDragOver = (event) => {
  // Necessary to allow dropping
};

const handleDragLeave = (event) => {
  const relatedTarget = event.relatedTarget;
  if (!event.currentTarget.contains(relatedTarget)) {
    isDraggingOver.value = false;
  }
};

const handleDrop = async (event) => {
  isDraggingOver.value = false;
  if (event.dataTransfer?.files) {
    await processFiles(event.dataTransfer.files);
  }
};

const openFileUpload = () => {
  fileInput.value?.click();
};

const handleFileUpload = async (event) => {
  const input = event.target;
  if (input.files) {
    await processFiles(input.files);
  }
  if (input) {
    input.value = ''; // Reset input
  }
};

// Process Files (Check type, Read, Call API)
const processFiles = async (fileList) => {
  if (!fileList) return;

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];

    // Check MIME type
    if (!allowedTextMimeTypes.includes(file.type.toLowerCase()) && !file.type.startsWith('text/')) {
      console.warn(`Skipping file '${file.name}' due to unsupported text type: ${file.type}`);
      alert(`Skipping file '${file.name}': Cannot read content of type ${file.type} as text.`);
      continue; 
    }

    // Read file content as text
    const reader = new FileReader();
    reader.onload = async (e) => {
      if (e.target?.result) {
        try {
          const fileContent = e.target.result;
          const fileType = file.type || 'text/plain';
          
          console.log(`Uploading document: ${file.name}`);
          const response = await addDocumentToProject(projectId.value, {
            name: file.name,
            content: fileContent,
            file_type: fileType
          });
          console.log('Document uploaded successfully:', response);
          
          // Update local state immediately
          project.value.documents.push({
            doc_id: response.doc_id,
            name: response.name,
            file_type: response.file_type
          });

        } catch (err) {
          console.error(`Error uploading document '${file.name}':`, err);
          alert(`Failed to upload document '${file.name}': ${err instanceof Error ? err.message : String(err)}`);
        }
      } else {
        console.error(`Error reading file '${file.name}': FileReader result is null`);
        alert(`Could not read file '${file.name}'.`);
      }
    };
    reader.onerror = (e) => {
      console.error(`Error reading file '${file.name}':`, reader.error);
      alert(`Error reading file '${file.name}'.`);
    };
    reader.readAsText(file); 
  }
};

// Document management
const viewDocument = (docId) => {
  // Implement document viewer or navigate to document view
  console.log('View document:', docId);
};

const removeDocument = async (docId) => {
  try {
    await deleteDocumentFromProject(projectId.value, docId);
    
    // Update local state
    project.value.documents = project.value.documents.filter(doc => doc.doc_id !== docId);
  } catch (err) {
    console.error('Error removing document:', err);
    // Show error notification
  }
};

const removeCollection = (collectionId) => {
  // Implement collection removal logic
  console.log('Remove collection:', collectionId);
  
  // Update local state
  project.value.collections = project.value.collections.filter(col => col.id !== collectionId);
};

// --- Open Chat Function ---
const openChat = (chatId) => {
  if (!chatId) {
    console.error('Attempted to open chat with invalid ID');
    return;
  }
  router.push({
    name: 'Chat', // Assuming your chat route is named 'Chat'
    params: { id: chatId }
  });
};

// --- Send Message from Input Area ---
const sendMessage = async () => {
  const currentTimestamp = new Date().toISOString();

  // Ensure message or files exist
  if (!message.value.trim() && chatAttachedFiles.value.length === 0) return;

  try {
    // 1. Create a new chat session
    const chatResponse = await createChat(); // createChat might need adjustments if it expects initial message data

    if (chatResponse && chatResponse.chat_id) {
      const chatId = chatResponse.chat_id;

      // 2. Link the new chat to the current project
      await linkChatToProject(projectId.value, chatId);
      console.log(`Chat ${chatId} linked to project ${projectId.value}`);

      // 3. Prepare context data (message, files, project info)
      //    (Assuming FileAttachment structure is compatible or simplified)
      const filesForAPI = await Promise.all(chatAttachedFiles.value.map(async (attachment) => {
        // Logic to read file content if needed (e.g., base64 or text)
        // This example assumes content is already handled or not needed for initial context passing
        let content = attachment.content;
        if (attachment.file && !content) { // Example: read if File object exists but content is missing
           content = await readFileAsBase64(attachment.file); // Needs readFileAsBase64 helper
        }
        return {
          name: attachment.name,
          content: content || '', // Ensure content is a string
          // type: attachment.type // Include type if available/needed
        };
      }));

      const contextData = {
        messageText: message.value.trim(),
        files: filesForAPI.length > 0 ? filesForAPI : undefined,
        projectId: projectId.value,
        projectName: project.value.name, // Pass project name context
        customInstructions: project.value.custom_instructions // Pass instructions context
      };

      // 4. Add chat to the store for sidebar update
      const newChatInfo = {
        chat_id: chatId,
        name: message.value.trim().substring(0, 50) || (filesForAPI.length > 0 ? filesForAPI[0].name : 'New Project Chat'),
        updated_at: currentTimestamp,
      };
      chatStore.addChat(newChatInfo);

      // ALSO update the local projectChats list for immediate UI feedback
      projectChats.value.unshift(newChatInfo);

      // 5. Store context data (handle potential size issues)
      const storageKey = `chat_context_${chatId}`;
      try {
        const serializedData = JSON.stringify(contextData);
        if (serializedData.length < 4 * 1024 * 1024) { 
          localStorage.setItem(storageKey, serializedData);
        } else {
          console.warn("Context data too large for localStorage, using sessionStorage.");
          sessionStorage.setItem(storageKey, serializedData);
        }
      } catch (e) {
        console.error('Error storing context data:', e);
        sessionStorage.setItem(`${storageKey}_error`, `Storage error: ${e instanceof Error ? e.message : String(e)}`);
      }

      // 6. Clear the input area state
      message.value = '';
      chatAttachedFiles.value = [];

      // 7. Navigate to the new chat
      router.push({
        name: 'Chat',
        params: { id: chatId }
      });

    } else {
      console.error("Error: Chat ID not returned from createChat API.");
      alert("Failed to create a new chat session. Please try again.");
    }
  } catch (error) {
    console.error('Error sending message or creating chat:', error);
    alert(`An error occurred while starting the chat: ${error instanceof Error ? error.message : String(error)}`);
  }
};

/**
 * Reads a File object and returns its content as a Base64 encoded string (without the data: URL prefix).
 * @param {File} file - The file to read.
 * @returns {Promise<string>} A promise that resolves with the base64 string or rejects with an error.
 */
const readFileAsBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (reader.result) {
        // Result is Data URL (e.g., 'data:text/plain;base64,SGVsbG8=')
        // Often you only need the base64 part after the comma
        const base64String = reader.result.split(',')[1];
        resolve(base64String || ''); // Return empty string if split fails
      } else {
        reject(new Error('Failed to read file content'));
      }
    };
    reader.onerror = () => reject(reader.error || new Error('File read error'));
    reader.readAsDataURL(file); // Read as data URL
  });
};

// Fetch data when component mounts
onMounted(() => {
  fetchProject();
});

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
  try {
    return new Intl.DateTimeFormat('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    }).format(date);
  } catch (e) {
    console.error('Error formatting date:', e);
    return 'Unknown date';
  }
};
</script>

<style scoped>
textarea {
  min-height: 100px;
}

textarea::placeholder {
  color: var(--secondary-text);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}
</style>