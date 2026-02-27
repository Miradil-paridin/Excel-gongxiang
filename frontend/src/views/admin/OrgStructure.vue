<template>
  <div class="org-structure-page">
    <el-page-header @back="goBack" content="管理后台 - 组织架构" />

    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <el-tab-pane label="单位管理" name="orgs">
        <div class="toolbar">
          <el-button type="primary" @click="showOrgDialog = true">新增单位</el-button>
        </div>
        <el-table :data="organizations" v-loading="loadingOrgs" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="单位名称" />
          <el-table-column prop="code" label="单位编码" width="180" />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="editOrg(row)">编辑</el-button>
              <el-button v-if="isSuperAdmin" type="danger" size="small" @click="removeOrg(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="部门管理" name="depts">
        <div class="toolbar toolbar-dept">
          <el-select v-model="deptOrgFilter" clearable placeholder="按单位筛选" style="width: 240px" @change="loadDepartments">
            <el-option v-for="org in organizations" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
          <el-button type="primary" @click="showDeptDialog = true">新增部门</el-button>
        </div>
        <el-table :data="departments" v-loading="loadingDepts" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="部门名称" />
          <el-table-column prop="code" label="部门编码" width="180" />
          <el-table-column prop="organization_name" label="所属单位" width="220" />
          <el-table-column prop="parent_name" label="上级部门" width="180" />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="editDept(row)">编辑</el-button>
              <el-button v-if="isSuperAdmin" type="danger" size="small" @click="removeDept(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="用户组管理" name="groups">
        <div class="toolbar">
          <el-button type="primary" @click="showGroupDialog = true">新增用户组</el-button>
        </div>
        <el-table :data="groups" v-loading="loadingGroups" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="用户组名称" />
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="editGroup(row)">编辑</el-button>
              <el-button v-if="isSuperAdmin" type="danger" size="small" @click="removeGroup(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showOrgDialog" :title="orgForm.id ? '编辑单位' : '新增单位'" width="420px">
      <el-form :model="orgForm" label-width="90px">
        <el-form-item label="单位名称"><el-input v-model="orgForm.name" /></el-form-item>
        <el-form-item label="单位编码"><el-input v-model="orgForm.code" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="orgForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeOrgDialog">取消</el-button>
        <el-button type="primary" @click="saveOrg">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDeptDialog" :title="deptForm.id ? '编辑部门' : '新增部门'" width="520px">
      <el-form :model="deptForm" label-width="90px">
        <el-form-item label="部门名称"><el-input v-model="deptForm.name" /></el-form-item>
        <el-form-item label="部门编码"><el-input v-model="deptForm.code" /></el-form-item>
        <el-form-item label="所属单位">
          <el-select v-model="deptForm.organization" style="width: 100%" filterable>
            <el-option v-for="org in organizations" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="deptForm.parent" clearable style="width: 100%" filterable>
            <el-option v-for="dept in parentDeptOptions" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用"><el-switch v-model="deptForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDeptDialog">取消</el-button>
        <el-button type="primary" @click="saveDept">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showGroupDialog" :title="groupForm.id ? '编辑用户组' : '新增用户组'" width="420px">
      <el-form :model="groupForm" label-width="90px">
        <el-form-item label="用户组名"><el-input v-model="groupForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeGroupDialog">取消</el-button>
        <el-button type="primary" @click="saveGroup">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createAdminDepartment,
  createAdminGroup,
  createAdminOrganization,
  deleteAdminDepartment,
  deleteAdminGroup,
  deleteAdminOrganization,
  getAdminDepartments,
  getAdminGroups,
  getAdminOrganizations,
  updateAdminDepartment,
  updateAdminGroup,
  updateAdminOrganization,
} from '@/api/admin'

const router = useRouter()
const goBack = () => router.back()
const isSuperAdmin = ref(false)

const activeTab = ref('orgs')
const deptOrgFilter = ref<number | null>(null)

const organizations = ref<any[]>([])
const departments = ref<any[]>([])
const groups = ref<any[]>([])

const loadingOrgs = ref(false)
const loadingDepts = ref(false)
const loadingGroups = ref(false)

