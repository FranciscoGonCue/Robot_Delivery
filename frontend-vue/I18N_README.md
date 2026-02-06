# 🌍 Sistema de Internacionalización (i18n)

El frontend soporta múltiples idiomas usando vue-i18n.

## Idiomas Disponibles

- 🇬🇧 **English** (en)
- 🇪🇸 **Español** (es)
- 🇭🇷 **Hrvatski** (hr) - Croata

## Cómo Usar

### Cambiar Idioma

El selector de idioma está disponible en el Sidebar. El idioma seleccionado se guarda en `localStorage` y persiste entre sesiones.

### Uso en Componentes

```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <h1>{{ t('dashboard.title') }}</h1>
  <p>{{ t('common.loading') }}</p>
</template>
```

## Estructura de Traducciones

Las traducciones están organizadas en:

```
src/i18n/
├── index.js          # Configuración de i18n
└── locales/
    ├── en.js         # Inglés
    ├── es.js         # Español
    └── hr.js         # Croata
```

## Añadir Nuevos Textos

Para añadir nuevas traducciones:

1. Abre los archivos en `src/i18n/locales/`
2. Añade la clave en **todos los idiomas**:

```javascript
// en.js
export default {
  mySection: {
    myText: 'Hello World'
  }
}

// es.js
export default {
  mySection: {
    myText: 'Hola Mundo'
  }
}

// hr.js
export default {
  mySection: {
    myText: 'Pozdrav svijetu'
  }
}
```

3. Usa en tu componente:

```vue
<template>
  <p>{{ t('mySection.myText') }}</p>
</template>
```

## Añadir Nuevo Idioma

1. Crear archivo en `src/i18n/locales/`, por ejemplo `fr.js` para francés
2. Copiar estructura de `en.js` y traducir
3. Importar en `src/i18n/index.js`:

```javascript
import fr from './locales/fr'

const i18n = createI18n({
  messages: {
    en,
    es,
    hr,
    fr  // Nuevo idioma
  }
})
```

4. Añadir opción en `LanguageSwitcher.vue`:

```vue
<option value="fr">🇫🇷 Français</option>
```

## Categorías de Traducción

- `common` - Textos comunes (loading, error, success, etc.)
- `auth` - Autenticación y registro
- `dashboard` - Panel de control
- `positions` - Posiciones/Targets
- `endpoints` - Endpoints guardados
- `robot` - Control de robot
- `store` - Gestión de tiendas
- `profile` - Perfil de usuario
- `deliveryStatus` - Estado de entregas
- `notifications` - Mensajes de notificación
- `config` - Configuración

## Detección Automática

El sistema detecta automáticamente el idioma del navegador al iniciar. Si el idioma del navegador es uno de los soportados, se usará automáticamente.

## Persistencia

El idioma seleccionado se guarda en `localStorage` con la clave `locale` y persiste entre sesiones del navegador.
