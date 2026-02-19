# OnlyOffice 集成 - 快速开始指南

## 🎯 本次修改概述

### 从原方案改为 OnlyOffice
- **原方案**: Tiptap (富文本) + Luckysheet (表格) - 两个独立编辑器
- **新方案**: OnlyOffice Document Server - 一体化办公套件

### 为什么选择 OnlyOffice？
1. ✅ **功能完整**: 同时支持 Word、Excel、PPT 三种格式
2. ✅ **协同编辑**: 原生支持多人实时协同
3. ✅ **格式兼容**: 高度兼容 Microsoft Office
4. ✅ **开源免费**: 社区版完全免费
5. ✅ **私有部署**: 数据完全自主

---

## 📋 已完成的工作 (步骤5)

### 后端调整
1. ✅ 更新 `Document` 模型，支持文件存储
2. ✅ 添加 OnlyOffice 配置到 `settings.py`
3. ✅ 创建 OnlyOffice 工具函数 (`documents/utils.py`)
4. ✅ 创建 OnlyOffice 回调视图 (`documents/callback_views.py`)
5. ✅ 编写集成说明文档

### 部署配置
6. ✅ 创建 Docker Compose 配置
7. ✅ 编写部署指南
8. ✅ 创建快速启动脚本

---

## 🚀 快速部署 (3步)

### 第1步：启动 OnlyOffice
```bash
cd docker
./start-onlyoffice.sh
```

等待 2-3 分钟，看到 "✅ OnlyOffice 服务已就绪" 即可。

### 第2步：迁移数据库
```bash
cd backend
source ../venv/bin/activate
python manage.py makemigrations documents
python manage.py migrate
```

### 第3步：启动后端
```bash
python manage.py runserver
```

---

## 📝 后续开发任务

### 1. 更新序列化器和视图 (后端)
- [ ] 更新 `DocumentSerializer`
- [ ] 添加 `get_editor_config` 接口
- [ ] 集成回调视图到 URL

### 2. 前端编辑器集成
- [ ] 安装 OnlyOffice 编辑器
- [ ] 创建编辑器页面组件
- [ ] 实现编辑器初始化和配置
- [ ] 测试文档编辑功能

### 3. 完整测试
- [ ] 测试文档创建和上传
- [ ] 测试文档编辑和保存
- [ ] 测试协同编辑功能
- [ ] 测试文档格式转换

---

## 📊 项目进度

| 步骤 | 名称 | 状态 | 进度 |
|------|------|------|------|
| 1 | 需求确认与系统设计 | ✅ 完成 | 100% |
| 2 | 搭建开发环境 | ✅ 完成 | 100% |
| 3 | 用户认证模块 | ✅ 完成 | 100% |
| 4 | 文档/文件管理 | ✅ 完成 | 100% |
| 5 | OnlyOffice 集成 | 🔄 进行中 | 70% |
| 6 | 分享与协作 | ⏳ 待开发 | 0% |
| 7 | 管理后台 | ⏳ 待开发 | 0% |

**总体进度**: 70% 📈

---

## 📚 相关文档

1. **[OnlyOffice集成说明](./OnlyOffice集成说明.md)** - 详细的技术方案
2. **[步骤5-OnlyOffice集成-完成总结](./步骤5-OnlyOffice集成-完成总结.md)** - 本次修改总结
3. **[docker/部署指南.md](../docker/部署指南.md)** - OnlyOffice 部署详细说明

---

## ⚠️ 注意事项

### 开发环境
- OnlyOffice 服务地址: `http://localhost:8081`
- JWT 认证暂时关闭 (开发环境)
- 确保 Docker 正常运行

### 生产环境
- 必须启用 JWT 认证
- 使用域名和 HTTPS
- 配置防火墙规则
- 定期备份数据

---

## 🎓 OnlyOffice 核心概念

### 1. Document Server
- 提供文档编辑服务
- 处理文档渲染和保存
- 支持协同编辑

### 2. Callback 机制
- 文档保存后回调后端
- 后端下载更新后的文档
- 保持数据一致性

### 3. JWT 认证
- 防止未授权访问
- 保护文档安全
- 生产环境必需

---

## 💡 常见问题

### Q1: OnlyOffice 启动失败？
**A**: 检查端口 8081 是否被占用，查看日志: `docker-compose logs`

### Q2: 健康检查返回 false？
**A**: 等待服务完全启动，首次启动需要 2-3 分钟

### Q3: 文档无法保存？
**A**: 检查 callback URL 是否正确，查看后端日志

### Q4: 如何修改端口？
**A**: 编辑 `docker-compose.yml`，修改 `ports` 配置

---

## 🎉 下一步

1. **立即测试**: 按照"快速部署"启动 OnlyOffice
2. **完善后端**: 完成序列化器和视图更新
3. **集成前端**: 创建编辑器页面组件
4. **完整测试**: 测试所有功能

**有任何问题请查看文档或询问！**
