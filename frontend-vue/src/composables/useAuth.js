import { ref, computed } from 'vue'
import { authService } from '../api/services'

const accessToken = ref(localStorage.getItem('access_token') || null)
const refreshToken = ref(localStorage.getItem('refresh_token') || null)
const user = ref(null)

// Load user from localStorage if exists
const storedUser = localStorage.getItem('user')
if (storedUser) {
  try {
    user.value = JSON.parse(storedUser)
  } catch (e) {
    console.error('Error parsing stored user:', e)
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => !!accessToken.value)

  const setTokens = (access, refresh) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const clearAuth = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  const register = async (username, email, password) => {
    try {
      const response = await authService.register({ username, email, password })
      
      if (response.success) {
        return { 
          success: true, 
          message: response.message,
          data: response 
        }
      } else {
        return {
          success: false,
          error: response.error || 'Registration failed'
        }
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Registration failed'
      }
    }
  }

  const login = async (username, password) => {
    try {
      const response = await authService.login({ username, password })
      
      if (response.success) {
        setTokens(response.access, response.refresh)
        setUser(response.user)
        return { success: true, user: response.user }
      } else {
        return { 
          success: false, 
          error: response.error || 'Login failed',
          message: response.message || '',
          requires_verification: response.requires_verification || false
        }
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
        message: error.response?.data?.message || '',
        requires_verification: error.response?.data?.requires_verification || false
      }
    }
  }

  const logout = async () => {
    try {
      if (refreshToken.value) {
        await authService.logout({ refresh: refreshToken.value })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearAuth()
    }
  }

  const getCurrentUser = async () => {
    try {
      const userData = await authService.getCurrentUser()
      setUser(userData)
      return { success: true, user: userData }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get user'
      }
    }
  }

  return {
    // State
    accessToken,
    refreshToken,
    user,
    isAuthenticated,

    // Methods
    register,
    login,
    logout,
    getCurrentUser,
    setTokens,
    clearAuth
  }
}
