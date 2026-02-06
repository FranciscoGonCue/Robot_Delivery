<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="modal-title">{{ isEditing ? t('endpoints.editEndpoint') : t('endpoints.createEndpoint') }}</h2>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <form @submit.prevent="saveEndpoint">
        <div class="form-group">
          <label class="form-label">{{ t('endpoints.endpointName') }}:</label>
          <input 
            v-model="form.name"
            type="text"
            class="form-input"
            :placeholder="t('endpoints.endpointName')"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">{{ t('endpoints.method') }} & {{ t('endpoints.path') }}:</label>
          <div class="method-input-group">
            <select v-model="form.method" class="form-select">
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
            <input 
              v-model="form.path"
              type="text"
              class="form-input"
              placeholder="/api/open/scene/v3/robot/status"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">{{ t('endpoints.params') }} (JSON):</label>
          <textarea 
            v-model="form.params"
            class="form-textarea"
            placeholder='{"page": 1, "limit": 10}'
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">{{ t('endpoints.body') }} (JSON):</label>
          <textarea 
            v-model="form.body"
            class="form-textarea"
            placeholder='{"uuid": "123", "pointId": "PT-001"}'
          ></textarea>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? t('common.loading') : (isEditing ? t('endpoints.updateSuccess') : t('endpoints.createSuccess')) }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { endpointsAPI } from '../api/services'
import { useNotifications } from '../composables/useNotifications'

const { t } = useI18n()
const props = defineProps({
  endpoint: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'created'])
const { error } = useNotifications()

const loading = ref(false)
const isEditing = computed(() => !!props.endpoint)

const form = reactive({
  name: '',
  method: 'GET',
  path: '',
  params: '',
  body: ''
})

// Initialize form with endpoint data if editing
onMounted(() => {
  if (props.endpoint) {
    form.name = props.endpoint.name
    form.method = props.endpoint.method
    form.path = props.endpoint.path
    form.params = props.endpoint.params
    form.body = props.endpoint.body
  }
})

const validateJSON = (str) => {
  if (!str) return true
  try {
    JSON.parse(str)
    return true
  } catch (e) {
    return false
  }
}

const saveEndpoint = async () => {
  // Validate JSON
  if (!validateJSON(form.params)) {
    error('✗ Invalid JSON in Params')
    return
  }
  
  if (!validateJSON(form.body)) {
    error('✗ Invalid JSON in Body')
    return
  }

  loading.value = true

  try {
    if (isEditing.value) {
      await endpointsAPI.update(props.endpoint.id, form)
    } else {
      await endpointsAPI.create(form)
    }
    emit('created')
  } catch (err) {
    error(isEditing.value ? '✗ Error updating endpoint' : '✗ Error creating endpoint')
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border: 2px solid #4a90e2;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.close-btn {
  font-size: 28px;
  font-weight: bold;
  color: #999;
  cursor: pointer;
  background: none;
  border: none;
}

.close-btn:hover {
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  min-height: 100px;
  font-family: monospace;
  resize: vertical;
}

.form-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.method-input-group {
  display: flex;
  gap: 10px;
}

.method-input-group select {
  width: 120px;
}

.method-input-group input {
  flex: 1;
}

.submit-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  width: 100%;
  transition: background-color 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #218838;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
