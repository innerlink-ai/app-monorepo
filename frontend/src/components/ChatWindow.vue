<template>
  <div class="flex flex-col h-full w-full pt-4" :style="chatWindowStyle">
    <!-- Chat Messages -->
    <div
      ref="chatBox"
      class="flex flex-col flex-1 overflow-y-auto overflow-x-hidden py-4 custom-scrollbar"
    >
      <div v-for="(msg, index) in messages" :key="index" class="w-full mb-4">
        <!-- User Message -->
        <div v-if="msg.isUser" class="w-full" :class="sidebarStore.isCollapsed ? 'px-24' : 'px-32'">
          <div class="flex justify-end">
            <div 
              class="relative bg-[var(--user-message-bg)] text-[var(--user-message-text)] p-4 rounded-2xl inline-block max-w-full mb-2"
            >
              <div
                class="whitespace-pre-wrap break-words anywhere text-[15px] leading-relaxed pb-2"
                :class="{'max-h-[120px] overflow-hidden': !msg.isExpanded && isLongMessage(msg.content)}"
                v-html="escapeHTML(msg.content)"
                :style="{ color: 'var(--user-message-text)' }"
              ></div>
              
              <!-- Show More/Less Button -->
              <button 
                v-if="isLongMessage(msg.content)"
                @click="toggleMessageExpand(index)"
                class="absolute bottom-0 right-0 flex items-center gap-1.5 px-3 py-1.5 text-sm text-[var(--secondary-text)] hover:text-[var(--text-color)] transition-all duration-200 rounded-lg bg-[var(--user-message-bg)] hover:bg-[var(--user-message-bg)] border border-transparent hover:border-[var(--border-color-lighter)] mt-2 cursor-pointer"
              >
                <span class="font-medium">{{ msg.isExpanded ? 'Show less' : 'Show more' }}</span>
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  width="16" 
                  height="16" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  stroke-width="2" 
                  stroke-linecap="round" 
                  stroke-linejoin="round"
                  class="transition-transform duration-200"
                  :class="{'rotate-180': msg.isExpanded}"
                >
                  <path d="m6 9 6 6 6-6"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <!-- Chatbot Message -->
        <div v-else class="w-full" :class="sidebarStore.isCollapsed ? 'px-24' : 'px-32'">
          <div class="flex justify-start">
            <div 
              class="bg-[var(--chat-bg)] text-[var(--text-color)] p-4 rounded-2xl w-full"
            >
              <!-- Thinking section (if available) -->
              <div v-if="hasThinking(msg.content)" class="mb-3">
                <details class="thinking-dropdown">
                  <summary class="cursor-pointer text-sm text-[var(--secondary-text)] font-medium hover:text-[var(--text-color)] transition-colors">
                    Thinking
                  </summary>
                  <div class="mt-2 pl-3 border-l-2 border-[var(--border-color)] text-[var(--secondary-text)] text-sm whitespace-pre-wrap break-words">
                    {{ getThinkingContent(msg.content) }}
                  </div>
                </details>
              </div>
              
              <!-- Rendered markdown content -->
              <div
                v-html="formatMessage(msg.content)"
                class="markdown-content break-words anywhere text-[15px] leading-relaxed"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Typing Indicator -->
      <div v-if="isTyping && !isStreaming" 
           class="w-full" 
           :class="sidebarStore.isCollapsed ? 'px-24' : 'px-32'">
        <div class="flex justify-start">
          <div 
            class="bg-[var(--chat-bg)] text-[var(--text-color)] p-3 rounded-2xl"
          >
            <div class="typing-indicator flex space-x-1.5 px-1">
              <div class="w-2 h-2 bg-[var(--text-color)] rounded-full"></div>
              <div class="w-2 h-2 bg-[var(--text-color)] rounded-full"></div>
              <div class="w-2 h-2 bg-[var(--text-color)] rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div 
      class="flex flex-col py-6 relative min-w-0"
      :class="sidebarStore.isCollapsed ? 'px-24' : 'px-32'"
    >
      <!-- Use ChatInputArea Component -->
      <ChatInputArea 
        v-model="message" 
        v-model:files="attachedFiles" 
        @send="sendMessage"
        :disabled="isStreaming" 
        :show-attachments-above="true"
      />

      <!-- Action Buttons (Optional - Keep if needed outside ChatInputArea) -->
      <!-- Example: Keep Screenshot button if it's meant to be separate -->
      <!-- <div class="flex items-center space-x-1 mt-2"> ... </div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSidebarStore } from '../stores/sidebarStore'
