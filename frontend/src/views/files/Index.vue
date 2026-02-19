<template>
  <div class="files-page">
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <div class="left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文件名"
          style="width: 200px"
          clearable
          @input="debounceSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="right">
        <el-upload
          ref="uploadRef"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          multiple
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon>
            上传文件
          </el-button>
        </el-upload>
      </div>
    </div>

    <!-- 文件列表 -->
    <el-table :data="files" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" label="文件名" min-width="250">
        <template #default="{ row }">
          <div class="file-name">
            <el-icon class="file-icon"><Document /></el-icon>
            <span>{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="size" label="大小" width="120">
        <template #default="{ row }">
          {{ formatSize(row.size) }}
        </template>
      </el-table-column>
      <el-table-column prop="mime_type" label="类型" width="150">
        <template #default="{ row }">
          <el-tag size="small">{{ getFileType(row.mime_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_username" label="上传者" width="120" />
      <el-table-column prop="created_at" label="上传时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleDownload(row)">下载</el-button>
          <el-button type="success" link @click="handleShare(row)">分享</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchFiles"
        @current-change="fetchFiles"
      />
    </div>

    <!-- 分享对话框 -->
    <el-dialog v-model="showShareDialog" title="分享文件" width="450px">
      <el-form :model="shareForm" label-width="80px">
        <el-form-item label="文件">
          <el-input :model-value="sharingFile?.name" disabled />
        </el-form-item>
        <el-form-item label="分享给">
          <el-select
            v-model="shareForm.user_ids"
            multiple
            filterable
            placeholder="选择用户"
            style="width: 100%"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="权限">
          <el-radio-group v-model="shareForm.permission">
            <el-radio value="read">只读</el-radio>
            <el-radio value="write">可下载</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShareDialog = false">取消</el-button>
        <el-button type="primary" @click="submitShare" :loading="sharing">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Upload, Document } from '@element-plus/icons-vue'
import { getFiles, deleteFile, uploadFile, type FileItem } from '@/api/files'
import { getUsers, createShare } from '@/api/shares'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 数据
const loading = ref(false)
const sharing = ref(false)
const files = ref<FileItem[]>([])
const userList = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 搜索
const searchKeyword = ref('')

// 上传
const uploadRef = ref()
const uploadUrl = `${API_BASE_URL}/files/`
const uploadHeaders = ref({
  Authorization: `Bearer ${localStorage.getItem('token')}`
})

// 对话框
const showShareDialog = ref(false)

// 分享
const sharingFile = ref<FileItem | null>(null)
const shareForm = ref({
  user_ids: [] as number[],
  permission: 'read'
})

let searchTimer: ReturnType<typeof setTimeout> | null = null

// 获取文件列表
const fetchFiles = async () => {
  loading.value = true
  try {
    const res: any = await getFiles({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value || undefined
    })
    files.value = res.results || res.data || []
    total.value = res.count || files.value.length
  } catch (error: any) {
    ElMessage.error(error.message || '获取文件列表失败')
  } finally {
    loading.value = false
  }
}

// 防抖搜索
const debounceSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchFiles()
  }, 300)
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

// 获取文件类型
const getFileType = (mimeType: string) => {
  if (!mimeType) return '文件'
  if (mimeType.startsWith('image/')) return '图片'
  if (mimeType.startsWith('video/')) return '视频'
  if (mimeType.startsWith('audio/')) return '音频'
  if (mimeType.includes('pdf')) return 'PDF'
  if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('tar')) return '压缩包'
  return '文件'
}

// 上传前
const beforeUpload = (file: File) => {
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过100MB')
    return false
  }
  return true
}

// 上传成功
const handleUploadSuccess = (response: any) => {
  ElMessage.success('文件上传成功')
  fetchFiles()
}

// 上传失败
const handleUploadError = (error: any) => {
  ElMessage.error(error.message || '上传失败')
}

// 下载
const handleDownload = async (file: FileItem) => {
  try {
    const response = await fetch(`${API_BASE_URL}/files/${file.id}/download/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (!response.ok) throw new Error('下载失败')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.name
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    ElMessage.success('下载成功')
  } catch (error: any) {
    ElMessage.error(error.message || '下载失败')
  }
}

// 删除
const handleDelete = async (file: FileItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除文件 "${file.name}" 吗？`, '提示', {
      type: 'warning'
    })
    await deleteFile(file.id)
    ElMessage.success('删除成功')
    fetchFiles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 分享
const handleShare = async (file: FileItem) => {
  sharingFile.value = file
  shareForm.value = { user_ids: [], permission: 'read' }
  // 获取用户列表
  try {
    const res: any = await getUsers()
    userList.value = res.data || []
  } catch (error) {
    userList.value = []
  }
  showShareDialog.value = true
}

// 提交分享
const submitShare = async () => {
  if (!sharingFile.value || shareForm.value.user_ids.length === 0) {
    ElMessage.warning('请选择要分享的用户')
    return
  }
  sharing.value = true
  try {
    for (const userId of shareForm.value.user_ids) {
      await createShare({
        file: sharingFile.value.id,
        sharee: userId,
        permission: shareForm.value.permission
      })
    }
    ElMessage.success('分享成功')
    showShareDialog.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '分享失败')
  } finally {
    sharing.value = false
  }
}

onMounted(() => {
  fetchFiles()
})
</script>

<style scoped>
.files-page {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.left {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 18px;
  color: #909399;
}
</style>
