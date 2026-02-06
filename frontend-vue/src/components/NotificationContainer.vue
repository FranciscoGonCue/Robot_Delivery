<template>
  <div class="notifications-container">
    <transition-group name="notification">
      <div 
        v-for="notification in notifications"
        :key="notification.id"
        :class="['notification', notification.type]"
      >
        {{ notification.message }}
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useNotifications } from '../composables/useNotifications'

const { notifications } = useNotifications()
</script>

<style scoped>
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification {
  padding: 15px 20px;
  border-radius: 5px;
  color: white;
  font-weight: bold;
  min-width: 200px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.notification.success {
  background-color: #28a745;
}

.notification.error {
  background-color: #dc3545;
}

/* Transition animations */
.notification-enter-active {
  animation: slideIn 0.3s ease;
}

.notification-leave-active {
  animation: slideOut 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(400px);
    opacity: 0;
  }
}
</style>
