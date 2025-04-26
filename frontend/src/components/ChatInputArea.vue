<template>
  <div class="flex-1 relative min-w-0 overflow-hidden">
    <!-- Attached Files Display (Above) -->
    <div 
      v-if="showAttachmentsAbove && files && files.length > 0" 
      class="mb-2 w-full"
    >
      <div class="flex flex-nowrap gap-2 overflow-x-auto pb-2 custom-scrollbar-thin">
        <div 
          v-for="(file, index) in files"
          :key="file.name + '-' + index + '-above'"
          class="flex-shrink-0 flex items-center bg-[var(--secondary-button-bg)] rounded-lg px-2 py-1 text-sm text-[var(--secondary-text)]"
        >
          <span>{{ file.name }}</span>
          <button 
            @click="removeFile(index)"
            class="ml-1.5 text-[var(--secondary-text)] hover:text-[var(--text-color)] transition-colors duration-150 cursor-pointer"
            title="Remove file"
          >
            <X class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Main Input Container -->
    <div class="flex flex-col rounded-xl border border-[var(--border-color)] overflow-hidden bg-[var(--prompt-bg)] relative input-container">
      <!-- Text Input Area -->
      <div class="flex-1">
        <textarea
          v-model="internalMessage"
          @keydown.enter.prevent="handleSend"
          placeholder="Ask me anything..."
          class="w-full p-4 bg-transparent text-[var(--text-color)] resize-none focus:outline-none"
          rows="2"
        ></textarea>
      </div>
      
      <!-- Attached Files Display - REMOVED from inside -->
      <!-- <div v-if="files && files.length > 0" class="p-3 border-t border-[var(--border-color)]"> ... </div> -->
      
      <!-- Bottom Controls -->
      <div class="flex items-center justify-between p-3">
        <!-- Action Buttons -->
        <div class="flex items-center space-x-1">
          <!-- Wrapper for Attachment Button + Badge -->
          <div class="relative">
            <!-- New Attachment Button -->
            <button
              @click="attachFile"
              class="inline-flex items-center justify-center w-9 h-9 text-[var(--secondary-text)] hover:text-[var(--text-color)] rounded-lg transition-colors duration-200 hover:bg-[var(--button-hover-lighter)] cursor-pointer"
              title="Attach file"
            >
              <Paperclip class="h-5 w-5" />
            </button>
            <!-- Badge Span -->
            <span
              v-if="files && files.length > 0"
              class="absolute -top-1 -right-1 bg-blue-500 text-white text-xs w-4 h-4 flex items-center justify-center rounded-full pointer-events-none"
            >
              {{ files.length }}
            </span>
          </div>
        </div>
        
        <!-- Send Button -->
        <button
          @click="handleSend"
          :disabled="isSendDisabled"
          class="p-2 rounded-lg text-white transition-colors duration-200 flex items-center justify-center"
          :class="[
            isSendDisabled
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 cursor-pointer'
          ]"
          title="Send message"
        >
          <Send class="h-5 w-5" />
        </button>
      </div>
      
      <input 
        type="file" 
        ref="fileInput" 
        @change="handleFileUpload" 
        class="hidden" 
        multiple 
        accept=".txt,.md,.py,.js,.ts,.html,.css,.json,.yaml,.yml,.csv,.java,.c,.cpp,.h,.hpp,.cs,.go,.php,.rb,.swift,.kt,.kts,.scala,.rs,.sh,.toml,.xml,.pdf,.docx,.pptx,.rtf"
      />
    </div>

    <!-- Attached Files Display (Below - Default) -->
    <div 
      v-if="!showAttachmentsAbove && files && files.length > 0" 
      class="mt-2 w-full"
    >
      <div class="flex flex-nowrap gap-2 overflow-x-auto pb-2 custom-scrollbar-thin">
        <div 
          v-for="(file, index) in files"
          :key="file.name + '-' + index + '-below'"
          class="flex-shrink-0 flex items-center bg-[var(--secondary-button-bg)] rounded-lg px-2 py-1 text-sm text-[var(--secondary-text)]"
        >
          <span>{{ file.name }}</span>
          <button 
            @click="removeFile(index)"
            class="ml-1.5 text-[var(--secondary-text)] hover:text-[var(--text-color)] transition-colors duration-150 cursor-pointer"
            title="Remove file"
          >
            <X class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Paperclip, X, Send } from 'lucide-vue-next';

// Types - Copied from NewChatPage for consistency
interface FileAttachment {
  name: string;
  size?: number;
  type?: string;
  file?: File;
  content?: string | null;
}

// Props
const props = withDefaults(defineProps<{
  modelValue: string; // For v-model binding of the message text
  files: FileAttachment[]; // For v-model:files binding
  showAttachmentsAbove?: boolean; // New prop
}>(), {
  showAttachmentsAbove: false // Default to false (below)
});

// Emits
const emit = defineEmits(['update:modelValue', 'update:files', 'send']);

// Refs
const fileInput = ref<HTMLInputElement | null>(null);

// Computed property for internal message handling with v-model
const internalMessage = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// Computed property for disabling send button
const isSendDisabled = computed(() => {
  return !props.modelValue.trim() && (!props.files || props.files.length === 0);
});

// Methods
const attachFile = () => {
  fileInput.value?.click();
};

// Define supported file extensions
const TEXT_EXTENSIONS = [
  '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.yaml', '.yml',
  '.csv', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.php', '.rb',
  '.swift', '.kt', '.kts', '.scala', '.rs', '.sh', '.toml', '.xml'
];
const BINARY_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.rtf'];
const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

const handleFileUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (!input.files || input.files.length === 0) return;
  
  const currentFiles = props.files || [];
  const fileLimit = 5; // Define max number of files
  
  // Check if adding these files would exceed the limit
  if (currentFiles.length + input.files.length > fileLimit) {
    alert(`You can only attach up to ${fileLimit} files. You already have ${currentFiles.length} files attached.`);
    if (input) input.value = ''; // Reset input value
    return;
  }
  
  const readPromises: Promise<FileAttachment>[] = [];
  
  for (let i = 0; i < input.files.length; i++) {
    const file = input.files[i];
    const fileExtension = ('.' + file.name.split('.').pop()?.toLowerCase()) || '';

    // Check file size
    if (file.size > MAX_FILE_SIZE_BYTES) {
      console.warn(`File ${file.name} exceeds the size limit of ${MAX_FILE_SIZE_MB}MB. Skipping.`);
      alert(`File "${file.name}" is too large (>${MAX_FILE_SIZE_MB}MB) and cannot be attached.`);
      continue; // Skip this file
    }
    
    // Determine how to read the file based on extension
    let readPromise: Promise<FileAttachment>;

    if (TEXT_EXTENSIONS.includes(fileExtension)) {
      console.log(`Reading text file: ${file.name}`);
      readPromise = readFileAsText(file).then(content => ({
        name: file.name,
        size: file.size,
        type: file.type,
        content: content
      }));
    } else if (BINARY_EXTENSIONS.includes(fileExtension)) {
      console.log(`Reading binary file as base64: ${file.name}`);
      readPromise = readFileAsBase64(file).then(base64Content => ({
        name: file.name,
        size: file.size,
        type: file.type,
        content: base64Content // Store base64 string
      }));
    } else {
      // Fallback for unsupported but accepted types: try reading as text
      console.warn(`Unsupported extension ${fileExtension} for file: ${file.name}. Attempting to read as text.`);
      readPromise = readFileAsText(file).then(content => ({
        name: file.name,
        size: file.size,
        type: file.type,
        content: content // Store the text content if successful
      }));
    }

    // Handle potential errors during file reading for *this specific file*
    readPromises.push(
      readPromise.catch(error => {
        console.error(`Error processing file ${file.name}:`, error);
        // Return a file object indicating error for this file
        return {
          name: file.name,
          size: file.size,
          type: file.type,
          content: `[Error reading file: ${error.message || 'Unknown error'}]` // Store error message in content
        };
      })
    );
  }

  // Wait for all files to be processed (reading attempts)
  try {
    const processedFiles = await Promise.all(readPromises);
    // Filter out any null/undefined results just in case, though catch should return error objects
    const validProcessedFiles = processedFiles.filter(f => f) as FileAttachment[]; 
    
    if (validProcessedFiles.length > 0) {
        emit('update:files', [...currentFiles, ...validProcessedFiles]);
    }
  } catch (error) {
    // This catch is unlikely to be hit if individual promises have catches,
    // but good practice to have it.
    console.error("Error processing one or more files:", error);
    alert("An error occurred while processing one or more files. Please try again.");
  }

  // Reset the input value regardless of success/failure of reads
  if (input) input.value = '';
};

// Helper to read file as text using Promise
const readFileAsText = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (e) => reject(reader.error || new Error(`File read error: ${e.type}`));
    reader.readAsText(file);
  });
};

// Helper to read file as Base64 Data URL and extract base64 string
const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string; // result is Data URL: data:mime/type;base64,xxxx
      // Extract base64 part by finding the first comma
      const base64String = result.split(',', 2)[1];
      if (base64String) {
        resolve(base64String);
      } else {
        // This case might happen if the file is empty or reading failed silently
        console.error(`Failed to extract base64 string for file: ${file.name}`);
        reject(new Error('Failed to extract base64 string from Data URL'));
      }
    };
    reader.onerror = (e) => reject(reader.error || new Error(`File read error: ${e.type}`));
    reader.readAsDataURL(file);
  });
};

const removeFile = (index: number) => {
  const newFiles = props.files.filter((_, i) => i !== index);
  emit('update:files', newFiles);
};

const handleSend = () => {
  if (!isSendDisabled.value) {
    emit('send');
  }
};

</script>

<style scoped>
textarea::placeholder {
  color: var(--secondary-text);
}

textarea {
  min-height: 40px;
}

/* Input container styling */
.input-container {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background: linear-gradient(to bottom, var(--prompt-bg), var(--prompt-bg));
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.input-container:focus-within {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-color: var(--border-color);
}

/* Light theme specific styles */
html[data-theme="light"] .input-container {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background: linear-gradient(to bottom, #ffffff, #f9fafb);
  border: 1px solid #e5e7eb;
}

html[data-theme="light"] .input-container:focus-within {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-color: #d1d5db;
}

/* Dark theme specific styles */
html[data-theme="dark"] .input-container {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  background: linear-gradient(to bottom, var(--prompt-bg), var(--prompt-bg));
  border: 1px solid var(--border-color);
}

html[data-theme="dark"] .input-container:focus-within {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  border-color: var(--border-color);
}

/* Styles for thin horizontal scrollbar */
.custom-scrollbar-thin {
  scrollbar-width: thin; /* For Firefox */
  scrollbar-color: var(--border-color) transparent; /* For Firefox */
}

.custom-scrollbar-thin::-webkit-scrollbar {
  height: 4px; /* Height for horizontal scrollbar */
}

.custom-scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: 2px;
}

.custom-scrollbar-thin:hover::-webkit-scrollbar-thumb {
  background-color: var(--button-hover); /* Optional: darker on hover */
}
</style> 