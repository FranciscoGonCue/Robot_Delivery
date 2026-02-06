<template>
  <div class="store-page">
    <div class="page-header">
      <h1>🏪 Store</h1>
      <p>Store information from Keenon</p>
      <button @click="loadStoreData" class="refresh-btn" :disabled="loading">
        <span class="icon">🔄</span>
        <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !storeData" class="loading-container">
      <div class="spinner"></div>
      <p>Loading store information...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>Error Loading Data</h3>
      <p>{{ error }}</p>
      <button @click="loadStoreData" class="btn-retry">Retry</button>
    </div>

    <!-- Store Data -->
    <div v-else-if="storeData" class="store-content">
      <div class="store-grid">
        <!-- Main Store Info Card -->
        <div class="card main-card">
          <div class="card-header">
            <h2>🏪 Store Information</h2>
          </div>
          <div class="card-body">
            <div class="store-name">
              {{ storeData.storeName || 'No name' }}
            </div>
            <div class="store-id">
              Store ID: {{ storeData.storeId }}
            </div>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Customer Name:</span>
                <span class="info-value">{{ storeData.customerName || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Address:</span>
                <span class="info-value">{{ storeData.address || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Location Card -->
        <div class="card">
          <div class="card-header">
            <h2>📍 Location Details</h2>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">Address:</span>
              <span class="info-value">{{ storeData.address || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Country:</span>
              <span class="info-value">{{ storeData.country || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Province:</span>
              <span class="info-value">{{ storeData.province || 'N/A' }}</span>
            </div>
          </div>
        </div>

        <!-- Brand Info Card -->
        <div class="card">
          <div class="card-header">
            <h2>🏷️ Brand Information</h2>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">Brand Name:</span>
              <span class="info-value">{{ storeData.brandName || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Third Shop ID:</span>
              <span class="info-value">{{ storeData.thirdShopId || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Third Shop Name:</span>
              <span class="info-value">{{ storeData.thirdShopName || 'N/A' }}</span>
            </div>
          </div>
        </div>

        <!-- ID Information Card -->
        <div class="card">
          <div class="card-header">
            <h2>🔑 Identifiers</h2>
          </div>
          <div class="card-body">
            <div class="id-display">
              <div class="id-item">
                <span class="id-label">Store ID</span>
                <span class="id-value primary">{{ storeData.storeId }}</span>
              </div>
              <div class="id-item" v-if="storeData.thirdShopId">
                <span class="id-label">Third Shop ID</span>
                <span class="id-value">{{ storeData.thirdShopId }}</span>
              </div>
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
      <div class="no-data-icon">🏪</div>
      <h3>No Store Data</h3>
      <p>No store information found at this time</p>
      <button @click="loadStoreData" class="btn-retry">Load Data</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import apiClient from '../api/config'

// Estado
const storeData = ref(null)
const loading = ref(true)
const error = ref(null)
const lastUpdateTime = ref('')
let refreshInterval = null

// Cargar datos de la tienda
const loadStoreData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get('/store/list/')
    
    if (response.data.success && response.data.data && response.data.data.length > 0) {
      // Tomar la primera tienda de la lista
      storeData.value = response.data.data[0]
      lastUpdateTime.value = new Date().toLocaleTimeString('en-US')
    } else {
      error.value = 'No stores found'
      storeData.value = null
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Error connecting to Keenon API'
    console.error('Error loading store data:', err)
    storeData.value = null
  } finally {
    loading.value = false
  }
}

// Cargar al montar
onMounted(() => {
  loadStoreData()
  
  // Auto-refresh cada 5 minutos (300000ms = 5 minutos)
  refreshInterval = setInterval(() => {
    if (!loading.value) {
      loadStoreData()
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
.store-page {
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

.store-content {
  max-width: 1400px;
}

.store-grid {
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
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.card-body {
  padding: 20px;
}

.main-card .card-body {
  text-align: center;
}

.store-name {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
}

.store-id {
  font-size: 14px;
  color: #7f8c8d;
  font-family: 'Courier New', monospace;
  margin-bottom: 25px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  display: inline-block;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
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

.id-display {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.id-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.id-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.id-value {
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
  font-family: 'Courier New', monospace;
}

.id-value.primary {
  color: #667eea;
  font-size: 24px;
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
