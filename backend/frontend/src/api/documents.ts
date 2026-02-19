import request from '@/utils/request'
import type { AxiosResponse } from 'axios'

// 文档类型
export type DocumentType = 'doc' | 'sheet'

// 文档接口类型定义
export interface Document {
  id: number
  title: string
  type: DocumentType
  content?: string
  creator: number
  creator_name: string
  created_at: string
  updated_at: string
  version: number
  permission: 'owner' | 'read' | 'write'
  is_deleted: boolean
}

export interface DocumentCreateData {
  title: string
  type: DocumentType
  content?: string
}

export interface DocumentUpdateData {
  title?: string
  content?: string
}

// 获取文档列表
export function getDocuments(params?: {
  type?: DocumentType | 'all'
  search?: string
  page?: number
  page_size?: number
  ordering?: string
}): Promise<AxiosResponse> {
  return request({
    url: '/documents/',
    method: 'get',
    params,
  })
}

// 创建文档
export function createDocument(data: DocumentCreateData): Promise<AxiosResponse> {
  return request({
    url: '/documents/',
    method: 'post',
    data,
  })
}

// 获取文档详情
export function getDocument(id: number): Promise<AxiosResponse> {
  return request({
    url: `/documents/${id}/`,
    method: 'get',
  })
}

// 更新文档
export function updateDocument(id: number, data: DocumentUpdateData): Promise<AxiosResponse> {
  return request({
    url: `/documents/${id}/`,
    method: 'patch',
    data,
  })
}

// 删除文档
export function deleteDocument(id: number): Promise<AxiosResponse> {
  return request({
    url: `/documents/${id}/`,
    method: 'delete',
  })
}

// 恢复文档
export function restoreDocument(id: number): Promise<AxiosResponse> {
  return request({
    url: `/documents/${id}/restore/`,
    method: 'post',
  })
}
