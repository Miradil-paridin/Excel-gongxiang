<template>
  <div class="admin-dashboard">
    <el-page-header @back="goBack" content="管理后台 - 仪表盘" />

    <el-card class="quick-entry-card" style="margin-top: 20px; margin-bottom: 20px">
      <el-space wrap>
        <el-button type="primary" @click="goTo('/admin/users')">用户管理</el-button>
        <el-button type="success" @click="goTo('/admin/org-structure')">组织架构</el-button>
        <el-button type="warning" @click="goTo('/admin/documents')">文档管理</el-button>
        <el-button type="danger" @click="goTo('/admin/files')">文件管理</el-button>
      </el-space>
    </el-card>

    <div class="dashboard-stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon user-icon">
              <UserFilled />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.user_total }}</div>
              <div class="stat-label">用户总数</div>
              <div class="stat-trend">
                <span class="trend-up" v-if="userTrend.length > 0">
                  +{{ userTrend[userTrend.length - 1].count }} (今日)
                </span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon doc-icon">
              <Document />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.document_total }}</div>
              <div class="stat-label">文档总数</div>
              <div class="stat-trend">
                <span class="trend-up" v-if="docTrend.length > 0">
                  +{{ docTrend[docTrend.length - 1].count }} (今日)
                </span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon file-icon">
              <Folder />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.file_total }}</div>
              <div class="stat-label">文件总数</div>
              <div class="stat-trend">
                <span class="trend-up" v-if="fileTrend.length > 0">
                  +{{ fileTrend[fileTrend.length - 1].count }} (今日)
                </span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon share-icon">
              <Share />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.share_total }}</div>
              <div class="stat-label">分享总数</div>
              <div class="stat-desc">
                活跃用户: {{ activeUsers }}
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="dashboard-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>用户增长趋势</span>
              </div>
            </template>
            <div ref="userChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>文档创建趋势</span>
              </div>
            </template>
            <div ref="docChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>文件上传趋势</span>
              </div>
            </template>
            <div ref="fileChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>存储使用情况</span>
              </div>
            </template>
            <div ref="storageChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="dashboard-tables">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>热门文档</span>
              </div>
            </template>
            <el-table :data="hotDocuments" style="width: 100%" max-height="300">
              <el-table-column prop="title" label="文档名称" />
              <el-table-column prop="creator__username" label="创建者" />
              <el-table-column prop="version" label="版本" />
              <el-table-column prop="updated_at" label="更新时间">
                <template #default="{ row }">
                  {{ formatDate(row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>热门文件</span>
              </div>
            </template>
            <el-table :data="hotFiles" style="width: 100%" max-height="300">
              <el-table-column prop="original_name" label="文件名" />
              <el-table-column prop="uploader__username" label="上传者" />
              <el-table-column prop="size" label="大小">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="上传时间">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  UserFilled,
  Document,
  Folder,
  Share
} from '@element-plus/icons-vue'
import { getAdminDashboard } from '@/api/admin'
import * as echarts from 'echarts'

const router = useRouter()

// 统计数据
const statistics = ref({
  user_total: 0,
  user_active: 0,
  document_total: 0,
  file_total: 0,
  share_total: 0,
  storage_used: 0
})

const userTrend = ref<any[]>([])
const docTrend = ref<any[]>([])
const fileTrend = ref<any[]>([])
const activeUsers = ref(0)
const hotDocuments = ref<any[]>([])
const hotFiles = ref<any[]>([])

// 图表引用
const userChartRef = ref<HTMLElement>()
const docChartRef = ref<HTMLElement>()
const fileChartRef = ref<HTMLElement>()
const storageChartRef = ref<HTMLElement>()

// 返回上一页
const goBack = () => {
  router.back()
}

const goTo = (path: string) => {
  router.push(path)
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  else if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  else return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

// 初始化用户增长图表
const initUserChart = () => {
  if (!userChartRef.value) return
  const chart = echarts.init(userChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: userTrend.value.map(item => item.date)
    },
    yAxis: { type: 'value' },
    series: [{
      data: userTrend.value.map(item => item.count),
      type: 'line',
      smooth: true,
      itemStyle: { color: '#409eff' }
    }]
  }
  chart.setOption(option)
}

// 初始化文档趋势图表
const initDocChart = () => {
  if (!docChartRef.value) return
  const chart = echarts.init(docChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: docTrend.value.map(item => item.date)
    },
    yAxis: { type: 'value' },
    series: [{
      data: docTrend.value.map(item => item.count),
      type: 'bar',
      itemStyle: { color: '#67c23a' }
    }]
  }
  chart.setOption(option)
}

// 初始化文件趋势图表
const initFileChart = () => {
  if (!fileChartRef.value) return
  const chart = echarts.init(fileChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: fileTrend.value.map(item => item.date)
    },
    yAxis: { type: 'value' },
    series: [{
      data: fileTrend.value.map(item => item.count),
      type: 'bar',
      itemStyle: { color: '#e6a23c' }
    }]
  }
  chart.setOption(option)
}

// 初始化存储使用图表
const initStorageChart = () => {
  if (!storageChartRef.value) return
  const chart = echarts.init(storageChartRef.value)
  const option = {
    tooltip: {
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: [
        { value: statistics.value.storage_used, name: '已使用' },
        { value: 100 * 1024 * 1024 * 1024 - statistics.value.storage_used, name: '剩余' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  chart.setOption(option)
}

// 加载仪表盘数据
const loadDashboard = async () => {
  try {
    const res = await getAdminDashboard()
    const data = res.data

    statistics.value = data.statistics
    userTrend.value = data.user_trend
    docTrend.value = data.doc_trend
    fileTrend.value = data.file_trend
    activeUsers.value = data.active_users
    hotDocuments.value = data.hot_documents
    hotFiles.value = data.hot_files

    // 初始化图表
    setTimeout(() => {
      initUserChart()
      initDocChart()
      initFileChart()
      initStorageChart()
    }, 100)
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error('加载仪表盘数据失败')
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}

.dashboard-stats {
  margin-bottom: 20px;
}

.stat-card {
  text-align: left;
  padding: 20px;
}

.stat-icon {
  font-size: 40px;
  float: left;
  margin-right: 15px;
}

.user-icon {
  color: #409eff;
}

.doc-icon {
  color: #67c23a;
}

.file-icon {
  color: #e6a23c;
}

.share-icon {
  color: #f56c6c;
}

.stat-info {
  overflow: hidden;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.stat-trend {
  font-size: 12px;
  color: #67c23a;
  margin-top: 5px;
}

.trend-up::before {
  content: '↑';
  margin-right: 3px;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  font-weight: bold;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.dashboard-tables {
  margin-top: 20px;
}
</style>
