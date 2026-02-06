<template>
  <div class="robot-page">
    <div class="page-header">
      <h1>🤖 Robot Control</h1>
      <p>Real-time information from Keenon robot</p>
      <button @click="loadRobotData" class="refresh-btn" :disabled="loading">
        <span class="icon">🔄</span>
        <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !robotData" class="loading-container">
      <div class="spinner"></div>
      <p>Loading robot information...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>Error Loading Data</h3>
      <p>{{ error }}</p>
      <button @click="loadRobotData" class="btn-retry">Retry</button>
    </div>

    <!-- Robot Data -->
    <div v-else-if="robotData" class="robot-content">
      <div class="robot-grid">
        <!-- Status Card -->
        <div class="card status-card">
          <div class="card-header">
            <h2>⚡ Robot Status</h2>
            <span class="status-badge" :class="{ online: robotData.onlineStatus === 1 }">
              {{ robotData.onlineStatus === 1 ? '🟢 Online' : '🔴 Offline' }}
            </span>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">Robot ID:</span>
              <span class="info-value">{{ robotData.robotId }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Robot Code:</span>
              <span class="info-value code">{{ robotData.robotCode }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Name:</span>
              <span class="info-value">{{ robotData.robotName || 'No name' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Model:</span>
              <span class="info-value">{{ robotData.robotModel || 'Keenon' }}</span>
            </div>
          </div>
        </div>

        <!-- Battery Card -->
        <div class="card">
          <div class="card-header">
            <h2>🔋 Battery</h2>
          </div>
          <div class="card-body">
            <div class="battery-display">
              <div class="battery-percentage">{{ robotData.power }}%</div>
              <div class="battery-bar">
                <div 
                  class="battery-fill" 
                  :style="`width: ${robotData.power}%`"
                  :class="getBatteryClass(robotData.power)"
                ></div>
              </div>
              <div class="battery-status">
                {{ getBatteryStatus(robotData.power) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Location Card -->
        <div class="card">
          <div class="card-header">
            <h2>📍 Location</h2>
          </div>
          <div class="card-body">
            <div class="location-info">
              <div class="location-icon">🗺️</div>
              <div class="location-text">
                {{ robotData.city || 'Location not available' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Technical Info Card -->
        <div class="card">
          <div class="card-header">
            <h2>⚙️ Technical Information</h2>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">Manufacturing Code:</span>
              <span class="info-value">{{ robotData.mftCode }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">App Version:</span>
              <span class="info-value">{{ robotData.appVersion }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Connection Type:</span>
              <span class="info-value">
                {{ getOnlineType(robotData.onlineType) }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">Store ID:</span>
              <span class="info-value">C00001185</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Last Update -->
      <div class="last-update">
        Last update: {{ lastUpdateTime }}
      </div>
    </div>

    <!-- No Data State -->
    <div v-else class="no-data-container">
      <div class="no-data-icon">🤖</div>
      <h3>No Robot Data</h3>
      <p>No robot information found at this time</p>
      <button @click="loadRobotData" class="btn-retry">Load Data</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import apiClient from '../api/config'

// Estado
const robotData = ref(null)
const loading = ref(true)
const error = ref(null)
const lastUpdateTime = ref('')
let refreshInterval = null

// Cargar datos del robot
const loadRobotData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get('/robot/list/')
    
    if (response.data.success && response.data.data && response.data.data.length > 0) {
      // Tomar el primer robot de la lista
      robotData.value = response.data.data[0]
      lastUpdateTime.value = new Date().toLocaleTimeString('en-US')
    } else {
      error.value = 'No robots found in the store'
      robotData.value = null
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Error connecting to Keenon API'
    console.error('Error loading robot data:', err)
    robotData.value = null
  } finally {
    loading.value = false
  }
}

// Obtener clase de batería según nivel
const getBatteryClass = (power) => {
  if (power > 60) return 'high'
  if (power > 30) return 'medium'
  return 'low'
}

// Obtener estado de batería
const getBatteryStatus = (power) => {
  if (power > 80) return 'Excellent'
  if (power > 60) return 'Good'
  if (power > 30) return 'Medium'
  if (power > 15) return 'Low'
  return 'Critical'
}

// Obtener tipo de conexión
const getOnlineType = (type) => {
  const types = {
    1: 'WiFi',
    2: '4G/LTE',
    3: 'Ethernet'
  }
  return types[type] || `Tipo ${type}`
}

// Cargar al montar
onMounted(() => {
  loadRobotData()
  
  // Auto-refresh cada 5 minutos (300000ms = 5 minutos)
  refreshInterval = setInterval(() => {
    if (!loading.value) {
      loadRobotData()
    }
  }, 300000) // 5 minutos
})

// Limpiar intervalo al desmontar
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.robot-page {
  width: 100%;
  height: 100%;
  padding: 30px;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 32px;
}

.page-header p {
  margin: 0;
  color: #7f8c8d;
  font-size: 16px;
  flex: 1;
}

.refresh-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn .icon {
  font-size: 16px;
  animation: rotate 1s linear infinite;
}

.refresh-btn:not(:disabled) .icon {
  animation: none;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-container,
.error-container,
.no-data-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.no-data-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.error-container h3,
.no-data-container h3 {
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.error-container p,
.no-data-container p {
  color: #7f8c8d;
  margin: 0 0 20px 0;
}

.btn-retry {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-retry:hover {
  background: #5568d3;
  transform: translateY(-2px);
}

.robot-content {
  max-width: 1400px;
}

.robot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
}

.status-badge.online {
  background: rgba(40, 167, 69, 0.3);
}

.card-body {
  padding: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ecf0f1;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #7f8c8d;
  font-size: 14px;
}

.info-value {
  color: #2c3e50;
  font-size: 14px;
  text-align: right;
  word-break: break-word;
  max-width: 60%;
}

.info-value.code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.battery-display {
  text-align: center;
}

.battery-percentage {
  font-size: 48px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 15px;
}

.battery-bar {
  width: 100%;
  height: 30px;
  background: #ecf0f1;
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: 10px;
}

.battery-fill {
  height: 100%;
  border-radius: 15px;
  transition: width 0.5s, background 0.5s;
}

.battery-fill.high {
  background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
}

.battery-fill.medium {
  background: linear-gradient(90deg, #ffc107 0%, #ff9800 100%);
}

.battery-fill.low {
  background: linear-gradient(90deg, #dc3545 0%, #c82333 100%);
}

.battery-status {
  color: #7f8c8d;
  font-size: 16px;
  font-weight: 600;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.location-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.location-text {
  color: #2c3e50;
  font-size: 15px;
  line-height: 1.5;
}

.last-update {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  color: #7f8c8d;
  font-size: 14px;
}
</style>
