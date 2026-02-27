<template>
  <div class="admin-users">
    <el-page-header @back="goBack" content="管理后台 - 用户管理" />

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <div class="toolbar-left">
            <span>用户列表</span>
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户名/邮箱"
              style="width: 260px; margin-left: 16px"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <el-button type="primary" @click="openCreateDialog">新增用户</el-button>
        </div>
      </template>

      <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="220" />
        <el-table-column prop="organization_name" label="单位" width="150" />
        <el-table-column prop="department_name" label="部门" width="150" />
        <el-table-column prop="role_title" label="岗位" width="120" />
        <el-table-column label="用户组" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="g in row.groups || []" :key="g" size="small" style="margin-right: 6px">{{ g }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="document_count" label="文档数" width="80" />
        <el-table-column prop="file_count" label="文件数" width="80" />
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

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.is_superuser" type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button v-if="!row.is_superuser && isSuperAdmin" type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="createDialogVisible" title="新增用户" width="620px">
      <el-form :model="createForm" label-width="110px">
        <el-form-item label="用户名"><el-input v-model="createForm.username" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="createForm.email" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="createForm.password" type="password" show-password /></el-form-item>
        <el-form-item label="姓名">
          <el-row :gutter="10" style="width: 100%">
            <el-col :span="12"><el-input v-model="createForm.last_name" placeholder="姓" /></el-col>
            <el-col :span="12"><el-input v-model="createForm.first_name" placeholder="名" /></el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="单位">
          <el-select v-model="createForm.organization" clearable filterable style="width: 100%" @change="onCreateOrganizationChange">
            <el-option v-for="org in organizations" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="createForm.department" clearable filterable style="width: 100%">
            <el-option v-for="dept in createDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位"><el-input v-model="createForm.role_title" /></el-form-item>
        <el-form-item label="用户组">
          <el-select v-model="createForm.group_ids" multiple clearable filterable style="width: 100%" :disabled="!isSuperAdmin">
            <el-option v-for="group in groups" :key="group.id" :label="group.name" :value="group.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员"><el-switch v-model="createForm.is_staff" :disabled="!isSuperAdmin" /></el-form-item>
        <el-form-item label="启用状态"><el-switch v-model="createForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateUser">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑用户" width="620px">
      <el-form :model="editForm" label-width="110px">
        <el-form-item label="用户名"><el-input v-model="editForm.username" disabled /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="editForm.email" /></el-form-item>
        <el-form-item label="重置密码"><el-input v-model="editForm.password" placeholder="留空则不修改" type="password" show-password /></el-form-item>
        <el-form-item label="姓名">
          <el-row :gutter="10" style="width: 100%">
            <el-col :span="12"><el-input v-model="editForm.last_name" placeholder="姓" /></el-col>
            <el-col :span="12"><el-input v-model="editForm.first_name" placeholder="名" /></el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="单位">
          <el-select v-model="editForm.organization" clearable filterable style="width: 100%" @change="onEditOrganizationChange">
            <el-option v-for="org in organizations" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="editForm.department" clearable filterable style="width: 100%">
            <el-option v-for="dept in editDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位"><el-input v-model="editForm.role_title" /></el-form-item>
        <el-form-item label="用户组">
          <el-select v-model="editForm.group_ids" multiple clearable filterable style="width: 100%" :disabled="!isSuperAdmin">
            <el-option v-for="group in groups" :key="group.id" :label="group.name" :value="group.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员"><el-switch v-model="editForm.is_staff" :disabled="!isSuperAdmin" /></el-form-item>
        <el-form-item label="启用状态"><el-switch v-model="editForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAdminUsers,
  createAdminUser,
  updateAdminUser,
  deleteAdminUser,
  getAdminOrganizations,
  getAdminDepartments,
  getAdminGroups,
} from '@/api/admin'

const router = useRouter()

const searchQuery = ref('')
const isSuperAdmin = ref(false)
const tableData = ref<any[]>([])
const loading = ref(false)

const pagination = ref({ page: 1, pageSize: 20, total: 0 })

const organizations = ref<any[]>([])
const departments = ref<any[]>([])
const groups = ref<any[]>([])

const createDialogVisible = ref(false)
const editDialogVisible = ref(false)

const createForm = ref<any>({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  organization: null,
  department: null,
  role_title: '',
  group_ids: [],
  is_staff: false,
  is_active: true,
})

const editForm = ref<any>({
  id: 0,
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  organization: null,
  department: null,
  role_title: '',
  group_ids: [],
  is_staff: false,
  is_active: false,
})

const createDepartments = computed(() => {
  if (!createForm.value.organization) return departments.value
  return departments.value.filter((d: any) => d.organization === createForm.value.organization)
})

const editDepartments = computed(() => {
  if (!editForm.value.organization) return departments.value
  return departments.value.filter((d: any) => d.organization === editForm.value.organization)
})

const goBack = () => router.back()

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadMeta = async () => {
  const [orgRes, deptRes, groupRes] = await Promise.all([
    getAdminOrganizations(),
    getAdminDepartments(),
    getAdminGroups(),
  ])
  organizations.value = orgRes.data || []
  departments.value = deptRes.data || []
  groups.value = groupRes.data || []
}

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getAdminUsers({ search: searchQuery.value || undefined })
    tableData.value = res.data || []
    pagination.value.total = tableData.value.length
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => loadUsers()
const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadUsers()
}

const resetCreateForm = () => {
  createForm.value = {
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    organization: null,
    department: null,
    role_title: '',
    group_ids: [],
    is_staff: false,
    is_active: true,
  }
}

const openCreateDialog = () => {
  resetCreateForm()
  createDialogVisible.value = true
}

const onCreateOrganizationChange = () => {
  const inOrg = createDepartments.value.some((d: any) => d.id === createForm.value.department)
  if (!inOrg) createForm.value.department = null
}

const onEditOrganizationChange = () => {
  const inOrg = editDepartments.value.some((d: any) => d.id === editForm.value.department)
  if (!inOrg) editForm.value.department = null
}

const handleCreateUser = async () => {
  if (!createForm.value.username || !createForm.value.password) {
    ElMessage.warning('请至少填写用户名和密码')
    return
  }
  try {
    await createAdminUser(createForm.value)
    ElMessage.success('用户创建成功')
    createDialogVisible.value = false
    loadUsers()
  } catch (error: any) {
    ElMessage.error(error.message || '创建失败')
  }
}

const openEditDialog = (row: any) => {
  editForm.value = {
    id: row.id,
    username: row.username,
    email: row.email,
    password: '',
    first_name: row.first_name,
    last_name: row.last_name,
    organization: row.organization || null,
    department: row.department || null,
    role_title: row.role_title || '',
    group_ids: row.group_ids || [],
    is_staff: row.is_staff,
    is_active: row.is_active,
  }
  editDialogVisible.value = true
}

const handleSaveUser = async () => {
  try {
    const payload = { ...editForm.value }
    if (!payload.password) delete payload.password
    await updateAdminUser(editForm.value.id, payload)
    ElMessage.success('用户信息更新成功')
    editDialogVisible.value = false
    loadUsers()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  }
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await deleteAdminUser(row.id)
      ElMessage.success('用户已删除')
      loadUsers()
    })
    .catch(() => {})
}

onMounted(async () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    isSuperAdmin.value = Boolean(user.is_superuser)
  } catch {
    isSuperAdmin.value = false
  }
  await loadMeta()
  await loadUsers()
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

.toolbar-left {
  display: flex;
  align-items: center;
}
</style>
