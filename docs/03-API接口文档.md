# 03-API接口文档

## 基础信息

- **Base URL**: `/api/`
- **认证方式**: JWT Token (Bearer Token)
- **数据格式**: JSON
- **响应格式**:
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {}
  }
  ```

## 认证相关接口

### 1. 用户注册

**POST** `/auth/register/`

**请求体**:
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "username": "zhangsan",
      "email": "zhangsan@example.com",
      "date_joined": "2026-02-14T10:00:00Z"
    }
  }
}
```

---

### 2. 用户登录

**POST** `/auth/login/`

**请求体**:
```json
{
  "username": "zhangsan",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "zhangsan",
      "email": "zhangsan@example.com",
      "is_staff": false,
      "avatar": "/media/avatars/default.png",
      "department": "技术部"
    }
  }
}
```

---

### 3. 获取当前用户信息

**GET** `/auth/me/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "is_staff": false,
    "is_active": true,
    "date_joined": "2026-02-14T10:00:00Z",
    "last_login": "2026-02-14T15:30:00Z",
    "profile": {
      "avatar": "/media/avatars/default.png",
      "department": "技术部",
      "phone": ""
    }
  }
}
```

---

### 4. 修改密码

**POST** `/auth/change-password/`

**请求头**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "old_password": "old123",
  "new_password": "new123",
  "confirm_password": "new123"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "密码修改成功"
}
```

---

## 文档管理接口

### 5. 创建文档

**POST** `/documents/`

**请求头**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "title": "我的第一个文档",
  "type": "doc"  // "doc" 或 "sheet"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "我的第一个文档",
    "type": "doc",
    "content": null,
    "creator": {
      "id": 1,
      "username": "zhangsan"
    },
    "created_at": "2026-02-14T16:00:00Z",
    "updated_at": "2026-02-14T16:00:00Z",
    "version": 1,
    "permission": "owner"  // owner/read/write
  }
}
```

---

### 6. 获取文档列表

**GET** `/documents/?type=doc&page=1&page_size=20`

**请求头**: `Authorization: Bearer <token>`

**查询参数**:
- `type`: doc/sheet/all (默认all)
- `page`: 页码 (默认1)
- `page_size`: 每页数量 (默认20)
- `search`: 搜索关键词 (可选)
- `sort`: 排序 (created_at/updated_at/title)

**响应**:
```json
{
  "code": 0,
  "data": {
    "count": 10,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "title": "我的第一个文档",
        "type": "doc",
        "creator": {
          "id": 1,
          "username": "zhangsan"
        },
        "updated_at": "2026-02-14T16:00:00Z",
        "permission": "owner"
      }
    ]
  }
}
```

---

### 7. 获取单个文档详情

**GET** `/documents/{id}/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "我的第一个文档",
    "type": "doc",
    "content": "<p>Hello World</p>",
    "creator": {
      "id": 1,
      "username": "zhangsan",
      "avatar": "/media/avatars/default.png"
    },
    "created_at": "2026-02-14T16:00:00Z",
    "updated_at": "2026-02-14T16:00:00Z",
    "version": 1,
    "permission": "owner",
    "is_shared": true,
    "share_count": 3
  }
}
```

---

### 8. 更新文档

**PUT/PATCH** `/documents/{id}/`

**请求头**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "title": "更新后的文档标题",
  "content": "<p>更新后的内容</p>"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "更新后的文档标题",
    "content": "<p>更新后的内容</p>",
    "version": 2,
    "updated_at": "2026-02-14T16:30:00Z"
  }
}
```

---

### 9. 删除文档

**DELETE** `/documents/{id}/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "message": "文档已删除"
}
```

---

### 10. 恢复已删除文档

**POST** `/documents/{id}/restore/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "message": "文档已恢复"
}
```

---

### 11. 获取文档版本历史

**GET** `/documents/{id}/versions/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "data": [
    {
      "version_number": 3,
      "changed_by": {
        "id": 1,
        "username": "zhangsan"
      },
      "changed_at": "2026-02-14T17:00:00Z",
      "change_summary": "更新标题"
    },
    {
      "version_number": 2,
      "changed_by": {
        "id": 1,
        "username": "zhangsan"
      },
      "changed_at": "2026-02-14T16:30:00Z",
      "change_summary": "添加内容"
    }
  ]
}
```

---

### 12. 恢复到指定版本

**POST** `/documents/{id}/versions/{version_number}/restore/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "message": "已恢复到版本3",
  "data": {
    "version": 4,
    "content": "..."
  }
}
```

---

## 文件管理接口

### 13. 上传文件

**POST** `/files/upload/` (multipart/form-data)

**请求头**: `Authorization: Bearer <token>`

**表单数据**:
- `file`: 二进制文件
- `folder_id`: 父文件夹ID (可选)

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "name": "abc123.pdf",
    "original_name": "报告.pdf",
    "path": "/data/uploads/abc123.pdf",
    "size": 1024000,
    "mime_type": "application/pdf",
    "thumbnail_path": "/media/thumbnails/abc123.png",
    "uploader": {
      "id": 1,
      "username": "zhangsan"
    },
    "created_at": "2026-02-14T18:00:00Z"
  }
}
```

