<template>
  <div class="language-switcher">
    <select 
      v-model="currentLocale" 
      @change="changeLanguage"
      class="language-select"
    >
      <option value="en">🇬🇧 English</option>
      <option value="es">🇪🇸 Español</option>
      <option value="hr">🇭🇷 Hrvatski</option>
    </select>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const currentLocale = ref(locale.value)

const changeLanguage = () => {
  locale.value = currentLocale.value
  localStorage.setItem('locale', currentLocale.value)
}

// Watch for external locale changes
watch(locale, (newLocale) => {
  currentLocale.value = newLocale
})
</script>

<style scoped>
.language-switcher {
  display: flex;
  align-items: center;
  gap: 10px;
}

.language-select {
  padding: 8px 12px;
  border: 2px solid #4a90e2;
  border-radius: 5px;
  background-color: white;
  color: #2c3e50;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 150px;
}

.language-select:hover {
  border-color: #357abd;
  background-color: #f8f9fa;
}

.language-select:focus {
  outline: none;
  border-color: #357abd;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.language-select option {
  padding: 10px;
}
</style>
