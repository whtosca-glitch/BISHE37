<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">设备环境监测平台</h1>
      <p class="login-subtitle">请输入账号和密码后登录</p>
      <form @submit.prevent="submitLogin">
        <label class="login-field">
          <span>账号</span>
          <input v-model.trim="form.username" type="text" autocomplete="username">
        </label>
        <label class="login-field">
          <span>密码</span>
          <input v-model.trim="form.password" type="password" autocomplete="current-password">
        </label>
        <button class="login-btn" type="submit" :disabled="submitting">
          {{ submitting ? '登录中...' : '登录' }}
        </button>
      </form>
      <div class="login-msg">{{ message }}</div>
    </div>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { getErrorMessage, postJson } from '../shared/api'

export default {
  name: 'LoginApp',
  setup() {
    const form = reactive({
      username: 'root',
      password: 'root01'
    })
    const submitting = ref(false)
    const message = ref('')

    async function submitLogin() {
      message.value = ''
      submitting.value = true
      try {
        await postJson('/api/login', {
          username: form.username,
          password: form.password
        })
        window.location.href = '/'
      } catch (error) {
        message.value = getErrorMessage(error, '登录失败')
      } finally {
        submitting.value = false
      }
    }

    return {
      form,
      message,
      submitting,
      submitLogin
    }
  }
}
</script>

<style>
html,
body,
#app {
  width: 100%;
  height: 100%;
  margin: 0;
}

body {
  font-family: "Microsoft YaHei", sans-serif;
  background: radial-gradient(circle at top, #103b7a 0%, #07162d 48%, #020814 100%);
  color: #fff;
}

.login-page {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 420px;
  max-width: 88vw;
  padding: 32px 34px 28px;
  box-sizing: border-box;
  background: rgba(3, 18, 51, 0.92);
  border: 1px solid rgba(0, 193, 222, 0.75);
  box-shadow: 0 0 24px rgba(0, 193, 222, 0.22);
  border-radius: 12px;
}

.login-title {
  margin: 0 0 10px;
  font-size: 28px;
  text-align: center;
  letter-spacing: 2px;
}

.login-subtitle {
  margin: 0 0 24px;
  text-align: center;
  color: #9cdcff;
  font-size: 14px;
}

.login-field {
  display: block;
  margin-bottom: 16px;
}

.login-field span {
  display: block;
  margin-bottom: 8px;
  color: #9cdcff;
  font-size: 14px;
}

.login-field input {
  width: 100%;
  height: 42px;
  padding: 0 12px;
  box-sizing: border-box;
  border: 1px solid #0f5ca8;
  border-radius: 6px;
  background: rgba(8, 29, 73, 0.92);
  color: #fff;
  outline: none;
}

.login-btn {
  width: 100%;
  height: 44px;
  border: 1px solid #f0ff00;
  border-radius: 6px;
  background: rgba(33, 53, 5, 0.35);
  color: #f0ff00;
  font-size: 16px;
  cursor: pointer;
}

.login-btn:disabled {
  cursor: default;
  opacity: 0.75;
}

.login-msg {
  min-height: 22px;
  margin-top: 14px;
  text-align: center;
  font-size: 14px;
  color: #ff8d8d;
}
</style>
