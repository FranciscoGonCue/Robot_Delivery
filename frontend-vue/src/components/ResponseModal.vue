<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content response-modal">
      <div class="modal-header">
        <h2 class="modal-title">{{ t('endpoints.response', 'Response') }}</h2>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div v-if="response" class="response-content">
        <span :class="['response-code', statusCodeClass]">
          {{ t('endpoints.status', 'Status') }}: {{ response.status_code }}
        </span>
        
        <h3 class="endpoint-info">
          {{ response.endpoint.method }} {{ response.endpoint.path }}
        </h3>
        
        <h4>{{ t('endpoints.response') }}:</h4>
        <div class="response-body">
          {{ formattedResponse }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps({
  response: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])

const statusCodeClass = computed(() => {
  return props.response?.status_code === 200 ? 'code-200' : 'code-error'
})

const formattedResponse = computed(() => {
  if (!props.response?.response) return ''
  return JSON.stringify(props.response.response, null, 2)
})
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
  max-width: 800px;
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

.response-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.response-code {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 5px;
  font-weight: bold;
  align-self: flex-start;
}

.code-200 {
  background-color: #28a745;
  color: white;
}

.code-error {
  background-color: #dc3545;
  color: white;
}

.endpoint-info {
  color: #2c3e50;
  margin: 0;
}

.response-body {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  font-family: monospace;
  font-size: 12px;
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
}
</style>
