import { createRouter, createWebHistory } from '../composables/index'
import NewChat from '../views/NewChatPage.vue'
import ChatPage from '../views/ChatPage.vue'
import LoginPage from '../views/LoginPage.vue'
import ResetPasswordPage from '../views/ResetPasswordPage.vue'
import AdminConsolePage from '../views/AdminConsolePage.vue'
import RegistrationPage from '../views/RegistrationPage.vue'
import ChatHistory from '../views/ChatHistory.vue'
import Collections from '../views/CollectionsPage.vue'
import CollectionsDetail from '../views/CollectionsDetail.vue'
import NewCollectionPage from '../views/NewCollectionPage.vue'
import SetNewPasswordPage from '../views/SetNewPasswordPage.vue'

import LoadingPage from '../views/LoadingPage.vue'
import UserSettings from '../views/UserSettings.vue'
import StartPage from '../views/StartPage.vue'

//import NewProjectPage from '../views/NewProjectPage.vue'
//import ProjectPage from '../views/ProjectPage.vue'
//import ProjectsPage from '../views/ProjectsPage.vue'

import { useAuthStore } from '../stores/authStore'
import axios from 'axios'

import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/start',
    name: 'start',
    component: StartPage,
    meta: { requiresAuth: false, hideSidebar: true }
  },
  {
    path: '/',
    name: 'Home',
    component: NewChat,
    meta: { requiresAuth: true }
  },
  {
    path: '/chat/:id',
    name: 'Chat',
    component: ChatPage,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/loading-chat',
    name: 'LoadingChat',
    component: LoadingPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { hideSidebar: true }
  },
  {
    path: '/resetpassword',
    name: 'ResetPassword',
    component: ResetPasswordPage,
    meta: { hideSidebar: true }
  },
  {
    path: '/newpassword',
    name: 'SetNewPassword',
    component: SetNewPasswordPage,
    meta: { hideSidebar: true }
  },
  {
    path: '/register',
    name: 'Register',
    meta: { hideSidebar: true },
    component: RegistrationPage,
    props: (route) => ({ token: route.query.token as string | undefined })
  },
  {
    path: '/admin-console',
    name: 'AdminConsolePage',
    component: AdminConsolePage,
    meta: { hideSidebar: false, requiresAuth: true }
  },
  {
    path: '/chat-history',
    name: 'ChatHistoryPage',
    component: ChatHistory,
    meta: { hideSidebar: false, requiresAuth: true }
  },
  {
    path: '/collections',
    name: 'Collections',
    component: Collections,
    meta: { hideSidebar: false, requiresAuth: true }
  },
  {
    path: '/collections/:id',
    name: 'collection-detail',
    component: CollectionsDetail, 
    meta: { hideSidebar: false, requiresAuth: true }
  },
  {
    path: '/collections/new',
    name: 'new-collection',
    component: NewCollectionPage, 
    meta: { hideSidebar: false, requiresAuth: true }
  },
  /*{
    path: '/projects',
    name: 'projects',
    component: ProjectsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/new',
    name: 'new-project',
    component: NewProjectPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:id',
    name: 'Project',
    component: ProjectPage,  // Use the ProjectPage component
    meta: { requiresAuth: true }
  },*/
  {
    path: '/settings',
    name: 'UserSettings',
    component: UserSettings,
    meta: { requiresAuth: true }
  },
  {
    path: '/:catchAll(.*)',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Add navigation guard to check for first-time setup
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const publicRoutes = ["Login", "Register", "ResetPasswordPage", "start"];
  
  // First-time setup check should happen regardless of authentication
  // (except for Register page which needs to process normally)
  if (to.name !== 'Register') {
    try {
      console.log("Router checking first user at:", "/check-first-user");
      const response = await axios.get('/check-first-user', {
        withCredentials: true
      });
      console.log('Router first user check response:', response.data);
      const { is_first_user } = response.data;
      
      if (is_first_user) {
        // If this is first-time setup and not already going to start page, redirect
        if (to.name !== 'start') {
          return next({ name: 'start' });
        }
        // Continue to start page
        return next();
      }
    } catch (error) {
      console.error('Router error checking first user:', error);
      // Continue with normal flow if check fails
    }
  }

  // Public routes don't need authentication check
  if (publicRoutes.includes(String(to.name))) {
    authStore.isLoading = false;
    return next();
  }

  // Check authentication for protected routes
  await authStore.checkAuth();
  if (!authStore.isAuthenticated) {
    return next('/login');
  }

  // Normal authenticated flow
  next();
});

export default router