import { createI18n } from 'vue-i18n'
import en from './locales/en'
import es from './locales/es'
import hr from './locales/hr'

// Get saved language from localStorage or use browser language
const savedLocale = localStorage.getItem('locale')
const browserLocale = navigator.language.split('-')[0]
const defaultLocale = savedLocale || (['en', 'es', 'hr'].includes(browserLocale) ? browserLocale : 'en')

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    es,
    hr
  }
})

export default i18n
