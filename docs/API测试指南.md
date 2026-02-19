# API 测试指南

## 使用 curl 测试

### 1. 注册用户

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

**成功响应**:
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "username": "zhangsan",
      "email": "zhangsan@example.com"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

### 2. 用户登录

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "password": "password123"
  }'
```

**成功响应**:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "zhangsan",
      "email": "zhangsan@example.com"
    }
  }
}
```

---

### 3. 获取用户信息

```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**成功响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "first_name": "",
    "last_name": "",
    "date_joined": "2026-02-14T10:00:00Z",
    "last_login": "2026-02-14T15:30:00Z"
  }
}
```

---

### 4. 修改密码

```bash
curl -X POST http://127.0.0.1:8000/api/auth/change-password/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "password123",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
  }'
```

**成功响应**:
```json
{
  "code": 0,
  "message": "密码修改成功，请重新登录"
}
```

---

## 使用浏览器测试

### 1. 访问 Django Admin

- URL: `http://127.0.0.1:8000/admin/`
- 使用 `python manage.py createsuperuser` 创建的管理员账号登录

### 2. 测试 DRF API 界面

- URL: `http://127.0.0.1:8000/api/auth/login/`
- 可以直接在浏览器中测试 API

---

## 常见错误

### 400 Bad Request
**原因**: 请求参数错误或缺失
**解决**: 检查请求体格式和必填字段

### 401 Unauthorized
**原因**: Token 无效或已过期
**解决**: 重新登录获取新 Token

### 403 Forbidden
**原因**: 权限不足
**解决**: 检查用户角色和权限

### 404 Not Found
**原因**: API 路径错误
**解决**: 检查 URL 是否正确

---

## Token 使用说明

### 获取 Token
登录成功后，响应中会包含 `token` 字段。

### 使用 Token
在请求头中添加:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

### Token 有效期
- Access Token: 12 小时
- 过期后需要重新登录
