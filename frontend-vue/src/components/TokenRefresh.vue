<template>
  <button 
    class="refresh-token-btn"
    :disabled="loading"
    @click="refreshToken"
  >
    {{ loading ? t('common.loading') : `🔄 ${t('robot.refreshToken')}` }}
  </button>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { tokenAPI } from '../api/services'
import { useNotifications } from '../composables/useNotifications'

const { t } = useI18n()
const { success, error } = useNotifications()
const loading = ref(false)

const refreshToken = async () => {
  loading.value = true
  
  try {
    const response = await tokenAPI.refresh()
    
    if (response.data.success) {
      success(`✓ ${t('robot.tokenRefreshed')}`)
    } else {
      error(`✗ ${t('robot.tokenError')}`)
    }
  } catch (err) {
    error(`✗ ${t('notifications.connectionError')}`)
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.refresh-token-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  width: 100%;
  transition: background-color 0.2s;
}

.refresh-token-btn:hover:not(:disabled) {
  background-color: #218838;
}

.refresh-token-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
