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
 * 创建用户
 */
export function createAdminUser(data: any) {
  return request({
    url: '/auth/admin/users/',
    method: 'post',
    data
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
 * 删除用户
 */
export function deleteAdminUser(id: number) {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: 'delete'
  })
}

/**
 * 组织管理
 */
export function getAdminOrganizations() {
  return request({
    url: '/auth/admin/organizations/',
    method: 'get'
  })
}

export function createAdminOrganization(data: any) {
  return request({
    url: '/auth/admin/organizations/',
    method: 'post',
    data
  })
}

export function updateAdminOrganization(id: number, data: any) {
  return request({
    url: `/auth/admin/organizations/${id}/`,
    method: 'patch',
    data
  })
}

export function deleteAdminOrganization(id: number) {
  return request({
    url: `/auth/admin/organizations/${id}/`,
    method: 'delete'
  })
}

/**
 * 部门管理
 */
export function getAdminDepartments(params?: any) {
  return request({
    url: '/auth/admin/departments/',
    method: 'get',
    params
  })
}

export function createAdminDepartment(data: any) {
  return request({
    url: '/auth/admin/departments/',
    method: 'post',
    data
  })
}

export function updateAdminDepartment(id: number, data: any) {
  return request({
    url: `/auth/admin/departments/${id}/`,
    method: 'patch',
    data
  })
}

export function deleteAdminDepartment(id: number) {
  return request({
    url: `/auth/admin/departments/${id}/`,
    method: 'delete'
  })
}

/**
 * 用户组管理
 */
export function getAdminGroups() {
  return request({
    url: '/auth/admin/groups/',
    method: 'get'
  })
}

export function createAdminGroup(data: any) {
  return request({
    url: '/auth/admin/groups/',
    method: 'post',
    data
  })
}

export function updateAdminGroup(id: number, data: any) {
  return request({
    url: `/auth/admin/groups/${id}/`,
    method: 'patch',
    data
  })
}

export function deleteAdminGroup(id: number) {
  return request({
    url: `/auth/admin/groups/${id}/`,
    method: 'delete'
  })
}

/**
 * 获取所有文档列表
 */
export function getAdminDocuments(params?: any) {
  return request({
    url: '/auth/admin/documents/',
    method: 'get',
    params
  })
}

/**
 * 删除文档（软删除）
 */
export function deleteAdminDocument(id: number) {
  return request({
    url: `/auth/admin/documents/${id}/delete/`,
    method: 'delete'
  })
}

/**
 * 彻底删除文档
 */
export function forceDeleteAdminDocument(id: number) {
  return request({
    url: `/auth/admin/documents/${id}/force-delete/`,
    method: 'delete'
  })
}

/**
 * 获取所有文件列表
 */
export function getAdminFiles(params?: any) {
  return request({
    url: '/auth/admin/files/',
    method: 'get',
    params
  })
}

/**
 * 删除文件（软删除）
 */
export function deleteAdminFile(id: number) {
  return request({
    url: `/auth/admin/files/${id}/delete/`,
    method: 'delete'
  })
}

/**
 * 彻底删除文件
 */
export function forceDeleteAdminFile(id: number) {
  return request({
    url: `/auth/admin/files/${id}/force-delete/`,
    method: 'delete'
  })
}

/**
 * 获取分享记录
 */
export function getAdminShares(params?: any) {
  return request({
    url: '/auth/admin/shares/',
    method: 'get',
    params
  })
}
