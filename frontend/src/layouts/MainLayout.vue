<template>
  <div class="app-shell">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="#6366f1"/>
            <path d="M8 10h16M8 16h10M8 22h13" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="logo-text" v-show="!sidebarCollapsed">协同文档</span>
      </div>

      <!-- 导航 -->
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" active-class="active" exact>
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/></svg>
          </span>
          <span class="nav-text" v-show="!sidebarCollapsed">首页</span>
        </router-link>

        <router-link to="/documents" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"/></svg>
          </span>
          <span class="nav-text" v-show="!sidebarCollapsed">文档管理</span>
        </router-link>

        <router-link to="/files" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/></svg>
          </span>
          <span class="nav-text" v-show="!sidebarCollapsed">文件管理</span>
        </router-link>

        <div class="nav-divider" v-show="!sidebarCollapsed"><span>协作</span></div>

        <router-link to="/shares/shared-with-me" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor"><path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"/></svg>
          </span>
          <span class="nav-text" v-show="!sidebarCollapsed">与我分享</span>
        </router-link>

        <router-link to="/shares/my-shares" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11 4a1 1 0 10-2 0v4a1 1 0 102 0V7zm-3 1a1 1 0 10-2 0v3a1 1 0 102 0V8zM8 9a1 1 0 00-2 0v2a1 1 0 102 0V9z" clip-rule="evenodd"/></svg>
          </span>
          <span class="nav-text" v-show="!sidebarCollapsed">我的分享</span>
        </router-link>

        <template v-if="isAdmin">
          <div class="nav-divider" v-show="!sidebarCollapsed"><span>管理</span></div>
          <router-link to="/admin/dashboard" class="nav-item" active-class="active">
            <span class="nav-icon">
              <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/></svg>
            </span>
            <span class="nav-text" v-show="!sidebarCollapsed">管理后台</span>
          </router-link>
        </template>
      </nav>

      <!-- 底部用户信息 -->
      <div class="sidebar-footer">
        <div class="user-info" v-show="!sidebarCollapsed">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-detail">
            <div class="user-name">{{ username }}</div>
            <div class="user-role">{{ isAdmin ? '管理员' : '普通用户' }}</div>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" :title="sidebarCollapsed ? '退出登录' : ''">
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd"/></svg>
          <span v-show="!sidebarCollapsed">退出</span>
        </button>
      </div>

      <!-- 折叠按钮 -->
      <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
        <svg viewBox="0 0 20 20" fill="currentColor" :style="{ transform: sidebarCollapsed ? 'rotate(180deg)' : 'none' }">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
      </button>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const sidebarCollapsed = ref(false)

const username = computed(() => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return user.username || '用户'
  } catch {
    return '用户'
  }
})

const isAdmin = computed(() => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return user.is_staff || false
  } catch {
    return false
  }
})

const userInitial = computed(() => username.value.charAt(0).toUpperCase())

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning',
    })
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
    router.push('/')
  } catch {}
}
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  background: #f1f5f9;
  overflow: hidden;
}

/* ===== 侧边栏 ===== */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, min-width 0.25s ease;
  position: relative;
  z-index: 10;
  box-shadow: 4px 0 15px rgba(0,0,0,0.15);
}

.sidebar.collapsed {
  width: 64px;
  min-width: 64px;
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.logo-icon svg {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: #f8fafc;
  white-space: nowrap;
  letter-spacing: -0.3px;
}

/* 导航 */
.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 10px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  margin-bottom: 2px;
  transition: all 0.18s ease;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 500;
}

.nav-item:hover {
  background: rgba(255,255,255,0.07);
  color: #e2e8f0;
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  border-left: 3px solid #6366f1;
  padding-left: 7px;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  width: 18px;
  height: 18px;
}

.nav-text {
  overflow: hidden;
}

.nav-divider {
  padding: 16px 10px 6px;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  white-space: nowrap;
}

/* 底部 */
.sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-detail {
  min-width: 0;
  overflow: hidden;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 11px;
  color: #64748b;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.18s;
  white-space: nowrap;
  flex-shrink: 0;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.logout-btn svg {
  width: 16px;
  height: 16px;
}

/* 折叠按钮 */
.collapse-btn {
  position: absolute;
  top: 50%;
  right: -13px;
  transform: translateY(-50%);
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid #1e293b;
  background: #1e293b;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s;
  z-index: 11;
}

.collapse-btn:hover {
  background: #6366f1;
  border-color: #6366f1;
  color: white;
}

.collapse-btn svg {
  width: 14px;
  height: 14px;
  transition: transform 0.25s ease;
}

/* 主内容区 */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
}
</style>
