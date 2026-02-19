<template>
  <div class="editor-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <span class="doc-title">{{ documentTitle }}</span>
      </div>
      <div class="right">
        <el-tag v-if="canEdit" type="success">可编辑</el-tag>
        <el-tag v-else type="info">只读</el-tag>
      </div>
    </div>

    <!-- 编辑器容器 -->
    <div id="onlyoffice-container" v-loading="loading" element-loading-text="加载编辑器..."></div>

    <!-- 错误提示 -->
    <el-empty v-if="error" :description="error" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getEditorConfig, getDocument } from '@/api/documents'

const route = useRoute()
const router = useRouter()

// 数据
const loading = ref(true)
const error = ref('')
const documentTitle = ref('')
const canEdit = ref(false)
let editor: any = null
let docEditor: any = null

// OnlyOffice 脚本 URL (会在获取配置后动态设置)
let ONLYOFFICE_SCRIPT = ''

// 获取文档ID
const getDocumentId = () => {
  const id = route.params.id
  return Array.isArray(id) ? id[0] : id
}

// 加载 OnlyOffice 脚本
const loadOnlyOfficeScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if ((window as any).DocsAPI && (window as any).DocsAPI.DocEditor) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.src = ONLYOFFICE_SCRIPT
    script.onload = () => resolve()
    script.onerror = () => {
      // OnlyOffice 服务未部署，显示提示信息
      loading.value = false
      error.value = 'OnlyOffice 服务未部署，无法打开编辑器。请部署 OnlyOffice Document Server 后再试。'
      reject(new Error('OnlyOffice service not deployed'))
    }
    document.head.appendChild(script)
  })
}

// 初始化编辑器
const initEditor = async () => {
  loading.value = true
  error.value = ''

  try {
    const docId = getDocumentId()

    // 获取文档信息
    const docRes: any = await getDocument(parseInt(docId))
    documentTitle.value = docRes.data?.title || '文档'

    // 获取编辑器配置
    const res: any = await getEditorConfig(parseInt(docId))
    console.log('Editor config response:', res)

    if (res.code !== 0) {
      throw new Error(res.message || '获取编辑器配置失败')
    }

    // 从 res.data 中获取配置
    const { config, onlyofficeUrl, canEdit: edit } = res.data
    console.log('Config:', config)
    console.log('OnlyOffice URL:', onlyofficeUrl)
    canEdit.value = edit

    // 设置 OnlyOffice 脚本 URL
    ONLYOFFICE_SCRIPT = `${onlyofficeUrl}web-apps/apps/api/documents/api.js`
    console.log('Loading OnlyOffice script from:', ONLYOFFICE_SCRIPT)

    // 加载 OnlyOffice 脚本
    await loadOnlyOfficeScript()
    console.log('OnlyOffice script loaded, DocsAPI:', (window as any).DocsAPI)

    // 创建编辑器
    const container = document.getElementById('onlyoffice-container')
    if (!container) {
      throw new Error('Editor container not found')
    }

    console.log('Creating DocEditor with config:', {
      document: config.document,
      documentType: config.documentType,
      editorConfig: config.editorConfig,
    })
    console.log('Document URL:', config.document.url)
    console.log('Document key:', config.document.key)

    // 创建 DocEditor 实例（第一个参数必须是元素 ID 字符串）
    docEditor = new (window as any).DocsAPI.DocEditor('onlyoffice-container', {
      document: config.document,
      documentType: config.documentType,
      editorConfig: config.editorConfig,
      token: config.token,
      width: '100%',
      height: '100%',
      events: {
        onAppReady: () => {
          console.log('OnlyOffice editor ready')
          loading.value = false
        },
        onError: (event: any) => {
          console.error('OnlyOffice editor error:', event)
          error.value = '编辑器加载失败，请检查 OnlyOffice 服务'
          loading.value = false
        }
      }
    })
    console.log('DocEditor created:', docEditor)

    // 检查页面中的iframe
    setTimeout(() => {
      const iframes = document.querySelectorAll('iframe')
      console.log('Iframes on page:', iframes.length)
      iframes.forEach((iframe, i) => {
        console.log(`Iframe ${i}:`, iframe.src, iframe.style.width, iframe.style.height)
      })
    }, 3000)

    loading.value = false
  } catch (err: any) {
    console.error('Editor error:', err)
    error.value = err.message || '加载编辑器失败'
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/documents')
}

// 组件卸载时销毁编辑器
onBeforeUnmount(() => {
  if (docEditor) {
    try {
      docEditor.destroyEditor()
    } catch (e) {
      console.error('Error destroying editor:', e)
    }
  }
})

onMounted(() => {
  initEditor()
})
</script>

<style scoped>
.editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.doc-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

#onlyoffice-container {
  flex: 1;
  width: 100%;
  min-height: 500px;
}
</style>
