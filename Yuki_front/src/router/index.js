import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import MainPage from '@/views/content/MainPage.vue'
import ConfDataset from "@/views/content/components/ConfDataset.vue";
import EmptyPage from "@/views/content/empty/EmptyPage.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginPage
    },
    {
      path: '/main',
      name: 'main',
      component: MainPage
    },
    {
      path: '/datasets',
      name: 'datasets',
      component: ConfDataset
    },
    {
      path: '/404',
      name: 'empty',
      component: EmptyPage
    },
  ]
})

export default router


