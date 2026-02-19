<template>
  <div class="shared-page">
    <!-- 标签页 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="与我分享的文档" name="documents">
        <el-table :data="sharedDocuments" v-loading="loading" style="width: 100%">
          <el-table-column prop="title" label="文档标题" min-width="200">
            <template #default="{ row }">
              <div class="item-title">
                <el-icon v-if="row.type === 'word'" class="type-icon word"><Document /></el-icon>
                <el-icon v-else-if="row.type === 'cell'" class="type-icon excel"><Grid /></el-icon>
                <el-icon v-else class="type-icon ppt"><PictureFilled /></el-icon>
                <span>{{ row.document_title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.document_type === 'word'" type="primary">Word</el-tag>
              <el-tag v-else-if="row.document_type === 'cell'" type="success">Excel</el-tag>
              <el-tag v-else type="warning">PPT</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="{ row }">
              <el-tag :type="row.permission === 'write' ? 'success' : 'info'">
                {{ row.permission === 'write' ? '可编辑' : '只读' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sharer_username" label="分享者" width="120" />
          <el-table-column prop="created_at" label="分享时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDocument(row)">打开</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="与我分享的文件" name="files">
        <el-table :data="sharedFiles" v-loading="loading" style="width: 100%">
          <el-table-column prop="name" label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="item-title">
                <el-icon class="type-icon"><Document /></el-icon>
                <span>{{ row.file_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="大小" width="120">
            <template #default="{ row }">
              {{ formatSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="{ row }">
              <el-tag :type="row.permission === 'write' ? 'success' : 'info'">
                {{ row.permission === 'write' ? '可下载' : '只读' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sharer_username" label="分享者" width="120" />
          <el-table-column prop="created_at" label="分享时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="downloadFile(row)">下载</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Grid, PictureFilled } from '@element-plus/icons-vue'
import { getSharedWithMe } from '@/api/shares'

const router = useRouter()

// 数据
const loading = ref(false)
const activeTab = ref('documents')
const sharedDocuments = ref<any[]>([])
const sharedFiles = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await getSharedWithMe()
    // 后端返回的是数组，按 target_type 分类
    const data = res.data || []
    sharedDocuments.value = data.filter((item: any) => item.target_type === 'document')
    sharedFiles.value = data.filter((item: any) => item.target_type === 'file')
    total.value = data.length
  } catch (error: any) {
    ElMessage.error(error.message || '获取分享列表失败')
  } finally {
    loading.value = false
  }
}

// 切换标签页
const handleTabChange = () => {
  currentPage.value = 1
  fetchData()
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化大小
const formatSize = (bytes: number) => {
  if (!bytes) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 打开文档
const openDocument = (item: any) => {
  router.push(`/editor/${item.document_id}`)
}

// 下载文件
const downloadFile = async (item: any) => {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
  try {
    const response = await fetch(`${API_BASE_URL}/files/${item.file_id}/download/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (!response.ok) throw new Error('下载失败')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = item.file_name
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    ElMessage.success('下载成功')
  } catch (error: any) {
    ElMessage.error(error.message || '下载失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.shared-page {
  padding: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 18px;
}

.type-icon.word {
  color: #409eff;
}

.type-icon.excel {
  color: #67c23a;
}

.type-icon.ppt {
  color: #e6a23c;
}
</style>
