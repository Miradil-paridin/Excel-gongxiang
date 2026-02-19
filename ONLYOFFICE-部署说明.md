# OnlyOffice 部署说明 - 两种方案

## 方案一：自动部署 (推荐) ✅

我已为您创建了一键部署脚本，**不需要手动操作**：

### 使用方法 (3步完成)

```bash
# 1. 进入 docker 目录
cd docker

# 2. 运行一键部署脚本
./start-onlyoffice.sh

# 3. 等待 2-3 分钟
# 看到 "✅ OnlyOffice 服务已就绪" 即可
```

**脚本自动完成**:
- ✅ 检查 Docker 环境
- ✅ 创建数据目录
- ✅ 启动 OnlyOffice 容器
- ✅ 等待服务启动
- ✅ 验证健康状态
- ✅ 显示成功信息

---

## 方案二：手动部署 (可选)

如果自动脚本有问题，可以手动部署：

### 1. 安装 Docker (如果未安装)

#### macOS
```bash
# 方式1: 使用 Homebrew (推荐)
brew install docker docker-compose

# 方式2: 下载 Docker Desktop
# 访问: https://www.docker.com/products/docker-desktop
```

#### Windows
```bash
# 下载 Docker Desktop for Windows
# 访问: https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian)
```bash
# 安装 Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 启动 OnlyOffice

```bash
cd docker

# 启动 OnlyOffice
docker-compose up -d

# 等待 2-3 分钟

# 检查状态
docker-compose ps

# 应该看到状态为 "Up"

# 验证服务
curl http://localhost:8081/healthcheck
# 应该返回: true
```

---

## 验证部署是否成功

### 1. 检查容器状态
```bash
docker-compose ps
```

正常输出:
```
                Name                          Command    State           Ports
----------------------------------------------------------------------------------------
onlyoffice-document-server   /bin/bash ...   Up      0.0.0.0:8081->80/tcp
```

### 2. 访问健康检查
```bash
curl http://localhost:8081/healthcheck
```

正常输出:
```
true
```

### 3. 浏览器访问
打开浏览器访问: `http://localhost:8081`

应该能看到 OnlyOffice 欢迎页面

---

## 常见问题解决

### 问题1: 端口 8081 被占用
```bash
# 查看占用端口的进程
lsof -i :8081

# 杀死进程
kill -9 <PID>

# 或修改 docker-compose.yml 使用其他端口
# 将 "8081:80" 改为 "8082:80"
```

### 问题2: Docker 未安装
**macOS**:
```bash
# 安装 Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Docker
brew install docker docker-compose
```

### 问题3: 容器启动失败
```bash
# 查看日志
docker-compose logs

# 重新启动
docker-compose restart

# 完全重新创建
docker-compose down
docker-compose up -d
```

### 问题4: 健康检查返回 false
```bash
# 等待服务完全启动 (首次需要 2-3 分钟)
sleep 180

# 再次检查
curl http://localhost:8081/healthcheck
```

---

## 不想部署 OnlyOffice 怎么办？

### 方案A: 临时跳过 OnlyOffice (快速测试)

如果您暂时不想部署 OnlyOffice，可以：

1. **跳过文档编辑功能**
   - 文档列表和文件管理仍然可以使用
   - 点击文档时提示"编辑器未配置"

2. **修改后端配置**
```python
# backend/docshare/settings.py

# 暂时注释掉 OnlyOffice 配置
# ONLYOFFICE_API_URL = 'http://localhost:8081/'
```

3. **前端修改**
```vue
<!-- frontend/src/views/editor/Index.vue -->

<!-- 临时显示占位页面 -->
<el-empty description="OnlyOffice 编辑器未配置" />
```

### 方案B: 使用简单文本编辑器 (临时方案)

```vue
<!-- frontend/src/views/editor/Index.vue -->

<template>
  <div class="editor-page">
    <el-input
      v-model="document.content"
      type="textarea"
      :rows="20"
      placeholder="文档内容..."
    />
    <el-button @click="save">保存</el-button>
  </div>
</template>
```

---

## 推荐部署顺序

### 如果您想完整体验系统：

```bash
# 1. 部署 OnlyOffice (5分钟)
cd docker
./start-onlyoffice.sh

# 2. 迁移数据库
cd backend
source ../venv/bin/activate
python manage.py makemigrations
python manage.py migrate

# 3. 启动后端
python manage.py runserver

# 4. 启动前端
cd frontend
npm run dev

# 5. 访问系统
# http://localhost:3000
```

### 如果您想快速测试 (跳过 OnlyOffice)：

```bash
# 1. 迁移数据库
cd backend
source ../venv/bin/activate
python manage.py migrate

# 2. 启动后端
python manage.py runserver

# 3. 启动前端
cd frontend
npm run dev

# 4. 访问系统 (文档编辑功能不可用)
# http://localhost:3000
```

---

## 资源占用说明

### OnlyOffice 资源需求
- **内存**: 建议 2GB+ (最低 1GB)
- **磁盘**: 2GB+ 可用空间
- **CPU**: 2 核心

### 如果资源不足

可以调整 `docker-compose.yml`:

```yaml
services:
  onlyoffice-document-server:
    # ... 其他配置
    mem_limit: 1g  # 限制内存使用
```

---

## 总结

### ✅ 推荐做法
使用自动部署脚本 (3步完成):
```bash
cd docker
./start-onlyoffice.sh
```

### ⏳ 快速测试
如果暂时不想部署，可以跳过 OnlyOffice，其他功能仍然可用。

### 📞 需要帮助
遇到问题请查看常见问题部分，或告诉我具体错误信息。

---

**下一步**: 您想先部署 OnlyOffice，还是跳过继续开发其他功能？
