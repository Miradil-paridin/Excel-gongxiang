# 集团级表格分发、上报与自动汇总系统

面向集团型企业（总部 + 多分公司）的私有化平台，提供“模板分发 -> 在线填报 -> 上报审核 -> 自动汇总 -> 导出分析”闭环。

## 1. 产品定位

### 1.1 一句话定义
- 面向集团企业的“表格分发、上报与自动汇总”系统，支持内网私有部署。

### 1.2 核心痛点
- 模板通过微信/邮件分发后被随意改动，导致总部无法统一汇总。
- 分公司上报后仍需人工复制粘贴汇总，耗时且易错。
- 催报靠人工，缺少进度可视化和统一留痕。

### 1.3 核心价值
- 格式锁定：总部统一模板，下级仅填写指定区域。
- 一键分发：按组织/部门/人员批量下发。
- 独立填报：每个填报方使用独立副本，互不干扰。
- 在线上报：系统内提交，实时同步总部。
- 自动汇总：按规则聚合并输出汇总结果。

## 2. 当前代码已实现能力（真实状态）

### 2.1 基础与架构
- 后端：Django 4.2 + DRF + JWT（`accounts`、`documents`、`files`、`shares`）。
- 前端：Vue 3 + TypeScript + Vite + Element Plus。
- 在线编辑：OnlyOffice 已集成。
- 环境配置：支持 `.env`（`python-decouple`）。

### 2.2 账号与组织
- 注册/登录/修改密码/当前用户信息。
- 管理端可维护：单位（Organization）、部门（Department）、用户组、用户信息。
- 管理员与普通用户权限分离，超级管理员可执行高风险管理动作。

### 2.3 文档与文件
- 文档：创建、列表、编辑、软删除、恢复。
- 文件：上传、列表、下载、软删除、恢复。
- 文件可一键转在线编辑文档。
- 同一用户重复打开同一文件会复用编辑映射，避免重复创建文档。

### 2.4 分享与副本
- 文档/文件分享（`read` / `write`）、启用停用、过期控制。
- “与我分享”“我的分享”页面可用。
- 已支持“基于分享创建个人填写副本”接口：`POST /api/shares/{id}/create-copy/`。

### 2.5 管理后台
- 仪表盘统计（用户/文档/文件/分享）。
- 管理端可管理用户、组织架构、文档、文件、分享记录。

### 2.6 启动与开发体验
- `start.sh` 一键启动前后端（含迁移与测试账号创建）。
- `Ctrl+C` 自动停止子进程并清理 8000/3000 端口。
- Node 版本固定：`.nvmrc` -> `20.19.0`。

## 3. 集团级目标方案（本次更新）

### 3.1 核心业务流程
1. 总部创建模板（定义可填区域、锁定结构）。
2. 总部创建分发任务（对象、截止时间、说明、规则）。
3. 分公司在“待办任务”中领取并填写副本。
4. 暂存草稿 -> 提交上报（支持撤回/退回）。
5. 系统按规则自动汇总，更新总部看板。
6. 总部在线查看并导出汇总 Excel。

### 3.2 功能模块
- 模板中心：模板创建、可填区域、版本管理、分类、预览。
- 分发任务：批量下发、状态跟踪、催报、退回、截止提醒。
- 填报端：待办列表、在线填报、草稿、上报、撤回、历史记录。
- 汇总统计：规则配置、自动聚合、汇总预览、导出、进度看板。
- 组织架构：集团 -> 分公司 -> 部门，多级权限隔离。
- 消息通知：新任务、催报、退回、截止提醒、汇总完成通知。

### 3.3 可填区域实现策略
- 方案 A（推荐）：基于 Excel 原生“保护工作表/锁定单元格”。
- 方案 B：用命名区域/元数据自定义规则控制。
- 建议：先落地方案 A，后续再补方案 B 做高级场景。

## 4. 技术架构建议

### 4.1 目标部署架构
- 网关层：Nginx（API、前端静态资源、OnlyOffice 反代）。
- 应用层：Vue SPA + Django API + OnlyOffice + Celery Worker。
- 数据层：PostgreSQL（主库） + Redis（缓存/消息队列）。

### 4.2 技术选型
- 前端：Vue3 + TS + Pinia + Element Plus。
- 后端：Django + DRF。
- 数据库：PostgreSQL（替代 SQLite）。
- 异步：Celery + Celery Beat。
- Excel 处理：openpyxl。
- 文件存储：本地（初期）/ MinIO（规模扩大）。
- 编排：Docker Compose。

