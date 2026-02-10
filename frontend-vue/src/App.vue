<template>
  <!-- Email Verification Page -->
  <EmailVerification v-if="showEmailVerification" />

  <!-- Login Page if not authenticated -->
  <LoginPage v-else-if="!isAuthenticated" @login-success="handleLoginSuccess" />

  <!-- Main App if authenticated -->
  <div v-else class="app-layout">
    <!-- Sidebar -->
    <Sidebar 
      :user="user"
      :current-view="currentView"
      @navigate="handleNavigation"
      @open-profile="showProfile = true"
      @logout="handleLogout"
    />

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Dashboard View -->
      <Dashboard v-if="currentView === 'dashboard'" />
      
      <!-- Store View -->
      <StorePage v-else-if="currentView === 'store'" />
      
      <!-- Robot View -->
      <RobotPage v-else-if="currentView === 'robot'" />
      
      <!-- Tasks View -->
      <TasksPage v-else-if="currentView === 'tasks'" />
      
      <!-- Mapping View -->
      <MappingPage v-else-if="currentView === 'mapping'" />
    </div>

    <!-- Notifications -->
    <NotificationContainer />

    <!-- User Profile Modal -->
    <UserProfile 
      v-if="showProfile"
      :user="user"
      @close="showProfile = false"
      @update-user="handleUserUpdate"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LoginPage from './components/LoginPage.vue'
import EmailVerification from './components/EmailVerification.vue'
import UserProfile from './components/UserProfile.vue'
import Sidebar from './components/Sidebar.vue'
import Dashboard from './components/Dashboard.vue'
import StorePage from './components/StorePage.vue'
import RobotPage from './components/RobotPage.vue'
import TasksPage from './components/TasksPage.vue'
import MappingPage from './components/MappingPage.vue'
import NotificationContainer from './components/NotificationContainer.vue'
import { useNotifications } from './composables/useNotifications'
import { useAuth } from './composables/useAuth'

const { success } = useNotifications()
const { isAuthenticated, user, logout, setUser } = useAuth()

// Check for email verification route
const currentRoute = ref(window.location.pathname)
const currentQuery = ref(new URLSearchParams(window.location.search))

const showEmailVerification = computed(() => {
  return currentRoute.value === '/verify-email' || currentQuery.value.has('token')
})

// State
const showProfile = ref(false)
const currentView = ref('dashboard') // dashboard, store, robot

// Auth Handlers
const handleLoginSuccess = () => {
  success('✓ Login successful')
  currentView.value = 'dashboard' // Reset to dashboard on login
}

const handleLogout = async () => {
  await logout()
  success('✓ Logged out successfully')
  currentView.value = 'dashboard' // Reset to dashboard on logout
}

const handleUserUpdate = (updatedUser) => {
  setUser(updatedUser)
  success('✓ Profile updated successfully')
}

// Navigation Handler
const handleNavigation = (view) => {
  currentView.value = view
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f6fa;
  overflow: hidden;
}

.app-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  margin-left: 260px; /* Width of sidebar */
  height: 100vh;
  overflow-y: auto;
  background-color: #f5f6fa;
}
</style>
