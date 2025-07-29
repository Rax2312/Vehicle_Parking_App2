import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ApiService from './services/ApiService'


createApp(App).use(router).mount('#app') 