---

### 14. 获取文件列表

**GET** `/files/?page=1&page_size=20`

**请求头**: `Authorization: Bearer <token>`

**查询参数**:
- `page`: 页码
- `page_size`: 每页数量
- `search`: 搜索关键词
- `mime_type`: MIME类型过滤
- `sort`: 排序 (created_at/size/name)

**响应**:
```json
{
  "code": 0,
  "data": {
    "count": 5,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "name": "abc123.pdf",
        "original_name": "报告.pdf",
        "size": 1024000,
        "mime_type": "application/pdf",
        "thumbnail_path": "/media/thumbnails/abc123.png",
        "uploader": {
          "id": 1,
          "username": "zhangsan"
        },
        "created_at": "2026-02-14T18:00:00Z",
        "download_url": "/api/files/1/download/"
      }
    ]
  }
}
```

---

### 15. 下载文件

**GET** `/files/{id}/download/`

**请求头**: `Authorization: Bearer <token>`

**响应**: 文件流 (Content-Disposition: attachment)

---

### 16. 获取文件预览

**GET** `/files/{id}/preview/`

**请求头**: `Authorization: Bearer <token>`

**响应**: HTML/图片等预览内容

---

### 17. 删除文件

**DELETE** `/files/{id}/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "message": "文件已删除"
}
```

---

## 分享管理接口

### 18. 创建分享

**POST** `/shares/`

**请求头**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "document_id": 1,  // 或 file_id
  "sharee_id": 2,    // 被分享用户ID
  "permission": "write",  // "read" 或 "write"
  "expired_at": "2026-03-14T00:00:00Z",  // 可选
  "message": "请帮忙审阅这个文档"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "document": {
      "id": 1,
      "title": "我的第一个文档"
    },
    "sharer": {
      "id": 1,
      "username": "zhangsan"
    },
    "sharee": {
      "id": 2,
      "username": "lisi"
    },
    "permission": "write",
    "shared_at": "2026-02-14T19:00:00Z",
    "expired_at": "2026-03-14T00:00:00Z",
    "is_active": true
  }
}
```

---

### 19. 获取"我的分享"列表

**GET** `/shares/my-shares/?page=1&page_size=20`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "data": {
    "count": 3,
    "results": [
      {
        "id": 1,
        "document": {
          "id": 1,
          "title": "我的第一个文档",
          "type": "doc"
        },
        "sharee": {
          "id": 2,
          "username": "lisi"
        },
        "permission": "write",
        "shared_at": "2026-02-14T19:00:00Z",
        "is_active": true
      }
    ]
  }
}
```

---

### 20. 获取"与我分享"列表

**GET** `/shares/shared-with-me/?page=1&page_size=20`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "data": {
    "count": 2,
    "results": [
      {
        "id": 1,
        "document": {
          "id": 1,
          "title": "我的第一个文档",
          "type": "doc"
        },
        "sharer": {
          "id": 1,
          "username": "zhangsan"
        },
        "permission": "read",
        "shared_at": "2026-02-14T19:00:00Z",
        "is_active": true
      }
    ]
  }
}
```

---

### 21. 更新分享权限

**PUT/PATCH** `/shares/{id}/`

**请求头**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "permission": "read",
  "is_active": false
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "permission": "read",
    "is_active": false
  }
}
```

---

### 22. 删除分享

