<template>
  <div class="page">
    <el-card class="card" shadow="hover">
      <template #header>
        <span>用户登录</span>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @submit.prevent>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit">登录</el-button>
          <el-button @click="goRegister">注册账号</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-dialog v-model="registerVisible" title="注册" width="420px" destroy-on-close>
      <el-form :model="reg" :rules="regRules" ref="regRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="reg.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="reg.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="reg.email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerVisible = false">取消</el-button>
        <el-button type="primary" :loading="regLoading" @click="onRegister">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const router = useRouter()
const formRef = ref()
const regRef = ref()
const loading = ref(false)
const regLoading = ref(false)
const registerVisible = ref(false)

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const reg = reactive({ username: '', password: '', email: '' })
const regRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

function saveSession(data) {
  localStorage.setItem('token', data.token)
  localStorage.setItem('user', JSON.stringify(data.user))
}

async function onSubmit() {
  await formRef.value?.validate().catch(() => null)
  loading.value = true
  try {
    const { data } = await http.post('/auth/login/', {
      username: form.username,
      password: form.password,
    })
    saveSession(data)
    ElMessage.success('登录成功')
    router.push({ name: 'home' })
  } catch (e) {
    const msg = e.response?.data?.detail || '登录失败'
    ElMessage.error(typeof msg === 'string' ? msg : '登录失败')
  } finally {
    loading.value = false
  }
}

function goRegister() {
  registerVisible.value = true
}

async function onRegister() {
  await regRef.value?.validate().catch(() => null)
  regLoading.value = true
  try {
    const { data } = await http.post('/auth/register/', { ...reg })
    saveSession(data)
    ElMessage.success('注册成功')
    registerVisible.value = false
    router.push({ name: 'home' })
  } catch (e) {
    const msg = e.response?.data?.detail || '注册失败'
    ElMessage.error(typeof msg === 'string' ? msg : '注册失败')
  } finally {
    regLoading.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}
.card {
  width: 420px;
}
</style>
