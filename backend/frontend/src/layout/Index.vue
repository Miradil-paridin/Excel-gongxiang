<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <el-icon :size="32">
          <Document />
        </el-icon>
        <span class="logo-text">协同文档</span>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-menu-item index="/documents">
          <el-icon><Document /></el-icon>
          <span>我的文档</span>
        </el-menu-item>

        <el-menu-item index="/files">
          <el-icon><Folder /></el-icon>
          <span>我的文件</span>
        </el-menu-item>

        <el-menu-item index="/shared">
          <el-icon><Share /></el-icon>
          <span>与我分享</span>
        </el-menu-item>

        <el-menu-item v-if="userStore.isStaff" index="/admin">
          <el-icon><Setting /></el-icon>
          <span>管理后台</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon @click="toggleSidebar" class="menu-icon">
            <Fold />
          </el-icon>
        </div>

        <div class="header-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文档、文件..."
            prefix-icon="Search"
            style="width: 300px"
          />

          <el-badge :value="0" class="notification-badge">
            <el-button icon="Bell" circle text />
          </el-badge>

          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="32">{{ userStore.username.substring(0, 1) }}</el-avatar>
              <span class="username">{{ userStore.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const searchQuery = ref('')

const toggleSidebar = () => {
  // TODO: 实现侧边栏折叠
  ElMessage.info('侧边栏折叠功能待实现')
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人设置功能待实现')
      break
    case 'password':
      ElMessage.info('修改密码功能待实现')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
        userStore.logout()
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background-color: #2b3a4b;
  color: white;
}

.logo-text {
  margin-left: 10px;
  font-size: 18px;
  font-weight: bold;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.menu-icon {
  font-size: 24px;
  cursor: pointer;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-badge {
  margin-right: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  color: #606266;
  font-size: 14px;
}
</style>
