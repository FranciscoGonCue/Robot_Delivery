<template>
  <div class="mapping-container">
    <div class="mapping-header">
      <h1>{{ t('mapping.title') }}</h1>
      <p class="subtitle">{{ t('mapping.subtitle') }}</p>
    </div>

    <div class="mapping-content">
      <div class="ip-input-section">
        <label for="robot-ip" class="input-label">
          {{ t('mapping.ipLabel') }}
          <AsteriskIndicator />
        </label>
        <div class="input-wrapper">
          <input
            id="robot-ip"
            v-model="robotIp"
            type="text"
            placeholder="ej: 192.168.25.52:8080"
            class="ip-input"
            @input="handleIpChange"
          />
          <button 
            class="check-btn"
            :disabled="!robotIp || isChecking"
            @click="checkAvailability"
          >
            {{ isChecking ? t('mapping.checking') : t('mapping.checkButton') }}
          </button>
        </div>
        <p class="input-help">Introduce la dirección IP y puerto del robot Keenon (ej: 192.168.25.52:8080)</p>
      </div>

      <!-- Status Messages -->
      <div v-if="checkStatus" class="status-section">
        <div v-if="checkStatus === 'available'" class="status-message success">
          <span class="status-icon">✓</span>
          <span>{{ t('mapping.available') }}</span>
        </div>
        <div v-else-if="checkStatus === 'unavailable'" class="status-message error">
          <span class="status-icon">✗</span>
          <span>{{ t('mapping.unavailable') }}</span>
        </div>
        <div v-else-if="checkStatus === 'error'" class="status-message error">
          <span class="status-icon">⚠</span>
          <span>{{ t('mapping.error') }}</span>
        </div>
      </div>

      <!-- Action Button -->
      <div class="action-section">
        <button
          class="open-mapping-btn"
          :class="{ enabled: isAvailable }"
          :disabled="!isAvailable"
          @click="openMappingInterface"
        >
          <span class="btn-icon">🗺️</span>
          <span>{{ t('mapping.openButton') }}</span>
        </button>
        
        <p v-if="!isAvailable && checkStatus" class="warning-message">
          {{ t('mapping.warningMessage') }}
        </p>
      </div>

      <!-- Instructions -->
      <div class="instructions-section">
        <h3>{{ t('mapping.instructionsTitle') }}</h3>
        <ol class="instructions-list">
          <li>{{ t('mapping.instruction1') }}</li>
          <li>{{ t('mapping.instruction2') }}</li>
          <li>{{ t('mapping.instruction3') }}</li>
          <li>{{ t('mapping.instruction4') }}</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AsteriskIndicator from './AsteriskIndicator.vue'
import { useNotifications } from '../composables/useNotifications'

const { t } = useI18n()
const { error, success } = useNotifications()

// State
const robotIp = ref('')
const isChecking = ref(false)
const checkStatus = ref(null) // 'available', 'unavailable', 'error'

// Computed
const isAvailable = computed(() => checkStatus.value === 'available')
const mappingUrl = computed(() => {
  if (!robotIp.value) return ''
  return `http://${robotIp.value}/#/install`
})

// Methods
const handleIpChange = () => {
  // Reset status when user changes IP
  checkStatus.value = null
}

const validateIp = (ip) => {
  // IP validation with optional port (IPv4:port)
  const ipPattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d{1,5})?$/
  return ipPattern.test(ip)
}

const checkAvailability = async () => {
  if (!robotIp.value.trim()) {
    error('Por favor, introduce una dirección IP')
    return
  }

  // Validate IP format
  if (!validateIp(robotIp.value.trim())) {
    error('Por favor, introduce una dirección IP válida (ej: 192.168.25.52:8080)')
    return
  }

  isChecking.value = true
  checkStatus.value = null

  try {
    const url = mappingUrl.value
    
    // Try to fetch the URL with a timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout

    const response = await fetch(url, {
      method: 'HEAD',
      mode: 'no-cors', // Allow cross-origin requests
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    // With no-cors, we can't read the response, but if it doesn't throw, the server is reachable
    checkStatus.value = 'available'
    success(t('mapping.connectionSuccess'))
  } catch (err) {
    if (err.name === 'AbortError') {
      checkStatus.value = 'unavailable'
      error(t('mapping.timeout'))
    } else {
      // Try alternative method: create an image element to test connectivity
      await checkWithImage()
    }
  } finally {
    isChecking.value = false
  }
}

// Alternative check method using image loading
const checkWithImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const timeout = setTimeout(() => {
      img.src = ''
      checkStatus.value = 'unavailable'
      resolve()
    }, 5000)

    img.onload = () => {
      clearTimeout(timeout)
      checkStatus.value = 'available'
      success(t('mapping.connectionSuccess'))
      resolve()
    }

    img.onerror = () => {
      clearTimeout(timeout)
      checkStatus.value = 'unavailable'
      resolve()
    }

    // Try to load favicon or any small resource
    img.src = `http://${robotIp.value}/favicon.ico?t=${Date.now()}`
  })
}

const openMappingInterface = () => {
  if (!isAvailable.value) return
  
  window.open(mappingUrl.value, '_blank')
  success(t('mapping.opened'))
}
</script>

<style scoped>
.mapping-container {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.mapping-header {
  margin-bottom: 2rem;
}

.mapping-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1rem;
}

.mapping-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ip-input-section {
  margin-bottom: 2rem;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.ip-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.ip-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.check-btn {
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.check-btn:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.check-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.6;
}

.input-help {
  color: #95a5a6;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.status-section {
  margin-bottom: 2rem;
}

.status-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  font-weight: 500;
}

.status-message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.status-icon {
  font-size: 1.25rem;
}

.action-section {
  margin-bottom: 2rem;
  text-align: center;
}

.open-mapping-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: not-allowed;
  transition: all 0.3s ease;
  opacity: 0.5;
}

.open-mapping-btn.enabled {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  cursor: pointer;
  opacity: 1;
}

.open-mapping-btn.enabled:hover {
  background: linear-gradient(135deg, #229954, #27ae60);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(46, 204, 113, 0.3);
}

.btn-icon {
  font-size: 1.5rem;
}

.warning-message {
  margin-top: 1rem;
  color: #e74c3c;
  font-weight: 500;
  font-size: 0.95rem;
}

.instructions-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.instructions-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.125rem;
}

.instructions-list {
  margin-left: 1.5rem;
  color: #555;
  line-height: 1.8;
}

.instructions-list li {
  margin-bottom: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .mapping-container {
    padding: 1rem;
  }

  .mapping-content {
    padding: 1.5rem;
  }

  .input-wrapper {
    flex-direction: column;
  }

  .check-btn {
    width: 100%;
  }

  .open-mapping-btn {
    width: 100%;
  }
}
</style>
