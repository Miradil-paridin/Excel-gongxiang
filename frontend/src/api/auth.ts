import request from '@/utils/request'

/**
 * 用户登录
 */
export function login(username: string, password: string) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data: {
      username,
      password
    }
  })
}

/**
 * 用户注册
 */
export function register(data: any) {
  return request({
    url: '/auth/register/',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  return request({
    url: '/auth/me/',
    method: 'get'
  })
}

/**
 * 修改密码
 */
export function changePassword(data: any) {
  return request({
    url: '/auth/change-password/',
    method: 'post',
    data
  })
}