import { fetchChat, generateStreamResponse } from "../services/chatService";
import { ref, onMounted, watch, nextTick, computed, useRouter } from '../composables/index'
import DOMPurify from 'dompurify';
import { collectionsService } from '../services/collectionService';
// Import showdown instead of marked (more reliable)
import showdown from 'showdown';
import ChatInputArea from './ChatInputArea.vue'; // Import the component

// Initialize the markdown converter
const converter = new showdown.Converter({
  simpleLineBreaks: true,  // Convert line breaks to <br>
  tables: true,            // Enable tables
  strikethrough: true,     // Enable strikethrough
  tasklists: true,         // Enable task lists
  ghCodeBlocks: true,      // Enable GitHub-style code blocks
  emoji: true              // Enable emoji
});

const router = useRouter();
const sidebarStore = useSidebarStore()
const currentStreamContent = ref('')
const isStreaming = ref(false)

const props = defineProps<{ chatId: string }>();
const message = ref('')
const messages = ref<{ content: string; isUser: boolean; isExpanded: boolean }[]>([]);
const isTyping = ref(false)
const chatBox = ref<HTMLElement | null>(null)

// For testing purposes
const useMockStream = ref(false) // Set to true to enable test mode

// Test data with example responses
const testResponses = [
  {
    content: "I'll help you test various markdown elements!\n\n## Headings\n\n# Heading 1\n## Heading 2\n### Heading 3\n\n## Text Formatting\n\n**Bold text** and *italic text* and ~~strikethrough~~\n\n## Lists\n\nOrdered list:\n1. First item\n2. Second item\n3. Third item\n\nUnordered list:\n- Item one\n- Item two\n- Item three\n\n## Code Blocks\n\nInline `code` example\n\n```javascript\n// A code block\nfunction testFunction() {\n  console.log(\"Hello world!\");\n  return true;\n}\n```\n\n## Blockquotes\n\n> This is a blockquote\n> It can span multiple lines\n\n## Tables\n\n| Header 1 | Header 2 | Header 3 |\n|----------|----------|----------|\n| Cell 1   | Cell 2   | Cell 3   |\n| Cell 4   | Cell 5   | Cell 6   |\n\n## Links\n\n[Example link](https://example.com)",
    isUser: false
  },
  {
    content: "I'm thinking about how to solve this problem...\nLet me try to understand what the requirements are.\nI'll need to parse the input and calculate the result step by step.\n</think>\n\nHere's the solution to your problem:\n\n## Step-by-Step Solution\n\n1. First, we identify the key variables\n2. Next, we apply the formula\n3. Finally, we calculate the result\n\n```\nResult = 42\n```",
    isUser: false
  }
];

const chatWindowStyle = computed(() => ({
  marginLeft: sidebarStore.isCollapsed ? "3.5rem" : "14rem",
  maxWidth: sidebarStore.isCollapsed ? "calc(100% - 3.5rem)" : "calc(100% - 14rem)",
  transition: "margin-left 0.3s ease, max-width 0.3s ease",
}));

const scrollToBottom = () => {
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight
  }
}

watch(messages, () => {
  nextTick(() => scrollToBottom())
})

