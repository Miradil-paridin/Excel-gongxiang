# ⚠️ Docker 未安装 - OnlyOffice 部署方案

## 当前状态检查

```bash
$ which docker
# 返回: docker not found
```

**结论**: 您的系统上 **未安装 Docker**，无法使用 `docker-compose` 部署 OnlyOffice。

---

## 三种解决方案

### 方案一：安装 Docker (推荐)

#### macOS 安装步骤

**方式 1: 使用 Homebrew (命令行)**
```bash
# 1. 安装 Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装 Docker Desktop
brew install --cask docker

# 3. 启动 Docker Desktop
# 在应用程序中找到 Docker 并启动

# 4. 等待 Docker 启动完成
# 在菜单栏看到 Docker 图标 (鲸鱼)

# 5. 验证安装
docker --version
docker-compose --version
```

**方式 2: 手动下载 (推荐)**
```bash
# 1. 访问 Docker 官网下载页面
https://www.docker.com/products/docker-desktop

# 2. 下载 Docker Desktop for Mac
# (选择 Apple Chip 版本，因为您的系统是 arm64)

# 3. 安装并启动 Docker Desktop

# 4. 验证安装
docker --version
docker-compose --version
```

#### 安装后部署 OnlyOffice

```bash
# 1. 进入 docker 目录
cd docker

# 2. 运行一键部署脚本
./start-onlyoffice.sh

# 3. 等待 2-3 分钟
# 看到 "✅ OnlyOffice 服务已就绪" 即可
```

---

### 方案二：跳过 OnlyOffice (快速测试)

如果您暂时不想安装 Docker，可以**跳过 OnlyOffice**，系统其他功能仍然可用：

#### 1. 修改后端配置
```python
# backend/docshare/settings.py

# 注释掉 OnlyOffice 配置
# ONLYOFFICE_API_URL = 'http://localhost:8081/'
# ONLYOFFICE_JWT_SECRET = 'your-secret-key-change-in-production'
# ONLYOFFICE_JWT_ENABLED = False
```

#### 2. 使用简单文本编辑器

创建临时编辑器页面:
```vue
<!-- frontend/src/views/editor/Index.vue -->

<template>
  <div class="editor-page">
    <div class="editor-header">
      <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
      <el-input v-model="document.title" size="small" style="width: 300px" />
      <el-button size="small" type="primary" @click="handleSave">保存</el-button>
    </div>

    <div class="editor-content">
      <el-input
        v-model="document.content"
        type="textarea"
        :rows="25"
        placeholder="请输入文档内容..."
        style="width: 100%"
      />
    </div>
  </div>
</template>

<script setup>
// ... 简单实现
</script>
```

**优点**:
- ✅ 无需安装 Docker
- ✅ 快速启动测试
- ✅ 文档列表和文件管理正常

**缺点**:
- ❌ 无富文本编辑
- ❌ 无协同编辑
- ❌ 无 Office 格式支持

---

### 方案三：使用在线 OnlyOffice 服务 (不推荐)

OnlyOffice 提供在线服务，但**不适合局域网部署**:
- ❌ 数据会上传到外部服务器
- ❌ 违背私有部署需求
- ❌ 可能需要付费

---

## 推荐方案

### 立即行动 (推荐方案一)

**如果您想完整体验系统**:

```bash
# 1. 安装 Docker Desktop for Mac
# 访问: https://www.docker.com/products/docker-desktop
# 下载并安装 (约 10-15 分钟)

# 2. 启动 Docker Desktop
# 等待启动完成

# 3. 验证安装
docker --version
# 应该显示: Docker version 20.xx.x

# 4. 部署 OnlyOffice
cd /Users/miradil/Desktop/excel-gongxiang/docker
./start-onlyoffice.sh

# 5. 等待 2-3 分钟后开始使用
```

### 临时测试 (推荐方案二)

**如果您想先测试其他功能**:

```bash
# 1. 跳过 OnlyOffice 部署
# 直接启动后端和前端

cd backend
source ../venv/bin/activate
python manage.py runserver

cd frontend
npm run dev

# 2. 访问系统
# 文档编辑功能会显示占位页面
# 但文档列表、文件管理等功能正常
```

---

## 安装 Docker 的好处

✅ **OnlyOffice 完整功能**:
- 富文本编辑 (Word)
- 表格编辑 (Excel)
- 演示编辑 (PPT)
- 协同编辑
- Office 格式兼容

✅ **数据完全自主**:
- 私有部署
- 局域网内部访问
- 无数据泄露风险

✅ **易于管理**:
- 一键启动/停止
- 数据持久化
- 容器隔离

---

## 下一步建议

### 选项 A: 安装 Docker (推荐)
1. 访问 https://www.docker.com/products/docker-desktop
2. 下载 Docker Desktop for Mac (Apple Chip)
3. 安装并启动
4. 部署 OnlyOffice
5. 完整体验系统

**预计时间**: 30-45 分钟

### 选项 B: 跳过 OnlyOffice
1. 注释掉 settings.py 中的 OnlyOffice 配置
2. 使用简单文本编辑器
3. 测试其他功能
4. 以后再部署 OnlyOffice

**立即可用**，但功能受限

---

## 如何选择？

**选择方案一 (安装 Docker)**:
- ✅ 想完整体验所有功能
- ✅ 需要 Office 文档编辑
- ✅ 有足够的时间 (30分钟)

**选择方案二 (跳过 OnlyOffice)**:
- ✅ 想快速测试系统
- ✅ 重点测试分享功能
- ✅ 暂时不需要文档编辑

---

**请告诉我您的选择**，我会根据您的选择继续完成步骤6的剩余开发！
