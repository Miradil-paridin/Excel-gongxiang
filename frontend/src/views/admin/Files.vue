<template>
  <div class="admin-files">
    <el-page-header @back="goBack" content="管理后台 - 文件管理" />

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>文件列表</span>
          <div class="search-container">
            <el-select
              v-model="filter.uploader"
              placeholder="按上传者筛选"
              clearable
              style="width: 200px; margin-right: 10px"
              @change="handleFilterChange"
            >
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.username"
                :value="user.id"
              />
            </el-select>
            <el-select
              v-model="filter.is_deleted"
              placeholder="删除状态"
              clearable
              style="width: 150px; margin-right: 10px"
              @change="handleFilterChange"
            >
              <el-option label="未删除" :value="false" />
              <el-option label="已删除" :value="true" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="original_name" label="文件名" width="250" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="mime_type" label="类型" width="150" />
        <el-table-column prop="uploader_name" label="上传者" width="120" />
        <el-table-column prop="uploader_email" label="邮箱" width="200" />
        <el-table-column prop="share_count" label="分享次数" width="100" />
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="删除状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_deleted" type="danger">已删除</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleDownload(row)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              v-if="!row.is_deleted"
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon>
              软删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Download, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminFiles, deleteAdminFile } from '@/api/admin'

const router = useRouter()

// 筛选条件
const filter = ref({
  uploader: null as number | null,
  is_deleted: null as boolean | null
})

// 用户列表
const users = ref<any[]>([])

// 表格数据
const tableData = ref<any[]>([])
const loading = ref(false)

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 返回上一页
const goBack = () => {
  router.back()
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  else if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  else return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

// 筛选变化
const handleFilterChange = () => {
  loadFiles()
}

// 下载文件
const handleDownload = (row: any) => {
  ElMessage.info('下载功能待实现')
}

// 删除文件
const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要软删除文件 "${row.original_name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteAdminFile(row.id)
      ElMessage.success('文件已删除')
      loadFiles()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 加载文件列表
const loadFiles = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filter.value.uploader) params.uploader = filter.value.uploader
    if (filter.value.is_deleted !== null) params.is_deleted = filter.value.is_deleted

    const res = await getAdminFiles(params)
    tableData.value = res.data || []
    pagination.value.total = tableData.value.length
  } catch (error) {
    console.error('加载文件列表失败:', error)
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

// 分页切换
const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadFiles()
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.admin-files {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.search-container {
  display: flex;
  align-items: center;
}
</style>
