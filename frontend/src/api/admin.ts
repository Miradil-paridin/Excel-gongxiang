import request from '@/utils/request'

/**
 * 获取统计信息
 */
export function getAdminStatistics() {
  return request({
    url: '/auth/admin/statistics/',
    method: 'get'
  })
}

/**
 * 获取仪表盘数据
 */
export function getAdminDashboard() {
  return request({
    url: '/auth/admin/dashboard/',
    method: 'get'
  })
}

/**
 * 获取用户列表
 */
export function getAdminUsers(params?: any) {
  return request({
    url: '/auth/admin/users/',
    method: 'get',
    params
  })
}

/**
 * 更新用户信息（禁用/启用、设为管理员）
 */
export function updateAdminUser(id: number, data: any) {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: 'patch',
    data
  })
}

/**
 * 获取所有文档列表
 */
export function getAdminDocuments(params?: any) {
  return request({
    url: '/admin/documents/',
    method: 'get',
    params
  })
}

/**
 * 删除文档（软删除）
 */
export function deleteAdminDocument(id: number) {
  return request({
    url: `/admin/documents/${id}/delete/`,
    method: 'delete'
  })
}

/**
 * 彻底删除文档
 */
export function forceDeleteAdminDocument(id: number) {
  return request({
    url: `/admin/documents/${id}/force-delete/`,
    method: 'delete'
  })
}

/**
 * 获取所有文件列表
 */
export function getAdminFiles(params?: any) {
  return request({
    url: '/admin/files/',
    method: 'get',
    params
  })
}

/**
 * 删除文件（软删除）
 */
export function deleteAdminFile(id: number) {
  return request({
    url: `/admin/files/${id}/delete/`,
    method: 'delete'
  })
}

/**
 * 彻底删除文件
 */
export function forceDeleteAdminFile(id: number) {
  return request({
    url: `/admin/files/${id}/force-delete/`,
    method: 'delete'
  })
}

/**
 * 获取分享记录
 */
export function getAdminShares(params?: any) {
  return request({
    url: '/admin/shares/',
    method: 'get',
    params
  })
}
