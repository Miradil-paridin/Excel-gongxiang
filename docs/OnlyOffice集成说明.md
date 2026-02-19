# OnlyOffice 集成说明

## 一、技术选型调整

### 编辑器选择：OnlyOffice Document Server

**为什么选择 OnlyOffice**:
- ✅ **功能强大**: 完整支持 Word、Excel、PPT 文档格式
- ✅ **开源免费**: 社区版完全免费，企业版可选
- ✅ **协同编辑**: 支持多人实时协同编辑
- ✅ **格式兼容**: 高度兼容 Microsoft Office 格式
- ✅ **私有部署**: 可在局域网内部署，数据完全自主
- ✅ **API 完善**: 提供完善的 JavaScript API

**对比其他编辑器**:
| 编辑器 | 富文本 | 表格 | 协同编辑 | Office兼容 | 部署复杂度 |
|--------|--------|------|----------|------------|------------|
| **OnlyOffice** | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Luckysheet | ❌ | ✅ | ❌ | ⭐⭐ | ⭐ |
| Tiptap | ✅ | ❌ | ❌ | ⭐ | ⭐ |
| Etherpad | ✅ | ❌ | ✅ | ⭐ | ⭐⭐ |

---

## 二、系统架构调整

### 新增组件：OnlyOffice Document Server

```
┌─────────────────────────────────────────────────────────────────┐
│                        局域网协同文档系统                           │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  前端 (Vue 3)                                                  │
│  ┌─────────────┬─────────────┬─────────────┬──────────────┐  │
│  │   首页      │  文档列表    │ OnlyOffice │  文件管理     │  │
│  │  登录/仪表盘 │  列表/搜索   │  编辑器页   │  上传/下载    │  │
│  └─────────────┴─────────────┴─────────────┴──────────────┘  │
└──────────────────────────┬────────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌───────────────────────────────────────────────────────────────┐
│  后端 (Django + DRF)                                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  API层: 认证、文档管理、文件管理、回调处理               │  │
│  │  业务层: 文档转换、权限控制、协作管理                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────┬──────────────────────────┘
             │                      │
             │                      │ HTTP Callback
             ▼                      ▼
    ┌──────────────┐      ┌───────────────────────┐
    │  PostgreSQL  │      │  OnlyOffice Document  │
    │  (主数据库)   │      │  Server (Docker)      │
    └──────────────┘      │  - 文档编辑服务        │
                          │  - 协同编辑引擎        │
                          │  - 格式转换服务        │
                          └───────────────────────┘
                                    │
                                    ▼
                          ┌──────────────┐
                          │  文件存储     │
                          │  /data/files/│
                          └──────────────┘
```

---

## 三、Document 模型调整

### 新增字段
```python
class Document(models.Model):
    """文档模型"""

    title = models.CharField(max_length=255, default='未命名文档')
    type = models.CharField(max_length=20, choices=[
        ('word', 'Word文档'),
        ('cell', 'Excel表格'),
        ('slide', 'PPT演示'),
    ])

    # OnlyOffice 相关字段
    file = models.FileField(upload_to='documents/', null=True)  # 文档文件
    file_url = models.URLField(blank=True)  # 文档访问URL
    file_key = models.CharField(max_length=255, blank=True)  # 文档唯一标识

    # 编辑状态
    is_locked = models.BooleanField(default=False)  # 是否被锁定编辑
    locked_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # 锁定用户
    locked_at = models.DateTimeField(null=True)  # 锁定时间

    # 协同编辑
    session_id = models.CharField(max_length=255, blank=True)  # 编辑会话ID

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
```

---

## 四、API 接口调整

### 新增接口

#### 1. 获取文档编辑配置
```http
GET /api/documents/{id}/editor-config/
Authorization: Bearer <token>

# 响应
{
  "code": 0,
  "data": {
    "document": {
      "fileType": "docx",
      "key": "document_unique_key",
      "title": "测试文档.docx",
      "url": "http://backend/file/path/test.docx"
    },
    "documentType": "word",
    "editorConfig": {
      "callbackUrl": "http://backend/api/documents/callback/",
      "mode": "edit",
      "user": {
        "id": "1",
        "name": "张三"
      },
      "lang": "zh-CN"
    }
  }
}
```

#### 2. OnlyOffice 回调接口
```http
POST /api/documents/callback/
Content-Type: application/json

# OnlyOffice 保存文档后回调
{
  "status": 2,  # 2=已保存, 3=强制保存
  "key": "document_unique_key",
  "url": "http://documentserver/cache/file.docx",
  "users": ["uid-1", "uid-2"]
}

# 响应
{
  "error": 0  # 0=成功
}
```

---

## 五、前端集成方案

### 1. 安装 OnlyOffice 编辑器组件
```bash
npm install @onlyoffice/document-editor-react
# 或使用原生 JavaScript 集成
```

### 2. 编辑器页面组件
```vue
<template>
  <div class="editor-container">
    <!-- OnlyOffice 编辑器容器 -->
    <div id="onlyoffice-editor"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { getEditorConfig } from '@/api/documents'

const props = defineProps({
  documentId: Number
})

let editor = null

onMounted(async () => {
  // 获取编辑器配置
  const response = await getEditorConfig(props.documentId)
  const config = response.data

  // 初始化 OnlyOffice 编辑器
  editor = new DocsAPI.DocEditor("onlyoffice-editor", config)
})

onUnmounted(() => {
  if (editor) {
    editor.destroyEditor()
  }
})
</script>
```