const showOrgDialog = ref(false)
const showDeptDialog = ref(false)
const showGroupDialog = ref(false)

const orgForm = ref<any>({ id: 0, name: '', code: '', is_active: true })
const deptForm = ref<any>({ id: 0, name: '', code: '', organization: null, parent: null, is_active: true })
const groupForm = ref<any>({ id: 0, name: '' })

const parentDeptOptions = computed(() => {
  if (!deptForm.value.organization) return departments.value
  return departments.value.filter((d: any) => d.organization === deptForm.value.organization && d.id !== deptForm.value.id)
})

const loadOrganizations = async () => {
  loadingOrgs.value = true
  try {
    const res = await getAdminOrganizations()
    organizations.value = res.data || []
  } finally {
    loadingOrgs.value = false
  }
}

const loadDepartments = async () => {
  loadingDepts.value = true
  try {
    const params = deptOrgFilter.value ? { organization: deptOrgFilter.value } : undefined
    const res = await getAdminDepartments(params)
    departments.value = res.data || []
  } finally {
    loadingDepts.value = false
  }
}

const loadGroups = async () => {
  loadingGroups.value = true
  try {
    const res = await getAdminGroups()
    groups.value = res.data || []
  } finally {
    loadingGroups.value = false
  }
}

const closeOrgDialog = () => {
  showOrgDialog.value = false
  orgForm.value = { id: 0, name: '', code: '', is_active: true }
}

const saveOrg = async () => {
  try {
    if (orgForm.value.id) {
      await updateAdminOrganization(orgForm.value.id, orgForm.value)
      ElMessage.success('单位更新成功')
    } else {
      await createAdminOrganization(orgForm.value)
      ElMessage.success('单位创建成功')
    }
    closeOrgDialog()
    loadOrganizations()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const editOrg = (row: any) => {
  orgForm.value = { ...row }
  showOrgDialog.value = true
}

const removeOrg = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除单位 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await deleteAdminOrganization(row.id)
    ElMessage.success('单位已删除')
    loadOrganizations()
    loadDepartments()
  } catch {}
}

const closeDeptDialog = () => {
  showDeptDialog.value = false
  deptForm.value = { id: 0, name: '', code: '', organization: null, parent: null, is_active: true }
}

const saveDept = async () => {
  if (!deptForm.value.organization) {
    ElMessage.warning('请选择所属单位')
    return
  }
  try {
    if (deptForm.value.id) {
      await updateAdminDepartment(deptForm.value.id, deptForm.value)
      ElMessage.success('部门更新成功')
    } else {
      await createAdminDepartment(deptForm.value)
      ElMessage.success('部门创建成功')
    }
    closeDeptDialog()
    loadDepartments()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const editDept = (row: any) => {
  deptForm.value = {
    id: row.id,
    name: row.name,
    code: row.code,
    organization: row.organization,
    parent: row.parent,
    is_active: row.is_active,
  }
  showDeptDialog.value = true
}

const removeDept = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除部门 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await deleteAdminDepartment(row.id)
    ElMessage.success('部门已删除')
    loadDepartments()
  } catch {}
}

const closeGroupDialog = () => {
  showGroupDialog.value = false
  groupForm.value = { id: 0, name: '' }
}

const saveGroup = async () => {
  try {
    if (groupForm.value.id) {
      await updateAdminGroup(groupForm.value.id, groupForm.value)
      ElMessage.success('用户组更新成功')
    } else {
      await createAdminGroup(groupForm.value)
      ElMessage.success('用户组创建成功')
    }
    closeGroupDialog()
    loadGroups()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const editGroup = (row: any) => {
  groupForm.value = { ...row }
  showGroupDialog.value = true
}

const removeGroup = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除用户组 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await deleteAdminGroup(row.id)
    ElMessage.success('用户组已删除')
    loadGroups()
  } catch {}
}

onMounted(async () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    isSuperAdmin.value = Boolean(user.is_superuser)
  } catch {
    isSuperAdmin.value = false
  }
  await Promise.all([loadOrganizations(), loadDepartments(), loadGroups()])
})
</script>

<style scoped>
.org-structure-page {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.toolbar-dept {
  justify-content: space-between;
}
</style>