## 5. 核心数据模型（建议）

- `Organization`：组织树（集团/分公司/部门）。
- `User`：用户与角色。
- `Template`：模板文件、版本、可填区域配置。
- `DistributionTask`：分发任务、截止时间、汇总规则。
- `Submission`：每个接收方的填报记录（草稿/已报/退回/撤回）。
- `AggregationResult`：任务级汇总结果与汇总文件。

## 6. API 规划（建议）

- 模板：`/api/templates/*`
- 任务：`/api/tasks/*`
- 填报：`/api/submissions/*`
- 汇总：`/api/tasks/{id}/aggregation|aggregate|export`

说明：以上为目标接口草案，当前代码中尚未全部实现。

## 7. 汇总引擎（建议实现）

### 7.1 规则驱动
- 支持 `sum`、`average`、`count`、`max/min`、`list`、`concat`、`formula`。
- 支持多种布局：`row_per_org`、`append_rows`、`sheet_per_org`、`pivot`。

### 7.2 执行链路
1. 上报后提取可填区域数据（openpyxl）。
2. 入库到结构化字段（JSON 或关系表）。
3. 触发 Celery 聚合任务。
4. 聚合后生成汇总 Excel 并持久化。
5. 通知总部“汇总已更新”。

## 8. 从现有代码迁移到目标系统

### 8.1 可复用
- JWT 认证、组织架构基础、OnlyOffice 集成、文件上传、管理后台、个人副本机制。

### 8.2 需新增
- 模板中心。
- 分发任务与任务实例（接收人维度）。
- 正式 Submission 工作流。
- 汇总引擎与规则配置 UI。
- 通知中心与催报。

### 8.3 必做升级
- SQLite -> PostgreSQL。
- 引入 Redis + Celery。
- 生产部署采用 Nginx + Gunicorn + OnlyOffice 反代。

## 9. 分阶段开发建议

1. 基础升级（1-2 周）：PostgreSQL、Redis、Celery、Docker Compose。
2. 模板与分发（2-3 周）：模板中心、任务下发、接收侧副本生成。
3. 填报流程（2-3 周）：草稿/上报/撤回/退回、进度看板、催报。
4. 汇总引擎（2-3 周）：数据提取、规则聚合、汇总导出。
5. 体验与商用（1-2 周）：审计、安全、运维与部署文档。

## 10. 我们补充的高价值功能建议

- 周期任务（月报/季报自动分发）。
- 填报校验规则（必填、类型、范围、跨字段校验）。
- 审核流（通过后才纳入汇总）。
- 数据看板（ECharts）。
- 更细粒度角色体系（集团管理员、分公司管理员、填报员）。
- 移动端适配（响应式或小程序）。

## 11. 商业化差异点

- 私有化部署，数据不出内网。
- Excel 原生编辑体验，培训成本低。
- 从“收表”升级到“自动汇总”。
- 轻量且可控，适合中小集团快速落地。

## 12. 快速启动（当前可运行）

### 12.1 环境
- Python 3.9+
- Node.js 20.19.0（建议 `nvm use`）
- Docker（用于 OnlyOffice，可选但推荐）

### 12.2 一键启动
```bash
./start.sh
```

支持启动参数（环境变量）：
- `OFFLINE=1`：离线模式，跳过 `pip install`，且若前端依赖不存在会直接提示退出
- `SKIP_PIP_INSTALL=1`：跳过后端依赖安装
- `SKIP_MIGRATE=1`：跳过数据库迁移
- `SKIP_CREATE_TEST_USERS=1`：跳过测试用户创建

### 12.2.1 Windows 11 离线打包与安装
- Windows 联网打包（在 Windows 机器执行）：
  - `powershell -ExecutionPolicy Bypass -File .\scripts\offline\pack-offline-win.ps1`
- Windows 离线安装（在目标机器执行）：
  - `powershell -ExecutionPolicy Bypass -File .\install-offline-win.ps1`

说明：
- Windows 离线包请务必在 Windows 联网机器生成，避免跨平台依赖不兼容（如 `node_modules`、Python 二进制轮子）。

### 12.3 手动启动（可选）
```bash
# backend
cd backend
cp .env.example .env
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver

# frontend
cd ../frontend
npm install
npm run dev
```

## 13. 说明
- `README` 同时作为产品方案与工程入口文档。
- 当前“分享 + 副本”能力可用于 MVP 验证；完整“任务分发 + 汇总引擎”仍在规划实现阶段。
