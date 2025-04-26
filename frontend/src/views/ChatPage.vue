<template>
  <div>
    <ChatWindow
      v-if="chatId"
      :chat-id="chatId"
      
    />
    <div v-else class="flex h-full w-full items-center justify-center">
      <p>Loading chat...</p>
    </div>
  </div>
</template>

<script setup lang="ts">

import { ChatWindow, useRoute, useRouter, ref, onMounted } from '../composables/index'

const route = useRoute();
const router = useRouter();
const chatId = ref<string>('');


onMounted(async () => {
  try {
    chatId.value = route.params.id as string;
  
  } catch (error) {
    console.error('Error loading chat:', error);
    await router.replace({ name: 'NewChat' });
  }
});
</script>