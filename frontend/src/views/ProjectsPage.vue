<template>
  <div 
    class="flex flex-col h-screen overflow-hidden"
    :style="contentStyle"
  >
    <!-- Header Section -->
    <div class="pt-3 pb-4 px-6 border-b border-[var(--border-color)] bg-[var(--bg-color)]">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <!-- Title and Info Button Wrapper -->
        <div 
          class="flex items-center gap-2 relative" 
          ref="infoContainerRef"
          @mouseleave="closeInfoPopup"
        >
          <Layers class="h-5 w-5 text-[var(--secondary-text)] stroke-[1]" />
          <h2 class="text-lg font-light text-[var(--secondary-text)]">Projects</h2>
          <button
            ref="infoButtonRef"
            @click.stop="toggleInfoPopup"
            @mouseenter="openInfoPopup"
            class="p-1 rounded-full text-[var(--secondary-text)] hover:text-[var(--text-color)] hover:bg-[var(--button-hover)] focus:outline-none transition-colors duration-150"
            title="About Projects"
          >
            <Info class="h-4 w-4" />
          </button>
          <!-- Info Popup -->
          <Transition name="fade">
            <div 
              v-if="showInfoPopup"
              ref="infoPopupRef"
              class="absolute top-full left-0 mt-2 w-64 p-3 bg-[var(--dropdown-bg)] border border-[var(--border-color)] rounded-lg shadow-lg z-10 text-sm text-[var(--text-color)]"
            >
            Securely store your sensitive information in encrypted folders so that they can be accessed across multiple conversations.
            </div>
          </Transition>
        </div>
        <button 
          @click="createNewProject"
          class="py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:opacity-90 cursor-pointer transition-all duration-200 flex items-center gap-2 text-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>New Project</span>
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
              placeholder="Search projects..." 
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

        <!-- Projects Content -->
        <div class="bg-[var(--bg-color)] transition-all duration-200">
          <!-- Loading state -->
          <div v-if="isLoading" class="p-8 text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-500 mx-auto"></div>
            <p class="text-sm mt-3">Loading projects...</p>
          </div>

          <!-- Error state -->
          <div v-else-if="error" class="p-8 text-center text-[var(--secondary-text)]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm">{{ error }}</p>
            <button @click="fetchProjects" class="text-sm text-[var(--primary-color)] hover:text-[var(--primary-hover)] mt-2">Try again</button>
          </div>

          <!-- Empty state -->
          <div v-else-if="filteredProjects.length === 0" class="p-8 text-center text-[var(--secondary-text)]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p class="text-sm">No projects found</p>
            <p class="text-xs mt-1">Create your first project to get started</p>
          </div>

          <!-- Projects Grid -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="project in filteredProjects" 
              :key="project.id"
              class="relative group border border-[var(--border-color)] rounded-xl p-4 hover:border-[var(--primary-color)] transition-colors duration-200"
            >
              <!-- Delete Button -->
              <button 
                @click.stop="confirmDeleteProject(project.id, project.name)"
                class="absolute top-2 right-2 p-1 rounded-full text-[var(--secondary-text)] hover:text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 opacity-0 group-hover:opacity-100 transition-all duration-150 cursor-pointer"
                title="Delete Project"
              >
                <Trash class="h-4 w-4" />
              </button>

              <div class="flex justify-between items-start">
                <div 
                  @click="navigateToProject(project.id)"
                  class="flex-1 cursor-pointer"
                >
                  <h3 class="font-medium text-sm mb-1.5">{{ project.name }}</h3>
                  <span class="text-xs px-2 py-1 rounded-full bg-[var(--border-color)] text-[var(--secondary-text)]">
                    {{ project.type }}
                  </span>
                </div>
              </div>
              <div 
                @click="navigateToProject(project.id)"
                class="cursor-pointer"
              >
                <p class="text-xs mt-2 text-[var(--secondary-text)] line-clamp-2">
                  {{ project.description || 'No description' }}
                </p>
                <div class="flex justify-between items-center mt-3">
                  <div class="flex items-center gap-4">
                    <span class="text-xs text-[var(--secondary-text)]">{{ project.chat_count }} chats</span>
                    <span class="text-xs text-[var(--secondary-text)]">Created {{ formatDate(new Date(project.created_at)) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

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
              Are you sure you want to delete the project <span class="font-medium text-[var(--text-color)]">'{{ projectToDeleteName }}'</span>? This action cannot be undone.
            </p>
            <div class="flex justify-end gap-3">
              <button 
                @click="showDeleteModal = false"
                class="px-4 py-2 border border-[var(--border-color)] rounded-lg text-sm hover:bg-[var(--button-hover)] transition-colors duration-150"
              >
                Cancel
              </button>
              <button 
                @click="executeDeleteProject"
                class="px-4 py-2 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 transition-colors duration-150"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>



<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useSidebarStore } from "../stores/sidebarStore";
import { useRouter } from 'vue-router';
import { Layers, Info, Trash, X } from 'lucide-vue-next';
// Import the project service
import { getProjects, deleteProject as apiDeleteProject } from '../services/projectService';

const sidebarStore = useSidebarStore();
const router = useRouter();

// State
const projects = ref([]);
const isLoading = ref(false);
const error = ref(null);
const searchQuery = ref('');
const showInfoPopup = ref(false);
const infoButtonRef = ref(null);
const infoPopupRef = ref(null);
const infoContainerRef = ref(null);

// Delete Modal State
const showDeleteModal = ref(false);
const projectToDeleteId = ref(null);
const projectToDeleteName = ref('');

// Computed filtered projects
const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value;
  
  const query = searchQuery.value.toLowerCase();
  return projects.value.filter(project => 
    project.name.toLowerCase().includes(query) ||
    (project.custom_instructions && project.custom_instructions.toLowerCase().includes(query))
  );
});