// Simple implementation to mock streaming responses
const simulateStreamResponse = (responseText: string, streamIndex: number): Promise<void> => {
  return new Promise((resolve) => {
    isStreaming.value = true;
    
    // Variable to track the current position in the response text
    let currentPosition = 0;
    
    // Stream the response character by character with varying speeds
    const streamInterval = setInterval(() => {
      // If we've reached the end of the text, clear the interval and resolve
      if (currentPosition >= responseText.length) {
        clearInterval(streamInterval);
        isStreaming.value = false;
        resolve();
        return;
      }
      
      // Determine how many characters to add this time (1-5)
      const charactersToAdd = Math.min(
        Math.ceil(Math.random() * 5), 
        responseText.length - currentPosition
      );
      
      // Get the next chunk of characters
      const nextChunk = responseText.substring(
        currentPosition, 
        currentPosition + charactersToAdd
      );
      
      // Update the content with the new chunk
      currentStreamContent.value += nextChunk;
      
      // Update the message in the UI
      messages.value[streamIndex] = {
        content: currentStreamContent.value,
        isUser: false,
        isExpanded: false
      };
      
      // Update the current position
      currentPosition += charactersToAdd;
      
      // Randomly add longer pauses (5% chance)
      if (Math.random() < 0.05) {
        clearInterval(streamInterval);
        setTimeout(() => {
          // Resume streaming after a pause
          const newInterval = setInterval(() => {
            // Copy of the logic above to continue streaming
            if (currentPosition >= responseText.length) {
              clearInterval(newInterval);
              isStreaming.value = false;
              resolve();
              return;
            }
            
            const charsToAdd = Math.min(
              Math.ceil(Math.random() * 5), 
              responseText.length - currentPosition
            );
            
            const chunk = responseText.substring(
              currentPosition, 
              currentPosition + charsToAdd
            );
            
            currentStreamContent.value += chunk;
            
            messages.value[streamIndex] = {
              content: currentStreamContent.value,
              isUser: false,
              isExpanded: false
            };
            
            currentPosition += charsToAdd;
            
            if (Math.random() < 0.05) {
              clearInterval(newInterval);
              setTimeout(() => {
                // This creates a new interval with the same logic
                // We don't want to nest this too deeply to avoid complexity
                const finalInterval = setInterval(() => {
                  if (currentPosition >= responseText.length) {
                    clearInterval(finalInterval);
                    isStreaming.value = false;
                    resolve();
                    return;
                  }
                  
                  const chars = Math.min(
                    Math.ceil(Math.random() * 5), 
                    responseText.length - currentPosition
                  );
                  
                  const finalChunk = responseText.substring(
                    currentPosition, 
                    currentPosition + chars
                  );
                  
                  currentStreamContent.value += finalChunk;
                  
                  messages.value[streamIndex] = {
                    content: currentStreamContent.value,
                    isUser: false,
                    isExpanded: false
                  };
                  
                  currentPosition += chars;
                }, 30 + Math.random() * 70);
              }, 300 + Math.random() * 700);
            }
          }, 30 + Math.random() * 70);
        }, 300 + Math.random() * 700);
      }
    }, 30 + Math.random() * 70); // Vary the speed between characters
  });
};

// Add these refs to manage file uploads and collections
const attachedFiles = ref<FileAttachment[]>([]);
const showCollections = ref(false);
const showContextOptions = ref(false);

// Define interface for collections
interface Collection {
  id: string;
  name: string;
  user_id?: string;
  type?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  document_count?: number;
}

const collections = ref<Collection[]>([]);
const isLoadingCollections = ref(false);
const collectionsError = ref<string | null>(null);
const collectionSearch = ref('');
const selectedCollection = ref<Collection | null>(null);

// Computed property for filtered collections
const filteredCollections = computed(() => {
  if (!collectionSearch.value) return collections.value;
  const searchTerm = collectionSearch.value.toLowerCase();
  return collections.value.filter(collection => 
    collection.name.toLowerCase().includes(searchTerm)
  );
});

