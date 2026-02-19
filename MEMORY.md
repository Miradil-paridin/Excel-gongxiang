# Excel-Gongxiang 项目记忆文件

> 创建时间: 2026-02-18
> 最后更新: 2026-02-18 (OnlyOffice 编辑器 Bug 修复)

---

## 项目概述

**项目名称**: 局域网协同文档与文件分享系统
**项目类型**: Web 全栈应用 (Django + Vue 3)
**定位**: 类似腾讯文档私有版的局域网部署版本

---

## 技术栈

### 后端
- Python 3.9.6 + Django 4.2.10
- Django REST Framework 3.14.0
- JWT 认证 (djangorestframework-simplejwt)
- 数据库: SQLite3
- 跨域: django-cors-headers
- 文档处理: python-docx, openpyxl, python-pptx

### 前端
- Vue 3 + TypeScript + Vite
- UI 库: Element Plus
- 状态管理: Pinia
- 路由: Vue Router
- HTTP: Axios
- 在线编辑: OnlyOffice Document Server

### 服务
- OnlyOffice Document Server (Docker, 端口 8081)

---

## 当前状态

### 运行中的服务
| 服务 | 端口 | 状态 |
|------|------|------|
| Django 后端 | 8000 | ✅ 运行中 (PID 6607) |
| Vue 前端 | 3000 | ✅ 运行中 (PID 3277) |
| OnlyOffice | 8081 | ✅ 运行中 (Docker) |
| SQLite 数据库 | - | ✅ 已有数据 |

### 测试账号
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | Admin@123456 | 管理员 |
| user1 | User1@123456 | 普通用户 |
| user2 | User2@123456 | 普通用户 |
| user3 | User3@123456 | 普通用户 |

---

## 已完成功能

### ✅ 用户系统
- 用户注册/登录
- JWT Token 认证
- 权限分级 (普通用户/管理员)

### ✅ 文档管理
- 文档 CRUD 操作
- 支持 Word/Excel/PPT 类型
- 自动创建空白文档文件
- 软删除和恢复

### ✅ 文件管理
- 任意格式文件上传/下载
- 文件列表展示

### ✅ 分享协作
- 文档/文件分享
- 权限控制 (只读/可编辑)
- 分享列表查看

### ✅ 管理后台
- 用户管理
- 文档管理
- 文件管理

### ✅ OnlyOffice 在线编辑
- OnlyOffice 服务集成
- 文档在线编辑
- 自动保存回调
- 多人编辑支持

---

## 待优化/开发功能

### 优先级：高
1. **前端代理配置优化**
   - 已添加 `/media` 代理，需要重启前端生效

2. **文档创建自动生成文件**
   - 确保新建文档时自动创建空白 Word/Excel/PPT 文件
   - 已实现 (使用 python-docx, openpyxl, python-pptx)

### 优先级：中
1. **在线编辑体验优化**
   - 编辑器加载状态优化
   - 错误提示完善

2. **实时协作**
   - 多人同时编辑状态显示
   - 文档锁定机制完善

### 优先级：低
1. **Luckysheet 集成** (替代 OnlyOffice 的 Excel 编辑)
2. **Tiptap 富文本编辑器**
3. **文档版本历史**
4. **文件预览功能**

---

## 重要配置

### 后端配置 (backend/docshare/settings.py)

```python
# OnlyOffice 配置
ONLYOFFICE_API_URL = 'http://localhost:8081/'
ONLYOFFICE_DOCUMENT_URL = 'http://192.168.31.129:8000'
ONLYOFFICE_JWT_SECRET = 'your-secret-key-change-in-production'
ONLYOFFICE_JWT_ENABLED = False  # 开发环境可设为 False

# 文件上传限制
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
```

### 前端代理 (frontend/vite.config.ts)
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  },
  '/media': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

### 允许访问的 hosts
```
localhost, 127.0.0.1, 0.0.0.0, 192.168.31.129
```

---

## 启动命令

### 方式一：一键启动 (推荐)
```bash
cd /Users/miradil/Desktop/excel-gongxiang
./start.sh
```

### 方式二：手动启动

#### 1. 启动后端
```bash
cd /Users/miradil/Desktop/excel-gongxiang/backend
source ../venv/bin/activate
python manage.py runserver
# 访问: http://localhost:8000
```

