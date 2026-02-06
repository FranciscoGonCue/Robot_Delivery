# Configuración de Verificación de Email

## Descripción

Este sistema implementa **verificación de email obligatoria** para todos los usuarios. Los usuarios no podrán iniciar sesión hasta que verifiquen su dirección de correo electrónico.

## Características

✅ **Registro con email obligatorio**
- Los usuarios deben proporcionar un email válido al registrarse
- El email no puede estar duplicado

✅ **Bloqueo de inicio de sesión**
- Los usuarios no pueden iniciar sesión hasta verificar su email
- Se muestra un mensaje claro indicando que deben verificar su cuenta

✅ **Emails de verificación**
- Email automático con enlace de verificación (válido por 24 horas)
- Email de confirmación después de verificar exitosamente

✅ **Reenvío de verificación**
- Los usuarios pueden solicitar un nuevo enlace si el anterior expiró
- Opción disponible desde la página de login

✅ **Interfaz completa**
- Página de verificación con feedback visual
- Mensajes de error/éxito claros
- Opción para reenviar email directamente desde errores

## Configuración para Desarrollo

Por defecto, el sistema usa `console.EmailBackend` que **imprime los emails en la consola** del servidor Django en lugar de enviarlos realmente.

### Ver emails en desarrollo

1. Inicia el servidor Django:
```bash
python3 manage.py runserver
```

2. Cuando un usuario se registre, verás el email en la consola del servidor:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Verifica tu cuenta - Robot Delivery Control
From: Robot Delivery <noreply@robotdelivery.com>
To: usuario@ejemplo.com
Date: ...

¡Bienvenido a Robot Delivery Control!
...
```

3. Copia el enlace de verificación de la consola y ábrelo en el navegador

## Configuración para Producción con Gmail

### Paso 1: Configurar Gmail App Password

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Ve a **Seguridad**
3. Activa **Verificación en dos pasos** (si no está activada)
4. Ve a **Contraseñas de aplicaciones**
5. Genera una nueva contraseña de aplicación para "Mail"
6. Guarda la contraseña generada (16 caracteres)

### Paso 2: Actualizar settings.py

Edita `/config/settings.py` y reemplaza la sección de email:

```python
# Email Configuration for Production with Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'  # Tu correo de Gmail
EMAIL_HOST_PASSWORD = 'tu-app-password-de-16-caracteres'  # La contraseña de aplicación
DEFAULT_FROM_EMAIL = 'Robot Delivery <tu-email@gmail.com>'
```

### Paso 3: Variables de entorno (Recomendado)

Para mayor seguridad, usa variables de entorno:

1. Crea un archivo `.env` en la raíz del proyecto:
```env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
SECRET_KEY=tu-clave-secreta
```

2. Instala python-decouple:
```bash
pip install python-decouple
```

3. Actualiza `settings.py`:
```python
from decouple import config

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
SECRET_KEY = config('SECRET_KEY')
```

4. Agrega `.env` a `.gitignore`:
```bash
echo ".env" >> .gitignore
```

## Configuración con Otros Proveedores de Email

### SendGrid

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'tu-api-key-de-sendgrid'
DEFAULT_FROM_EMAIL = 'Robot Delivery <noreply@tudominio.com>'
```

### Mailgun

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@tudominio.mailgun.org'
EMAIL_HOST_PASSWORD = 'tu-password-mailgun'
DEFAULT_FROM_EMAIL = 'Robot Delivery <noreply@tudominio.com>'
```

### Amazon SES

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-access-key'
EMAIL_HOST_PASSWORD = 'tu-secret-key'
DEFAULT_FROM_EMAIL = 'Robot Delivery <noreply@tudominio.com>'
```

## Endpoints de la API

### 1. Registro (POST /api/auth/register/)