// Methods for collection handling
const selectCollection = (collection: Collection) => {
  selectedCollection.value = collection;
  showCollections.value = false;
};

const removeCollection = () => {
  selectedCollection.value = null;
};

const createNewCollection = () => {
  // This would open a modal or navigate to collection creation in a real app
  console.log('Create new collection');
  showCollections.value = false;
};

// Methods for additional attachment options
const connectGitHub = () => {
  // In a real implementation, this would open OAuth flow or file picker
  console.log('Connect to GitHub');
  // Could open a modal to authenticate with GitHub and select repositories/files
};

const connectGoogleDrive = () => {
  // In a real implementation, this would integrate with Google Drive API
  console.log('Connect to Google Drive');
  // Could open the Google Drive picker or auth flow
};

// Define interface for userMessage at the top
interface UserMessage {
  content: string;
  isUser: boolean;
  attachments: Array<{ name: string; type: string }>;
  collectionId?: string;
  isExpanded: boolean;
}

// Update the sendMessage function to ensure consistent handling of multiple files
const sendMessage = async () => {
  // Check if streaming, or if message and files are empty
  if (isStreaming.value || (!message.value.trim() && attachedFiles.value.length === 0)) return;

  // Prepare user message content
  const promptToSend = message.value.trim(); // Text to send to the backend
  let userMessageContentForDisplay = promptToSend; // Text to display in the UI
  const currentFiles = attachedFiles.value; // Capture files before clearing
  
  // Append file names to the message content *for display* if files are attached
  if (currentFiles.length > 0) {
    // Add file emoji and count to the prompt for display
    if (userMessageContentForDisplay) {
      userMessageContentForDisplay += ` 📁 ${currentFiles.length} file${currentFiles.length > 1 ? 's' : ''} added`;
    } else {
      userMessageContentForDisplay = `📁 ${currentFiles.length} file${currentFiles.length > 1 ? 's' : ''} added`;
    }
  }

  // Add user message to the chat UI (using the display content)
  const userMessage: UserMessage = { 
    content: userMessageContentForDisplay, 
    isUser: true,
    // Keep attachments array for potential future use or backend info
    attachments: currentFiles.map(file => ({ 
      name: file.name,
      type: file.type || ''
    })),
    collectionId: selectedCollection.value?.id,
    isExpanded: false
  };
  
  messages.value.push(userMessage);
  
  // Clear the input message field *after* preparing content
  message.value = ''; 
  
  // Log the files being sent
  console.log('Sending message with files:', {
    fileCount: currentFiles.length,
    fileNames: currentFiles.map(file => file.name)
  });
  
  // Prepare for bot response
  isTyping.value = true;
  currentStreamContent.value = '';
  const streamIndex = messages.value.length;
  messages.value.push({ content: '', isUser: false, isExpanded: false });

  try {
    if (useMockStream.value) {
      // Test mode: Select a random response and simulate streaming
      const randomResponse = testResponses[Math.floor(Math.random() * testResponses.length)];
      await simulateStreamResponse(randomResponse.content, streamIndex);
    } else {
      // Real API call: Process files first using the captured list
      const processedFiles = await Promise.all(currentFiles.map(async (file, index) => {
        console.log(`Processing file ${index + 1}/${currentFiles.length}: ${file.name}`);
        
        // If we have a file reference, read it now
        if ('file' in file && file.file && (file.content === null || file.content === undefined)) {
          try {
            console.log(`Reading content for ${file.name} from file reference`);
            const content = await readFileAsBase64(file.file);
            return { 
              name: file.name,
              content
            };
          } catch (error) {
            console.error(`Error reading file ${file.name}:`, error);
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            return { 
              name: file.name,
              content: `[Error reading file: ${errorMessage}]`
            };
          }
        } else {
          // Use existing content
          return { 
            name: file.name,
            content: file.content || ''
          };
        }
      }));
      
      // Log processed files (without showing full content)
      console.log('Processed files for API:', {
        filesCount: processedFiles.length,
        fileNames: processedFiles.map(f => f.name),
        contentTypes: processedFiles.map(f => typeof f.content)
      });
      
      // Use the actual API service with properly formatted files
      await generateStreamResponse(
        props.chatId,
        promptToSend, 
        (chunk: string) => {
          if (!isStreaming.value) {
            isStreaming.value = true;
            isTyping.value = false;
          }
          
          currentStreamContent.value += chunk;
          messages.value[streamIndex] = {
            content: currentStreamContent.value,
            isUser: false,
            isExpanded: false
          };
          messages.value = [...messages.value];
          nextTick(() => scrollToBottom());
        },
        () => {
          isTyping.value = false;
          isStreaming.value = false;
          nextTick(() => scrollToBottom());
        },
        (error) => {
          console.error('Error in stream:', error);
          isTyping.value = false;
          isStreaming.value = false;
          messages.value = messages.value.filter((_, index) => index !== streamIndex);
        },
        // Include properly formatted files and collection
        {
          files: processedFiles,
          collection: selectedCollection.value ? {
            id: selectedCollection.value.id,
            name: selectedCollection.value.name
          } : undefined
        }
      );
    }
  } catch (error) {
    console.error('Error sending message:', error);
    isTyping.value = false;
    isStreaming.value = false;
    messages.value = messages.value.filter((_, index) => index !== streamIndex);
  }
  
  // Clear attachments and selected collection after sending
  attachedFiles.value = [];
  selectedCollection.value = null;
};

