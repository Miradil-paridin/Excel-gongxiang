<template>
  <div class="dashboard-page">
    <!-- 页头 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">你好，{{ username }} 👋</h1>
        <p class="page-subtitle">{{ greeting }}，今天是 {{ today }}</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" @click="router.push('/documents')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1, #8b5cf6)">
          <svg viewBox="0 0 20 20" fill="white"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-label">我的文档</div>
          <div class="stat-desc">在线编辑 Word / Excel / PPT</div>
        </div>
        <div class="stat-arrow">
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
        </div>
      </div>

      <div class="stat-card" @click="router.push('/files')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #059669)">
          <svg viewBox="0 0 20 20" fill="white"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-label">文件管理</div>
          <div class="stat-desc">上传下载任意格式文件</div>
        </div>
        <div class="stat-arrow">
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
        </div>
      </div>

      <div class="stat-card" @click="router.push('/shares/shared-with-me')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706)">
          <svg viewBox="0 0 20 20" fill="white"><path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-label">与我分享</div>
          <div class="stat-desc">他人分享给我的文档文件</div>
        </div>
        <div class="stat-arrow">
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
        </div>
      </div>

      <div class="stat-card" @click="router.push('/shares/my-shares')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #ef4444, #dc2626)">
          <svg viewBox="0 0 20 20" fill="white"><path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11 4a1 1 0 10-2 0v4a1 1 0 102 0V7zm-3 1a1 1 0 10-2 0v3a1 1 0 102 0V8zM8 9a1 1 0 00-2 0v2a1 1 0 102 0V9z" clip-rule="evenodd"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-label">我的分享</div>
          <div class="stat-desc">管理我发起的所有分享</div>
        </div>
        <div class="stat-arrow">
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
        </div>
      </div>
    </div>

    <!-- 快速操作 + 系统信息 -->
    <div class="bottom-grid">
      <div class="panel quick-actions">
        <div class="panel-header">
          <h3>快速新建</h3>
        </div>
        <div class="quick-list">
          <button class="quick-btn" @click="quickCreate('word')">
            <div class="quick-icon word">W</div>
            <span>Word 文档</span>
          </button>
          <button class="quick-btn" @click="quickCreate('cell')">
            <div class="quick-icon excel">X</div>
            <span>Excel 表格</span>
          </button>
          <button class="quick-btn" @click="quickCreate('slide')">
            <div class="quick-icon ppt">P</div>
            <span>PPT 演示</span>
          </button>
        </div>
      </div>

      <div class="panel system-info">
        <div class="panel-header">
          <h3>系统信息</h3>
        </div>
        <div class="info-list">
          <div class="info-row">
            <span class="info-key">当前用户</span>
            <span class="info-val">{{ username }}</span>
          </div>
          <div class="info-row">
            <span class="info-key">账号角色</span>
            <span class="info-val">
              <span class="role-tag" :class="{ admin: isAdmin }">{{ isAdmin ? '管理员' : '普通用户' }}</span>
            </span>
          </div>
          <div class="info-row">
            <span class="info-key">OnlyOffice</span>
            <span class="info-val"><span class="status-dot"></span> 运行中</span>
          </div>
          <div class="info-row">
            <span class="info-key">系统版本</span>
            <span class="info-val">v1.0.0</span>
          </div>
        </div>
        <template v-if="isAdmin">
          <div class="admin-link" @click="router.push('/admin/dashboard')">
            <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/></svg>
            进入管理后台
          </div>
        </template>
      </div>
    </div>

    <!-- 快速创建弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新建文档" width="380px" align-center>
      <el-form :model="newDoc" size="large">
        <el-form-item label="文档标题">
          <el-input v-model="newDoc.title" :placeholder="`请输入${typeLabel}标题`" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createDocument } from '@/api/documents'

const router = useRouter()

const username = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || '{}').username || '用户' } catch { return '用户' }
})
const isAdmin = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || '{}').is_staff || false } catch { return false }
})

const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
const hour = new Date().getHours()
const greeting = hour < 6 ? '夜深了，注意休息' : hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好'

const showCreateDialog = ref(false)
const creating = ref(false)
const newDoc = ref({ title: '', type: 'word' })
const typeLabel = computed(() => ({ word: 'Word 文档', cell: 'Excel 表格', slide: 'PPT 演示' }[newDoc.value.type] || '文档'))

const quickCreate = (type: string) => {
  newDoc.value = { title: '', type }
  showCreateDialog.value = true
}

const submitCreate = async () => {
  if (!newDoc.value.title.trim()) {
    ElMessage.warning('请输入文档标题')
    return
  }
  creating.value = true
  try {
    const res: any = await createDocument(newDoc.value)
    ElMessage.success('文档创建成功')
    showCreateDialog.value = false
    const docId = res?.data?.id || res?.id
    if (docId) router.push(`/editor/${docId}`)
    else router.push('/documents')
  } catch (error: any) {
    ElMessage.error(error.message || '创建失败')
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.dashboard-page {
  padding: 32px 36px;
  max-width: 1100px;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border-color: #e2e8f0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 3px;
}

.stat-desc {
  font-size: 12px;
  color: #94a3b8;
}

.stat-arrow {
  color: #cbd5e1;
  flex-shrink: 0;
}
.stat-arrow svg { width: 18px; height: 18px; }

/* 底部双栏 */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.panel {
  background: white;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  overflow: hidden;
}

.panel-header {
  padding: 18px 20px 14px;
  border-bottom: 1px solid #f1f5f9;
}

.panel-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

/* 快速操作 */
.quick-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.15s;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.quick-btn:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.quick-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  color: white;
  flex-shrink: 0;
}

.quick-icon.word { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.quick-icon.excel { background: linear-gradient(135deg, #10b981, #059669); }
.quick-icon.ppt { background: linear-gradient(135deg, #f59e0b, #d97706); }

/* 系统信息 */
.info-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
}

.info-key { color: #64748b; }
.info-val {
  font-weight: 500;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  display: inline-block;
}

.role-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #e2e8f0;
  color: #475569;
}
.role-tag.admin {
  background: #ede9fe;
  color: #7c3aed;
}

.admin-link {
  margin: 0 16px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f5f3ff;
  border-radius: 8px;
  color: #7c3aed;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.admin-link:hover { background: #ede9fe; }
.admin-link svg { width: 16px; height: 16px; }
</style>
