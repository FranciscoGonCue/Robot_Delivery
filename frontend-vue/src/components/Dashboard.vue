<template>
  <div class="dashboard">
    <div class="dashboard-content">
      <!-- Endpoints Panel (Left) -->
      <div class="panel endpoints-panel">
        <EndpointsList 
          ref="endpointsListRef"
          @execute="handleExecuteEndpoint"
          @edit="handleEditEndpoint"
        />
      </div>

      <!-- Positions Panel (Center) -->
      <div class="panel positions-panel">
        <PositionsList @send-robot="handleSendRobot" />
      </div>

      <!-- Indicator Panel (Right) -->
      <div class="panel indicator-panel">
        <div class="buttons-row">
          <TokenRefresh />
          <CreateEndpointButton @click="handleCreateEndpoint" />
        </div>
        <AsteriskIndicator :active-point="activePointId" />
      </div>
    </div>

    <!-- Orders Table -->
    <div class="orders-section">
      <div class="orders-header">
        <h2>📊 {{ t('dashboard.orderHistory', 'Order History') }}</h2>
        <div v-if="mostFrequentPoint" class="most-frequent">
          <span class="label">🎯 {{ t('dashboard.mostFrequent', 'Most Frequent') }}:</span>
          <span class="point-name">{{ mostFrequentPoint.point_name || mostFrequentPoint.point_id }}</span>
          <span class="count">({{ mostFrequentPoint.count }} {{ t('dashboard.times', 'times') }})</span>
        </div>
      </div>
      
      <div v-if="loadingOrders" class="loading">🔄 {{ t('common.loading') }}...</div>
      
      <div v-else-if="orders.length === 0" class="no-orders">
        📦 {{ t('dashboard.noOrders', 'No orders yet') }}
      </div>
      
      <div v-else class="table-container">
        <table class="orders-table">
          <thead>
            <tr>
              <th>#</th>
              <th>📍 {{ t('dashboard.destination', 'Destination') }}</th>
              <th>🤖 {{ t('dashboard.robot', 'Robot') }}</th>
              <th>📅 {{ t('dashboard.date', 'Date') }}</th>
              <th>✅ {{ t('dashboard.status', 'Status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(order, index) in orders" :key="order.id" :class="{ 'success-row': order.success }">
              <td>{{ orders.length - index }}</td>
              <td class="point-name">{{ order.point_name || order.point_id }}</td>
              <td class="robot-id">{{ order.robot_uuid.substring(0, 12) }}...</td>
              <td>{{ formatDate(order.created_at) }}</td>
              <td>
                <span class="status-badge" :class="order.success ? 'success' : 'failed'">
                  {{ order.success ? t('dashboard.success', 'Success') : t('dashboard.failed', 'Failed') }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <CreateEndpointModal 
      v-if="showCreateModal" 
      :endpoint="editingEndpoint"
      @close="handleCloseModal"
      @created="handleEndpointCreated"
    />

    <ResponseModal 
      v-if="showResponseModal"
      :response="currentResponse"
      @close="showResponseModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import EndpointsList from './EndpointsList.vue'
import PositionsList from './PositionsList.vue'
import AsteriskIndicator from './AsteriskIndicator.vue'
import TokenRefresh from './TokenRefresh.vue'
import CreateEndpointButton from './CreateEndpointButton.vue'
import CreateEndpointModal from './CreateEndpointModal.vue'
import ResponseModal from './ResponseModal.vue'
import { useNotifications } from '../composables/useNotifications'
import { endpointsAPI, robotAPI } from '../api/services'

const { t } = useI18n()
const { success, error } = useNotifications()

// Refs
const endpointsListRef = ref(null)

// State
const showCreateModal = ref(false)
const showResponseModal = ref(false)
const currentResponse = ref(null)
const activePointId = ref(null)
const editingEndpoint = ref(null)
const orders = ref([])
const loadingOrders = ref(false)

const mostFrequentPoint = computed(() => {
  if (orders.value.length === 0) return null
  
  const pointCounts = {}
  orders.value.forEach(order => {
    const key = order.point_id
    if (!pointCounts[key]) {
      pointCounts[key] = {
        point_id: order.point_id,
        point_name: order.point_name,
        count: 0
      }
    }
    pointCounts[key].count++
  })
  
  return Object.values(pointCounts).sort((a, b) => b.count - a.count)[0]
})

const loadOrders = async () => {
  loadingOrders.value = true
  try {
    const response = await robotAPI.getOrders()
    if (response.data.success) {
      orders.value = response.data.orders
    }
  } catch (err) {
    console.error('Error loading orders:', err)
  } finally {
    loadingOrders.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// Handlers
const handleSendRobot = ({ pointid, statusCode }) => {
  if (statusCode === 200 || statusCode === 201) {
    activePointId.value = pointid
    // Recargar órdenes después de enviar el robot
    setTimeout(() => loadOrders(), 500)
  }
}

const handleEndpointCreated = () => {
  const wasEditing = !!editingEndpoint.value
  showCreateModal.value = false
  editingEndpoint.value = null
  success(wasEditing ? '✓ Endpoint updated successfully' : '✓ Endpoint created successfully')
  
  // Refresh endpoints list
  if (endpointsListRef.value) {
    endpointsListRef.value.loadEndpoints()
  }
}

const handleEditEndpoint = (endpoint) => {
  editingEndpoint.value = endpoint
  showCreateModal.value = true
}

const handleCreateEndpoint = () => {
  editingEndpoint.value = null
  showCreateModal.value = true
}

const handleCloseModal = () => {
  showCreateModal.value = false
  editingEndpoint.value = null
}

const handleExecuteEndpoint = async (endpointId) => {
  try {
    const response = await endpointsAPI.execute(endpointId)
    currentResponse.value = response.data
    showResponseModal.value = true
    
    if (response.data.status_code === 200) {
      success('✓ Request successful (200)')
    }
  } catch (err) {
    error('✗ Error executing endpoint')
  }
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  display: flex;
  gap: 20px;
  height: 60vh;
  max-width: 1800px;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.panel {
  background-color: white;
  border: 2px solid #4a90e2;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.endpoints-panel {
  width: 280px;
  max-height: 60vh;
  overflow-y: auto;
}

.positions-panel {
  flex: 1;
  overflow-y: auto;
}

.indicator-panel {
  width: 380px;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  overflow-y: auto;
}

.buttons-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.buttons-row :deep(button) {
  font-size: 13px;
  padding: 10px 16px;
}

/* Orders Section */
.orders-section {
  background-color: white;
  border: 2px solid #4a90e2;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.orders-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e0e0e0;
  flex-shrink: 0;
}

.orders-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
}

.most-frequent {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 8px 16px;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  font-size: 13px;
}

.most-frequent .label {
  font-size: 13px;
}

.most-frequent .point-name {
  font-size: 15px;
  font-weight: 700;
}

.most-frequent .count {
  font-size: 12px;
  opacity: 0.9;
}

.loading, .no-orders {
  text-align: center;
  padding: 30px;
  color: #666;
  font-size: 14px;
}

.table-container {
  overflow: auto;
  flex: 1;
  min-height: 0;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.orders-table thead {
  background-color: #f5f7fa;
  position: sticky;
  top: 0;
  z-index: 10;
}

.orders-table th {
  padding: 10px 8px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #4a90e2;
  font-size: 12px;
}

.orders-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 12px;
}

.orders-table tbody tr:hover {
  background-color: #f8f9fa;
}

.orders-table .success-row {
  background-color: #f0f9ff;
}

.orders-table .point-name {
  font-weight: 600;
  color: #2c3e50;
}

.orders-table .robot-id {
  font-family: monospace;
  color: #666;
  font-size: 11px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.success {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background-color: #f8d7da;
  color: #721c24;
}
</style>