// Keep readFileAsBase64 as it's used by sendMessage to process stored file references
const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (reader.result) {
        resolve(reader.result as string);
      } else {
        reject(new Error('Failed to read file content'));
      }
    };
    reader.onerror = () => reject(reader.error || new Error('File read error'));
    reader.readAsDataURL(file); // Read as data URL (base64)
  });
};

// Initialize the chat
onMounted(async () => {
  // Add detailed debugging of router state to see what's available
  console.log('ChatWindow mounted, checking router state...');
  console.log('Router current route:', router.currentRoute.value);
  console.log('History state object:', history.state);
  
  // Check for context data in localStorage and sessionStorage
  const localStorageKey = `chat_context_${props.chatId}`;
  const storedContextData = localStorage.getItem(localStorageKey) || sessionStorage.getItem(localStorageKey);
  const storageError = sessionStorage.getItem(`${localStorageKey}_error`);
  let contextData;
  
  if (storedContextData) {
    try {
      contextData = JSON.parse(storedContextData);
      console.log('Found context data in storage:', {
        key: localStorageKey,
        storage: localStorage.getItem(localStorageKey) ? 'localStorage' : 'sessionStorage',
        hasData: !!contextData,
        messageText: contextData?.messageText,
        hasFiles: !!contextData?.files,
        filesCount: contextData?.files?.length || 0
      });
      
      // Clean up storage after reading the data
      localStorage.removeItem(localStorageKey);
      sessionStorage.removeItem(localStorageKey);
      sessionStorage.removeItem(`${localStorageKey}_error`);
    } catch (e) {
      console.error('Error parsing context data from storage:', e);
    }
  } else if (storageError) {
    console.warn('Storage error was reported when saving context data:', storageError);
    sessionStorage.removeItem(`${localStorageKey}_error`);
  } else {
    console.log('No context data found in storage for key:', localStorageKey);
  }
  
  try {
    if (!useMockStream.value) {
      // Only fetch real chat data if not in test mode
      const chatData = await fetchChat(props.chatId);
      
      if (chatData) {
        const initialMessage = contextData?.messageText;
        const initialFiles = contextData?.files;
        const initialCollection = contextData?.collection;
        
        console.log('Using context data in ChatWindow:', {
          message: initialMessage,
          hasFiles: initialFiles ? true : false,
          filesCount: initialFiles?.length || 0,
          fileNames: initialFiles?.map((f: any) => f.name) || [],
          hasCollection: initialCollection ? true : false,
          collectionInfo: initialCollection ? `${initialCollection.id} - ${initialCollection.name}` : 'none'
        });
        
        if (initialMessage || (initialFiles && initialFiles.length > 0)) {
          // Add any existing messages from the chat first
          messages.value = chatData.messages || [];
          
          // Add the new user message if provided
          if (initialMessage) {
            messages.value.push({ content: initialMessage, isUser: true, isExpanded: false });
          } else if (initialFiles && initialFiles.length > 0) {
            // If no message but files present, add a placeholder user message
            messages.value.push({ 
              content: `Files attached: ${initialFiles.map((f: any) => f.name).join(", ")}`, 
              isUser: true,
              isExpanded: false
            });
          }
          
          // Prepare for bot response
          currentStreamContent.value = '';
          const streamIndex = messages.value.length;
          messages.value.push({ content: '', isUser: false, isExpanded: false });
          isTyping.value = true;

          try {
            // Process initial files to ensure they're properly formatted
            const processedFiles = initialFiles && Array.isArray(initialFiles) 
              ? initialFiles.map((file: any, index: number) => {
                  console.log(`Processing file ${index + 1}/${initialFiles.length}: ${file.name}`);
                  return {
                    name: file.name || `file-${index}`,
                    content: file.content || '',
                    isExpanded: false
                  };
                })
              : undefined;
            
            // Log the processed files
            console.log('Processed files for API:', {
              hasFiles: !!processedFiles,
              filesCount: processedFiles?.length || 0,
              fileNames: processedFiles?.map((f: any) => f.name) || [],
              contentSamples: processedFiles?.map((f: any) => 
                f.content ? `${f.content.substring(0, 20)}... (${f.content.length} chars)` : 'No content'
              ) || []
            });

            // Generate response with properly formatted context data - use empty string as message if only files provided
            await generateStreamResponse(
              props.chatId,
              initialMessage || "", // Use empty string if no message but files present
              (chunk: string) => {
                if (!isStreaming.value) {
                  isStreaming.value = true;
                }
                
                currentStreamContent.value += chunk;
                messages.value[streamIndex] = {
                  content: currentStreamContent.value,
                  isUser: false,
                  isExpanded: false
                };
                messages.value = [...messages.value];
                nextTick(() => scrollToBottom());
              },
              () => {
                isTyping.value = false;
                isStreaming.value = false;
                nextTick(() => scrollToBottom());
              },
              (error) => {
                console.error('Error in stream:', error);
                isTyping.value = false;
                isStreaming.value = false;
                messages.value = messages.value.filter((_, index) => index !== streamIndex);
              },
              // Include properly formatted context data
              {
                files: processedFiles,
                collection: initialCollection
              }
            );
          } catch (error) {
            console.error('Error generating initial response:', error);
            isTyping.value = false;
            isStreaming.value = false;
            messages.value = messages.value.filter((_, index) => index !== streamIndex);
          }
        } else {
          messages.value = chatData.messages || [];
        }
        nextTick(() => scrollToBottom());
      } else {
        await router.replace({ name: 'NewChat' });
      }
    } else {
      // In test mode, just load an empty state
      messages.value = [];
      nextTick(() => scrollToBottom());
    }
  } catch (error) {
    console.error('Error loading chat:', error);
    // In case of error, start with empty state
    messages.value = [];
    nextTick(() => scrollToBottom());
  }
});

