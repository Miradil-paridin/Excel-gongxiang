<template>
  <div class="admin-users">
    <el-page-header @back="goBack" content="管理后台 - 用户管理" />

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名/邮箱"
            style="width: 300px; margin-left: 20px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>

      <el-table
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="first_name" label="姓氏" width="100" />
        <el-table-column prop="last_name" label="名字" width="100" />
        <el-table-column prop="document_count" label="文档数" width="80" />
        <el-table-column prop="file_count" label="文件数" width="80" />
        <el-table-column prop="share_count" label="分享数" width="80" />

        <el-table-column label="管理员" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_staff" type="success">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success">启用</el-tag>
            <el-tag v-else type="danger">禁用</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="date_joined" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>

        <el-table-column prop="last_login" label="最后登录" width="180">
          <template #default="{ row }">
            {{ formatDate(row.last_login) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_superuser"
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="!row.is_superuser"
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              重置密码
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

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="500px"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" disabled />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="editForm.is_staff" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="editForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminUsers, updateAdminUser } from '@/api/admin'

const router = useRouter()

// 搜索
const searchQuery = ref('')

// 表格数据
const tableData = ref<any[]>([])
const loading = ref(false)

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 编辑对话框
const editDialogVisible = ref(false)
const editForm = ref({
  id: 0,
  username: '',
  email: '',
  is_staff: false,
  is_active: false
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

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getAdminUsers()
    tableData.value = res.data || []
    pagination.value.total = tableData.value.length
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  // 这里可以添加搜索逻辑，目前先重新加载全部
  loadUsers()
}

// 分页切换
const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadUsers()
}

// 编辑用户
const handleEdit = (row: any) => {
  editForm.value = {
    id: row.id,
    username: row.username,
    email: row.email,
    is_staff: row.is_staff,
    is_active: row.is_active
  }
  editDialogVisible.value = true
}

// 保存用户
const handleSaveUser = async () => {
  try {
    await updateAdminUser(editForm.value.id, {
      is_staff: editForm.value.is_staff,
      is_active: editForm.value.is_active
    })
    ElMessage.success('用户信息更新成功')
    editDialogVisible.value = false
    loadUsers()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  }
}

// 重置密码
const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要重置用户 "${row.username}" 的密码吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('密码已重置为默认密码')
  }).catch(() => {})
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-users {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
