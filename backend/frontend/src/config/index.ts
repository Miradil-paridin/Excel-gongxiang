/**
 * 应用配置
 */
const API_BASE_URL = 'http://localhost:8000/api'

export default {
  // API 基础URL
  apiBaseUrl: API_BASE_URL,

  // 后端WebSocket地址
  wsBaseUrl: 'ws://localhost:8000',

  // 上传文件最大大小 (100MB)
  maxUploadSize: 100 * 1024 * 1024,

  // 允许的文件类型
  allowedFileTypes: [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'zip', 'rar', '7z', 'tar', 'gz'
  ],

  // 自动保存间隔 (毫秒)
  autoSaveInterval: 30000,

  // Token存储键
  tokenKey: 'auth_token',
}
