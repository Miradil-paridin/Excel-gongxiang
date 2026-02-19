<template>
  <div class="files-page">
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="12">
          <el-input
            v-model="queryParams.search"
            placeholder="搜索文件名..."
            prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-upload
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <span>我的文件</span>
      </template>

      <el-table :data="fileList" v-loading="loading" style="width: 100%">
        <el-table-column prop="original_name" label="文件名" min-width="200">
          <template #default="{ row }">
            <el-icon :size="16" style="margin-right: 8px">
              <Picture v-if="row.file_type === 'image'" />
              <Document v-else-if="row.file_type === 'document'" />
              <Tickets v-else-if="row.file_type === 'spreadsheet'" />
              <Folder v-else />
            </el-icon>
            {{ row.original_name }}
          </template>
        </el-table-column>

        <el-table-column prop="file_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.file_type === 'image'" type="warning">图片</el-tag>
            <el-tag v-else-if="row.file_type === 'document'" type="primary">文档</el-tag>
            <el-tag v-else-if="row.file_type === 'spreadsheet'" type="success">表格</el-tag>
            <el-tag v-else>其他</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="file_size_display" label="大小" width="100" />
        <el-table-column prop="uploader_name" label="上传者" width="120" />

        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleDownload(row)">下载</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="pagination.total > 0"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchFiles"
        @size-change="fetchFiles"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFiles, downloadFile, deleteFile, type File } from '@/api/files'
import config from '@/config'

const uploadUrl = `${config.apiBaseUrl}/files/`
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
}

const loading = ref(false)
const fileList = ref<File[]>([])

const queryParams = reactive({
  search: '',
  page: 1,
  page_size: 20,
  ordering: '-created_at',
})

const pagination = reactive({
  total: 0,
  page: 1,
  page_size: 20,
})

// 格式化时间
const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 获取文件列表
const fetchFiles = async () => {
  loading.value = true
  try {
    const response = await getFiles(queryParams)
    fileList.value = response.data.results || response.data
    pagination.total = response.data.count || fileList.value.length
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '获取文件列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  queryParams.page = 1
  fetchFiles()
}

// 上传成功
const handleUploadSuccess = (response: any) => {
  ElMessage.success('文件上传成功')
  fetchFiles()
}

// 上传失败
const handleUploadError = (error: any) => {
  ElMessage.error(error.response?.data?.message || '上传失败')
}

// 下载文件
const handleDownload = async (row: File) => {
  try {
    const blob = await downloadFile(row.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = row.original_name
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '下载失败')
  }
}

// 删除文件
const handleDelete = async (row: File) => {
  try {
    await ElMessageBox.confirm(`确定要删除文件 "${row.original_name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await deleteFile(row.id)
    ElMessage.success('文件已删除')
    fetchFiles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
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

.search-card {
  margin-bottom: 20px;
}

.table-card {
  min-height: 400px;
}
</style>
