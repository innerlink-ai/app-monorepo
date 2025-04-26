<template>
  <div class="flex flex-col h-screen overflow-hidden bg-[var(--bg-color)]">
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--primary-color)] mx-auto"></div>
        <p class="text-[var(--text-color)] mt-4 text-lg">Loading chat...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// This is just a loading transition page
// No logic needed as we're only showing this briefly during navigation
</script> 