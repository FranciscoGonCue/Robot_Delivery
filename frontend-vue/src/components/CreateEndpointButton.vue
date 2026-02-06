<template>
  <button class="create-endpoint-btn" @click="$emit('click')">
    ➕ {{ t('endpoints.createEndpoint') }}
  </button>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
defineEmits(['click'])
</script>

<style scoped>
.create-endpoint-btn {
  background-color: #007bff;
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

.create-endpoint-btn:hover {
  background-color: #0056b3;
}
</style>
