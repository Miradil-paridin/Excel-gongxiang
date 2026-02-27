<template>
  <div class="tasks-page">
    <div class="toolbar">
      <el-button type="primary" @click="showTemplateDialog = true">上传模板</el-button>
      <el-button type="success" @click="openCreateTask">创建分发任务</el-button>
    </div>

    <el-table :data="tasks" v-loading="loading" style="width: 100%">
      <el-table-column prop="title" label="任务标题" min-width="220" />
      <el-table-column prop="template_name" label="模板" width="180" />
      <el-table-column prop="template_version" label="模板版本" width="100" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="deadline" label="截止时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.deadline) }}
        </template>
      </el-table-column>
      <el-table-column label="进度" width="260">
        <template #default="{ row }">
          <span>{{ progressText(row.id) }}</span>
          <el-button link type="primary" @click="loadProgress(row.id)">刷新</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showTemplateDialog" title="上传模板" width="460px">
      <el-form label-width="90px">
        <el-form-item label="模板名称">
          <el-input v-model="templateForm.name" />
        </el-form-item>
        <el-form-item label="模板分类">
          <el-input v-model="templateForm.category" />
        </el-form-item>
        <el-form-item label="模板文件">
          <input type="file" @change="onTemplateFileChange" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTemplateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitTemplate">上传</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTaskDialog" title="创建分发任务" width="520px">
      <el-form label-width="90px">
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" />
        </el-form-item>
        <el-form-item label="模板">
          <el-select v-model="taskForm.template" style="width: 100%">
            <el-option v-for="item in templates" :key="item.id" :label="`${item.name} (v${item.version})`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="接收用户">
          <el-select v-model="taskForm.target_users" multiple style="width: 100%">
            <el-option v-for="u in users" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="taskForm.deadline"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitTask">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers } from '@/api/shares'
import { createTask, createTemplate, getTaskProgress, getTasks, getTemplates } from '@/api/workflow'

const loading = ref(false)
const submitting = ref(false)
const showTemplateDialog = ref(false)
const showTaskDialog = ref(false)
const templates = ref<any[]>([])
const tasks = ref<any[]>([])
const users = ref<any[]>([])
const progressMap = ref<Record<number, string>>({})

const templateForm = reactive({
  name: '',
  category: '',
  file: null as File | null
})

const taskForm = reactive({
  title: '',
  template: undefined as number | undefined,
  target_users: [] as number[],
  deadline: ''
})

const formatDate = (value?: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

const progressText = (taskId: number) => progressMap.value[taskId] || '-'

const onTemplateFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  templateForm.file = input.files?.[0] || null
}

const loadTemplates = async () => {
  const res: any = await getTemplates()
  templates.value = Array.isArray(res) ? res : (res.data || [])
}

const loadTasks = async () => {
  loading.value = true
  try {
    const res: any = await getTasks()
    tasks.value = Array.isArray(res) ? res : (res.data || [])
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  const res: any = await getUsers()
  users.value = res.data || []
}

const loadProgress = async (taskId: number) => {
  try {
    const res: any = await getTaskProgress(taskId)
    progressMap.value[taskId] = `已报 ${res.submitted || 0}/${res.total || 0}`
  } catch (error: any) {
    ElMessage.error(error.message || '获取进度失败')
  }
}

const submitTemplate = async () => {
  if (!templateForm.name.trim() || !templateForm.file) {
    ElMessage.warning('请填写名称并选择文件')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('name', templateForm.name)
    formData.append('category', templateForm.category)
    formData.append('file', templateForm.file)
    await createTemplate(formData)
    ElMessage.success('模板上传成功')
    showTemplateDialog.value = false
    templateForm.name = ''
    templateForm.category = ''
    templateForm.file = null
    await loadTemplates()
  } catch (error: any) {
    ElMessage.error(error.message || '上传失败')
  } finally {
    submitting.value = false
  }
}

const openCreateTask = async () => {
  if (!templates.value.length) {
    await loadTemplates()
  }
  if (!users.value.length) {
    await loadUsers()
  }
  showTaskDialog.value = true
}

const submitTask = async () => {
  if (!taskForm.title.trim() || !taskForm.template || !taskForm.target_users.length) {
    ElMessage.warning('请完整填写任务信息')
    return
  }

  submitting.value = true
  try {
    await createTask({
      title: taskForm.title,
      template: taskForm.template,
      target_users: taskForm.target_users,
      deadline: taskForm.deadline || null,
      status: 'active'
    })
    ElMessage.success('任务创建成功')
    showTaskDialog.value = false
    taskForm.title = ''
    taskForm.template = undefined
    taskForm.target_users = []
    taskForm.deadline = ''
    await loadTasks()
  } catch (error: any) {
    ElMessage.error(error.message || '创建任务失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadTemplates()
  await loadTasks()
})
</script>

<style scoped>
.tasks-page {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}
</style>
