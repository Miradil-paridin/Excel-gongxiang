<template>
  <div class="shares-page">
    <!-- 标签页 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="我的文档分享" name="documents">
        <el-table :data="sharedDocuments" v-loading="loading" style="width: 100%">
          <el-table-column prop="title" label="文档标题" min-width="200">
            <template #default="{ row }">
              <div class="item-title">
                <el-icon v-if="row.document_type === 'word'" class="type-icon word"><Document /></el-icon>
                <el-icon v-else-if="row.document_type === 'cell'" class="type-icon excel"><Grid /></el-icon>
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
          <el-table-column prop="sharee_username" label="分享给" width="120" />
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="{ row }">
              <el-tag :type="row.permission === 'write' ? 'success' : 'info'">
                {{ row.permission === 'write' ? '可编辑' : '只读' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '有效' : '已失效' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="shared_at" label="分享时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.shared_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="warning" link @click="toggleShare(row)">
                {{ row.is_active ? '取消' : '启用' }}
              </el-button>
              <el-button type="danger" link @click="deleteShare(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="我的文件分享" name="files">
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
          <el-table-column prop="sharee_username" label="分享给" width="120" />
          <el-table-column prop="permission" label="权限" width="100">
            <template #default="{ row }">
              <el-tag :type="row.permission === 'write' ? 'success' : 'info'">
                {{ row.permission === 'write' ? '可下载' : '只读' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '有效' : '已失效' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="shared_at" label="分享时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.shared_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="warning" link @click="toggleShare(row)">
                {{ row.is_active ? '取消' : '启用' }}
              </el-button>
              <el-button type="danger" link @click="deleteShare(row)">删除</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Grid, PictureFilled } from '@element-plus/icons-vue'
import { getMyShares, toggleShare as toggleShareApi, deleteShare as deleteShareApi } from '@/api/shares'

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
    const res: any = await getMyShares()
    // 后端返回的是数组，按 target_type 分类
    const data = Array.isArray(res) ? res : (res.data || [])
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

// 切换分享状态
const toggleShare = async (item: any) => {
  try {
    await toggleShareApi(item.id)
    ElMessage.success(item.is_active ? '已取消分享' : '已启用分享')
    fetchData()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 删除分享
const deleteShare = async (item: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条分享记录吗？', '提示', {
      type: 'warning'
    })
    await deleteShareApi(item.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.shares-page {
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
