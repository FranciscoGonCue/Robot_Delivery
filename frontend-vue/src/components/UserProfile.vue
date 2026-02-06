<template>
  <div class="profile-modal-overlay" @click="$emit('close')">
    <div class="profile-modal" @click.stop>
      <div class="profile-header">
        <h2>My Profile</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <div class="profile-content">
        <!-- User Info Section -->
        <div class="profile-section">
          <h3>User Information</h3>
          <div class="info-row">
            <label>Username:</label>
            <span class="value">{{ user?.username }}</span>
          </div>
          <div class="info-row">
            <label>Email:</label>
            <div class="email-info">
              <span class="value">{{ user?.email || '(no email)' }}</span>
              <span v-if="user?.is_verified" class="badge verified">✓ Verified</span>
              <span v-else-if="user?.email" class="badge unverified">⚠ Not Verified</span>
            </div>
          </div>
        </div>

        <!-- Email Verification Section -->
        <div v-if="user?.email && !user?.is_verified" class="profile-section verification-section">
          <h3>Email Verification</h3>
          <p class="info-text">
            Your email is not verified. Verify your email for better security.
          </p>
          <button 
            @click="handleRequestVerification" 
            class="btn btn-primary"
            :disabled="sendingVerification"
          >
            {{ sendingVerification ? 'Sending...' : 'Send Verification Email' }}
          </button>
          <div v-if="verificationMessage" class="success-message">
            {{ verificationMessage }}
          </div>
          <div v-if="verificationError" class="error-message">
            {{ verificationError }}
          </div>
        </div>

        <!-- Update Email Section -->
        <div class="profile-section">
          <h3>Update Email</h3>
          <form @submit.prevent="handleUpdateEmail">
            <div class="form-group">
              <label for="new-email">New Email:</label>
              <input
                id="new-email"
                v-model="newEmail"
                type="email"
                placeholder="new@example.com"
              />
              <small class="help-text">
                If you change your email, you will need to verify it again
              </small>
            </div>
            <button type="submit" class="btn btn-secondary" :disabled="updatingEmail || !newEmail">
              {{ updatingEmail ? 'Updating...' : 'Update Email' }}
            </button>
          </form>
          <div v-if="emailUpdateMessage" class="success-message">
            {{ emailUpdateMessage }}
          </div>
          <div v-if="emailUpdateError" class="error-message">
            {{ emailUpdateError }}
          </div>
        </div>

        <!-- Change Password Section -->
        <div class="profile-section">
          <h3>Change Password</h3>
          <form @submit.prevent="handleChangePassword">
            <div class="form-group">
              <label for="current-password">Current Password:</label>
              <input
                id="current-password"
                v-model="passwordForm.current"
                type="password"
                placeholder="Current password"
                required
              />
            </div>
            <div class="form-group">
              <label for="new-password">New Password:</label>
              <input
                id="new-password"
                v-model="passwordForm.new"
                type="password"
                placeholder="New password (min. 6 characters)"
                required
              />
            </div>
            <div class="form-group">
              <label for="confirm-password">Confirm New Password:</label>
              <input
                id="confirm-password"
                v-model="passwordForm.confirm"
                type="password"
                placeholder="Confirm password"
                required
              />
            </div>
            <button type="submit" class="btn btn-secondary" :disabled="changingPassword">
              {{ changingPassword ? 'Changing...' : 'Change Password' }}
            </button>
          </form>
          <div v-if="passwordMessage" class="success-message">
            {{ passwordMessage }}
          </div>
          <div v-if="passwordError" class="error-message">
            {{ passwordError }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import apiClient from '../api/config'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'update-user'])

// Email verification
const sendingVerification = ref(false)
const verificationMessage = ref('')
const verificationError = ref('')

// Update email
const newEmail = ref('')
const updatingEmail = ref(false)
const emailUpdateMessage = ref('')
const emailUpdateError = ref('')

// Change password
const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})
const changingPassword = ref(false)
const passwordMessage = ref('')
const passwordError = ref('')

const handleRequestVerification = async () => {
  sendingVerification.value = true
  verificationMessage.value = ''
  verificationError.value = ''

  try {
    const response = await apiClient.post('/auth/profile/request-verification/', {
      frontend_url: window.location.origin
    })
    
    if (response.data.success) {
      verificationMessage.value = response.data.message
    } else {
      verificationError.value = response.data.error || response.data.message
    }
  } catch (error) {
    verificationError.value = error.response?.data?.error || 'Error sending verification email'
  } finally {
    sendingVerification.value = false
  }
}

const handleUpdateEmail = async () => {
  if (!newEmail.value) return
  
  updatingEmail.value = true
  emailUpdateMessage.value = ''
  emailUpdateError.value = ''

  try {
    const response = await apiClient.put('/auth/profile/update/', {
      email: newEmail.value,
      frontend_url: window.location.origin
    })
    
    if (response.data.success) {
      emailUpdateMessage.value = response.data.message + ' A verification email has been sent.'
      emit('update-user', response.data.user)
      newEmail.value = ''
      
      // Clear message after 5 seconds
      setTimeout(() => {
        emailUpdateMessage.value = ''
      }, 5000)
    } else {
      emailUpdateError.value = response.data.error
    }
  } catch (error) {
    emailUpdateError.value = error.response?.data?.error || 'Error updating email'
  } finally {
    updatingEmail.value = false
  }
}

const handleChangePassword = async () => {
  passwordMessage.value = ''
  passwordError.value = ''

  // Validate passwords match
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    passwordError.value = 'Passwords do not match'
    return
  }

  // Validate password length
  if (passwordForm.value.new.length < 6) {
    passwordError.value = 'Password must be at least 6 characters long'
    return
  }

  changingPassword.value = true

  try {
    const response = await apiClient.post('/auth/profile/change-password/', {
      current_password: passwordForm.value.current,
      new_password: passwordForm.value.new
    })
    
    if (response.data.success) {
      passwordMessage.value = response.data.message
      passwordForm.value = { current: '', new: '', confirm: '' }
      
      // Clear message after 5 seconds
      setTimeout(() => {
        passwordMessage.value = ''
      }, 5000)
    } else {
      passwordError.value = response.data.error
    }
  } catch (error) {
    passwordError.value = error.response?.data?.error || 'Error changing password'
  } finally {
    changingPassword.value = false
  }
}
</script>

<style scoped>
.profile-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.profile-modal {
  background: white;
  border-radius: 15px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 2px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 15px 15px 0 0;
}

.profile-header h2 {
  margin: 0;
  font-size: 24px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.profile-content {
  padding: 30px;
}

.profile-section {
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid #e0e0e0;
}

.profile-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.profile-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-row label {
  font-weight: 600;
  color: #555;
  min-width: 100px;
}

.info-row .value {
  color: #333;
}

.email-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge.verified {
  background: #d4edda;
  color: #155724;
}

.badge.unverified {
  background: #fff3cd;
  color: #856404;
}

.verification-section {
  background: #fff9e6;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ffc107;
}

.info-text {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 600;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.help-text {
  display: block;
  margin-top: 5px;
  color: #888;
  font-size: 12px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
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

.btn-secondary {
  background: #28a745;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  font-size: 14px;
  border: 1px solid #c3e6cb;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  font-size: 14px;
  border: 1px solid #f5c6cb;
}

/* Scrollbar styling */
.profile-modal::-webkit-scrollbar {
  width: 8px;
}

.profile-modal::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.profile-modal::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.profile-modal::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
