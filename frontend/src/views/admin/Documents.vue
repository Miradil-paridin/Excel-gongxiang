<template>
  <div class="admin-documents">
    <el-page-header @back="goBack" content="管理后台 - 文档管理" />

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>文档列表</span>
          <div class="search-container">
            <el-select
              v-model="filter.creator"
              placeholder="按创建者筛选"
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
              v-model="filter.type"
              placeholder="按类型筛选"
              clearable
              style="width: 150px; margin-right: 10px"
              @change="handleFilterChange"
            >
              <el-option label="Word文档" value="word" />
              <el-option label="Excel表格" value="cell" />
              <el-option label="PPT演示" value="slide" />
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
        <el-table-column prop="title" label="文档名称" width="250" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'word'" type="primary">Word</el-tag>
            <el-tag v-else-if="row.type === 'cell'" type="success">Excel</el-tag>
            <el-tag v-else type="warning">PPT</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建者" width="120" />
        <el-table-column prop="creator_email" label="邮箱" width="200" />
        <el-table-column prop="share_count" label="分享次数" width="100" />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
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
              @click="handleView(row)"
            >
              <el-icon><View /></el-icon>
              预览
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
import { View, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminDocuments, deleteAdminDocument } from '@/api/admin'

const router = useRouter()

// 筛选条件
const filter = ref({
  creator: null as number | null,
  type: null as string | null,
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

// 筛选变化
const handleFilterChange = () => {
  loadDocuments()
}

// 预览文档
const handleView = (row: any) => {
  ElMessage.info(`文档 "${row.title}" 预览功能待实现`)
}

// 删除文档
const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要软删除文档 "${row.title}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteAdminDocument(row.id)
      ElMessage.success('文档已删除')
      loadDocuments()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 加载文档列表
const loadDocuments = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filter.value.creator) params.creator = filter.value.creator
    if (filter.value.type) params.type = filter.value.type
    if (filter.value.is_deleted !== null) params.is_deleted = filter.value.is_deleted

    const res = await getAdminDocuments({ params })
    tableData.value = res.data || []
    pagination.value.total = tableData.value.length
  } catch (error) {
    console.error('加载文档列表失败:', error)
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
  }
}

// 分页切换
const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadDocuments()
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.admin-documents {
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
