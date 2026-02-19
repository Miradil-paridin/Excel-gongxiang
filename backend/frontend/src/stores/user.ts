import { defineStore } from 'pinia'
import { login, getUserInfo, type LoginData, type UserInfo } from '@/api/auth'
import { ElMessage } from 'element-plus'

interface UserState {
  token: string | null
  userInfo: UserInfo | null
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('auth_token'),
    userInfo: null,
  }),

  getters: {
    isLoggedIn(): boolean {
      return !!this.token
    },

    username(): string {
      return this.userInfo?.username || ''
    },

    isStaff(): boolean {
      // 简单判断，可根据实际需求扩展
      return this.username === 'admin'
    },
  },

  actions: {
    // 登录
    async login(data: LoginData) {
      try {
        const response = await login(data)
        if (response.data?.token) {
          this.token = response.data.token
          localStorage.setItem('auth_token', response.data.token)
          await this.getUserInfo()
          ElMessage.success('登录成功')
          return true
        }
        return false
      } catch (error) {
        ElMessage.error('登录失败')
        return false
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        const response = await getUserInfo()
        if (response.data) {
          this.userInfo = response.data
          return response.data
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },

    // 登出
    logout() {
      this.token = null
      this.userInfo = null
      localStorage.removeItem('auth_token')
    },
  },
})
