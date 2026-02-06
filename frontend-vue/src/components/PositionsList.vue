<template>
  <div class="positions-container">
    <h2 class="title">{{ t('positions.title') }}</h2>
    
    <div v-if="loading" class="loading">{{ t('positions.loadingPositions') }}</div>
    
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else-if="positions.length === 0" class="empty">
      {{ t('positions.noPositions') }}
    </div>
    
    <div v-else class="positions-list">
      <div 
        v-for="position in positions" 
        :key="position.uuid"
        class="position-item"
      >
        <div class="position-info">
          <div class="position-name">{{ position.name }}</div>
          <div class="position-id">ID: {{ position.pointid }}</div>
        </div>
        <button 
          class="go-button"
          :disabled="sendingRobot[position.pointid]"
          @click="sendRobot(position.pointid)"
        >
          {{ sendingRobot[position.pointid] ? t('positions.sending') : t('positions.goButton') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { targetsAPI, robotAPI } from '../api/services'
import { useNotifications } from '../composables/useNotifications'

const { t } = useI18n()
const emit = defineEmits(['send-robot'])
const { success, error: notifyError } = useNotifications()

// State
const positions = ref([])
const loading = ref(true)
const error = ref(null)
const sendingRobot = reactive({})

// Methods
const loadPositions = async () => {
  try {
    loading.value = true
    const response = await targetsAPI.getAll()
    
    // Mapear los datos de la API de Keenon al formato esperado
    if (response.data.success) {
      positions.value = response.data.data.map(target => ({
        uuid: target.uuid,
        name: target.pointName,
        pointid: target.pointId,
        area: target.area
      }))
      error.value = null
    } else {
      error.value = response.data.error || t('positions.errorLoading')
    }
  } catch (err) {
    error.value = t('positions.errorLoading')
    console.error(err)
  } finally {
    loading.value = false
  }
}

const sendRobot = async (pointid) => {
  // Encontrar el target completo para obtener el uuid
  const target = positions.value.find(p => p.pointid === pointid)
  if (!target) {
    notifyError('✗ Target not found')
    return
  }
  
  sendingRobot[pointid] = true
  
  try {
    const response = await robotAPI.call(target.uuid, target.pointid)
    const data = response.data
    
    if (data.status_code) {
      const code = data.status_code
      
      if (code === 200 || code === 201) {
        success(`✓ Robot sent successfully (Code: ${code})`)
        emit('send-robot', { pointid, statusCode: code })
      } else if (code === 400) {
        notifyError('✗ Error 400: Bad request')
      } else if (code === 401) {
        notifyError('✗ Error 401: Unauthorized - Invalid token')
      } else if (code === 403) {
        notifyError('✗ Error 403: Forbidden - No permissions')
      } else if (code === 404) {
        notifyError('✗ Error 404: Point not found')
      } else if (code === 500) {
        notifyError('✗ Error 500: Keenon server error')
      } else {
        notifyError(`✗ Error code ${code}`)
      }
    }
  } catch (err) {
    notifyError('✗ Connection error with server')
    console.error(err)
  } finally {
    sendingRobot[pointid] = false
  }
}

// Lifecycle
onMounted(() => {
  loadPositions()
})

// Auto reload every 30 seconds
setInterval(loadPositions, 30000)
</script>

<style scoped>
.positions-container {
  width: 100%;
}

.title {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5em;
}

.loading, .error, .empty {
  text-align: center;
  padding: 30px;
  color: #666;
}

.error {
  color: #dc3545;
}

.positions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.position-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 5px;
  transition: transform 0.2s;
}

.position-item:hover {
  transform: translateX(2px);
}

.position-info {
  flex: 1;
}

.position-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.position-id {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.go-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.2s;
}

.go-button:hover:not(:disabled) {
  background-color: #357abd;
}

.go-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
