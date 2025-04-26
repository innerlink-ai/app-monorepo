// src/composables/index.ts

// Vue Core
export {
    ref,
    computed,
    onMounted,watch, nextTick , onBeforeUnmount  
  } from 'vue';


  // Vue Router
  export {
    useRouter,
    useRoute, 
    createWebHistory, 
    createRouter, 
  } from 'vue-router';
  
  // Pinia Store

  export { defineStore } from "pinia";
  
  export {
    useAuthStore
  } from '../stores/authStore';
  
  export {
    useSidebarStore
  } from '../stores/sidebarStore';
  
  // Third Party Libraries
  export {
    default as axios
  } from 'axios';
  
  export {
    Send, ChevronLeft, ChevronRight, MessageCircle, User, Wrench, Library, Boxes, Archive, FolderDot, FolderPlus, Grid, Layers,
    Database, FolderArchive, Clock, DatabaseZap, Blocks, MessagesSquare, MessageSquarePlus // Add these new icons
  } from 'lucide-vue-next';
  
  
  // Services
  export {
    checkAdminAuth,
    validateEmail,
    inviteUser,
    fetchUsers,
    fetchPendingInvites
  } from '../services/adminService';
  
  export {
    verifyInvite,
    register
  } from '../services/userService';
  
  export {
    createChat
  } from '../services/chatService';
  

  
  // Components (if needed)
  export {
    default as ChatWindow
  } from '../components/ChatWindow.vue';