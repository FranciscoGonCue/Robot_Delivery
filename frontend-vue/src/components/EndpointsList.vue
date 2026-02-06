<template>
  <div class="endpoints-container">
    <h3 class="title">📡 Saved Endpoints</h3>
    
    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else-if="endpoints.length === 0" class="no-endpoints">
      No endpoints created yet
    </div>
    
    <div v-else class="endpoints-list">
      <div 
        v-for="endpoint in endpoints"
        :key="endpoint.id"
        class="endpoint-item"
      >
        <span :class="['endpoint-method', `method-${endpoint.method}`]">
          {{ endpoint.method }}
        </span>
        <div class="endpoint-name">{{ endpoint.name }}</div>
        <div class="endpoint-path">{{ endpoint.path }}</div>
        <div class="button-group">
          <button 
            class="execute-btn"
            @click="$emit('execute', endpoint.id)"
          >
            ▶ Execute
          </button>
          <button 
            class="edit-btn"
            @click="$emit('edit', endpoint)"
          >
            ✏ Edit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { endpointsAPI } from '../api/services'

defineEmits(['execute', 'edit'])

const endpoints = ref([])
const loading = ref(true)

const loadEndpoints = async () => {
  try {
    loading.value = true
    const response = await endpointsAPI.getAll()
    endpoints.value = response.data
  } catch (err) {
    console.error('Error loading endpoints:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadEndpoints()
})

// Expose method to parent
defineExpose({ loadEndpoints })
</script>

<style scoped>
.endpoints-container {
  width: 100%;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 15px;
}

.loading, .no-endpoints {
  text-align: center;
  color: #999;
  padding: 20px;
}

.endpoints-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.endpoint-item {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
}

.endpoint-method {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  margin-right: 5px;
}

.method-GET { background-color: #28a745; }
.method-POST { background-color: #007bff; }
.method-PUT { background-color: #ffc107; color: #333; }
.method-DELETE { background-color: #dc3545; }

.endpoint-name {
  font-weight: bold;
  color: #333;
  margin: 5px 0;
}

.endpoint-path {
  font-size: 12px;
  color: #666;
  font-family: monospace;
  margin: 5px 0;
}

.button-group {
  display: flex;
  gap: 5px;
  margin-top: 5px;
}

.execute-btn {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  flex: 1;
  transition: background-color 0.2s;
}

.execute-btn:hover {
  background-color: #357abd;
}

.edit-btn {
  background-color: #ff9800;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  flex: 1;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background-color: #e68900;
}
</style>
