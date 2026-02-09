<template>
  <div class="sidebar">
    <!-- Logo/Header -->
    <div class="sidebar-header">
      <h2>Robot Control</h2>
    </div>

    <!-- Language Switcher -->
    <div class="language-section">
      <LanguageSwitcher />
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <button
        class="nav-item"
        :class="{ active: currentView === 'dashboard' }"
        @click="$emit('navigate', 'dashboard')"
      >
        <span class="icon">📊</span>
        <span>{{ t('dashboard.title') }}</span>
      </button>

      <button
        class="nav-item"
        :class="{ active: currentView === 'store' }"
        @click="$emit('navigate', 'store')"
      >
        <span class="icon">🏪</span>
        <span>{{ t('store.title') }}</span>
      </button>

      <button
        class="nav-item"
        :class="{ active: currentView === 'robot' }"
        @click="$emit('navigate', 'robot')"
      >
        <span class="icon">🤖</span>
        <span>{{ t('robot.title') }}</span>
      </button>

      <button
        class="nav-item"
        :class="{ active: currentView === 'tasks' }"
        @click="$emit('navigate', 'tasks')"
      >
        <span class="icon">📋</span>
        <span>{{ t('tasks.title', 'Tasks') }}</span>
      </button>
    </nav>

    <!-- User Section (Bottom) -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          {{ user?.username?.charAt(0).toUpperCase() }}
        </div>
        <div class="user-details">
          <span class="username">
            {{ user?.username }}
            <span v-if="user?.is_verified" class="verified-badge" title="Email verificado">✓</span>
          </span>
          <span class="user-email">{{ user?.email || 'Sin email' }}</span>
        </div>
      </div>

      <button class="sidebar-btn profile-btn" @click="$emit('open-profile')">
        <span class="icon">👤</span>
        <span>{{ t('profile.myProfile') }}</span>
      </button>

      <button class="sidebar-btn logout-btn" @click="$emit('logout')">
        <span class="icon">🚪</span>
        <span>{{ t('common.logout') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from './LanguageSwitcher.vue'

const { t } = useI18n()

defineProps({
  user: {
    type: Object,
    required: true
  },
  currentView: {
    type: String,
    required: true
  }
})

defineEmits(['navigate', 'open-profile', 'logout'])
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
}

.sidebar-header {
  padding: 30px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.language-section {
  padding: 15px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-item {
  width: 100%;
  padding: 15px 25px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  text-align: left;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 500;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-left-color: #3498db;
}

.nav-item.active {
  background: rgba(52, 152, 219, 0.2);
  color: white;
  border-left-color: #3498db;
  font-weight: 600;
}

.nav-item .icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.user-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  color: white;
}

.user-email {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.verified-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: #28a745;
  color: white;
  border-radius: 50%;
  font-size: 10px;
  font-weight: bold;
}

.sidebar-btn {
  width: 100%;
  padding: 12px 15px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
}

.sidebar-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.sidebar-btn .icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.profile-btn {
  background: rgba(102, 126, 234, 0.3);
}

.profile-btn:hover {
  background: rgba(102, 126, 234, 0.5);
}

.logout-btn {
  background: rgba(231, 76, 60, 0.3);
  margin-bottom: 0;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 0.5);
}

/* Scrollbar styling */
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
