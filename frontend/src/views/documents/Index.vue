<template>
  <div class="documents-page">
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <div class="left">
        <el-select v-model="typeFilter" placeholder="文档类型" clearable style="width: 120px" @change="fetchDocuments">
          <el-option label="全部" value="" />
          <el-option label="Word文档" value="word" />
          <el-option label="Excel表格" value="cell" />
          <el-option label="PPT演示" value="slide" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文档标题"
          style="width: 200px; margin-left: 10px"
          clearable
          @input="debounceSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建文档
        </el-button>
      </div>
    </div>

    <!-- 文档列表 -->
    <el-table :data="documents" v-loading="loading" style="width: 100%" @row-click="handleRowClick">
      <el-table-column prop="title" label="标题" min-width="200">
        <template #default="{ row }">
          <div class="doc-title">
            <el-icon v-if="row.type === 'word'" class="doc-icon word"><DocIcon /></el-icon>
            <el-icon v-else-if="row.type === 'cell'" class="doc-icon excel"><Grid /></el-icon>
            <el-icon v-else class="doc-icon ppt"><PictureFilled /></el-icon>
            <span>{{ row.title }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.type === 'word'" type="primary">Word</el-tag>
          <el-tag v-else-if="row.type === 'cell'" type="success">Excel</el-tag>
          <el-tag v-else type="warning">PPT</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_username" label="创建者" width="120" />
      <el-table-column prop="updated_at" label="更新时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click.stop="openEditor(row)">编辑</el-button>
          <el-button type="success" link @click.stop="handleShare(row)">分享</el-button>
          <el-button type="danger" link @click.stop="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchDocuments"
        @current-change="fetchDocuments"
      />
    </div>

    <!-- 新建文档对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建文档" width="400px">
      <el-form :model="newDoc" label-width="80px">
        <el-form-item label="文档标题">
          <el-input v-model="newDoc.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="文档类型">
          <el-radio-group v-model="newDoc.type">
            <el-radio value="word">Word 文档</el-radio>
            <el-radio value="cell">Excel 表格</el-radio>
            <el-radio value="slide">PPT 演示</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createNewDocument" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 分享对话框 -->
    <el-dialog v-model="showShareDialog" title="分享文档" width="450px">
      <el-form :model="shareForm" label-width="80px">
        <el-form-item label="文档">
          <el-input :model-value="sharingDoc?.title" disabled />
        </el-form-item>
        <el-form-item label="分享给">
          <el-select
            v-model="shareForm.user_ids"
            multiple
            filterable
            placeholder="选择用户"
            style="width: 100%"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="权限">
          <el-radio-group v-model="shareForm.permission">
            <el-radio value="read">只读</el-radio>
            <el-radio value="write">可编辑</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShareDialog = false">取消</el-button>
        <el-button type="primary" @click="submitShare" :loading="sharing">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Document as DocIcon, Grid, PictureFilled } from '@element-plus/icons-vue'
import { getDocuments, createDocument as createDocumentApi, deleteDocument, type Document } from '@/api/documents'
import { getUsers } from '@/api/shares'

const router = useRouter()

// 数据
const loading = ref(false)
const creating = ref(false)
const sharing = ref(false)
const documents = ref<Document[]>([])
const userList = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选
const typeFilter = ref('')
const searchKeyword = ref('')

// 对话框
const showCreateDialog = ref(false)
const showShareDialog = ref(false)

// 新建文档
const newDoc = ref({
  title: '',
  type: 'word'
})

// 分享
const sharingDoc = ref<Document | null>(null)
const shareForm = ref({
  user_ids: [] as number[],
  permission: 'read'
})

let searchTimer: ReturnType<typeof setTimeout> | null = null

// 获取文档列表
const fetchDocuments = async () => {
  loading.value = true
  try {
    const res: any = await getDocuments({
      page: currentPage.value,
      page_size: pageSize.value,
      type: typeFilter.value || undefined,
      search: searchKeyword.value || undefined
    })
    documents.value = res.results || res.data || []
    total.value = res.count || documents.value.length
  } catch (error: any) {
    ElMessage.error(error.message || '获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 防抖搜索
const debounceSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchDocuments()
  }, 300)
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

// 创建文档
const createNewDocument = async () => {
  if (!newDoc.value.title.trim()) {
    ElMessage.warning('请输入文档标题')
    return
  }
  creating.value = true
  try {
    await createDocumentApi(newDoc.value)
    ElMessage.success('文档创建成功')
    showCreateDialog.value = false
    newDoc.value = { title: '', type: 'word' }
    fetchDocuments()
  } catch (error: any) {
    ElMessage.error(error.message || '创建失败')
  } finally {
    creating.value = false
  }
}

// 处理删除
const handleDelete = async (doc: Document) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档 "${doc.title}" 吗？`, '提示', {
      type: 'warning'
    })
    await deleteDocument(doc.id)
    ElMessage.success('删除成功')
    fetchDocuments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 打开编辑器
const openEditor = (doc: Document) => {
  router.push(`/editor/${doc.id}`)
}

// 点击行
const handleRowClick = (row: Document) => {
  openEditor(row)
}

// 分享
const handleShare = async (doc: Document) => {
  sharingDoc.value = doc
  shareForm.value = { user_ids: [], permission: 'read' }
  // 获取用户列表
  try {
    const res: any = await getUsers()
    userList.value = res.results || res.data || []
  } catch (error) {
    userList.value = []
  }
  showShareDialog.value = true
}

// 提交分享
import { createShare } from '@/api/shares'

const submitShare = async () => {
  if (!sharingDoc.value || shareForm.value.user_ids.length === 0) {
    ElMessage.warning('请选择要分享的用户')
    return
  }
  sharing.value = true
  try {
    for (const userId of shareForm.value.user_ids) {
      await createShare({
        document: sharingDoc.value.id,
        sharee: userId,
        permission: shareForm.value.permission
      })
    }
    ElMessage.success('分享成功')
    showShareDialog.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '分享失败')
  } finally {
    sharing.value = false
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

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.left {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.doc-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.doc-icon {
  font-size: 18px;
}

.doc-icon.word {
  color: #409eff;
}

.doc-icon.excel {
  color: #67c23a;
}

.doc-icon.ppt {
  color: #e6a23c;
}
</style>
