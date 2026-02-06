<template>
  <div class="asterisk-section">
    <h3 class="section-title">Delivery Status</h3>
    <div class="asterisk-container">
      <div class="asterisk-center">*</div>
      
      <!-- Rays and Points -->
      <div 
        v-for="(position, index) in positions"
        :key="position.uuid"
      >
        <div 
          class="asterisk-ray"
          :style="getRayStyle(index)"
        ></div>
        <div 
          class="asterisk-point"
          :class="{ active: activePoint === position.pointid }"
          :style="getPointStyle(index)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { targetsAPI } from '../api/services'

const props = defineProps({
  activePoint: {
    type: String,
    default: null
  }
})

// State
const positions = ref([])

// Computed
const numPoints = computed(() => positions.value.length)

// Methods
const loadPositions = async () => {
  try {
    const response = await targetsAPI.getAll()
    
    // Mapear los datos de la API de Keenon
    if (response.data.success) {
      positions.value = response.data.data.map(target => ({
        uuid: target.uuid,
        pointid: target.pointId
      }))
    }
  } catch (err) {
    console.error('Error loading positions:', err)
  }
}

const getRayStyle = (index) => {
  if (numPoints.value === 0) return {}
  
  const angle = (2 * Math.PI / numPoints.value) * index - Math.PI / 2
  return {
    transform: `rotate(${angle}rad)`
  }
}

const getPointStyle = (index) => {
  if (numPoints.value === 0) return {}
  
  const angle = (2 * Math.PI / numPoints.value) * index - Math.PI / 2
  const x = Math.cos(angle) * 150
  const y = Math.sin(angle) * 150
  
  return {
    transform: `translate(${x}px, ${y}px) translate(-50%, -50%)`
  }
}

// Lifecycle
onMounted(() => {
  loadPositions()
})

// Watch for changes
setInterval(loadPositions, 30000)
</script>

<style scoped>
.asterisk-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
}

.asterisk-container {
  position: relative;
  width: 350px;
  height: 350px;
}

.asterisk-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background-color: #4a90e2;
  border-radius: 50%;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.asterisk-ray {
  position: absolute;
  top: 50%;
  left: 50%;
  transform-origin: 0 0;
  width: 150px;
  height: 3px;
  background-color: #4a90e2;
}

.asterisk-point {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  background-color: #ccc;
  border: 3px solid #4a90e2;
  border-radius: 50%;
  transform-origin: 0 0;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.asterisk-point.active {
  background-color: #28a745;
  box-shadow: 0 0 10px #28a745;
}
</style>
