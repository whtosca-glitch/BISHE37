<template>
  <div class="t_container">
    <header class="t_header">
      <div class="header_entry_bar">
        <button id="app_demo_btn" type="button" class="device_action_btn" @click="goAppDemo">设备控制</button>
      </div>
      <span>设备环境监测平台</span>
      <div class="header_action_bar">
        <button id="add_device_btn" type="button" class="device_action_btn" @click="openModal('add')">新增设备</button>
        <button id="delete_device_btn" type="button" class="device_action_btn" @click="openModal('delete')">删减设备</button>
        <button id="force_excel_btn" type="button" class="device_action_btn force_btn" @click="enableForceExcelMode">
          {{ state.forceExcelMode ? '已强制本地' : '强制启动' }}
        </button>
      </div>
    </header>

    <main class="t_main">
      <div class="t_left_box">
        <img class="t_l_line" src="/img/left_line.png" alt="">
        <div class="t_mbox t_rbox">
          <i />
          <span>近五日报错数</span>
          <h2>{{ metrics.error_count }}</h2>
        </div>
        <div class="t_mbox t_gbox">
          <i />
          <span>本月新增设备数</span>
          <h2>{{ metrics.new_devices_this_month }}</h2>
        </div>
        <div class="t_mbox t_ybox">
          <i />
          <span>设备在线消耗</span>
          <h2>{{ metrics.online_devices }}</h2>
        </div>
        <img class="t_r_line" src="/img/right_line.png" alt="">
      </div>

      <div class="t_center_box">
        <div class="t_top_box">
          <img class="t_l_line" src="/img/left_line.png" alt="">
          <ul class="t_nav">
            <li>
              <span>设备数</span>
              <h1>{{ metrics.total_devices }}</h1>
              <i />
            </li>
            <li>
              <span>当前在线数量</span>
              <h1>{{ metrics.online_devices }}</h1>
              <i />
            </li>
            <li>
              <span>当日天气</span>
              <h1>{{ metrics.weather_today }}</h1>
            </li>
          </ul>
          <img class="t_r_line" src="/img/right_line.png" alt="">
        </div>

        <div class="t_bottom_box">
          <img class="t_l_line" src="/img/left_line.png" alt="">
          <div class="weather_switch_bar">
            <button
              type="button"
              class="device_action_btn"
              :class="{ force_btn: state.viewMode === 'weather' }"
              @click="switchView('weather')"
            >
              天气预报
            </button>
            <button
              type="button"
              class="device_action_btn"
              :class="{ force_btn: state.viewMode === 'rcs' }"
              @click="switchView('rcs')"
            >
              RCS地图
            </button>
          </div>

          <div v-show="state.viewMode === 'weather'" id="weather_view" class="weather_switch_view">
            <div ref="weatherChartRef" class="echart" style="width: 100%; height: 3.6rem;" />
          </div>

          <div v-show="state.viewMode === 'rcs'" id="rcs_map_view" class="weather_switch_view">
            <div class="rcs_map_panel">
              <div class="rcs_map_header">
                <div>
                  <h2>RCS设备地图</h2>
                  <p>20个固定槽位，点击空位可新增，点击设备可查看、修改或删减</p>
                </div>
                <div class="rcs_map_legend">
                  <span><i class="rcs_legend_dot rcs_dot_online" />在线</span>
                  <span><i class="rcs_legend_dot rcs_dot_offline" />离线</span>
                  <span><i class="rcs_legend_dot rcs_dot_unknown" />未知</span>
                  <span><i class="rcs_legend_dot rcs_dot_empty" />空位</span>
                </div>
              </div>

              <div class="rcs_map_body">
                <div class="rcs_map_canvas">
                  <div id="rcs_slot_layer" class="rcs_slot_layer">
                    <button
                      v-for="slot in rcsSlots"
                      :key="slot.slotIndex"
                      type="button"
                      class="rcs_slot"
                      :class="[slot.statusClass, { rcs_slot_active: state.selectedSlotIndex === slot.slotIndex }]"
                      :style="{ left: `${slot.left}%`, top: `${slot.top}%` }"
                      @click="selectSlot(slot.slotIndex)"
                    >
                      <span class="rcs_slot_dot" />
                      <span class="rcs_slot_index">{{ slot.slotIndex }}号位</span>
                      <span class="rcs_slot_name">{{ slot.name }}</span>
                      <span class="hidden">{{ slot.statusText }}</span>
                    </button>
                  </div>
                </div>

                <div class="rcs_detail_panel">
                  <div class="rcs_detail_top">
                    <span>{{ selectedSlotTitle }}</span>
                    <span id="rcs_slot_state" class="rcs_detail_state">{{ selectedSlotState }}</span>
                  </div>
                  <div class="rcs_detail_metrics">
                    <div>设备名称：<span>{{ selectedSlotInfo.name }}</span></div>
                    <div>设备ID：<span>{{ selectedSlotInfo.id }}</span></div>
                    <div>当前IP：<span>{{ selectedSlotInfo.ip }}</span></div>
                    <div>温度：<span>{{ selectedSlotInfo.temp }}</span></div>
                    <div>湿度：<span>{{ selectedSlotInfo.humi }}</span></div>
                    <div>烟雾：<span>{{ selectedSlotInfo.smoke }}</span></div>
                  </div>
                  <div class="rcs_detail_tip">{{ selectedSlotTip }}</div>
                  <div class="device_form_actions rcs_detail_actions">
                    <button
                      v-if="!selectedSlotDevice"
                      type="button"
                      class="device_action_btn force_btn"
                      @click="openModal('add', { slot_index: state.selectedSlotIndex })"
                    >
                      新增到此
                    </button>
                    <template v-else>
                      <button type="button" class="device_action_btn" @click="openModal('edit', selectedSlotDevice)">修改设备</button>
                      <button type="button" class="device_action_btn" @click="openModal('delete', selectedSlotDevice)">删减设备</button>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <img class="t_r_line" src="/img/right_line.png" alt="">
        </div>
      </div>

      <div class="t_right_box">
        <img class="t_l_line" src="/img/left_line.png" alt="">
        <div ref="usageChartRef" class="echart" style="width: 50%; height: 4.6rem; position: absolute;" />
        <header class="t_b_h">
          <span style="width: 200px;">设备启动成功在线次数</span>
          <img src="/img/end.png" style="left: 45%;" alt="">
          <h3 id="total_starts" style="left: 65%;">{{ totalStarts }}<span>次</span></h3>
        </header>
        <main class="t_b_m">
          <img src="/img/map.png" alt="">
          <div
            id="dev_info_panel"
            style="position: absolute; left: 52%; top: 22%; width: 3.19rem; height: 1.67rem; color: #00f0ff; text-align: center; padding-top: 30px; box-sizing: border-box; z-index: 10; font-size: 0.16rem; line-height: 1.8;"
          >
            <div>IP: <span>{{ currentPanel.ip }}</span></div>
            <div>名称: <span>{{ currentPanel.name }}</span></div>
            <div>ID: <span>{{ currentPanel.id }}</span></div>
          </div>
          <div class="t_b_box">
            <span>溫度</span>
            <i />
            <h2>{{ currentPanel.temp }}</h2>
          </div>
          <div class="t_b_box1">
            <span>湿度</span>
            <i />
            <h2>{{ currentPanel.humi }}</h2>
          </div>
          <div class="t_b_box2">
            <span>烟雾浓度</span>
            <i />
            <h2>{{ currentPanel.smoke }}</h2>
          </div>
          <div class="t_b_box3">
            <span>是否在线</span>
            <i />
            <h2>{{ currentPanel.online }}</h2>
          </div>
        </main>
        <img class="t_r_line" src="/img/right_line.png" alt="">
      </div>

      <div class="bottom_row">
        <div class="b_left_box">
          <img class="t_l_line" src="/img/left_line.png" alt="">
          <div ref="statusTrendChartRef" class="echart" style="width: 100%; height: 3.6rem;" />
          <img class="t_r_line" src="/img/right_line.png" alt="">
        </div>

        <div class="b_center_box">
          <img class="t_l_line" src="/img/left_line.png" alt="">
          <div ref="healthChartRef" class="echart" style="width: 100%; height: 3.6rem;" />
          <img class="t_r_line" src="/img/right_line.png" alt="">
        </div>

        <div class="b_right_box">
          <img class="t_l_line" src="/img/left_line.png" alt="">
          <h1 class="t_title">告警中心</h1>
          <div class="alarm_config_bar">
            <label>温度阈值 <input v-model="alarmThresholds.temp" type="number" step="0.1"></label>
            <label>湿度阈值 <input v-model="alarmThresholds.humi" type="number" step="0.1"></label>
            <label>烟雾阈值 <input v-model="alarmThresholds.smoke" type="number" step="0.1"></label>
            <button type="button" class="device_action_btn alarm_save_btn" @click="saveAlarmConfig">保存阈值</button>
          </div>
          <div id="alarm_table_wrap" class="alarm_table_wrap">
            <table class="t_table">
              <thead>
                <tr>
                  <th>告警ID</th>
                  <th>告警规则名称</th>
                  <th>告警时间</th>
                  <th>告警等级</th>
                  <th>处理状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody id="alarm_table_body">
                <tr v-if="!alarmPageItems.length">
                  <td colspan="6">暂无告警数据</td>
                </tr>
                <tr
                  v-for="item in alarmPageItems"
                  :key="item.log_id"
                  class="alarm_row"
                  @click="processAlarm(item.log_id)"
                >
                  <td>{{ item.alarm_id || '--' }}</td>
                  <td>{{ item.rule_name || '--' }}</td>
                  <td>{{ item.alarm_time || '--' }}</td>
                  <td>
                    <span class="alarm_level_badge" :class="getAlarmLevelClass(item.alarm_status)">
                      {{ item.alarm_status || '--' }}
                    </span>
                  </td>
                  <td>
                    <span class="alarm_process_badge" :class="item.process_status === '已处理' ? 'alarm_process_done' : 'alarm_process_pending'">
                      {{ item.process_status || '未处理' }}
                    </span>
                  </td>
                  <td>
                    <button type="button" class="device_action_btn alarm_detail_btn" @click.stop="loadAlarmDetail(item.log_id)">详情</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="alarm_pager">
            <button type="button" class="device_action_btn" :disabled="alarmState.pageIndex <= 1" @click="changeAlarmPage(-1)">上一页</button>
            <span id="alarm_page_info">{{ alarmState.pageIndex }} / {{ alarmTotalPages }}</span>
            <button type="button" class="device_action_btn" :disabled="alarmState.pageIndex >= alarmTotalPages" @click="changeAlarmPage(1)">下一页</button>
          </div>
          <img class="t_r_line" src="/img/right_line.png" alt="">
        </div>
      </div>
    </main>

    <div class="device_modal" :class="{ hidden: !modal.visible }">
      <div class="device_modal_mask" @click="closeModal" />
      <div class="device_modal_panel">
        <h2>{{ modalTitle }}</h2>
        <form @submit.prevent="submitModal">
          <input v-model="deviceForm.record_id" type="hidden">
          <div class="device_form_grid" :class="{ hidden: modal.mode === 'delete' }">
            <label class="device_form_item">
              <span>显示名称</span>
              <input v-model.trim="deviceForm.display_name" type="text" placeholder="如：仓库1号设备">
            </label>
            <label class="device_form_item">
              <span>当前IP</span>
              <input v-model.trim="deviceForm.ip" type="text" placeholder="如：192.168.1.10">
            </label>
            <label class="device_form_item">
              <span>启动成功在线次数</span>
              <input v-model.trim="deviceForm.start_success_count" type="number" min="0">
            </label>
            <label class="device_form_item">
              <span>RCS地图槽位</span>
              <select v-model="deviceForm.slot_index">
                <option value="">自动分配</option>
                <option v-for="slotNo in 20" :key="slotNo" :value="String(slotNo)">{{ slotNo }}号位</option>
              </select>
            </label>
            <label class="device_form_item">
              <span>OneNET设备名称</span>
              <input v-model.trim="deviceForm.onenet_device_name" type="text" placeholder="必填">
            </label>
            <label class="device_form_item">
              <span>产品ID</span>
              <input v-model.trim="deviceForm.product_id" type="text" placeholder="必填">
            </label>
            <label class="device_form_item">
              <span>用户ID</span>
              <input v-model.trim="deviceForm.user_id" type="text" placeholder="必填">
            </label>
            <label class="device_form_item">
              <span>AccessKey</span>
              <input v-model.trim="deviceForm.access_key" type="text" placeholder="必填">
            </label>
            <label class="device_form_item">
              <span>鉴权版本</span>
              <input v-model.trim="deviceForm.auth_version" type="text">
            </label>
            <label class="device_form_item">
              <span>设备秘钥</span>
              <input v-model.trim="deviceForm.device_secret" type="text" placeholder="可选">
            </label>
            <label class="device_form_item">
              <span>设备ID</span>
              <input v-model.trim="deviceForm.device_id" type="text" placeholder="可选">
            </label>
            <label class="device_form_item device_form_item_full">
              <span>备注</span>
              <input v-model.trim="deviceForm.notes" type="text" placeholder="可选">
            </label>
          </div>
          <div class="device_delete_block" :class="{ hidden: modal.mode !== 'delete' }">
            <label class="device_form_item device_form_item_full">
              <span>选择要删减的设备</span>
              <select v-model="modal.deleteRecordId">
                <option v-for="device in state.devices" :key="device.record_id" :value="device.record_id">
                  {{ `${device.id || '--'} / ${device.name || device.device_name || '--'}` }}
                </option>
              </select>
            </label>
          </div>
          <div class="device_form_actions">
            <button type="button" class="device_action_btn" @click="closeModal">返回主页</button>
            <button type="submit" class="device_action_btn force_btn">{{ modalSubmitText }}</button>
          </div>
        </form>
      </div>
    </div>

    <div id="device_toast" class="device_toast" :class="deviceToastClass">{{ toast.text }}</div>

    <div class="device_modal" :class="{ hidden: !alarmDetail.visible }">
      <div class="device_modal_mask" @click="alarmDetail.visible = false" />
      <div class="device_modal_panel alarm_detail_panel">
        <h2>告警详情</h2>
        <div class="alarm_detail_summary">
          告警设备：{{ alarmDetail.current.alarm_id || '--' }}<br>
          告警类型：{{ alarmDetail.current.rule_name || '--' }}<br>
          告警等级：{{ alarmDetail.current.alarm_status || '--' }}<br>
          处理状态：{{ alarmDetail.current.process_status || '未处理' }}<br>
          告警时间：{{ alarmDetail.current.alarm_time || '--' }}<br>
          最新数值：{{ alarmDetail.current.metric_value || '--' }}
        </div>
        <div class="alarm_detail_section">
          <h3>处理记录</h3>
          <div class="alarm_detail_records">
            <div v-if="!(alarmDetail.current.process_records || []).length" class="alarm_detail_item">暂无处理记录</div>
            <div v-for="(record, index) in alarmDetail.current.process_records || []" :key="index" class="alarm_detail_item">
              处理时间：{{ record.time || '--' }}<br>
              处理动作：{{ record.action || '--' }}<br>
              处理人：{{ record.operator || '--' }}<br>
              说明：{{ record.note || '--' }}
            </div>
          </div>
        </div>
        <div class="alarm_detail_section">
          <h3>同类告警历史</h3>
          <div class="alarm_detail_records">
            <div v-if="!alarmDetail.history.length" class="alarm_detail_item">暂无历史告警</div>
            <div v-for="item in alarmDetail.history" :key="item.log_id || item.alarm_time" class="alarm_detail_item">
              告警时间：{{ item.alarm_time || '--' }}<br>
              告警等级：{{ item.alarm_status || '--' }}<br>
              处理状态：{{ item.process_status || '--' }}<br>
              监测值：{{ item.metric_value || '--' }}
            </div>
          </div>
        </div>
        <div class="device_form_actions">
          <button type="button" class="device_action_btn force_btn" @click="alarmDetail.visible = false">关闭</button>
        </div>
      </div>
    </div>

    <div class="alarm_notice" :class="{ hidden: !alarmToast.visible }">
      <div class="alarm_notice_inner" :class="alarmToast.color === 'red' ? 'alarm_notice_inner_red' : 'alarm_notice_inner_blue'">
        <div class="alarm_notice_title">告警提示</div>
        <div class="alarm_notice_text">{{ alarmToast.text }}</div>
        <button type="button" class="device_action_btn force_btn" @click="alarmToast.visible = false">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { deleteJson, getErrorMessage, getJson, postJson, putJson } from '../shared/api'

