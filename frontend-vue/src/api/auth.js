import apiClient from './config'

// Authentication API
export const loginUser = async (username, password) => {
  try {
    const response = await apiClient.post('/auth/login/', { username, password })
    return response.data
  } catch (error) {
    console.error('Login error:', error)
    return { 
      success: false, 
      error: error.response?.data?.error || 'Login failed',
      message: error.response?.data?.message || '',
      requires_verification: error.response?.data?.requires_verification || false
    }
  }
}

export const registerUser = async (username, email, password) => {
  try {
    const response = await apiClient.post('/auth/register/', { 
      username, 
      email, 
      password,
      frontend_url: window.location.origin
    })
    return response.data
  } catch (error) {
    console.error('Register error:', error)
    return { 
      success: false, 
      error: error.response?.data?.error || 'Registration failed' 
    }
  }
}

export const verifyEmail = async (token) => {
  try {
    const response = await apiClient.get(`/auth/verify-email/?token=${token}`)
    return response.data
  } catch (error) {
    console.error('Verification error:', error)
    return { 
      success: false, 
      error: error.response?.data?.error || 'Verification failed',
      message: error.response?.data?.message || '',
      expired: error.response?.data?.expired || false
    }
  }
}

export const resendVerificationEmail = async (identifier) => {
  try {
    // Check if identifier is an email or username
    const isEmail = identifier.includes('@')
    const payload = isEmail 
      ? { email: identifier, frontend_url: window.location.origin }
      : { username: identifier, frontend_url: window.location.origin }
    
    const response = await apiClient.post('/auth/resend-verification/', payload)
    return response.data
  } catch (error) {
    console.error('Resend verification error:', error)
    return { 
      success: false, 
      error: error.response?.data?.error || 'Failed to resend verification email',
      message: error.response?.data?.message || ''
    }
  }
}

export const logoutUser = async (refreshToken) => {
  try {
    const response = await apiClient.post('/auth/logout/', { refresh: refreshToken })
    return response.data
  } catch (error) {
    console.error('Logout error:', error)
    return { success: false, error: error.response?.data?.error || 'Logout failed' }
  }
}

export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/auth/user/')
    return response.data
  } catch (error) {
    console.error('Get user error:', error)
    return null
  }
}