// Check if a message has a thinking section
const hasThinking = (content: string): boolean => {
  return content.includes('</think>');
};

// Extract the thinking content
const getThinkingContent = (content: string): string => {
  if (!hasThinking(content)) return '';
  
  const parts = content.split('</think>');
  if (parts.length > 1) {
    // Remove any HTML or markdown syntax
    return parts[0].replace(/<\/?[^>]+(>|$)/g, '').trim();
  }
  return '';
};

// Format message with markdown and remove special tokens
const formatMessage = (content: string): string => {
  // Extract the main content (after </think> if it exists)
  let mainContent = content;
  if (content.includes('</think>')) {
    mainContent = content.split('</think>').pop() || content;
  }
  
  // Remove end of sentence markers and any trailing whitespace
  mainContent = mainContent
    .replace(/[.?!]$/g, '')
    .replace(/\n{3,}/g, '\n\n')  // Replace excessive newlines
    .trim();
  
  try {
    // Convert markdown to HTML
    const html = converter.makeHtml(mainContent);
    
    // Sanitize the HTML to prevent XSS attacks
    return DOMPurify.sanitize(html);
  } catch (e) {
    console.error('Error in markdown rendering:', e);
    // Fallback to simple HTML escaping
    return escapeHTML(mainContent);
  }
};

