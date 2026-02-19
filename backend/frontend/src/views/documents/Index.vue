<template>
  <div class="documents-page">
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-select v-model="queryParams.type" placeholder="全部类型" clearable style="width: 100%">
            <el-option label="全部" value="" />
            <el-option label="文档" value="doc" />
            <el-option label="表格" value="sheet" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input
            v-model="queryParams.search"
            placeholder="搜索文档标题..."
            prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :span="10" style="text-align: right">
          <el-button type="primary" @click="handleCreate('doc')">
            <el-icon><Plus /></el-icon>
            新建文档
          </el-button>
          <el-button type="success" @click="handleCreate('sheet')">
            <el-icon><Plus /></el-icon>
            新建表格
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <span>我的文档</span>
      </template>

      <el-table :data="documentList" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-icon :size="16" style="margin-right: 8px">
              <Document v-if="row.type === 'doc'" />
              <Tickets v-if="row.type === 'sheet'" />
            </el-icon>
            <el-link type="primary" @click="handleOpen(row)">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'doc'" type="primary">文档</el-tag>
            <el-tag v-if="row.type === 'sheet'" type="success">表格</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="creator_name" label="创建者" width="120" />
        <el-table-column prop="version" label="版本" width="80" />

        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.updated_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleOpen(row)">编辑</el-button>
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
        @current-change="fetchDocuments"
        @size-change="fetchDocuments"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建文档' : '编辑文档'"
      width="500px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'create'" label="类型">
          <el-radio-group v-model="form.type">
            <el-radio-button label="doc">文档</el-radio-button>
            <el-radio-button label="sheet">表格</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getDocuments,
  createDocument,
  updateDocument,
  deleteDocument,
  type Document,
  type DocumentType,
} from '@/api/documents'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')

const queryParams = reactive({
  type: '',
  search: '',
  page: 1,
  page_size: 20,
  ordering: '-updated_at',
})

const pagination = reactive({
  total: 0,
  page: 1,
  page_size: 20,
})

const documentList = ref<Document[]>([])

const form = reactive({
  id: 0,
  title: '',
  type: 'doc' as DocumentType,
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

// 获取文档列表
const fetchDocuments = async () => {
  loading.value = true
  try {
    const response = await getDocuments(queryParams)
    documentList.value = response.data.results || response.data
    pagination.total = response.data.count || documentList.value.length
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  queryParams.page = 1
  fetchDocuments()
}

// 创建文档
const handleCreate = (type: DocumentType) => {
  dialogMode.value = 'create'
  form.title = ''
  form.type = type
  dialogVisible.value = true
}

// 打开文档（跳转到编辑器）
const handleOpen = (row: Document) => {
  router.push(`/editor/${row.id}`)
}

// 编辑文档（修改标题）
const handleEdit = (row: Document) => {
  dialogMode.value = 'edit'
  form.id = row.id
  form.title = row.title
  dialogVisible.value = true
}

// 删除文档
const handleDelete = async (row: Document) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档 "${row.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await deleteDocument(row.id)
    ElMessage.success('文档已删除')
    fetchDocuments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      const response = await createDocument({
        title: form.title,
        type: form.type,
      })
      ElMessage.success('文档创建成功')
      dialogVisible.value = false
      fetchDocuments()
      // 跳转到编辑器页面
      router.push(`/editor/${response.data.id}`)
    } else {
      await updateDocument(form.id, { title: form.title })
      ElMessage.success('文档更新成功')
      dialogVisible.value = false
      fetchDocuments()
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.documents-page {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  min-height: 400px;
}
</style>
