function buildQueryString(query) {
  const params = new URLSearchParams()

  Object.entries(query || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return
    }
    params.set(key, String(value))
  })

  const text = params.toString()
  return text ? `?${text}` : ''
}

async function parseResponse(response) {
  const text = await response.text()
  let payload = {}

  try {
    payload = text ? JSON.parse(text) : {}
  } catch (error) {
    payload = { code: response.ok ? 0 : response.status, msg: text || '响应解析失败' }
  }

  if (response.status === 401) {
    window.location.href = '/login.html'
    throw payload
  }

  if (!response.ok || payload.code !== 0) {
    throw payload
  }

  return payload
}

export async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    credentials: 'same-origin',
    ...options
  })
  return parseResponse(response)
}

export function getJson(url, query = {}) {
  return requestJson(`${url}${buildQueryString(query)}`)
}

export function postJson(url, body = {}, query = {}) {
  return requestJson(`${url}${buildQueryString(query)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })
}

export function putJson(url, body = {}, query = {}) {
  return requestJson(`${url}${buildQueryString(query)}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })
}

export function deleteJson(url, query = {}) {
  return requestJson(`${url}${buildQueryString(query)}`, {
    method: 'DELETE'
  })
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
