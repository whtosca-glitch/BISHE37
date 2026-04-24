<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h1>设备控制页</h1>
        <p>实现温度、湿度、烟雾浓度与开关状态的监听和控制</p>
      </div>
      <div>
        <button id="refresh_btn" class="btn" @click="loadCurrentDevice">立即刷新</button>
        <button id="back_btn" class="btn warn" @click="goBack">返回主页</button>
      </div>
    </div>

    <div class="panel">
      <div class="toolbar">
        <label class="field">
          <span>选择设备</span>
          <select v-model="state.currentRecordId" @change="loadCurrentDevice">
            <option v-if="!state.devices.length" value="">暂无设备</option>
            <option
              v-for="device in state.devices"
              :key="device.record_id"
              :value="device.record_id"
            >
              {{ `${device.id || '--'} / ${device.name || '--'}` }}
            </option>
          </select>
        </label>
        <label class="field">
          <span>轮询状态</span>
          <input type="text" value="每 3 秒刷新" readonly>
        </label>
        <button id="reload_devices_btn" class="btn" @click="loadDevices">刷新设备</button>
      </div>

      <div class="status-grid">
        <div class="status-card">
          <div class="label">温度</div>
          <div class="value">{{ currentMetrics.temp }}</div>
        </div>
        <div class="status-card">
          <div class="label">湿度</div>
          <div class="value">{{ currentMetrics.humi }}</div>
        </div>
        <div class="status-card">
          <div class="label">烟雾浓度</div>
          <div class="value">{{ currentMetrics.smoke }}</div>
        </div>
        <div class="status-card">
          <div class="label">设备开关 / 在线状态</div>
          <div class="value">{{ currentMetrics.status }}</div>
        </div>
      </div>
      <div id="device_info" class="log">当前设备：{{ currentMetrics.info }}</div>
    </div>

    <div class="panel">
      <div class="controls">
        <div class="control-box">
          <h3>设备开关控制</h3>
          <div class="switch-row">
            <button class="btn" @click="sendControl('status', 'true')">打开设备</button>
            <button class="btn warn" @click="sendControl('status', 'false')">关闭设备</button>
          </div>
          <div class="log">说明：通过 OneNET `set-device-property` 下发设备状态。</div>
        </div>

        <div class="control-box">
          <h3>温度控制</h3>
          <div class="control-row">
            <label class="field">
              <span>设置温度值</span>
              <input
                v-model.trim="controlForm.temp"
                type="number"
                step="0.1"
                :placeholder="placeholders.temp"
              >
            </label>
            <button class="btn" @click="sendControl('temp', controlForm.temp)">下发</button>
          </div>
        </div>

        <div class="control-box">
          <h3>湿度控制</h3>
          <div class="control-row">
            <label class="field">
              <span>设置湿度值</span>
              <input
                v-model.trim="controlForm.humi"
                type="number"
                step="0.1"
                :placeholder="placeholders.humi"
              >
            </label>
            <button class="btn" @click="sendControl('humi', controlForm.humi)">下发</button>
          </div>
        </div>

        <div class="control-box">
          <h3>烟雾浓度控制</h3>
          <div class="control-row">
            <label class="field">
              <span>设置烟雾浓度值</span>
              <input
                v-model.trim="controlForm.smoke"
                type="number"
                step="0.1"
                :placeholder="placeholders.smoke"
              >
            </label>
            <button class="btn" @click="sendControl('smoke', controlForm.smoke)">下发</button>
          </div>
        </div>
      </div>
    </div>

    <div id="toast" :class="['toast', toast.show ? `show ${toast.type}` : '']">{{ toast.text }}</div>
  </div>
</template>

<script>
import { onBeforeUnmount, onMounted, reactive } from 'vue'
import { getErrorMessage, getJson, postJson } from '../shared/api'

function formatMetric(value, suffix) {
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  return `${value}${suffix}`
}

function buildPlaceholder(label, value) {
  if (value === undefined || value === null || value === '') {
    return `请输入要控制的${label}`
  }
  return `当前监听值：${value}`
}

