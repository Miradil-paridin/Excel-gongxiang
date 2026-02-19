import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue')
  },
  {
    path: '/editor/:id',
    name: 'Editor',
    component: () => import('@/views/editor/Index.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/home/Dashboard.vue'),
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('@/views/documents/Index.vue'),
      },
      {
        path: 'files',
        name: 'Files',
        component: () => import('@/views/files/Index.vue'),
      },
      {
        path: 'shares/shared-with-me',
        name: 'SharedWithMe',
        component: () => import('@/views/shares/SharedWithMe.vue'),
      },
      {
        path: 'shares/my-shares',
        name: 'MyShares',
        component: () => import('@/views/shares/MyShares.vue'),
      },
      {
        path: 'admin',
        redirect: '/admin/dashboard'
      },
      {
        path: 'admin/dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/documents',
        name: 'AdminDocuments',
        component: () => import('@/views/admin/Documents.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/files',
        name: 'AdminFiles',
        component: () => import('@/views/admin/Files.vue'),
        meta: { requiresAdmin: true }
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  let user: any = {}
  try {
    const userStr = localStorage.getItem('user')
    if (userStr && userStr !== 'undefined') {
      user = JSON.parse(userStr)
    }
  } catch (e) {
    user = {}
  }

  const requiresAuth = to.meta.requiresAuth || to.matched.some(r => r.meta.requiresAuth)
  const requiresAdmin = to.meta.requiresAdmin || to.matched.some(r => r.meta.requiresAdmin)

  if (requiresAuth && !token) {
    next('/')
  } else if (requiresAdmin && !user.is_staff) {
    ElMessage.error('无权访问管理后台')
    next('/dashboard')
  } else {
    next()
  }
})

export default router