// Basic HTML escaping function
const escapeHTML = (str: string): string =>
  str.replace(/[&<>"']/g, (m) => {
    switch (m) {
      case '&': return '&amp;'
      case '<': return '&lt;'
      case '>': return '&gt;'
      case '"': return '&quot;'
      case "'": return '&#39;'
      default: return m
    }
  });

// Toggle collections dropdown
const toggleCollectionsDropdown = () => {
  showCollections.value = !showCollections.value;
};

// Toggle context options
const toggleContextOptions = () => {
  showContextOptions.value = !showContextOptions.value;
  // Close collections dropdown if context options are being hidden
  if (!showContextOptions.value) {
    showCollections.value = false;
  }
};

// Add new methods for collections modal
const showCollectionsModal = ref(false);
const selectCollectionFromModal = (collection: Collection) => {
  selectedCollection.value = collection;
  showCollectionsModal.value = false;
};

// Method to remove collection and keep modal open to select another
const removeCollectionInModal = () => {
  selectedCollection.value = null;
};

// Function to fetch collections from the API
const fetchCollections = async () => {
  isLoadingCollections.value = true;
  collectionsError.value = null;
  
  try {
    const data = await collectionsService.getCollections();
    collections.value = data;
  } catch (error) {
    console.error('Error fetching collections:', error);
    collectionsError.value = 'Failed to load collections';
  } finally {
    isLoadingCollections.value = false;
  }
};

// Function to open the collections modal and fetch collections
const openCollectionsModal = () => {
  showCollectionsModal.value = true;
  fetchCollections();
};

// In the script section, add a proper interface for FileAttachment
// Add this near the other interfaces
interface FileAttachment {
  name: string;
  content?: string | null;
  type?: string;
  size?: number;
  file?: File;
  error?: boolean;
  isExpanded: boolean;
}

// Helper function to format file size
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) {
    return bytes + ' bytes';
  } else if (bytes < 1024 * 1024) {
    return (bytes / 1024).toFixed(1) + ' KB';
  } else {
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
};

// Helper function to check if a message is long
const isLongMessage = (content: string): boolean => {
  return content.length > 120;
};

// Helper function to toggle message expansion
const toggleMessageExpand = (index: number) => {
  messages.value[index].isExpanded = !messages.value[index].isExpanded;
};
</script>

<style>
/* Typing indicator animation */
@keyframes blink {
  0%, 100% { transform: translateY(0); opacity: 0.3; }
  50% { transform: translateY(-1px); opacity: 1; }
}

.typing-indicator div {
  animation: blink 1.2s ease-in-out infinite;
}

.typing-indicator div:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator div:nth-child(3) {
  animation-delay: 0.4s;
}

.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: 3px;
}

.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: var(--button-hover);
}

.anywhere {
  overflow-wrap: anywhere;
}

.overflow-y-auto {
  scroll-behavior: smooth;
}

textarea {
  min-height: 40px;
}

textarea::placeholder {
  color: var(--secondary-text);
}

