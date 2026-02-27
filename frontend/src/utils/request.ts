import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 如果返回的数据中包含 code，根据 code 判断是否成功
    if (response.data && response.data.code !== undefined) {
      if (response.data.code !== 0) {
        // 业务错误
        console.error('业务错误:', response.data.message || '请求失败')
        return Promise.reject(new Error(response.data.message || '请求失败'))
      }
    }
    // 返回完整响应数据
    return response.data
  },
  (error) => {
    console.error('响应错误:', error)
    // token 过期或未认证
    if (error.response?.status === 401) {
      // 清除 token 并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export default service
