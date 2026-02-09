<template>
  <div class="tasks-page">
    <div class="page-header">
      <h1>📋 {{ t('tasks.title', 'Tasks') }}</h1>
      <p>{{ t('tasks.subtitle', 'List of delivered orders from Keenon') }}</p>
      <button @click="loadTasks" class="refresh-btn" :disabled="loading">
        <span class="icon">🔄</span>
        <span>{{ loading ? t('common.loading') : t('tasks.refresh', 'Refresh') }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !tasks" class="loading-container">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>{{ t('common.error') }}</h3>
      <p>{{ error }}</p>
      <button @click="loadTasks" class="btn-retry">{{ t('robot.retry', 'Retry') }}</button>
    </div>

    <!-- Tasks List -->
    <div v-else-if="tasks && tasks.length > 0" class="tasks-content">
      <div class="tasks-stats">
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-content">
            <div class="stat-value">{{ filteredTasks.length }}</div>
            <div class="stat-label">{{ t('tasks.totalTasks', 'Total Tasks') }}</div>
          </div>
        </div>
        
        <!-- Filter Buttons -->
        <div class="filter-buttons">
          <button 
            class="filter-btn" 
            :class="{ active: currentFilter === 'all' }"
            @click="currentFilter = 'all'"
          >
            <span class="filter-icon">📋</span>
            <span>{{ t('tasks.filterAll', 'All') }}</span>
            <span class="filter-count">{{ tasks.length }}</span>
          </button>
          <button 
            class="filter-btn filter-completed" 
            :class="{ active: currentFilter === 'completed' }"
            @click="currentFilter = 'completed'"
          >
            <span class="filter-icon">✅</span>
            <span>{{ t('tasks.filterCompleted', 'Completed') }}</span>
            <span class="filter-count">{{ completedCount }}</span>
          </button>
          <button 
            class="filter-btn filter-failed" 
            :class="{ active: currentFilter === 'failed' }"
            @click="currentFilter = 'failed'"
          >
            <span class="filter-icon">❌</span>
            <span>{{ t('tasks.filterFailed', 'Failed') }}</span>
            <span class="filter-count">{{ failedCount }}</span>
          </button>
        </div>
      </div>

      <div class="tasks-grid">
        <div v-for="(task, index) in filteredTasks" :key="task.robotId + task.startTime + index" class="task-card">
          <div class="task-header">
            <h3>{{ t('tasks.task', 'Task') }} #{{ index + 1 }}</h3>
            <span class="task-status" :class="getStatusClass(task.taskStatus)">
              {{ getStatusLabel(task.taskStatus) }}
            </span>
          </div>
          <div class="task-body">
            <div class="task-info">
              <div class="info-row">
                <span class="info-label">🤖 {{ t('tasks.robotId', 'Robot ID') }}:</span>
                <span class="info-value">{{ task.robotId }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">🏪 {{ t('tasks.storeId', 'Store ID') }}:</span>
                <span class="info-value">{{ task.storeId }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">🕒 {{ t('tasks.startTime', 'Start Time') }}:</span>
                <span class="info-value">{{ task.startTime }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">⏱️ {{ t('tasks.endTime', 'End Time') }}:</span>
                <span class="info-value">{{ task.endTime }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">🔙 {{ t('tasks.backTime', 'Back Time') }}:</span>
                <span class="info-value">{{ task.backTime }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">📏 {{ t('tasks.mileage', 'Mileage') }}:</span>
                <span class="info-value">{{ task.taskMileage }} m</span>
              </div>
              <div class="info-row">
                <span class="info-label">🎯 {{ t('tasks.taskMode', 'Task Mode') }}:</span>
                <span class="info-value">{{ getTaskMode(task.taskMode) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Tasks State -->
    <div v-else-if="tasks && tasks.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <h3>{{ t('tasks.noTasks', 'No tasks found') }}</h3>
      <p>{{ t('tasks.noTasksMessage', 'There are no tasks available at this moment') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { tasksAPI } from '../api/services'
import { useNotifications } from '../composables/useNotifications'

const { t } = useI18n()
const { error: showError } = useNotifications()

const tasks = ref(null)
const loading = ref(false)
const error = ref(null)
const currentFilter = ref('all')

// Computed properties para contar tareas
const completedCount = computed(() => {
  return tasks.value ? tasks.value.filter(task => task.taskStatus === 1).length : 0
})

const failedCount = computed(() => {
  return tasks.value ? tasks.value.filter(task => task.taskStatus === -1).length : 0
})

const filteredTasks = computed(() => {
  if (!tasks.value) return []
  
  if (currentFilter.value === 'completed') {
    return tasks.value.filter(task => task.taskStatus === 1)
  } else if (currentFilter.value === 'failed') {
    return tasks.value.filter(task => task.taskStatus === -1)
  }
  
  return tasks.value
})

const loadTasks = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await tasksAPI.getAll()
    
    if (response.data.success) {
      tasks.value = response.data.data || []
    } else {
      error.value = response.data.error || t('tasks.loadError', 'Failed to load tasks')
      showError(error.value)
    }
  } catch (err) {
    error.value = err.response?.data?.error || t('notifications.connectionError', 'Connection error')
    showError(error.value)
  } finally {
    loading.value = false
  }
}

const getStatusClass = (status) => {
  // taskStatus: 1 = completado, -1 = fallido, 0 = pendiente/en progreso
  if (status === 1) return 'status-completed'
  if (status === -1) return 'status-failed'
  return 'status-pending'
}

const getStatusLabel = (status) => {
  if (status === 1) return t('tasks.statusCompleted', 'Completed')
  if (status === -1) return t('tasks.statusFailed', 'Failed')
  return t('tasks.statusPending', 'Pending')
}

const getTaskMode = (mode) => {
  const modes = {
    1: t('tasks.modeDelivery', 'Delivery'),
    2: t('tasks.modeReturn', 'Return'),
    3: t('tasks.modePatrol', 'Patrol'),
    4: t('tasks.modeFoodDelivery', 'Food Delivery')
  }
  return modes[mode] || `Mode ${mode}`
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.tasks-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 30px;
  align-items: flex-start;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.page-header p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  margin-top: 10px;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateY(-1px);
}

.refresh-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}

.icon {
  font-size: 16px;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #666;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  background-color: #fff5f5;
  border: 1px solid #ffdddd;
  border-radius: 8px;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.error-container h3 {
  color: #d32f2f;
  margin: 0 0 10px 0;
}

.error-container p {
  color: #666;
  margin: 0 0 20px 0;
}

.btn-retry {
  padding: 10px 24px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-retry:hover {
  background-color: #45a049;
}

/* Tasks Stats */
.tasks-stats {
  margin-bottom: 30px;
  display: flex;
  gap: 20px;
  align-items: stretch;
  flex-wrap: wrap;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  flex: 0 0 auto;
}

.stat-icon {
  font-size: 48px;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* Filter Buttons */
.filter-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background-color: white;
  color: #333;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.filter-btn.active {
  background-color: #667eea;
  color: white;
  border-color: #667eea;
}

.filter-btn.filter-completed.active {
  background-color: #4CAF50;
  border-color: #4CAF50;
}

.filter-btn.filter-failed.active {
  background-color: #f44336;
  border-color: #f44336;
}

.filter-icon {
  font-size: 18px;
}

.filter-count {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  min-width: 24px;
  text-align: center;
}

.filter-btn.active .filter-count {
  background-color: rgba(255, 255, 255, 0.3);
}

/* Tasks Grid */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.task-card {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.task-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 18px;
  font-weight: 600;
}

.task-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-completed {
  background-color: #d4edda;
  color: #155724;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-progress {
  background-color: #cce5ff;
  color: #004085;
}

.status-failed {
  background-color: #f8d7da;
  color: #721c24;
}

.status-default {
  background-color: #e2e3e5;
  color: #383d41;
}

.task-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

.info-value {
  color: #1a1a1a;
  font-size: 14px;
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #1a1a1a;
  margin: 0 0 10px 0;
}

.empty-state p {
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .tasks-page {
    padding: 15px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .tasks-grid {
    grid-template-columns: 1fr;
  }

  .tasks-stats {
    flex-direction: column;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
    width: 100%;
  }

  .filter-buttons {
    width: 100%;
    justify-content: center;
  }

  .filter-btn {
    flex: 1;
    min-width: auto;
    justify-content: center;
  }
}
</style>
