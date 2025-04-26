import { ref } from 'vue';
import { defineStore } from 'pinia';
import { fetchChats } from '../services/chatHistoryService';

// Define a Chat interface
export interface Chat {
  chat_id: string;
  name: string;
  message_count?: number;
  updated_at: string;
  preview?: string;
}

export const useChatStore = defineStore('chat', () => {
  const recentChats = ref<Chat[]>([]); // Initialize as empty array with proper type
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  async function fetchRecentChats(): Promise<void> {
    if (isLoading.value) return;

    isLoading.value = true;
    error.value = null;
    try {
      const chats = await fetchChats();
      // Keep only the latest 25 (or desired number)
      recentChats.value = chats.slice(0, 25); // Take the first 25 (newest)
    } catch (err) {
      console.error('Failed to load recent chats in store:', err);
      error.value = err instanceof Error ? err.message : 'Failed to load chats';
      recentChats.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Adds a new chat to the beginning of the recent chats list.
   * @param newChat - The new chat object
   */
  function addChat(newChat: Chat): void {
    // Basic validation
    if (!newChat || !newChat.chat_id || !newChat.name || !newChat.updated_at) {
      console.error('Attempted to add invalid chat object to store:', newChat);
      return;
    }
    // Add the new chat to the beginning of the list
    recentChats.value.unshift(newChat);
    
    // Optional: Keep the list trimmed to a certain size
    if (recentChats.value.length > 25) {
      recentChats.value = recentChats.value.slice(0, 25);
    }
  }

  return {
    recentChats,
    isLoading,
    error,
    fetchRecentChats,
    addChat
  };
});