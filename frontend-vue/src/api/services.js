import apiClient from './config'

// Authentication API
export const authService = {
  register: (data) => apiClient.post('/auth/register/', {
    ...data,
    frontend_url: window.location.origin
  }).then(res => res.data).catch(err => ({
    success: false,
    error: err.response?.data?.error || 'Registration failed'
  })),
  
  login: (data) => apiClient.post('/auth/login/', data).then(res => res.data).catch(err => ({
    success: false,
    error: err.response?.data?.error || 'Login failed',
    message: err.response?.data?.message || '',
    requires_verification: err.response?.data?.requires_verification || false
  })),
  
  logout: (data) => apiClient.post('/auth/logout/', data).then(res => res.data),
  getCurrentUser: () => apiClient.get('/auth/user/').then(res => res.data),
  refreshToken: (refresh) => apiClient.post('/auth/token/refresh/', { refresh }).then(res => res.data),
  
  verifyEmail: (token) => apiClient.get(`/auth/verify-email/?token=${token}`).then(res => res.data).catch(err => ({
    success: false,
    error: err.response?.data?.error || 'Verification failed',
    message: err.response?.data?.message || '',
    expired: err.response?.data?.expired || false
  })),
  
  resendVerification: (identifier) => {
    const isEmail = identifier.includes('@')
    const payload = isEmail 
      ? { email: identifier, frontend_url: window.location.origin }
      : { username: identifier, frontend_url: window.location.origin }
    
    return apiClient.post('/auth/resend-verification/', payload).then(res => res.data).catch(err => ({
      success: false,
      error: err.response?.data?.error || 'Failed to resend verification email',
      message: err.response?.data?.message || ''
    }))
  }
}

// Targets API (formerly Positions)
export const targetsAPI = {
  getAll: () => apiClient.get('/targets/')
}

// Robot API
export const robotAPI = {
  call: (uuid, pointId) => apiClient.post('/robot/call/', { uuid, pointId })
}

// Token API (Keenon API token, not JWT)
export const tokenAPI = {
  refresh: () => apiClient.post('/token/refresh/')
}

// Endpoints API
export const endpointsAPI = {
  getAll: () => apiClient.get('/endpoints/'),
  create: (data) => apiClient.post('/endpoints/create/', data),
  update: (id, data) => apiClient.put(`/endpoints/${id}/update/`, data),
  execute: (id) => apiClient.post(`/endpoints/${id}/execute/`)
}
