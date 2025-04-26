import { createApp } from "vue";
import App from "./App.vue";
import './assets/style.css'
import { createPinia } from "pinia"; // ✅ Import Pinia
const pinia = createPinia();
import router from './router'  // adjust the path if necessary

createApp(App).use(router).use(pinia).mount('#app')
