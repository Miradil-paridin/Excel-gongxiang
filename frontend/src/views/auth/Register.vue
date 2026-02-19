<template>
  <div class="login-page">
    <div class="login-left">
      <div class="brand">
        <div class="brand-logo">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="40" height="40" rx="10" fill="white" fill-opacity="0.15"/>
            <path d="M10 13h20M10 20h13M10 27h16" stroke="white" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="brand-name">协同文档</span>
      </div>
      <div class="hero-text">
        <h1>加入我们<br>开始协作</h1>
        <p>创建账号后即可使用所有协作功能</p>
      </div>
    </div>

    <div class="login-right">
      <div class="login-form-wrap">
        <div class="form-header">
          <h2>创建账号</h2>
          <p>填写以下信息完成注册</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" size="large">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名（登录用）" prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="form.email" placeholder="邮箱（可选）" prefix-icon="Message" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="login-btn" @click="handleRegister" :loading="loading">
              {{ loading ? '注册中...' : '立即注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>已有账号？</span>
          <el-link type="primary" @click="$router.push('/')">立即登录</el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })

const validateConfirm = (_: any, value: string, callback: any) => {
  if (value !== form.password) callback(new Error('两次密码不一致'))
  else callback()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      const res: any = await request({
        url: '/auth/register/',
        method: 'post',
        data: { username: form.username, email: form.email, password: form.password }
      })
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      ElMessage.success('注册成功，欢迎加入！')
      router.push('/dashboard')
    } catch (error: any) {
      ElMessage.error(error.message || '注册失败，用户名可能已存在')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page { display: flex; min-height: 100vh; }

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
  padding: 50px 60px;
  display: flex;
  flex-direction: column;
  color: white;
  position: relative;
  overflow: hidden;
}
.login-left::before {
  content: '';
  position: absolute;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  top: -100px; right: -100px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-logo svg { width: 40px; height: 40px; }
.brand-name { font-size: 22px; font-weight: 700; }
.hero-text { margin: auto 0; }
.hero-text h1 { font-size: 44px; font-weight: 800; line-height: 1.15; margin: 0 0 16px; letter-spacing: -1px; }
.hero-text p { font-size: 16px; color: rgba(255,255,255,0.65); margin: 0; }

.login-right {
  width: 480px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 50px;
}
.login-form-wrap { width: 100%; max-width: 360px; }
.form-header { margin-bottom: 32px; }
.form-header h2 { font-size: 28px; font-weight: 700; color: #0f172a; margin: 0 0 8px; letter-spacing: -0.5px; }
.form-header p { font-size: 14px; color: #64748b; margin: 0; }

.login-btn {
  width: 100%; height: 44px; font-size: 15px; font-weight: 600;
  background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
  border: none !important; border-radius: 8px !important;
}
.form-footer { text-align: center; margin-top: 20px; font-size: 14px; color: #64748b; }

@media (max-width: 768px) {
  .login-left { display: none; }
  .login-right { width: 100%; }
}
</style>
