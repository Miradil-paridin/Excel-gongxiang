<template>
  <div class="editor-page">
    <div class="editor-header">
      <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
      <el-input v-model="document.title" size="small" style="width: 300px" />

      <div class="header-buttons">
        <el-button size="small" type="primary" @click="handleSave" :loading="saving">
          保存
        </el-button>
        <el-button size="small" @click="handleCancel">取消</el-button>
      </div>
    </div>

    <div class="editor-content">
      <div v-if="document.type === 'doc'" class="doc-editor">
        <el-input
          v-model="document.content"
          type="textarea"
          :rows="20"
          placeholder="请输入文档内容..."
          style="width: 100%"
        />
      </div>

      <div v-if="document.type === 'sheet'" class="sheet-editor">
        <el-empty description="表格编辑器集成中..." />
        <p style="text-align: center; color: #909399; margin-top: 20px">
          后续将集成 Luckysheet 表格编辑器
        </p>
      </div>
    </div>

    <div class="editor-footer">
      <span>文档类型: {{ document.type === 'doc' ? '富文本文档' : '表格文档' }}</span>
      <span>版本: {{ document.version }}</span>
      <span>最后更新: {{ formatTime(document.updated_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDocument, updateDocument, type Document } from '@/api/documents'

const router = useRouter()
const route = useRoute()

const saving = ref(false)
const document = ref<Document>({
  id: 0,
  title: '',
  type: 'doc',
  content: '',
  creator: 0,
  creator_name: '',
  created_at: '',
  updated_at: '',
  version: 1,
  permission: 'owner',
  is_deleted: false,
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

// 获取文档
const fetchDocument = async () => {
  const id = Number(route.params.id)
  try {
    const response = await getDocument(id)
    document.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '获取文档失败')
    router.back()
  }
}

// 保存文档
const handleSave = async () => {
  saving.value = true
  try {
    await updateDocument(document.value.id, {
      title: document.value.title,
      content: document.value.content,
    })
    ElMessage.success('文档保存成功')
    router.back()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  router.back()
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchDocument()
})
</script>

<style scoped>
.editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  gap: 16px;
}

.header-buttons {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.editor-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background-color: #f5f7fa;
}

.doc-editor,
.sheet-editor {
  background-color: white;
  border-radius: 4px;
  padding: 20px;
  min-height: 500px;
}

.editor-footer {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background-color: white;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.1);
  gap: 20px;
  font-size: 12px;
  color: #909399;
}
</style>