**Request:**
```json
{
  "username": "usuario1",
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

**Response (éxito):**
```json
{
  "success": true,
  "message": "User registered successfully. Please check your email to verify your account.",
  "email_sent": true,
  "user": {
    "id": 1,
    "username": "usuario1",
    "email": "usuario@ejemplo.com",
    "is_verified": false
  }
}
```

### 2. Login (POST /api/auth/login/)

**Request:**
```json
{
  "username": "usuario1",
  "password": "password123"
}
```

**Response (sin verificar):**
```json
{
  "error": "Email not verified",
  "message": "Please verify your email before logging in. Check your inbox for the verification link.",
  "email": "usuario@ejemplo.com",
  "requires_verification": true
}
```

**Response (verificado):**
```json
{
  "success": true,
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "usuario1",
    "email": "usuario@ejemplo.com",
    "is_verified": true
  }
}
```

### 3. Verificar Email (GET /api/auth/verify-email/?token=...)

**Response (éxito):**
```json
{
  "success": true,
  "message": "Email verified successfully! You can now login.",
  "user": {
    "username": "usuario1",
    "email": "usuario@ejemplo.com"
  }
}
```

### 4. Reenviar Verificación (POST /api/auth/resend-verification/)

**Request (con email):**
```json
{
  "email": "usuario@ejemplo.com"
}
```

**Request (con username):**
```json
{
  "username": "usuario1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification email sent successfully",
  "email": "usuario@ejemplo.com"
}
```

## Flujo de Usuario

### Registro

1. Usuario completa formulario de registro (username, email, password)
2. Sistema crea usuario en base de datos
3. Sistema genera token de verificación único (UUID)
4. Sistema envía email con enlace de verificación
5. Usuario ve mensaje: "Por favor revisa tu email para verificar tu cuenta"

### Verificación

1. Usuario recibe email con enlace: `http://localhost:5173/?token=xxx-xxx-xxx`
2. Usuario hace clic en el enlace
3. Sistema valida el token:
   - ✅ Token válido → Marca cuenta como verificada
   - ❌ Token expirado → Muestra opción para reenviar
   - ❌ Token inválido → Muestra error
4. Usuario es redirigido al login

### Login

1. Usuario intenta iniciar sesión
2. Sistema valida credenciales
3. Sistema verifica estado de email:
   - ✅ Verificado → Genera tokens JWT y permite acceso
   - ❌ No verificado → Muestra error con opción para reenviar email

## Personalización de Emails

Los emails se encuentran en `/django_app/email_service.py`:

### Email de Verificación

- **Asunto**: "Verifica tu cuenta - Robot Delivery Control"
- **Contenido**: HTML responsivo con botón de verificación
- **Validez**: 24 horas

### Email de Confirmación

- **Asunto**: "Cuenta verificada exitosamente - Robot Delivery Control"
- **Contenido**: Confirmación de verificación exitosa

## Seguridad

✅ **Tokens únicos y seguros**
- Usa UUID4 para tokens de verificación
- Tokens de un solo uso

✅ **Expiración de tokens**
- Los enlaces expiran después de 24 horas
- Se puede regenerar un nuevo token

✅ **Validación de duplicados**
- No se permiten usernames duplicados
- No se permiten emails duplicados

✅ **Bloqueo preventivo**
- Los usuarios no verificados no pueden acceder al sistema
- Validación tanto en backend como frontend

## Troubleshooting

### Los emails no se envían

1. Verifica que estés usando el backend correcto en `settings.py`
2. Para Gmail, asegúrate de usar App Password, no la contraseña normal
3. Verifica que el puerto y TLS estén configurados correctamente
4. Revisa los logs del servidor para errores específicos

### Token inválido o expirado

1. Los tokens expiran después de 24 horas
2. Usa la opción "Reenviar email de verificación"
3. Se generará un nuevo token válido

### Usuario no puede iniciar sesión

1. Verifica que el email esté verificado en el admin de Django:
   - Visita: http://localhost:8000/admin/
   - Ve a: django_app → Email Verifications
   - Verifica el estado de `is_verified`

2. Para verificar manualmente un usuario:
```python
python3 manage.py shell

from django.contrib.auth.models import User
from django_app.models import EmailVerification

user = User.objects.get(username='usuario1')
verification = EmailVerification.objects.get(user=user)
verification.is_verified = True
verification.save()
```

## Testing en Desarrollo

### Probar el flujo completo

1. Inicia el servidor Django:
```bash
python3 manage.py runserver
```

2. Inicia el frontend Vue:
```bash
cd frontend-vue
npm run dev
```

3. Registra un usuario nuevo

4. Copia el enlace de verificación de la consola de Django

5. Pega el enlace en el navegador para verificar

6. Intenta iniciar sesión

### Verificar usuarios existentes

Si ya tienes usuarios creados antes de implementar la verificación:

```bash
python3 manage.py shell
```

```python
from django.contrib.auth.models import User
from django_app.models import EmailVerification

# Crear verificación para usuarios existentes
for user in User.objects.all():
    verification, created = EmailVerification.objects.get_or_create(user=user)
    # Opcional: verificar automáticamente
    verification.is_verified = True
    verification.save()
    print(f"Usuario {user.username}: {'creado' if created else 'actualizado'}")
```

## Próximas Mejoras

- [ ] Recuperación de contraseña por email
- [ ] Cambio de email con re-verificación
- [ ] Notificaciones por email de actividad sospechosa
- [ ] Templates de email personalizables desde el admin
- [ ] Rate limiting para reenvío de emails
- [ ] Verificación en dos pasos (2FA)

## Soporte

Para preguntas o problemas, revisa:
1. Los logs del servidor Django
2. La consola del navegador (Frontend)
3. El estado de la base de datos (Django Admin)