**DELETE** `/shares/{id}/`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 0,
  "message": "分享已取消"
}
```

---

## 协同编辑接口 (WebSocket)

### 23. WebSocket连接

**URL**: `/ws/documents/{document_id}/`

**连接时发送**:
```json
{
  "action": "connect",
  "token": "jwt_token",
  "client_id": "unique_client_id"
}
```

**服务器响应**:
```json
{
  "action": "connected",
  "document_id": 1,
  "user": {
    "id": 1,
    "username": "zhangsan"
  },
  "current_content": "...",
  "version": 1,
  "online_users": [
    {"id": 1, "username": "zhangsan"},
    {"id": 2, "username": "lisi"}
  ]
}
```

---

### 24. 发送操作

**客户端发送**:
```json
{
  "action": "operation",
  "operation": {
    "type": "insert",
    "position": 10,
    "text": "Hello"
  },
  "version": 1
}
```

**服务器广播**:
```json
{
  "action": "operation_broadcast",
  "operation": {
    "type": "insert",
    "position": 10,
    "text": "Hello"
  },
  "user": {
    "id": 1,
    "username": "zhangsan"
  },
  "timestamp": "2026-02-14T20:00:00Z"
}
```

---

### 25. 离开文档

**客户端发送**:
```json
{
  "action": "disconnect"
}
```

**服务器响应**:
```json
{
  "action": "user_left",
  "user": {
    "id": 1,
    "username": "zhangsan"
  },
  "online_users": [
    {"id": 2, "username": "lisi"}
  ]
}
```

---

## 管理后台接口

### 26. 仪表盘统计数据

**GET** `/admin/dashboard/stats/`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**响应**:
```json
{
  "code": 0,
  "data": {
    "total_users": 150,
    "total_documents": 520,
    "total_files": 1280,
    "total_shares": 860,
    "active_users_today": 45,
    "active_users_week": 120,
    "storage_used": 10240000000,  // bytes
    "recent_activities": [
      {
        "user": "zhangsan",
        "action": "create",
        "target": "文档: 项目计划",
        "time": "2026-02-14T15:30:00Z"
      }
    ]
  }
}
```

---

### 27. 用户列表

**GET** `/admin/users/?page=1&page_size=20&search=zhang`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**响应**:
```json
{
  "code": 0,
  "data": {
    "count": 150,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "is_active": true,
        "is_staff": false,
        "date_joined": "2026-01-01T10:00:00Z",
        "last_login": "2026-02-14T15:30:00Z",
        "document_count": 12,
        "file_count": 5
      }
    ]
  }
}
```

---

### 28. 禁用/启用用户

**PATCH** `/admin/users/{id}/toggle-active/`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**响应**:
```json
{
  "code": 0,
  "message": "用户已禁用",
  "data": {
    "id": 1,
    "is_active": false
  }
}
```

---

### 29. 重置用户密码

**POST** `/admin/users/{id}/reset-password/`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**请求体**:
```json
{
  "new_password": "new123"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "密码已重置"
}
```

---

### 30. 设置管理员权限

**PATCH** `/admin/users/{id}/set-staff/`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**请求体**:
```json
{
  "is_staff": true
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "is_staff": true
  }
}
```

---

### 31. 文档/文件列表（管理员视角）

**GET** `/admin/documents/?page=1&page_size=20`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**响应**:
```json
{
  "code": 0,
  "data": {
    "count": 520,
    "results": [
      {
        "id": 1,
        "title": "我的第一个文档",
        "type": "doc",
        "creator": {
          "id": 1,
          "username": "zhangsan",
          "email": "zhangsan@example.com"
        },
        "created_at": "2026-02-14T16:00:00Z",
        "is_deleted": false,
        "share_count": 3
      }
    ]
  }
}
```

---

### 32. 删除文档/文件（管理员）

**DELETE** `/admin/documents/{id}/force-delete/`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**响应**:
```json
{
  "code": 0,
  "message": "文档已强制删除"
}
```

---

### 33. 系统设置

**GET** `/admin/settings/`

**请求头**: `Authorization: Bearer <token>` (需管理员权限)

**响应**:
```json
{
  "code": 0,
  "data": {
    "max_upload_size": 104857600,  // 100MB
    "allowed_file_types": ["pdf", "doc", "docx", "xls", "xlsx", "jpg", "png"],
    "storage_path": "/data/uploads/",
    "enable_registration": true,
    "default_permission": "read"
  }
}
```

---

**下一步**: 前端页面原型设计
