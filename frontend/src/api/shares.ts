import request from '@/utils/request'

export interface Share {
  id: number
  document_id?: number
  file_id?: number
  sharee_id: number
  sharee_username?: string
  sharer_id: number
  sharer_username?: string
  permission: 'read' | 'write'
  is_active: boolean
  expires_at?: string
  message?: string
  created_at: string
}

/**
 * 获取分享列表
 */
export function getShares(params?: any) {
  return request({
    url: '/shares/',
    method: 'get',
    params
  })
}

/**
 * 获取我的分享（我分享出去的）
 */
export function getMyShares() {
  return request({
    url: '/shares/my-shares/',
    method: 'get'
  })
}

/**
 * 获取分享给我的
 */
export function getSharedWithMe() {
  return request({
    url: '/shares/shared-with-me/',
    method: 'get'
  })
}

/**
 * 创建分享
 */
export function createShare(data: {
  document?: number
  file?: number
  sharee: number
  permission: 'read' | 'write'
  expired_at?: string
  message?: string
}) {
  return request({
    url: '/shares/',
    method: 'post',
    data
  })
}

/**
 * 更新分享
 */
export function updateShare(id: number, data: Partial<Share>) {
  return request({
    url: `/shares/${id}/`,
    method: 'patch',
    data
  })
}

/**
 * 删除分享
 */
export function deleteShare(id: number) {
  return request({
    url: `/shares/${id}/`,
    method: 'delete'
  })
}

/**
 * 切换分享状态
 */
export function toggleShare(id: number) {
  return request({
    url: `/shares/${id}/toggle/`,
    method: 'post'
  })
}

/**
 * 获取用户列表（用于选择分享对象）
 */
export function getUsers() {
  return request({
    url: '/auth/users/',
    method: 'get'
  })
}