const slotPositions = [
  { left: 12, top: 18 }, { left: 29, top: 18 }, { left: 46, top: 18 }, { left: 63, top: 18 }, { left: 80, top: 18 },
  { left: 12, top: 38 }, { left: 29, top: 38 }, { left: 46, top: 38 }, { left: 63, top: 38 }, { left: 80, top: 38 },
  { left: 12, top: 58 }, { left: 29, top: 58 }, { left: 46, top: 58 }, { left: 63, top: 58 }, { left: 80, top: 58 },
  { left: 12, top: 78 }, { left: 29, top: 78 }, { left: 46, top: 78 }, { left: 63, top: 78 }, { left: 80, top: 78 }
]

function formatMetricValue(value, unit) {
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  return `${value}${unit}`
}

function getDeviceStateText(device) {
  if (!device) {
    return '空位'
  }
  if (device.online === true) {
    return '在线'
  }
  if (device.online === false) {
    return '离线'
  }
  return '未知'
}

function getStartCount(device) {
  return Number(device.starts ?? device.start_success_count ?? 0) || 0
}

function createEmptyDeviceForm() {
  return {
    record_id: '',
    display_name: '',
    ip: '',
    start_success_count: '1',
    slot_index: '',
    onenet_device_name: '',
    product_id: '',
    user_id: '',
    access_key: '',
    auth_version: '2020-05-29',
    device_secret: '',
    device_id: '',
    notes: ''
  }
}

