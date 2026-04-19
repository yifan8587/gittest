<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand">用户管理系统</div>
      <div class="right">
        <span class="who">{{ user?.username }}</span>
        <el-tag v-if="user?.is_staff" type="warning" size="small">管理员</el-tag>
        <el-button link type="primary" @click="logout">退出</el-button>
      </div>
    </el-header>
    <el-main>
      <template v-if="user?.is_staff">
        <div class="toolbar">
          <el-button type="primary" @click="openCreate">新增用户</el-button>
          <el-button @click="loadUsers" :loading="listLoading">刷新</el-button>
        </div>
        <el-table :data="users" border stripe v-loading="listLoading" style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="用户名" min-width="120" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="first_name" label="名" width="100" />
          <el-table-column prop="last_name" label="姓" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="员工" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.is_staff" type="warning" size="small">是</el-tag>
              <span v-else>否</span>
            </template>
          </el-table-column>
          <el-table-column prop="date_joined" label="注册时间" min-width="170" />
          <el-table-column label="操作" fixed="right" width="160">
            <template #default="{ row }">
              <el-button type="primary" link @click="openEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="remove(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <template v-else>
        <el-card class="profile-card">
          <template #header>我的资料</template>
          <el-form :model="profile" :rules="profileRules" ref="profileRef" label-width="100px" style="max-width: 520px">
            <el-form-item label="用户名">
              <el-input v-model="profile.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profile.email" />
            </el-form-item>
            <el-form-item label="名" prop="first_name">
              <el-input v-model="profile.first_name" />
            </el-form-item>
            <el-form-item label="姓" prop="last_name">
              <el-input v-model="profile.last_name" />
            </el-form-item>
            <el-form-item label="新密码" prop="password">
              <el-input v-model="profile.password" type="password" show-password placeholder="不修改请留空" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saveLoading" @click="saveProfile">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </template>
    </el-main>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用户' : '新增用户'" width="520px" destroy-on-close>
      <el-form :model="edit" :rules="editRules" ref="editRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="edit.username" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item :label="editingId ? '新密码' : '密码'" prop="password">
          <el-input v-model="edit.password" type="password" show-password :placeholder="editingId ? '不修改请留空' : ''" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="edit.email" />
        </el-form-item>
        <el-form-item label="名" prop="first_name">
          <el-input v-model="edit.first_name" />
        </el-form-item>
        <el-form-item label="姓" prop="last_name">
          <el-input v-model="edit.last_name" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="edit.is_active" />
        </el-form-item>
        <el-form-item label="员工">
          <el-switch v-model="edit.is_staff" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="submitEdit">确定</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'

const router = useRouter()

const user = ref(null)
const users = ref([])
const listLoading = ref(false)
const saveLoading = ref(false)
const dialogVisible = ref(false)
const dialogLoading = ref(false)
const editingId = ref(null)
const profileRef = ref()
const editRef = ref()

const profile = reactive({
  id: null,
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
})

const profileRules = {
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

const edit = reactive({
  username: '',
  password: '',
  email: '',
  first_name: '',
  last_name: '',
  is_active: true,
  is_staff: false,
})

const editRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    {
      validator: (_r, v, cb) => {
        if (!editingId.value && !v) cb(new Error('请输入密码'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
}

function readUserFromStorage() {
  try {
    const raw = localStorage.getItem('user')
    user.value = raw ? JSON.parse(raw) : null
  } catch {
    user.value = null
  }
}

async function refreshMe() {
  const { data } = await http.get('/auth/me/')
  user.value = data
  localStorage.setItem('user', JSON.stringify(data))
  syncProfile()
}

function syncProfile() {
  if (!user.value) return
  profile.id = user.value.id
  profile.username = user.value.username
  profile.email = user.value.email || ''
  profile.first_name = user.value.first_name || ''
  profile.last_name = user.value.last_name || ''
  profile.password = ''
}

watch(
  () => user.value,
  () => syncProfile(),
  { deep: true }
)

async function loadUsers() {
  listLoading.value = true
  try {
    const { data } = await http.get('/users/')
    users.value = Array.isArray(data) ? data : data.results || []
  } catch (e) {
    ElMessage.error('加载用户列表失败')
  } finally {
    listLoading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(edit, {
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
  })
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(edit, {
    username: row.username,
    password: '',
    email: row.email || '',
    first_name: row.first_name || '',
    last_name: row.last_name || '',
    is_active: row.is_active,
    is_staff: row.is_staff,
  })
  dialogVisible.value = true
}

async function submitEdit() {
  await editRef.value?.validate().catch(() => null)
  dialogLoading.value = true
  try {
    const payload = { ...edit }
    if (editingId.value && !payload.password) delete payload.password
    if (editingId.value) {
      await http.patch(`/users/${editingId.value}/`, payload)
      ElMessage.success('已更新')
    } else {
      await http.post('/users/', payload)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    await loadUsers()
    await refreshMe()
  } catch (e) {
    const d = e.response?.data
    const msg = d?.detail || (typeof d === 'object' ? JSON.stringify(d) : '保存失败')
    ElMessage.error(typeof msg === 'string' ? msg : '保存失败')
  } finally {
    dialogLoading.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${row.username}」？`, '确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await http.delete(`/users/${row.id}/`)
    ElMessage.success('已删除')
    await loadUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

async function saveProfile() {
  await profileRef.value?.validate().catch(() => null)
  saveLoading.value = true
  try {
    const payload = {
      email: profile.email,
      first_name: profile.first_name,
      last_name: profile.last_name,
    }
    if (profile.password) payload.password = profile.password
    await http.patch(`/users/${profile.id}/`, payload)
    ElMessage.success('已保存')
    profile.password = ''
    await refreshMe()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saveLoading.value = false
  }
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  user.value = null
  router.push({ name: 'login' })
}

onMounted(async () => {
  readUserFromStorage()
  try {
    await refreshMe()
    if (user.value?.is_staff) await loadUsers()
  } catch {
    router.push({ name: 'login' })
  }
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f6f8fa;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.brand {
  font-weight: 600;
  font-size: 18px;
}
.right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.who {
  color: #606266;
}
.toolbar {
  margin-bottom: 16px;
}
.profile-card {
  max-width: 640px;
}
</style>