---

## 六、部署方案

### 使用 Docker 部署 OnlyOffice Document Server

#### 1. 创建 docker-compose.yml
```yaml
version: '3.8'

services:
  onlyoffice-document-server:
    image: onlyoffice/documentserver:latest
    container_name: onlyoffice-document-server
    restart: always
    ports:
      - "8081:80"
    volumes:
      - ./onlyoffice/data:/var/www/onlyoffice/Data
      - ./onlyoffice/logs:/var/log/onlyoffice
    environment:
      - JWT_ENABLED=true
      - JWT_SECRET=your-secret-key-here
```

#### 2. 启动服务
```bash
docker-compose up -d
```

#### 3. 访问地址
- OnlyOffice Document Server: `http://localhost:8081`
- 健康检查: `http://localhost:8081/healthcheck`

---

## 七、后端配置

### settings.py 配置
```python
# OnlyOffice 配置
ONLYOFFICE_API_URL = 'http://localhost:8081/'
ONLYOFFICE_JWT_SECRET = 'your-secret-key-here'
ONLYOFFICE_JWT_HEADER = 'AuthorizationJWT'
ONLYOFFICE_STORAGE_PATH = os.path.join(BASE_DIR, 'media', 'documents')

# 文档类型映射
ONLYOFFICE_DOCUMENT_TYPES = {
    'docx': 'word',
    'xlsx': 'cell',
    'pptx': 'slide',
    'doc': 'word',
    'xls': 'cell',
    'ppt': 'slide',
    'odt': 'word',
    'ods': 'cell',
    'odp': 'slide',
    'rtf': 'word',
    'txt': 'word',
}
```

---

## 八、安全配置

### 1. JWT 认证
```python
import jwt
from datetime import datetime, timedelta

def generate_security_token(payload):
    """生成 OnlyOffice JWT Token"""
    payload['exp'] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(payload, settings.ONLYOFFICE_JWT_SECRET, algorithm='HS256')
```

### 2. 回调验证
```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def document_callback(request):
    """OnlyOffice 文档保存回调"""
    if request.method != 'POST':
        return JsonResponse({'error': 1})

    # 验证 JWT
    token = request.headers.get(settings.ONLYOFFICE_JWT_HEADER)
    if not verify_jwt_token(token):
        return JsonResponse({'error': 1})

    data = json.loads(request.body)
    if data.get('status') in [2, 3]:  # 已保存或强制保存
        # 下载并保存文档
        download_and_save_document(data['url'], data['key'])
        return JsonResponse({'error': 0})

    return JsonResponse({'error': 0})
```

---

## 九、功能特性

### 1. 文档编辑
- ✅ Word 文档编辑 (.docx, .doc, .odt, .rtf)
- ✅ Excel 表格编辑 (.xlsx, .xls, .ods)
- ✅ PPT 演示编辑 (.pptx, .ppt, .odp)

### 2. 协同编辑
- ✅ 多人实时协同编辑
- ✅ 光标位置显示
- ✅ 操作冲突解决
- ✅ 版本自动保存

### 3. 格式转换
- ✅ 支持多种格式导入导出
- ✅ PDF 导出
- ✅ 打印功能

### 4. 权限控制
- ✅ 只读模式
- ✅ 可编辑模式
- ✅ 表单填写模式
- ✅ 评论模式

---

## 十、开发任务清单

### 后端任务
- [ ] 安装 Docker 和 Docker Compose
- [ ] 部署 OnlyOffice Document Server
- [ ] 修改 Document 模型，添加 OnlyOffice 相关字段
- [ ] 实现文档上传和存储逻辑
- [ ] 实现编辑器配置接口 (`/api/documents/{id}/editor-config/`)
- [ ] 实现 OnlyOffice 回调接口 (`/api/documents/callback/`)
- [ ] 实现文档下载和版本管理

### 前端任务
- [ ] 安装 OnlyOffice 编辑器组件
- [ ] 创建编辑器页面组件
- [ ] 实现编辑器配置获取
- [ ] 实现编辑器初始化和销毁
- [ ] 添加加载状态和错误处理

### 测试任务
- [ ] 测试文档创建和编辑
- [ ] 测试文档保存和回调
- [ ] 测试协同编辑功能
- [ ] 测试文档格式转换
- [ ] 测试权限控制

---

## 十一、注意事项

1. **网络配置**: 确保后端能访问 OnlyOffice Document Server
2. **文件存储**: 配置合适的文件存储路径和备份策略
3. **JWT 安全**: 使用强密码作为 JWT_SECRET
4. **性能优化**: 考虑使用 CDN 加速静态资源
5. **日志监控**: 开启 OnlyOffice 日志，便于问题排查

---

## 十二、参考资料

- [OnlyOffice 官方文档](https://api.onlyoffice.com/)
- [Document Server Docker](https://hub.docker.com/r/onlyoffice/documentserver/)
- [JavaScript API](https://api.onlyoffice.com/editors/basic)
- [回调机制](https://api.onlyoffice.com/editors/callback)

---

**下一步**: 开始实现 OnlyOffice 集成
