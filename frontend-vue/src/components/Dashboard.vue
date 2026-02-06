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
        <TokenRefresh />
        <CreateEndpointButton @click="handleCreateEndpoint" />
        <AsteriskIndicator :active-point="activePointId" />
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
import { ref } from 'vue'
import EndpointsList from './EndpointsList.vue'
import PositionsList from './PositionsList.vue'
import AsteriskIndicator from './AsteriskIndicator.vue'
import TokenRefresh from './TokenRefresh.vue'
import CreateEndpointButton from './CreateEndpointButton.vue'
import CreateEndpointModal from './CreateEndpointModal.vue'
import ResponseModal from './ResponseModal.vue'
import { useNotifications } from '../composables/useNotifications'
import { endpointsAPI } from '../api/services'

const { success, error } = useNotifications()

// Refs
const endpointsListRef = ref(null)

// State
const showCreateModal = ref(false)
const showResponseModal = ref(false)
const currentResponse = ref(null)
const activePointId = ref(null)
const editingEndpoint = ref(null)

// Handlers
const handleSendRobot = ({ pointid, statusCode }) => {
  if (statusCode === 200 || statusCode === 201) {
    activePointId.value = pointid
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
</script>

<style scoped>
.dashboard {
  width: 100%;
  height: 100%;
  padding: 30px;
  box-sizing: border-box;
}

.dashboard-content {
  display: flex;
  gap: 20px;
  height: 100%;
  max-width: 1800px;
}

.panel {
  background-color: white;
  border: 2px solid #4a90e2;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.endpoints-panel {
  width: 300px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.positions-panel {
  flex: 1;
  overflow-y: auto;
}

.indicator-panel {
  width: 400px;
  max-height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}
</style>