/* Thinking dropdown styling */
.thinking-dropdown summary {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background-color: var(--sidebar-bg);
}

.thinking-dropdown summary::-webkit-details-marker {
  display: none;
}

.thinking-dropdown summary::before {
  content: "▶";
  font-size: 0.7em;
  margin-right: 0.5rem;
  transition: transform 0.2s;
}

.thinking-dropdown[open] summary::before {
  transform: rotate(90deg);
}

/* Markdown styling */
.markdown-content h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: var(--text-color);
}

.markdown-content h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
  color: var(--text-color);
}

.markdown-content h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.markdown-content h4, .markdown-content h5, .markdown-content h6 {
  font-size: 1rem;
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.markdown-content p {
  margin-bottom: 0.75rem;
  color: var(--text-color);
}

.markdown-content ul, .markdown-content ol {
  padding-left: 1.5rem;
  margin-bottom: 0.75rem;
  color: var(--text-color);
}

.markdown-content ul {
  list-style-type: disc;
}

.markdown-content ol {
  list-style-type: decimal;
}

.markdown-content li {
  margin-bottom: 0.25rem;
  color: var(--text-color);
}

.markdown-content blockquote {
  border-left: 4px solid var(--border-color);
  padding-left: 1rem;
  margin-left: 0;
  margin-right: 0;
  font-style: italic;
  margin-bottom: 0.75rem;
  color: var(--text-color);
}

.markdown-content a {
  color: #3b82f6;
  text-decoration: underline;
}

.markdown-content hr {
  border: 0;
  border-top: 1px solid var(--border-color);
  margin: 1rem 0;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.markdown-content th, .markdown-content td {
  border: 1px solid var(--border-color);
  padding: 0.5rem;
}

.markdown-content th {
  background-color: var(--sidebar-bg);
  font-weight: 600;
}

/* Code block styling */
.markdown-content pre {
  background-color: var(--sidebar-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-x: auto;
  margin: 0.75rem 0;
  color: var(--text-color);
}

.markdown-content code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.9em;
  color: var(--text-color);
}

.markdown-content p code {
  background-color: var(--sidebar-bg);
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  font-size: 0.9em;
}

/* Light theme improvements */
html[data-theme="light"] {
  --user-message-text: #000000; /* Black text for user messages in light theme */
  --text-color: #1a1a1a; /* Dark text for light theme */
  --secondary-text: #555555; /* Darker secondary text for better contrast */
}

/* Dark theme settings to ensure user message text is visible */
html[data-theme="dark"] {
  --user-message-text: #ffffff; /* White text for user messages in dark theme */
}

/* Remove shadows in light theme */
html[data-theme="light"] .shadow-sm {
  box-shadow: none;
}

/* Refined borders for light theme */
html[data-theme="light"] .border {
  border-color: #e5e7eb; /* Lighter border color */
}

/* Subtly rounded corners for a cleaner look */
html[data-theme="light"] .rounded-2xl {
  border-radius: 1rem;
}

/* Improve code block contrast in light theme */
html[data-theme="light"] .markdown-content pre,
html[data-theme="light"] .markdown-content p code {
  background-color: #f3f4f6;
  border-color: #e5e7eb;
  color: #1a1a1a;
}

/* Improve table appearance in light theme */
html[data-theme="light"] .markdown-content th {
  background-color: #f3f4f6;
}

/* Add this new CSS variable for lighter button hover effect */
:root {
  --button-hover-lighter: rgba(128, 128, 128, 0.1);
  --border-color-lighter: rgba(128, 128, 128, 0.07);
}
html[data-theme="dark"] {
  --button-hover-lighter: rgba(255, 255, 255, 0.05);
  --border-color-lighter: rgba(255, 255, 255, 0.03);
}
html[data-theme="light"] {
  --button-hover-lighter: rgba(0, 0, 0, 0.03);
  --border-color-lighter: rgba(0, 0, 0, 0.05);
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
</style>