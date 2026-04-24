import axios from 'axios'

const apiClient = axios.create({
  withCredentials: true
})

apiClient.interceptors.response.use(
  (response) => {
    const payload = response.data || {}
    if (payload.code !== 0) {
      return Promise.reject(payload)
    }
    return payload
  },
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        window.location.href = '/login.html'
      }
      const payload = error.response.data || {}
      return Promise.reject({
        code: payload.code || error.response.status,
        msg: payload.msg || '请求失败'
      })
    }
    return Promise.reject({ code: -1, msg: error.message || '网络错误' })
  }
)

function cleanQuery(query) {
  const cleaned = {}
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      cleaned[key] = value
    }
  })
  return cleaned
}

export function getJson(url, query = {}) {
  return apiClient.get(url, { params: cleanQuery(query) })
}

export function postJson(url, body = {}, query = {}) {
  return apiClient.post(url, body, { params: cleanQuery(query) })
}

export function putJson(url, body = {}, query = {}) {
  return apiClient.put(url, body, { params: cleanQuery(query) })
}

export function deleteJson(url, query = {}) {
  return apiClient.delete(url, { params: cleanQuery(query) })
}

export function getErrorMessage(error, fallbackText) {
  if (error && typeof error.msg === 'string' && error.msg.trim()) {
    return error.msg
  }
  if (error instanceof Error && error.message) {
    return error.message
  }
  return fallbackText
}
