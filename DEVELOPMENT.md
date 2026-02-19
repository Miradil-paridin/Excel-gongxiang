# 开发说明文档

## 项目结构

```
excel-gongxiang/
├── backend/              # Django 后端
├── frontend/             # Vue 3 前端
├── venv/                 # Python 虚拟环境
└── docs/                 # 设计文档
```

## 后端开发 (Django)

### 启动开发服务器

```bash
# 激活虚拟环境
source ../venv/bin/activate

# 运行 Django 开发服务器
python manage.py runserver

# 默认访问: http://127.0.0.1:8000
```

### 数据库迁移

```bash
# 创建迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate
```

### 创建管理员账户

```bash
python manage.py createsuperuser
```

### Django Admin 后台

访问: `http://127.0.0.1:8000/admin/`

---

## 前端开发 (Vue 3)

### 启动开发服务器

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev

# 默认访问: http://localhost:3000
```

### 构建生产版本

```bash
npm run build
```

---

## API 文档

### 认证接口

#### 注册
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "password123",
  "password_confirm": "password123"
}
```

#### 登录
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "password123"
}
```

#### 获取用户信息
```http
GET /api/auth/me/
Authorization: Bearer <token>
```

#### 修改密码
```http
POST /api/auth/change-password/
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "old123",
  "new_password": "new123",
  "new_password_confirm": "new123"
}
```

---

## 技术栈

### 后端
- Python 3.9.6
- Django 4.2.10
- Django REST Framework 3.14.0
- djangorestframework-simplejwt (JWT 认证)
- SQLite (数据库)

### 前端
- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia
- Vue Router
- Axios

---

## 开发约定

### 后端

1. **响应格式**:
   ```json
   {
     "code": 0,
     "message": "成功",
     "data": {}
   }
   ```

2. **认证方式**: JWT Token (Bearer Token)

3. **代码组织**:
   - 每个功能模块独立 app
   - serializers.py - 序列化器
   - views.py - 视图
   - urls.py - 路由
   - permissions.py - 权限类

### 前端

1. **组件命名**: PascalCase (e.g., Login.vue)

2. **路径别名**:
   - `@` 指向 `src/` 目录

3. **状态管理**: 使用 Pinia Store

4. **API 调用**: 统一在 `src/api/` 目录

---

## 常见问题

### 后端

**Q: 数据库文件在哪里？**
A: `backend/db.sqlite3`

**Q: 如何重置数据库？**
A:
```bash
rm db.sqlite3
python manage.py migrate
```

**Q: Token 过期时间？**
A: Access Token 12小时，Refresh Token 7天

### 前端

**Q: 如何配置 API 地址？**
A: 修改 `src/config/index.ts` 中的 `apiBaseUrl`

**Q: Token 存储在哪里？**
A: `localStorage` 中的 `auth_token` 键

---

## 下一步开发计划

1. ✅ 用户认证模块 (已完成)
2. ⏳ 文档管理模块 (进行中)
3. ⏳ 文件上传下载
4. ⏳ 分享功能
5. ⏳ 实时协同编辑
6. ⏳ 管理后台