// Fetch projects function
const fetchProjects = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    // Call the project service to get projects
    const projectList = await getProjects();
    
    // Transform the response to match our UI needs
    projects.value = projectList.map(project => ({
      id: project.project_id,
      name: project.name,
      description: project.custom_instructions || 'No description',
      type: project.documents.length > 0 ? 'With Documents' : 'Empty',
      chat_count: 0, // We'll need to update this if you have a way to count chats
      created_at: project.created_at,
      updated_at: project.updated_at
    }));
  } catch (err) {
    error.value = err.message || 'Failed to fetch projects';
    console.error('Error fetching projects:', err);
  } finally {
    isLoading.value = false;
  }
};

// Info popup methods
const toggleInfoPopup = () => {
  showInfoPopup.value = !showInfoPopup.value;
};

const openInfoPopup = () => {
  showInfoPopup.value = true;
};

const closeInfoPopup = () => {
  showInfoPopup.value = false;
};

// Fetch projects when component mounts
onMounted(() => {
  fetchProjects();
});

// Navigation functions
const navigateToProject = (projectId) => {
  router.push(`/projects/${projectId}`);
};

const createNewProject = () => {
  router.push('/projects/new');
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

// --- Delete Project Logic ---
const confirmDeleteProject = (projectId, projectName) => {
  projectToDeleteId.value = projectId;
  projectToDeleteName.value = projectName;
  showDeleteModal.value = true;
};

const executeDeleteProject = async () => {
  if (!projectToDeleteId.value) return;

  try {
    console.log(`Attempting to delete project: ${projectToDeleteId.value}`);
    await apiDeleteProject(projectToDeleteId.value);
    console.log(`Project ${projectToDeleteId.value} deleted successfully.`);

    // Remove project from local list
    projects.value = projects.value.filter(p => p.id !== projectToDeleteId.value);

    // Close modal
    showDeleteModal.value = false;
    projectToDeleteId.value = null;
    projectToDeleteName.value = '';

    // Optional: Show success notification/toast

  } catch (err) {
    console.error(`Error deleting project ${projectToDeleteId.value}:`, err);
    // Close modal even on error
    showDeleteModal.value = false;
    // Optional: Show error notification/toast
    alert(`Failed to delete project: ${err instanceof Error ? err.message : String(err)}`);
    // Reset deletion state
    projectToDeleteId.value = null;
    projectToDeleteName.value = '';
  }
};
</script>