export default {
  name: 'DashboardApp',
  setup() {
    const weatherChartRef = ref(null)
    const statusTrendChartRef = ref(null)
    const healthChartRef = ref(null)
    const usageChartRef = ref(null)

    const charts = {
      weather: null,
      statusTrend: null,
      health: null,
      usage: null
    }

    const state = reactive({
      devices: [],
      selectedIndex: 0,
      forceExcelMode: false,
      viewMode: 'weather',
      selectedSlotIndex: 1,
      pollTimerId: null,
      activeAlarmToastShown: false
    })

    const metrics = reactive({
      error_count: '--',
      new_devices_this_month: '--',
      online_devices: '--',
      total_devices: '--',
      weather_today: '--'
    })

    const currentPanel = reactive({
      ip: '--',
      name: '--',
      id: '--',
      temp: '--',
      humi: '--',
      smoke: '--',
      online: '--'
    })

    const selectedSlotMetrics = reactive({
      temp: '--',
      humi: '--',
      smoke: '--',
      status: '待选择'
    })

    const toast = reactive({
      visible: false,
      text: '',
      color: 'blue',
      timerId: null
    })

    const alarmToast = reactive({
      visible: false,
      text: '',
      color: 'red'
    })

    const modal = reactive({
      visible: false,
      mode: 'add',
      editingRecordId: '',
      deleteRecordId: ''
    })

    const deviceForm = reactive(createEmptyDeviceForm())

    const alarmState = reactive({
      rules: [],
      items: [],
      pageIndex: 1,
      pageSize: 5
    })

    const alarmThresholds = reactive({
      temp: '',
      humi: '',
      smoke: ''
    })

    const alarmDetail = reactive({
      visible: false,
      current: {},
      history: []
    })

    const weatherForecast = ref([])

    const slotMap = computed(() => {
      const map = {}
      state.devices.forEach((device) => {
        const slotIndex = Number(device.slot_index) || 0
        if (slotIndex >= 1 && slotIndex <= 20) {
          map[slotIndex] = device
        }
      })
      return map
    })

    const selectedSlotDevice = computed(() => slotMap.value[state.selectedSlotIndex] || null)

    const rcsSlots = computed(() => {
      return slotPositions.map((position, index) => {
        const slotIndex = index + 1
        const device = slotMap.value[slotIndex]
        let statusClass = 'rcs_slot_empty'
        let statusText = '空位'
        let name = '空位'
        if (device) {
          name = device.name || device.device_name || `设备${slotIndex}`
          if (device.online === true) {
            statusClass = 'rcs_slot_online'
            statusText = '在线'
          } else if (device.online === false) {
            statusClass = 'rcs_slot_offline'
            statusText = '离线'
          } else {
            statusClass = 'rcs_slot_unknown'
            statusText = '未知'
          }
        }
        return {
          slotIndex,
          left: position.left,
          top: position.top,
          statusClass,
          statusText,
          name
        }
      })
    })

    const selectedSlotTitle = computed(() => {
      if (!selectedSlotDevice.value) {
        return `当前为 ${state.selectedSlotIndex} 号空位`
      }
      return `${selectedSlotDevice.value.slot_index || state.selectedSlotIndex} 号槽位`
    })

    const selectedSlotState = computed(() => {
      if (!selectedSlotDevice.value) {
        return '空位'
      }
      return selectedSlotMetrics.status || getDeviceStateText(selectedSlotDevice.value)
    })

    const selectedSlotInfo = computed(() => {
      if (!selectedSlotDevice.value) {
        return {
          name: '--',
          id: '--',
          ip: '--',
          temp: '--',
          humi: '--',
          smoke: '--'
        }
      }
      return {
        name: selectedSlotDevice.value.name || selectedSlotDevice.value.device_name || '--',
        id: selectedSlotDevice.value.id || '--',
        ip: selectedSlotDevice.value.ip || '--',
        temp: selectedSlotMetrics.temp,
        humi: selectedSlotMetrics.humi,
        smoke: selectedSlotMetrics.smoke
      }
    })

    const selectedSlotTip = computed(() => {
      if (!selectedSlotDevice.value) {
        return '点击“新增到此”后，将直接把新设备绑定到当前空位。'
      }
      return '当前设备已绑定到此槽位，可在地图中直接修改或删减。'
    })

    const totalStarts = computed(() => {
      return state.devices.reduce((sum, device) => sum + getStartCount(device), 0)
    })

    const alarmTotalPages = computed(() => {
      return Math.max(1, Math.ceil(alarmState.items.length / alarmState.pageSize))
    })

    const alarmPageItems = computed(() => {
      const start = (alarmState.pageIndex - 1) * alarmState.pageSize
      return alarmState.items.slice(start, start + alarmState.pageSize)
    })

    const modalTitle = computed(() => {
      if (modal.mode === 'edit') {
        return '修改设备'
      }
      if (modal.mode === 'delete') {
        return '删减设备'
      }
      return '新增设备'
    })

    const modalSubmitText = computed(() => {
      if (modal.mode === 'edit') {
        return '保存修改'
      }
      if (modal.mode === 'delete') {
        return '确认删减'
      }
      return '确定'
    })

    const deviceToastClass = computed(() => {
      return {
        hidden: !toast.visible,
        device_toast_green: toast.visible && toast.color === 'green',
        device_toast_blue: toast.visible && toast.color !== 'green'
      }
    })

    function showToast(text, color = 'blue') {
      if (!text) {
        return
      }
      toast.visible = true
      toast.text = text
      toast.color = color
      if (toast.timerId) {
        clearTimeout(toast.timerId)
      }
      toast.timerId = setTimeout(() => {
        toast.visible = false
      }, 2600)
    }

    function showAlarmToast(text, color = 'red') {
      if (!text) {
        return
      }
      alarmToast.visible = true
      alarmToast.text = text
      alarmToast.color = color
    }

    function initCharts() {
      charts.weather = echarts.init(weatherChartRef.value)
      charts.statusTrend = echarts.init(statusTrendChartRef.value)
      charts.health = echarts.init(healthChartRef.value)
      charts.usage = echarts.init(usageChartRef.value)
      charts.usage.on('click', (params) => {
        if (typeof params.dataIndex === 'number') {
          state.selectedIndex = params.dataIndex
          syncCurrentDevice()
        }
      })
      charts.usage.on('dblclick', (params) => {
        if (typeof params.dataIndex === 'number') {
          const device = state.devices[params.dataIndex]
          if (device) {
            state.selectedIndex = params.dataIndex
            openModal('edit', device)
          }
        }
      })
    }

    function resizeCharts() {
      Object.values(charts).forEach((chart) => {
        if (chart) {
          chart.resize()
        }
      })
    }

    function disposeCharts() {
      Object.keys(charts).forEach((key) => {
        if (charts[key]) {
          charts[key].dispose()
          charts[key] = null
        }
      })
    }

    function goAppDemo() {
      window.location.href = '/app_demo.html'
    }

    function switchView(mode) {
      state.viewMode = mode
      resizeCharts()
      if (mode === 'rcs') {
        refreshSelectedSlotDetail(true)
      }
    }

    async function fetchMetrics() {
      try {
        const res = await getJson('/api/metrics', {
          force_excel: state.forceExcelMode ? 1 : 0
        })
        const data = res.data || {}
        metrics.error_count = data.error_count ?? '--'
        metrics.new_devices_this_month = data.new_devices_this_month ?? '--'
        metrics.online_devices = data.online_devices ?? '--'
        metrics.total_devices = data.total_devices ?? '--'
      } catch (error) {
        showToast(getErrorMessage(error, '获取监控指标失败'), 'blue')
      }
    }

    async function fetchStatusTrend() {
      try {
        const res = await getJson('/api/status-trend', {
          force_excel: state.forceExcelMode ? 1 : 0
        })
        renderStatusTrendChart(res.data || {})
      } catch (error) {
        showToast(getErrorMessage(error, '获取最近五天在线统计失败'), 'blue')
      }
    }

    function renderStatusTrendChart(data) {
      const items = data.items || []
      const today = data.today || {}
      const xAxisData = items.map((item) => item.label || item.date || '--')
      const onlineData = items.map((item) => Number(item.online_count) || 0)
      const offlineData = items.map((item) => Number(item.offline_count) || 0)

      charts.statusTrend.setOption({
        title: {
          show: true,
          top: '10%',
          left: '3%',
          text: '最近五天在线统计',
          textStyle: {
            fontSize: 18,
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter(params) {
            const lines = [params[0]?.name || '--']
            params.forEach((item) => {
              lines.push(`${item.seriesName}：${item.value}`)
            })
            if (params.length && params[0].axisValue === xAxisData[xAxisData.length - 1]) {
              lines.push(`今日总设备：${today.total_devices || 0}`)
            }
            return lines.join('<br/>')
          },
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          top: '12%',
          right: '5%',
          itemGap: 16,
          itemWidth: 10,
          itemHeight: 10,
          data: ['在线机数', '离线机数'],
          textStyle: {
            color: '#fff',
            fontSize: 12
          }
        },
        grid: {
          x: 30,
          y: 80,
          x2: 30,
          y2: 45
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          axisTick: { show: false },
          axisLine: {
            show: true,
            lineStyle: { color: '#1AA1FD' },
            symbol: ['none', 'arrow']
          },
          axisLabel: {
            show: true,
            interval: 0,
            color: '#1AA1FD',
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          axisTick: { show: false },
          axisLine: {
            show: true,
            lineStyle: { color: '#1AA1FD' },
            symbol: ['none', 'arrow']
          },
          axisLabel: {
            show: true,
            color: '#fff'
          },
          splitLine: { show: false }
        },
        series: [
          {
            name: '在线机数',
            type: 'bar',
            data: onlineData,
            barWidth: 12,
            itemStyle: { color: '#3FA7DC', borderRadius: 4 },
            label: { show: true, position: 'top', color: '#fff' }
          },
          {
            name: '离线机数',
            type: 'bar',
            data: offlineData,
            barWidth: 12,
            itemStyle: { color: '#7091C4', borderRadius: 4 },
            label: { show: true, position: 'top', color: '#fff' }
          }
        ]
      }, true)
    }

    async function fetchWeather() {
      try {
        const res = await getJson('/api/weather')
        const forecast = ((res.data && res.data.forecast) || []).slice(0, 5)
        weatherForecast.value = forecast
        if (forecast.length) {
          metrics.weather_today = forecast[0].type || '--'
        }
        renderWeatherChart(forecast)
      } catch (error) {
        showToast(getErrorMessage(error, '天气数据请求失败'), 'blue')
      }
    }

    function renderWeatherChart(forecast) {
      const xData = []
      const highData = []
      const lowData = []
      forecast.forEach((day) => {
        xData.push(`${day.date}日\n${day.type}`)
        highData.push(parseInt(String(day.high || '').replace(/[^0-9-]/g, ''), 10))
        lowData.push(parseInt(String(day.low || '').replace(/[^0-9-]/g, ''), 10))
      })
      charts.weather.setOption({
        title: {
          text: '5天天气预报',
          x: 'center',
          top: '10%',
          textStyle: { color: '#FFF', fontSize: 16 }
        },
        tooltip: {
          trigger: 'axis',
          formatter(params) {
            let html = `${String(params[0]?.name || '').replace('\n', ' ')}<br/>`
            params.forEach((item) => {
              html += `${item.seriesName}: ${item.value}℃<br/>`
            })
            return html
          }
        },
        legend: {
          data: ['高温', '低温'],
          top: '10%',
          right: '5%',
          textStyle: { color: '#fff' }
        },
        grid: {
          top: '30%',
          left: '10%',
          right: '10%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: xData,
          axisLine: { lineStyle: { color: '#1AA1FD' } },
          axisLabel: { color: '#fff', fontSize: 12, margin: 15 }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: {
            lineStyle: {
              color: 'rgba(26, 161, 253, 0.2)',
              type: 'dashed'
            }
          },
          axisLabel: { color: '#fff', formatter: '{value} ℃' }
        },
        series: [
          {
            name: '高温',
            type: 'line',
            data: highData,
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: { color: '#F57474' },
            lineStyle: { width: 3, color: '#F57474' },
            label: { show: true, position: 'top', formatter: '{c}℃', color: '#fff' }
          },
          {
            name: '低温',
            type: 'line',
            data: lowData,
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: { color: '#1089E7' },
            lineStyle: { width: 3, color: '#1089E7' },
            label: { show: true, position: 'bottom', formatter: '{c}℃', color: '#fff' }
          }
        ]
      }, true)
    }

    async function fetchDevices(options = {}) {
      try {
        const res = await getJson('/api/devices', {
          force_excel: state.forceExcelMode ? 1 : 0
        })
        state.devices = (res.data && res.data.devices) || []
        if (state.selectedIndex >= state.devices.length) {
          state.selectedIndex = 0
        }
        if (!options.silentStorageStatus && res.data && res.data.storage && res.data.storage.toast_text) {
          showToast(res.data.storage.toast_text, res.data.storage.toast_color || 'blue')
        }
        renderHealthChart()
        renderUsageChart()
        ensureSelectedSlot()
        refreshSelectedSlotDetail(true)
        if (state.devices.length) {
          await syncCurrentDevice()
        } else {
          resetCurrentPanel()
        }
      } catch (error) {
        state.devices = []
        renderHealthChart()
        renderUsageChart()
        resetCurrentPanel()
        showToast(getErrorMessage(error, '请先运行本地设备服务'), 'blue')
      }
    }

    async function fetchDeviceProperty(recordId) {
      const res = await getJson('/api/device-properties', {
        record_id: recordId,
        force_excel: state.forceExcelMode ? 1 : 0
      })
      return res.data || {}
    }

    function resetCurrentPanel() {
      currentPanel.ip = '--'
      currentPanel.name = '--'
      currentPanel.id = '--'
      currentPanel.temp = '--'
      currentPanel.humi = '--'
      currentPanel.smoke = '--'
      currentPanel.online = '--'
    }

    async function syncCurrentDevice() {
      const currentDevice = state.devices[state.selectedIndex]
      if (!currentDevice) {
        resetCurrentPanel()
        return
      }
      currentPanel.ip = currentDevice.ip || '未配置'
      currentPanel.name = currentDevice.name || '--'
      currentPanel.id = currentDevice.id || '--'
      currentPanel.temp = '加载中...'
      currentPanel.humi = '加载中...'
      currentPanel.smoke = '加载中...'
      currentPanel.online = currentDevice.online ? '在线' : '离线'

      try {
        const propertyMap = await fetchDeviceProperty(currentDevice.record_id)
        currentDevice.online = propertyMap.status === 'true'
        currentDevice.id = propertyMap.device_id || currentDevice.id
        currentDevice.ip = propertyMap.ip || currentDevice.ip
        currentPanel.ip = currentDevice.ip || '未配置'
        currentPanel.name = currentDevice.name || '--'
        currentPanel.id = currentDevice.id || '--'
        currentPanel.temp = formatMetricValue(propertyMap.temp, '℃')
        currentPanel.humi = formatMetricValue(propertyMap.humi, '%')
        currentPanel.smoke = formatMetricValue(propertyMap.smoke, 'ppm')
        currentPanel.online = currentDevice.online ? '在线' : '离线'
        renderHealthChart()
        renderUsageChart()
        refreshSelectedSlotDetail(false)
      } catch (error) {
        currentPanel.temp = '获取失败'
        currentPanel.humi = '获取失败'
        currentPanel.smoke = '获取失败'
        currentPanel.online = currentDevice.online ? '在线' : '未知'
      }
    }

    function renderHealthChart() {
      const onlineCount = state.devices.filter((device) => device.online === true).length
      const offlineCount = state.devices.filter((device) => device.online !== true).length
      charts.health.setOption({
        title: {
          text: '本月设备状态统计',
          top: 35,
          left: 20,
          textStyle: { fontSize: 18, color: '#fff' }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          right: 20,
          top: 35,
          data: ['故障', '正常'],
          textStyle: { color: '#fff' }
        },
        series: [
          {
            name: '设备状态',
            type: 'pie',
            radius: ['0', '60%'],
            center: ['50%', '60%'],
            color: ['#e72325', '#98e002', '#2ca3fd'],
            label: {
              formatter: '{b}\n{d}%'
            },
            data: [
              { value: offlineCount, name: '故障' },
              { value: onlineCount, name: '正常', selected: true }
            ]
          }
        ]
      }, true)
    }

    function renderUsageChart() {
      const total = totalStarts.value
      const titleData = []
      const valueData = []
      const percentData = []
      const borderData = []
      const statusFlags = []
      const colors = ['#1089E7', '#F57474', '#56D0E3', '#F8B448', '#8B78F6']

      state.devices.forEach((device) => {
        const starts = getStartCount(device)
        const isOnline = !!device.online
        titleData.push(`${device.id || '--'} ${device.name || device.device_name || '--'}${isOnline ? '' : ' [离线]'}`)
        valueData.push(starts)
        percentData.push(total ? Number(((starts / total) * 100).toFixed(2)) : 0)
        borderData.push(100)
        statusFlags.push(isOnline)
      })

      charts.usage.setOption({
        title: {
          text: '设备使用频率',
          x: 'center',
          textStyle: { color: '#FFF' },
          left: '6%',
          top: '10%'
        },
        grid: {
          top: '20%',
          left: '32%'
        },
        xAxis: { show: false },
        yAxis: [
          {
            show: true,
            data: titleData,
            inverse: true,
            axisLine: { show: false },
            splitLine: { show: false },
            axisTick: { show: false },
            axisLabel: {
              color: '#fff',
              formatter(value, index) {
                return [`{lg|${index + 1}}  {title|${value}} `].join('\n')
              },
              rich: {
                lg: {
                  backgroundColor: '#339911',
                  color: '#fff',
                  borderRadius: 15,
                  align: 'center',
                  width: 15,
                  height: 15
                }
              }
            }
          },
          {
            show: true,
            inverse: true,
            data: valueData,
            axisLabel: {
              fontSize: 12,
              color: '#fff'
            },
            axisLine: { show: false },
            splitLine: { show: false },
            axisTick: { show: false }
          }
        ],
        series: [
          {
            name: '条',
            type: 'bar',
            yAxisIndex: 0,
            data: percentData,
            barWidth: 10,
            itemStyle: {
              borderRadius: 20,
              color(params) {
                if (!statusFlags[params.dataIndex]) {
                  return '#6c7a89'
                }
                return colors[params.dataIndex % colors.length]
              }
            },
            label: {
              show: true,
              position: 'inside',
              formatter: '{c}%'
            }
          },
          {
            name: '框',
            type: 'bar',
            yAxisIndex: 1,
            barGap: '-100%',
            data: borderData,
            barWidth: 15,
            itemStyle: {
              color: 'none',
              borderColor: '#00c1de',
              borderWidth: 3,
              borderRadius: 15
            }
          }
        ]
      }, true)
    }

    function ensureSelectedSlot() {
      if (!slotMap.value[state.selectedSlotIndex]) {
        const firstDevice = state.devices.find((device) => Number(device.slot_index))
        if (firstDevice) {
          state.selectedSlotIndex = Number(firstDevice.slot_index)
        }
      }
    }

    async function refreshSelectedSlotDetail(fetchRemote = true) {
      const device = selectedSlotDevice.value
      if (!device) {
        selectedSlotMetrics.temp = '--'
        selectedSlotMetrics.humi = '--'
        selectedSlotMetrics.smoke = '--'
        selectedSlotMetrics.status = '空位'
        return
      }

      selectedSlotMetrics.temp = '加载中...'
      selectedSlotMetrics.humi = '加载中...'
      selectedSlotMetrics.smoke = '加载中...'
      selectedSlotMetrics.status = getDeviceStateText(device)

      if (!fetchRemote) {
        return
      }

      try {
        const data = await fetchDeviceProperty(device.record_id)
        device.online = data.status === 'true'
        device.id = data.device_id || device.id
        device.ip = data.ip || device.ip
        selectedSlotMetrics.temp = formatMetricValue(data.temp, '℃')
        selectedSlotMetrics.humi = formatMetricValue(data.humi, '%')
        selectedSlotMetrics.smoke = formatMetricValue(data.smoke, 'ppm')
        selectedSlotMetrics.status = data.status === 'true' ? '在线' : '离线'
      } catch (error) {
        selectedSlotMetrics.temp = '获取失败'
        selectedSlotMetrics.humi = '获取失败'
        selectedSlotMetrics.smoke = '获取失败'
      }
    }

    function selectSlot(slotIndex) {
      state.selectedSlotIndex = slotIndex
      refreshSelectedSlotDetail(true)
    }

    async function fetchAlarmConfig() {
      try {
        const res = await getJson('/api/alarm-config')
        alarmState.rules = (res.data && res.data.rules) || []
        alarmState.rules.forEach((rule) => {
          if (rule.rule_key === 'temp') {
            alarmThresholds.temp = rule.threshold_value
          } else if (rule.rule_key === 'humi') {
            alarmThresholds.humi = rule.threshold_value
          } else if (rule.rule_key === 'smoke') {
            alarmThresholds.smoke = rule.threshold_value
          }
        })
      } catch (error) {
        showToast(getErrorMessage(error, '获取告警阈值失败'), 'blue')
      }
    }

    async function fetchAlarmList() {
      try {
        const res = await getJson('/api/alarms', {
          force_excel: state.forceExcelMode ? 1 : 0,
          limit: 200
        })
        alarmState.rules = (res.data && res.data.config && res.data.config.rules) || alarmState.rules
        alarmState.items = (res.data && res.data.items) || []
        alarmState.pageIndex = Math.min(alarmState.pageIndex, alarmTotalPages.value)
        alarmState.pageIndex = Math.max(1, alarmState.pageIndex)
        showAlarmPopup((res.data && res.data.new_alarm_items) || [], (res.data && res.data.active_alarm_items) || [])
      } catch (error) {
        alarmState.items = []
        alarmState.pageIndex = 1
      }
    }

    function buildAlarmRules() {
      let rules = [...alarmState.rules]
      if (!rules.length) {
        rules = [
          { rule_key: 'temp', enabled: 1 },
          { rule_key: 'humi', enabled: 1 },
          { rule_key: 'smoke', enabled: 1 },
          { rule_key: 'status', enabled: 1 }
        ]
      }
      return rules.map((rule) => {
        const nextRule = { ...rule, enabled: 1 }
        if (rule.rule_key === 'temp') {
          nextRule.threshold_value = alarmThresholds.temp
        } else if (rule.rule_key === 'humi') {
          nextRule.threshold_value = alarmThresholds.humi
        } else if (rule.rule_key === 'smoke') {
          nextRule.threshold_value = alarmThresholds.smoke
        }
        return nextRule
      })
    }

    async function saveAlarmConfig() {
      try {
        const res = await postJson('/api/alarm-config', {
          rules: buildAlarmRules()
        })
        alarmState.rules = (res.data && res.data.rules) || []
        showToast(res.msg || '阈值已保存', 'blue')
        fetchAlarmList()
      } catch (error) {
        showToast(getErrorMessage(error, '阈值保存失败'), 'blue')
      }
    }

    function showAlarmPopup(newItems, activeItems) {
      let sourceItems = newItems
      if (!sourceItems.length && !state.activeAlarmToastShown && activeItems.length) {
        sourceItems = activeItems
      }
      if (!sourceItems.length) {
        return
      }
      state.activeAlarmToastShown = true
      showAlarmToast(sourceItems.map((item) => `${item.alarm_id || '--'} ${item.rule_name || '--'}报警`).join('；'), 'red')
    }

    async function processAlarm(logId) {
      try {
        const res = await postJson('/api/alarm-process', { log_id: logId })
        const current = (res.data && res.data.current) || {}
        alarmState.items = alarmState.items.map((item) => item.log_id === logId ? { ...item, ...current } : item)
        if (alarmDetail.visible && alarmDetail.current.log_id === logId) {
          alarmDetail.current = current
        }
      } catch (error) {
        showToast(getErrorMessage(error, '处理告警失败'), 'blue')
      }
    }

    async function loadAlarmDetail(logId) {
      try {
        const res = await getJson('/api/alarm-detail', { log_id: logId })
        alarmDetail.current = (res.data && res.data.current) || {}
        alarmDetail.history = (res.data && res.data.history) || []
        alarmDetail.visible = true
      } catch (error) {
        showToast(getErrorMessage(error, '获取告警详情失败'), 'blue')
      }
    }

    function getAlarmLevelClass(level) {
      if (level === '紧急') {
        return 'alarm_level_emergency'
      }
      if (level === '重要') {
        return 'alarm_level_important'
      }
      if (level === '次要') {
        return 'alarm_level_minor'
      }
      return 'alarm_level_notice'
    }

    function changeAlarmPage(step) {
      alarmState.pageIndex += step
      if (alarmState.pageIndex < 1) {
        alarmState.pageIndex = 1
      }
      if (alarmState.pageIndex > alarmTotalPages.value) {
        alarmState.pageIndex = alarmTotalPages.value
      }
    }

    function resetDeviceForm() {
      Object.assign(deviceForm, createEmptyDeviceForm())
    }

    function fillDeviceForm(device) {
      resetDeviceForm()
      if (!device) {
        return
      }
      const raw = device.raw || {}
      deviceForm.record_id = raw.record_id || device.record_id || ''
      deviceForm.display_name = raw.display_name || device.name || ''
      deviceForm.ip = raw.ip || device.ip || ''
      deviceForm.start_success_count = String(raw.start_success_count ?? getStartCount(device) ?? 1)
      deviceForm.slot_index = raw.slot_index !== undefined && raw.slot_index !== null && raw.slot_index !== '' ? String(raw.slot_index) : String(device.slot_index || '')
      deviceForm.onenet_device_name = raw.onenet_device_name || device.device_name || ''
      deviceForm.product_id = raw.product_id || ''
      deviceForm.user_id = raw.user_id || ''
      deviceForm.access_key = raw.access_key || ''
      deviceForm.auth_version = raw.auth_version || '2020-05-29'
      deviceForm.device_secret = raw.device_secret || ''
      deviceForm.device_id = raw.device_id || device.id || ''
      deviceForm.notes = raw.notes || ''
    }

    function openModal(mode, device = null) {
      modal.visible = true
      modal.mode = mode
      if (mode === 'delete') {
        modal.editingRecordId = ''
        modal.deleteRecordId = device?.record_id || state.devices[0]?.record_id || ''
        return
      }
      if (mode === 'edit') {
        modal.editingRecordId = device?.record_id || ''
        fillDeviceForm(device)
        return
      }
      modal.editingRecordId = ''
      resetDeviceForm()
      if (device && device.slot_index) {
        deviceForm.slot_index = String(device.slot_index)
      }
    }

    function closeModal() {
      modal.visible = false
      modal.editingRecordId = ''
      modal.deleteRecordId = ''
      resetDeviceForm()
    }

    function buildDevicePayload() {
      return {
        record_id: deviceForm.record_id,
        display_name: deviceForm.display_name,
        ip: deviceForm.ip,
        start_success_count: deviceForm.start_success_count,
        slot_index: deviceForm.slot_index,
        onenet_device_name: deviceForm.onenet_device_name,
        product_id: deviceForm.product_id,
        user_id: deviceForm.user_id,
        access_key: deviceForm.access_key,
        auth_version: deviceForm.auth_version,
        device_secret: deviceForm.device_secret,
        device_id: deviceForm.device_id,
        notes: deviceForm.notes
      }
    }

    async function submitModal() {
      if (modal.mode === 'delete') {
        await submitDeleteDevice()
        return
      }
      await submitSaveDevice()
    }

    async function submitSaveDevice() {
      const isEdit = modal.mode === 'edit' && modal.editingRecordId
      try {
        const res = isEdit
          ? await putJson(`/api/devices/${encodeURIComponent(modal.editingRecordId)}`, buildDevicePayload())
          : await postJson('/api/devices', buildDevicePayload())
        closeModal()
        showToast(res.msg || (isEdit ? '设备已更新' : '设备已保存'), (res.data && res.data.storage && res.data.storage.toast_color) || 'blue')
        await fetchMetrics()
        await fetchDevices({ silentStorageStatus: true })
        if (isEdit) {
          const index = state.devices.findIndex((item) => item.record_id === modal.editingRecordId)
          state.selectedIndex = index >= 0 ? index : 0
        } else {
          state.selectedIndex = state.devices.length ? state.devices.length - 1 : 0
        }
        await syncCurrentDevice()
      } catch (error) {
        showToast(getErrorMessage(error, isEdit ? '修改设备失败' : '新增设备失败'), 'blue')
      }
    }

    async function submitDeleteDevice() {
      if (!modal.deleteRecordId) {
        showToast('请先选择需要删减的设备', 'blue')
        return
      }
      try {
        const res = await deleteJson(`/api/devices/${encodeURIComponent(modal.deleteRecordId)}`)
        closeModal()
        state.selectedIndex = 0
        showToast(res.msg || '设备已删减', (res.data && res.data.storage && res.data.storage.toast_color) || 'blue')
        await fetchMetrics()
        await fetchDevices({ silentStorageStatus: true })
      } catch (error) {
        showToast(getErrorMessage(error, '删减设备失败'), 'blue')
      }
    }

    async function refreshAll() {
      await fetchMetrics()
      await Promise.all([
        fetchDevices({ silentStorageStatus: true }),
        fetchStatusTrend(),
        fetchWeather(),
        fetchAlarmList()
      ])
    }

    function startPolling() {
      if (state.pollTimerId) {
        clearInterval(state.pollTimerId)
      }
      state.pollTimerId = setInterval(() => {
        refreshAll()
      }, 30000)
    }

    async function enableForceExcelMode() {
      if (state.forceExcelMode) {
        return
      }
      state.forceExcelMode = true
      showToast('已切换本地数据模式', 'blue')
      await refreshAll()
    }

    function handleResize() {
      resizeCharts()
    }

    onMounted(async () => {
      initCharts()
      window.addEventListener('resize', handleResize)
      await fetchAlarmConfig()
      await refreshAll()
      startPolling()
    })

    onBeforeUnmount(() => {
      if (state.pollTimerId) {
        clearInterval(state.pollTimerId)
      }
      if (toast.timerId) {
        clearTimeout(toast.timerId)
      }
      window.removeEventListener('resize', handleResize)
      disposeCharts()
    })

    return {
      alarmDetail,
      alarmPageItems,
      alarmState,
      alarmThresholds,
      alarmToast,
      alarmTotalPages,
      changeAlarmPage,
      closeModal,
      currentPanel,
      deviceForm,
      deviceToastClass,
      enableForceExcelMode,
      getAlarmLevelClass,
      goAppDemo,
      healthChartRef,
      loadAlarmDetail,
      metrics,
      modal,
      modalSubmitText,
      modalTitle,
      openModal,
      processAlarm,
      rcsSlots,
      refreshSelectedSlotDetail,
      saveAlarmConfig,
      selectedSlotDevice,
      selectedSlotIndex: state.selectedSlotIndex,
      selectedSlotInfo,
      selectedSlotState,
      selectedSlotTip,
      selectedSlotTitle,
      selectSlot,
      state,
      statusTrendChartRef,
      submitModal,
      switchView,
      toast,
      totalStarts,
      usageChartRef,
      weatherChartRef
    }
  }
}
</script>
