import request from '@/utils/request'

export interface FileItem {
  id: number
  name: string
  file: string
  file_url?: string
  mime_type: string
  size: number
  creator: number
  creator_username?: string
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface FileListParams {
  page?: number
  page_size?: number
  search?: string
}

/**
 * 获取文件列表
 */
export function getFiles(params?: FileListParams) {
  return request({
    url: '/files/',
    method: 'get',
    params
  })
}

/**
 * 获取文件详情
 */
export function getFile(id: number) {
  return request({
    url: `/files/${id}/`,
    method: 'get'
  })
}

/**
 * 上传文件
 */
export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/files/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除文件
 */
export function deleteFile(id: number) {
  return request({
    url: `/files/${id}/`,
    method: 'delete'
  })
}

/**
 * 恢复文件
 */
export function restoreFile(id: number) {
  return request({
    url: `/files/${id}/restore/`,
    method: 'post'
  })
}

/**
 * 下载文件
 */
export function downloadFile(id: number) {
  return request({
    url: `/files/${id}/download/`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 将上传文件转换为在线文档并打开编辑器
 */
export function openFileInEditor(id: number) {
  return request({
    url: `/files/${id}/open-in-editor/`,
    method: 'post'
  })
}
