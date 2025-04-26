
import {  ref, defineStore } from '../composables/index'
export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref(false);

  const toggleSidebar = () => {
    isCollapsed.value = !isCollapsed.value;
  };

  return { isCollapsed, toggleSidebar };
});