export default {
  name: 'AppDemoApp',
  setup() {
    const state = reactive({
      devices: [],
      currentRecordId: '',
      timerId: null
    })

    const currentMetrics = reactive({
      temp: '--',
      humi: '--',
      smoke: '--',
      status: '--',
      info: '--'
    })

    const controlForm = reactive({
      temp: '',
      humi: '',
      smoke: ''
    })

    const placeholders = reactive({
      temp: '请输入要控制的温度',
      humi: '请输入要控制的湿度',
      smoke: '请输入要控制的烟雾浓度'
    })

    const toast = reactive({
      show: false,
      text: '',
      type: 'success',
      timerId: null
    })

    function showToast(text, type = 'success') {
      toast.show = true
      toast.text = text
      toast.type = type
      if (toast.timerId) {
        clearTimeout(toast.timerId)
      }
      toast.timerId = setTimeout(() => {
        toast.show = false
      }, 2600)
    }

    function syncPlaceholders(data) {
      placeholders.temp = buildPlaceholder('温度', data.temp)
      placeholders.humi = buildPlaceholder('湿度', data.humi)
      placeholders.smoke = buildPlaceholder('烟雾浓度', data.smoke)
    }

    function resetCurrentDevice() {
      currentMetrics.temp = '--'
      currentMetrics.humi = '--'
      currentMetrics.smoke = '--'
      currentMetrics.status = '--'
      currentMetrics.info = '--'
    }

    async function loadDevices() {
      try {
        const res = await getJson('/api/devices')
        state.devices = (res.data && res.data.devices) || []
        if (!state.currentRecordId && state.devices.length) {
          state.currentRecordId = state.devices[0].record_id
        }
        await loadCurrentDevice()
      } catch (error) {
        showToast(getErrorMessage(error, '设备列表加载失败'), 'error')
      }
    }

    async function loadCurrentDevice() {
      if (!state.currentRecordId) {
        resetCurrentDevice()
        return
      }

      try {
        const res = await getJson('/api/app-demo-device', {
          record_id: state.currentRecordId
        })
        const data = res.data || {}
        currentMetrics.temp = formatMetric(data.temp, '℃')
        currentMetrics.humi = formatMetric(data.humi, '%')
        currentMetrics.smoke = formatMetric(data.smoke, 'ppm')
        currentMetrics.status = data.status === 'true'
          ? '开启 / 在线'
          : (data.status === 'false' ? '关闭 / 离线' : '未知')
        currentMetrics.info = `${data.display_name || '--'} / ${data.device_name || '--'} / ${data.device_id || '--'}`
        syncPlaceholders(data)
      } catch (error) {
        showToast(getErrorMessage(error, '设备实时数据加载失败'), 'error')
      }
    }

    async function sendControl(controlKey, value) {
      if (!state.currentRecordId) {
        showToast('请先选择设备', 'error')
        return
      }

      if (['temp', 'humi', 'smoke'].includes(controlKey) && value === '') {
        showToast('请输入要下发的数值', 'error')
        return
      }

      const payload = {
        record_id: state.currentRecordId,
        [controlKey]: value
      }

      try {
        const res = await postJson('/api/device-control', payload)
        showToast(res.msg || '控制下发成功', 'success')
        if (controlKey !== 'status') {
          controlForm[controlKey] = ''
        }
        setTimeout(() => {
          loadCurrentDevice()
        }, 800)
      } catch (error) {
        showToast(getErrorMessage(error, '控制下发失败'), 'error')
      }
    }

    function goBack() {
      window.location.href = '/'
    }

    function startPolling() {
      if (state.timerId) {
        clearInterval(state.timerId)
      }
      state.timerId = setInterval(() => {
        loadCurrentDevice()
      }, 3000)
    }

    onMounted(() => {
      loadDevices()
      startPolling()
    })

    onBeforeUnmount(() => {
      if (state.timerId) {
        clearInterval(state.timerId)
      }
      if (toast.timerId) {
        clearTimeout(toast.timerId)
      }
    })

    return {
      controlForm,
      currentMetrics,
      goBack,
      loadCurrentDevice,
      loadDevices,
      placeholders,
      sendControl,
      state,
      toast
    }
  }
}
</script>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100%;
}

body {
  font-family: "Microsoft YaHei", sans-serif;
  background: radial-gradient(circle at top, #12336b 0%, #08162f 45%, #020a16 100%);
  color: #fff;
}

.page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 40px;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}

.title h1 {
  margin: 0 0 8px;
  font-size: 30px;
}

.title p {
  margin: 0;
  color: #9cdcff;
  font-size: 14px;
}

.btn {
  min-width: 96px;
  height: 38px;
  padding: 0 16px;
  border: 1px solid rgba(52, 157, 255, 0.85);
  border-radius: 6px;
  background: rgba(3, 35, 87, 0.78);
  color: #fff;
  cursor: pointer;
}

.btn.warn {
  border-color: rgba(255, 227, 74, 0.95);
  color: #ffee75;
}

.panel {
  background: rgba(4, 22, 58, 0.88);
  border: 1px solid rgba(55, 164, 255, 0.45);
  border-radius: 12px;
  padding: 20px;
  box-sizing: border-box;
  box-shadow: 0 0 18px rgba(0, 103, 255, 0.14);
  margin-bottom: 18px;
}

.toolbar {
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 12px;
  align-items: end;
}

.field span {
  display: block;
  margin-bottom: 6px;
  color: #9cdcff;
  font-size: 14px;
}

.field select,
.field input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  box-sizing: border-box;
  border: 1px solid rgba(52, 157, 255, 0.55);
  border-radius: 6px;
  background: rgba(7, 30, 76, 0.94);
  color: #fff;
  outline: none;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: 18px;
}

.status-card {
  padding: 18px 16px;
  border-radius: 10px;
  background: rgba(9, 37, 88, 0.75);
  border: 1px solid rgba(70, 176, 255, 0.25);
}

.status-card .label {
  color: #8fd2ff;
  font-size: 14px;
  margin-bottom: 10px;
}

.status-card .value {
  font-size: 28px;
  font-weight: 700;
}

.controls {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.control-box {
  background: rgba(9, 37, 88, 0.75);
  border: 1px solid rgba(70, 176, 255, 0.25);
  border-radius: 10px;
  padding: 18px 16px;
}

.control-box h3 {
  margin: 0 0 14px;
  font-size: 18px;
}

.control-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: end;
}

.switch-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.log {
  min-height: 22px;
  margin-top: 10px;
  color: #8fd2ff;
  font-size: 14px;
}

.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  min-width: 280px;
  max-width: 80vw;
  padding: 12px 16px;
  border-radius: 8px;
  text-align: center;
  display: none;
}

.toast.show {
  display: block;
}

.toast.success {
  background: rgba(19, 148, 84, 0.95);
  border: 1px solid #63f3b0;
}

.toast.error {
  background: rgba(173, 39, 39, 0.96);
  border: 1px solid #ff9494;
}

@media (max-width: 900px) {
  .toolbar,
  .controls,
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
