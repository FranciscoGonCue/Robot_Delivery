# 🎨 Robot Control - Vue.js Frontend

Frontend moderno construido con **Vue 3** + **Vite** + **Axios**.

## 🚀 Quick Start

### Instalar dependencias

```bash
npm install
```

### Ejecutar en modo desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: `http://localhost:5173`

### Build para producción

```bash
npm run build
```

Los archivos optimizados estarán en `dist/`

## 📁 Estructura del Proyecto

```
frontend-vue/
├── src/
│   ├── api/                    # API configuration & services
│   │   ├── config.js          # Axios configuration
│   │   └── services.js        # API endpoints
│   │
│   ├── components/            # Vue components
│   │   ├── PositionsList.vue
│   │   ├── EndpointsList.vue
│   │   ├── AsteriskIndicator.vue
│   │   ├── TokenRefresh.vue
│   │   ├── CreateEndpointButton.vue
│   │   ├── CreateEndpointModal.vue
│   │   ├── ResponseModal.vue
│   │   └── NotificationContainer.vue
│   │
│   ├── composables/           # Reusable composition functions
│   │   └── useNotifications.js
│   │
│   ├── App.vue               # Main component
│   ├── main.js               # Entry point
│   └── style.css             # Global styles
│
├── package.json
├── vite.config.js
└── README.md
```

## 🎯 Características

### ✅ Componentes Vue Modulares
- Cada componente en su propio archivo `.vue`
- Single File Components (SFC)
- Composition API (Vue 3)

### ✅ Gestión de Estado
- Composables para lógica reutilizable
- Reactive state management
- No necesita Vuex/Pinia para esta app

### ✅ API Integration
- Axios para peticiones HTTP
- Servicios organizados por feature
- Interceptores para manejo de errores

### ✅ Notificaciones
- Sistema de notificaciones reactivo
- Auto-dismiss después de 3 segundos
- Transiciones suaves

## 🔧 Configuración

### API Base URL

Editar `src/api/config.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api'
```

### Puerto de desarrollo

Editar `vite.config.js`:

```javascript
export default defineConfig({
  server: {
    port: 5173
  }
})
```

## 📦 Dependencias

### Principales
- **Vue 3** - Framework frontend
- **Vite** - Build tool y dev server
- **Axios** - Cliente HTTP

### Scripts npm

```bash
npm run dev       # Modo desarrollo
npm run build     # Build producción
npm run preview   # Preview build
```

## 🎨 Ventajas de Vue.js

### vs Vanilla JavaScript:

1. **Componentes Reutilizables** ✅
   - Código modular y organizado
   - Fácil mantenimiento

2. **Reactividad** ✅
   - UI se actualiza automáticamente
   - No más manipulación manual del DOM

3. **Single File Components** ✅
   - HTML + JS + CSS en un archivo
   - Scoped styles

4. **Composition API** ✅
   - Lógica reutilizable con composables
   - Mejor TypeScript support

5. **Ecosystem** ✅
   - Vue Router para navegación
   - Pinia para state management
   - Gran comunidad

## 🔄 Comunicación con Backend

La app se comunica con el backend Django en:
- **Backend:** `http://localhost:8000/api`
- **Frontend:** `http://localhost:5173`

CORS debe estar habilitado en Django.

## 🏗️ Arquitectura de Componentes

```
App.vue
├── EndpointsList.vue          (Left panel)
├── PositionsList.vue          (Center panel)
└── IndicatorPanel
    ├── TokenRefresh.vue
    ├── CreateEndpointButton.vue
    └── AsteriskIndicator.vue

Modals (conditional):
├── CreateEndpointModal.vue
└── ResponseModal.vue

Global:
└── NotificationContainer.vue
```

## 💡 Composables

### useNotifications

```javascript
const { success, error, notifications } = useNotifications()

// Usar
success('✓ Operation successful')
error('✗ Something went wrong')
```

## 🎯 Próximos Pasos

### Mejoras Sugeridas:

1. **Vue Router**
   - Múltiples vistas/páginas
   - Navegación entre secciones

2. **Pinia (State Management)**
   - Estado global centralizado
   - Mejor para apps más grandes

3. **TypeScript**
   - Type safety
   - Mejor DX

4. **Testing**
   - Vitest para unit tests
   - Cypress para E2E

5. **UI Library**
   - Element Plus
   - Vuetify
   - PrimeVue

## 🐛 Troubleshooting

### "Failed to fetch"
Backend no está corriendo. Iniciar:
```bash
cd ../
python3 manage.py runserver
```

### "CORS Error"
Verificar que Django tenga CORS habilitado

### Puerto en uso
Cambiar puerto en `vite.config.js`

## 📚 Recursos

- [Vue 3 Docs](https://vuejs.org/)
- [Vite Docs](https://vitejs.dev/)
- [Axios Docs](https://axios-http.com/)
- [Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)

## ✨ Ventajas vs Frontend Vanilla

| Feature | Vanilla JS | Vue.js |
|---------|-----------|--------|
| Componentes | ❌ | ✅ |
| Reactividad | ❌ | ✅ |
| Dev Server | ❌ | ✅ (HMR) |
| Build Optimizado | ❌ | ✅ |
| Modularidad | ⚠️ | ✅ |
| Type Safety | ❌ | ✅ (TS) |
| Ecosystem | ❌ | ✅ |

---

**Made with Vue 3 ❤️**
