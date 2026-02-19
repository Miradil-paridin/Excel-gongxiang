import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/Index.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { title: '首页' },
      },
      {
        path: '/documents',
        name: 'Documents',
        component: () => import('@/views/documents/Index.vue'),
        meta: { title: '我的文档' },
      },
      {
        path: '/files',
        name: 'Files',
        component: () => import('@/views/files/Index.vue'),
        meta: { title: '我的文件' },
      },
      {
        path: '/editor/:id',
        name: 'Editor',
        component: () => import('@/views/editor/Index.vue'),
        meta: { title: '文档编辑' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const isAuthenticated = !!userStore.token

  // 需要登录的页面
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  }
  // 已登录用户访问登录页，跳转到首页
  else if (to.path === '/login' && isAuthenticated) {
    next({ path: '/' })
  }
  // 已登录用户访问注册页，跳转到首页
  else if (to.path === '/register' && isAuthenticated) {
    next({ path: '/' })
  } else {
    next()
  }
})

export default router
