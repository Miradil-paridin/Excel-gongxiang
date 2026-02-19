import request from '@/utils/request'

export interface Document {
  id: number
  title: string
  type: string
  file?: string
  file_url?: string
  creator: number
  creator_username?: string
  created_at: string
  updated_at: string
  version: number
  is_deleted: boolean
  is_locked?: boolean
  locked_by?: number
}

export interface DocumentListParams {
  page?: number
  page_size?: number
  type?: string
  search?: string
  ordering?: string
}

/**
 * 获取文档列表
 */
export function getDocuments(params?: DocumentListParams) {
  return request({
    url: '/documents/',
    method: 'get',
    params
  })
}

/**
 * 获取文档详情
 */
export function getDocument(id: number) {
  return request({
    url: `/documents/${id}/`,
    method: 'get'
  })
}

/**
 * 创建文档
 */
export function createDocument(data: { title: string; type: string }) {
  return request({
    url: '/documents/',
    method: 'post',
    data
  })
}

/**
 * 更新文档
 */
export function updateDocument(id: number, data: Partial<Document>) {
  return request({
    url: `/documents/${id}/`,
    method: 'patch',
    data
  })
}

/**
 * 删除文档
 */
export function deleteDocument(id: number) {
  return request({
    url: `/documents/${id}/`,
    method: 'delete'
  })
}

/**
 * 恢复文档
 */
export function restoreDocument(id: number) {
  return request({
    url: `/documents/${id}/restore/`,
    method: 'post'
  })
}

/**
 * 获取文档编辑器配置
 */
export function getEditorConfig(id: number) {
  return request({
    url: `/documents/${id}/editor-config/`,
    method: 'get'
  })
}
