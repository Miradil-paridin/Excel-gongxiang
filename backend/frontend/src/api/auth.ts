import request from '@/utils/request'
import type { AxiosResponse } from 'axios'

// 用户接口类型定义
export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
}

export interface ChangePasswordData {
  old_password: string
  new_password: string
  new_password_confirm: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  date_joined: string
  last_login?: string
}

// 登录
export function login(data: LoginData): Promise<AxiosResponse> {
  return request({
    url: '/auth/login/',
    method: 'post',
    data,
  })
}

// 注册
export function register(data: RegisterData): Promise<AxiosResponse> {
  return request({
    url: '/auth/register/',
    method: 'post',
    data,
  })
}

// 获取当前用户信息
export function getUserInfo(): Promise<AxiosResponse> {
  return request({
    url: '/auth/me/',
    method: 'get',
  })
}

// 修改密码
export function changePassword(data: ChangePasswordData): Promise<AxiosResponse> {
  return request({
    url: '/auth/change-password/',
    method: 'post',
    data,
  })
}

// 登出（前端清空token）
export function logout(): void {
  localStorage.removeItem('auth_token')
  window.location.href = '/login'
}
