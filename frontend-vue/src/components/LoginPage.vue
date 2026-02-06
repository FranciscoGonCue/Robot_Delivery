<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="title">Robot Delivery Control</h1>
      
      <div v-if="!showRegister" class="form-container">
        <h2>Login</h2>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              v-model="loginForm.username"
              type="text"
              placeholder="Enter username"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="loginForm.password"
              type="password"
              placeholder="Enter password"
              required
            />
          </div>
          
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        
        <div class="toggle-form">
          <p>Don't have an account?</p>
          <button @click="toggleForm" class="btn btn-link">Register</button>
        </div>
      </div>
      
      <div v-else class="form-container">
        <h2>Register</h2>
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label for="reg-username">Username</label>
            <input
              id="reg-username"
              v-model="registerForm.username"
              type="text"
              placeholder="Choose a username"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="reg-email">Email (opcional)</label>
            <input
              id="reg-email"
              v-model="registerForm.email"
              type="email"
              placeholder="Enter email"
            />
            <small class="help-text">Recomendado para verificación y recuperación de cuenta</small>
          </div>
          
          <div class="form-group">
            <label for="reg-password">Password</label>
            <input
              id="reg-password"
              v-model="registerForm.password"
              type="password"
              placeholder="Choose a password"
              required
            />
          </div>
          
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
          
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Registering...' : 'Register' }}
          </button>
        </form>
        
        <div class="toggle-form">
          <p>Already have an account?</p>
          <button @click="toggleForm" class="btn btn-link">Login</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'

const emit = defineEmits(['login-success'])

const { login, register } = useAuth()

const showRegister = ref(false)
const loading = ref(false)
const error = ref('')
const successMessage = ref('')

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: ''
})

const toggleForm = () => {
  showRegister.value = !showRegister.value
  error.value = ''
  successMessage.value = ''
}

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await login(loginForm.value.username, loginForm.value.password)
    
    if (result.success) {
      emit('login-success')
    } else {
      error.value = result.error || result.message || 'Login failed'
    }
  } catch (err) {
    error.value = 'An unexpected error occurred'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  successMessage.value = ''
  
  try {
    const result = await register(
      registerForm.value.username,
      registerForm.value.email,
      registerForm.value.password
    )
    
    if (result.success) {
      successMessage.value = result.message || 'Registration successful! You can now login.'
      setTimeout(() => {
        showRegister.value = false
        loginForm.value.username = registerForm.value.username
        registerForm.value = { username: '', email: '', password: '' }
        successMessage.value = ''
      }, 3000)
    } else {
      error.value = result.error || 'Registration failed'
    }
  } catch (err) {
    error.value = 'An unexpected error occurred'
    console.error('Registration error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4a90e2;
  padding: 20px;
}

.login-box {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 24px;
}

.form-container h2 {
  text-align: center;
  color: #555;
  margin-bottom: 20px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-link {
  background: none;
  color: #667eea;
  padding: 5px 10px;
  font-size: 14px;
}

.btn-link:hover {
  text-decoration: underline;
}

.toggle-form {
  margin-top: 20px;
  text-align: center;
}

.toggle-form p {
  color: #666;
  margin-bottom: 10px;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 15px;
  font-size: 14px;
  text-align: center;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 15px;
  font-size: 14px;
  text-align: center;
  border: 1px solid #c3e6cb;
}

.help-text {
  display: block;
  margin-top: 5px;
  color: #888;
  font-size: 12px;
}
</style>
