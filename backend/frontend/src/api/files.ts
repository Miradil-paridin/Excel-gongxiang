import request from '@/utils/request'
import type { AxiosResponse } from 'axios'

// 文件接口类型定义
export interface File {
  id: number
  original_name: string
  file_url?: string
  size: number
  file_size_display: string
  mime_type: string
  file_type: 'image' | 'document' | 'spreadsheet' | 'presentation' | 'archive' | 'file'
  uploader: number
  uploader_name: string
  created_at: string
  is_deleted: boolean
}

export interface FileUploadData {
  file: File
}

// 获取文件列表
export function getFiles(params?: {
  search?: string
  page?: number
  page_size?: number
  ordering?: string
}): Promise<AxiosResponse> {
  return request({
    url: '/files/',
    method: 'get',
    params,
  })
}

// 上传文件
export function uploadFile(file: File): Promise<AxiosResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/files/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// 获取文件详情
export function getFile(id: number): Promise<AxiosResponse> {
  return request({
    url: `/files/${id}/`,
    method: 'get',
  })
}

// 删除文件
export function deleteFile(id: number): Promise<AxiosResponse> {
  return request({
    url: `/files/${id}/`,
    method: 'delete',
  })
}

// 下载文件
export function downloadFile(id: number): Promise<Blob> {
  return request({
    url: `/files/${id}/download/`,
    method: 'get',
    responseType: 'blob',
  })
}

// 恢复文件
export function restoreFile(id: number): Promise<AxiosResponse> {
  return request({
    url: `/files/${id}/restore/`,
    method: 'post',
  })
}
