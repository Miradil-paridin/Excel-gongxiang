<template>
  <div class="my-tasks-page">
    <el-table :data="assignments" v-loading="loading" style="width: 100%">
      <el-table-column prop="task_title" label="任务标题" min-width="220" />
      <el-table-column prop="template_name" label="模板" width="180" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="task_deadline" label="截止时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.task_deadline) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button type="primary" link @click="saveDraft(row)">保存草稿</el-button>
          <el-button type="success" link @click="submitRow(row)">上报</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createSubmission, getMyTaskAssignments, submitSubmission } from '@/api/workflow'

const loading = ref(false)
const assignments = ref<any[]>([])
const submissionMap = ref<Record<number, number>>({})

const formatDate = (value?: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

const loadAssignments = async () => {
  loading.value = true
  try {
    const res: any = await getMyTaskAssignments()
    assignments.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error: any) {
    ElMessage.error(error.message || '获取任务失败')
  } finally {
    loading.value = false
  }
}

const saveDraft = async (row: any) => {
  try {
    const res: any = await createSubmission({
      assignment: row.id,
      extracted_data: {}
    })
    const submissionId = res?.id || res?.data?.id
    if (submissionId) {
      submissionMap.value[row.id] = submissionId
    }
    ElMessage.success('草稿已保存')
    await loadAssignments()
  } catch (error: any) {
    ElMessage.error(error.message || '保存草稿失败')
  }
}

const submitRow = async (row: any) => {
  try {
    let submissionId = submissionMap.value[row.id]
    if (!submissionId) {
      const draftResp: any = await createSubmission({
        assignment: row.id,
        extracted_data: {}
      })
      submissionId = draftResp?.id || draftResp?.data?.id
      if (!submissionId) throw new Error('创建草稿失败')
      submissionMap.value[row.id] = submissionId
    }
    await submitSubmission(submissionId)
    ElMessage.success('上报成功')
    await loadAssignments()
  } catch (error: any) {
    ElMessage.error(error.message || '上报失败')
  }
}

onMounted(async () => {
  await loadAssignments()
})
</script>

<style scoped>
.my-tasks-page {
  padding: 20px;
}
</style>
