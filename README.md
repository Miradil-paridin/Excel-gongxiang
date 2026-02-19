# 局域网协同文档与文件分享系统

类似腾讯文档私有版的局域网部署Web应用

---

## 目录结构

```
.
├── docs/                          # 设计文档
│   ├── 01-系统架构设计.md
│   ├── 02-数据库设计.md
│   ├── 03-API接口文档.md
│   └── 04-前端页面原型说明.md
├── backend/                       # 后端项目（Django + DRF）
│   ├── requirements.txt
│   └── ...
├── frontend/                      # 前端项目（Vue 3）
│   ├── package.json
│   └── ...
└── docker/                        # OnlyOffice部署配置（可选）
    └── docker-compose.yml
```

---

## 技术栈

### 后端
- **框架**: Python 3.9.6 + Django 4.2.10 + Django REST Framework
- **认证**: JWT Token (djangorestframework-simplejwt)
- **数据库**: SQLite3 (轻量级，适合局域网小规模使用)
- **跨域**: django-cors-headers

### 前端
- **框架**: Vue 3 + TypeScript + Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP**: Axios
- **在线表格**: Luckysheet（计划中）
- **富文本**: Tiptap（计划中）

### 开发工具
- **Python虚拟环境**: venv
- **包管理**: pip, npm

---

## 核心功能

1. **用户系统**: 注册/登录、权限分级（普通用户/管理员）
2. **文档管理**: 在线文档（富文本）、在线表格（Excel类）
3. **文件管理**: 任意格式文件上传、预览
4. **分享协作**: 文档/文件分享（只读/可编辑）、多人实时编辑
5. **管理后台**: 用户管理、文档管理、系统统计

---

## 快速开始

### 环境准备

1. **Python 3.9+**
2. **Node.js 18+**

### 启动后端

```bash
cd backend
source ../venv/bin/activate  # Windows: ..\venv\Scripts\activate
python manage.py runserver
```

访问: **http://127.0.0.1:8000**

### 启动前端

```bash
cd frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

访问: **http://localhost:3000**

### 创建管理员账户

```bash
cd backend
source ../venv/bin/activate
python manage.py createsuperuser
```

### 开发文档

详细开发说明请查看 [DEVELOPMENT.md](./DEVELOPMENT.md)

---

## 项目进度

- ✅ **步骤1**: 需求确认与系统设计 (完成)
  - 系统架构设计
  - 数据库设计 (SQLite)
  - API接口文档
  - 前端页面原型

- ✅ **步骤2**: 搭建开发环境 (完成)
  - Django后端项目初始化
  - Vue 3前端项目初始化
  - 配置数据库连接
  - 安装项目依赖

- ✅ **步骤3**: 实现用户认证模块 (完成)
  - 用户注册/登录 API
  - JWT Token 认证
  - 登录/注册页面
  - 用户状态管理

- ⏳ **步骤4**: 实现文档管理模块 (待开发)
- ⏳ **步骤5**: 实现文件管理模块 (待开发)
- ⏳ **步骤6**: 实现分享与协作功能 (待开发)
- ⏳ **步骤7**: 实现管理后台 (待开发)
