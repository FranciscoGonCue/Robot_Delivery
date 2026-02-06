import { ref } from 'vue'

const notifications = ref([])
let notificationId = 0

export function useNotifications() {
  const addNotification = (message, type = 'success') => {
    const id = notificationId++
    notifications.value.push({
      id,
      message,
      type
    })

    // Auto remove after 3 seconds
    setTimeout(() => {
      removeNotification(id)
    }, 3000)
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const success = (message) => addNotification(message, 'success')
  const error = (message) => addNotification(message, 'error')

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error
  }
}
