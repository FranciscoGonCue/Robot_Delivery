<template>
  <div class="verification-container">
    <div class="verification-box">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <h2>{{ t('auth.verifying', 'Verifying your email...') }}</h2>
        <p>{{ t('common.pleaseWait', 'Please wait a moment') }}</p>
      </div>
      
      <div v-else-if="success" class="success-state">
        <div class="icon success-icon">✓</div>
        <h2>{{ t('auth.emailVerified', 'Email Verified!') }}</h2>
        <p class="message">{{ message }}</p>
        <p class="sub-message">{{ t('auth.canLogin', 'You can now log in with your account') }}</p>
        <button @click="goToLogin" class="btn btn-primary">
          {{ t('auth.goToLogin', 'Go to Login') }}
        </button>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="icon error-icon">✕</div>
        <h2>{{ t('auth.verificationError', 'Verification Error') }}</h2>
        <p class="message error">{{ message }}</p>
        
        <div v-if="expired" class="expired-section">
          <p>{{ t('auth.linkExpired', 'The verification link has expired.') }}</p>
          <p>{{ t('auth.wantNewLink', 'Do you want to receive a new link?') }}</p>
          <button @click="showResendForm = true" class="btn btn-primary">
            {{ t('auth.resendVerification', 'Resend Verification Email') }}
          </button>
        </div>
        
        <div v-if="showResendForm" class="resend-form">
          <h3>{{ t('auth.resendVerification') }}</h3>
          <form @submit.prevent="handleResendVerification">
            <div class="form-group">
              <label for="email">{{ t('auth.emailOrUsername', 'Email or Username') }}</label>
              <input
                id="email"
                v-model="resendEmail"
                type="text"
                :placeholder="t('auth.emailOrUsername')"
                required
              />
            </div>
            <button type="submit" class="btn btn-primary" :disabled="resending">
              {{ resending ? t('common.loading') : t('auth.resendEmail', 'Resend Email') }}
            </button>
          </form>
          <div v-if="resendSuccess" class="success-message">
            {{ t('auth.verificationSent', 'Verification email sent successfully') }}
          </div>
          <div v-if="resendError" class="error-message">
            {{ resendError }}
          </div>
        </div>
        
        <button @click="goToLogin" class="btn btn-secondary" style="margin-top: 20px;">
          {{ t('auth.backToLogin', 'Back to Login') }}
        </button>
      </div>
      
      <div v-else-if="alreadyVerified" class="info-state">
        <div class="icon info-icon">ℹ</div>
        <h2>{{ t('auth.alreadyVerified', 'Email Already Verified') }}</h2>
        <p class="message">{{ t('auth.alreadyVerifiedMessage', 'Your account has already been verified') }}</p>
        <button @click="goToLogin" class="btn btn-primary">
          {{ t('auth.goToLogin') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { verifyEmail, resendVerificationEmail } from '../api/auth'

const { t } = useI18n()
const loading = ref(true)
const success = ref(false)
const error = ref(false)
const message = ref('')
const expired = ref(false)
const alreadyVerified = ref(false)
const showResendForm = ref(false)
const resendEmail = ref('')
const resending = ref(false)
const resendSuccess = ref(false)
const resendError = ref('')

onMounted(async () => {
  // Get token from URL query parameters
  const urlParams = new URLSearchParams(window.location.search)
  const token = urlParams.get('token')
  
  if (!token) {
    error.value = true
    message.value = 'Token de verificación no proporcionado'
    loading.value = false
    return
  }
  
  await performVerification(token)
})

const performVerification = async (token) => {
  try {
    const result = await verifyEmail(token)
    
    if (result.success) {
      if (result.already_verified) {
        alreadyVerified.value = true
        message.value = result.message
      } else {
        success.value = true
        message.value = result.message
      }
    } else {
      error.value = true
      message.value = result.message || result.error
      expired.value = result.expired || false
    }
  } catch (err) {
    error.value = true
    message.value = 'Error al verificar el email'
    console.error('Verification error:', err)
  } finally {
    loading.value = false
  }
}

const handleResendVerification = async () => {
  resending.value = true
  resendError.value = ''
  resendSuccess.value = false
  
  try {
    const result = await resendVerificationEmail(resendEmail.value)
    
    if (result.success) {
      resendSuccess.value = true
      resendEmail.value = ''
      setTimeout(() => {
        showResendForm.value = false
        resendSuccess.value = false
      }, 3000)
    } else {
      resendError.value = result.error || result.message
    }
  } catch (err) {
    resendError.value = 'Error al reenviar el email'
    console.error('Resend error:', err)
  } finally {
    resending.value = false
  }
}

const goToLogin = () => {
  // Clear URL parameters and reload to show login
  window.history.pushState({}, '', '/')
  window.location.reload()
}
</script>

<style scoped>
.verification-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.verification-box {
  background: white;
  border-radius: 15px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 50px;
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.loading-state, .success-state, .error-state, .info-state {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

.success-icon {
  color: #28a745;
}

.error-icon {
  color: #dc3545;
}

.info-icon {
  color: #17a2b8;
}

h2 {
  color: #333;
  margin-bottom: 15px;
  font-size: 28px;
}

.message {
  color: #555;
  font-size: 16px;
  margin-bottom: 10px;
}

.message.error {
  color: #dc3545;
}

.sub-message {
  color: #777;
  font-size: 14px;
  margin-bottom: 30px;
}

.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin: 5px;
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

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.expired-section {
  margin: 20px 0;
  padding: 20px;
  background: #fff3cd;
  border-radius: 8px;
  border: 1px solid #ffc107;
}

.expired-section p {
  color: #856404;
  margin: 5px 0;
}

.resend-form {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.resend-form h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 18px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
  text-align: left;
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

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  font-size: 14px;
  border: 1px solid #c3e6cb;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  font-size: 14px;
  border: 1px solid #f5c6cb;
}
</style>