#### 2. 启动前端
```bash
cd /Users/miradil/Desktop/excel-gongxiang/frontend
npm run dev
# 访问: http://localhost:3000
```

#### 3. OnlyOffice 服务 (如需重启)
```bash
cd /Users/miradil/Desktop/excel-gongxiang/docker
docker-compose up -d
# 访问: http://localhost:8081
```

---

## 项目结构

```
excel-gongxiang/
├── backend/                 # Django 后端
│   ├── accounts/           # 用户认证
│   ├── documents/          # 文档管理
│   │   ├── models.py      # Document 模型
│   │   ├── views.py       # API 视图
│   │   ├── serializers.py # 数据序列化
│   │   ├── callback_views.py  # OnlyOffice 回调
│   │   └── urls.py        # 路由配置
│   ├── files/             # 文件管理
│   ├── shares/            # 分享协作
│   ├── docshare/          # Django 配置
│   │   └── settings.py   # 核心配置
│   ├── db.sqlite3         # 数据库
│   └── requirements.txt   # Python 依赖
│
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/           # API 接口
│   │   ├── views/
│   │   │   ├── auth/      # 登录/注册
│   │   │   ├── documents/ # 文档管理
│   │   │   ├── files/     # 文件管理
│   │   │   ├── shares/    # 分享功能
│   │   │   ├── admin/     # 管理后台
│   │   │   └── editor/    # OnlyOffice 编辑器
│   │   └── router/        # 路由配置
│   └── vite.config.ts     # Vite 配置
│
├── docker/                 # OnlyOffice 部署
│   ├── docker-compose.yml
│   └── start-onlyoffice.sh
│
└── venv/                   # Python 虚拟环境
```

---

## API 接口概览

### 认证
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出

### 文档
- `GET /api/documents/` - 文档列表
- `POST /api/documents/` - 创建文档
- `GET /api/documents/{id}/` - 文档详情
- `PATCH /api/documents/{id}/` - 更新文档
- `DELETE /api/documents/{id}/` - 删除文档
- `GET /api/documents/{id}/editor-config/` - 获取编辑器配置

### 文件
- `GET /api/files/` - 文件列表
- `POST /api/files/upload/` - 上传文件
- `GET /api/files/{id}/` - 下载文件
- `DELETE /api/files/{id}/` - 删除文件

### 分享
- `GET /api/shares/` - 分享列表
- `POST /api/shares/` - 创建分享
- `DELETE /api/shares/{id}/` - 取消分享

---

## 已修复 Bug

### ✅ OnlyOffice 编辑器点击无显示 (2026-02-18)
**原因 1**: `frontend/src/views/editor/Index.vue` 中 `DocsAPI.DocEditor` 第一个参数传入了 DOM 元素对象，应该传 **元素 ID 字符串** `'onlyoffice-container'`
**修复**: 改为 `DocsAPI.DocEditor('onlyoffice-container', {...})` 并删除 callbackUrl 覆盖行

**原因 2**: OnlyOffice 7.4.0 默认有 SSRF 安全防护，**拒绝从私有 IP 地址（192.168.x.x）下载文档**
**错误日志**: `DNS lookup 192.168.31.129 is not allowed. Because, It is private IP address.`
**修复**: 在 `docker/docker-compose.yml` 中添加 `ALLOW_PRIVATE_IP_ADDRESS=true` 并重启容器

---

## 常见问题

### Q: 前端无法访问后端 API
A: 检查前端是否运行，检查代理配置是否正确

### Q: OnlyOffice 编辑器无法加载
A:
1. 检查 OnlyOffice 服务: `curl http://localhost:8081/healthcheck`
2. 检查后端能否被 OnlyOffice 访问: `docker exec onlyoffice-document-server curl http://192.168.31.129:8000/media/...`
3. 检查 `DocsAPI.DocEditor` 第一个参数是否为 ID 字符串（不是 DOM 元素）

### Q: 文档创建后没有文件
A: 检查 python-docx, openpyxl, python-pptx 是否安装

---

## 下次开发指引

1. **查看本文件** - 了解项目状态
2. **检查服务状态** - `./start.sh` 或手动检查端口
3. **启动开发** - 按上述启动命令
4. **修改代码后** - 如修改 vite.config.ts 需要重启前端

---

*Memory created by Claude Code*
