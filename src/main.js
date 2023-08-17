import './assets/style.css'

import { createApp } from 'vue'
import App from './App.vue'


import {route} from './router' // 載入配置檔


createApp(App).use(route).mount('#app')
