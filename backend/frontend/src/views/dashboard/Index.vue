<template>
  <div class="dashboard">
    <div class="welcome-card">
      <el-card>
        <div class="welcome-header">
          <h2>👋 欢迎，{{ userStore.username }}！</h2>
          <p>今天是 {{ currentDate }}</p>
        </div>

        <div class="quick-actions">
          <el-button type="primary" size="large" @click="createDocument('doc')">
            <el-icon><Plus /></el-icon>
            新建文档
          </el-button>
          <el-button type="success" size="large" @click="createDocument('sheet')">
            <el-icon><Plus /></el-icon>
            新建表格
          </el-button>
          <el-upload :action="uploadUrl" :show-file-list="false">
            <el-button type="warning" size="large">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
        </div>
      </el-card>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <el-icon :size="32" color="#409EFF">
              <Document />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.documents }}</div>
              <div class="stat-label">我的文档</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <el-icon :size="32" color="#67C23A">
              <Tickets />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.files }}</div>
              <div class="stat-label">我的文件</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <el-icon :size="32" color="#E6A23C">
              <Share />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.shared }}</div>
              <div class="stat-label">与我分享</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <el-icon :size="32" color="#909399">
              <Files />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.storage }}</div>
              <div class="stat-label">已用存储</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="recent-docs">
      <template #header>
        <div class="card-header">
          <span>📅 近期文档</span>
          <el-button type="text" @click="$router.push('/documents')">查看更多</el-button>
        </div>
      </template>

      <el-empty v-if="recentDocs.length === 0" description="暂无文档" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import config from '@/config'

const router = useRouter()
const userStore = useUserStore()

const uploadUrl = computed(() => `${config.apiBaseUrl}/files/upload/`)

const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  })
})

const stats = ref({
  documents: 0,
  files: 0,
  shared: 0,
  storage: '0 MB',
})

const recentDocs = ref([])

const createDocument = (type: 'doc' | 'sheet') => {
  ElMessage.info(`创建${type === 'doc' ? '文档' : '表格'}功能待实现`)
}

const handleUpload = (file: File) => {
  ElMessage.info('文件上传功能待实现')
}
</script>

<script lang="ts">
import { ElMessage } from 'element-plus'
export default {
  methods: {
    ElMessage,
  },
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}

.welcome-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.quick-actions {
  margin-top: 24px;
  display: flex;
  gap: 16px;
  justify-content: center;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.recent-docs {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
