import { createRouter, createWebHistory } from 'vue-router'
import FileList from './views/FileList.vue'
import FileEdit from './views/FileEdit.vue'

const routes = [
  {
    path: '/',
    name: 'FileList',
    component: FileList
  },
  {
    path: '/edit/:filename',
    name: 'FileEdit',
    component: FileEdit
  },
  {
    path: '/create',
    name: 'FileCreate',
    component: FileEdit
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
