# Security Review - LiveDomain Backend

## Vulnerabilidades Identificadas y Corregidas

### 1. Rate Limiting (✅ CORREGIDO)
- **Problema**: No había protección contra ataques de fuerza bruta en endpoints de autenticación
- **Riesgo**: Permitía intentos ilimitados de login/registro/password reset
- **Solución**: Implementado `RateLimiter` con ventanas temporales:
  - **Login**: 5 intentos por 15 minutos (por IP)
  - **Registro**: 3 intentos por 60 minutos (por IP)
  - **Reset de contraseña**: 3 intentos por 30 minutos (por IP)
- **Ubicación**: `app/core/rate_limiter.py`

### 2. Headers de Seguridad (✅ CORREGIDO)
- **Problema**: Faltaban headers HTTP críticos para seguridad del navegador
- **Riesgo**: Vulnerabilidad a clickjacking, MIME sniffing, XSS
- **Solución**: Middleware `SecurityHeadersMiddleware` implementa:
  - `X-Frame-Options: DENY` → Previene clickjacking
  - `X-Content-Type-Options: nosniff` → Previene MIME type sniffing
  - `X-XSS-Protection: 1; mode=block` → Protección contra XSS
  - `Strict-Transport-Security: max-age=31536000` → Fuerza HTTPS en producción
  - `Content-Security-Policy` → Política de seguridad de contenido
  - `Referrer-Policy: strict-origin-when-cross-origin` → Control de referencia
  - `Permissions-Policy` → Restricción de permisos del navegador
- **Ubicación**: `app/middleware/security.py`

### 3. CORS Mejorado (✅ CORREGIDO)
- **Problema**: CORS permitía todos los métodos y headers
- **Riesgo**: Exposición a ataques CORS no autorizados
- **Solución**:
  - **Métodos permitidos**: GET, POST, PUT, DELETE, OPTIONS (no *)
  - **Headers permitidos**: Content-Type, Authorization (no *)
  - **Desarrollo**: Permite localhost en puertos específicos
  - **Producción**: Solo FRONTEND_BASE_URL configurado
- **Ubicación**: `app/main.py`

### 4. Información Sensible en Errores (ESTADO ACTUAL)
- **Evaluación**: Los mensajes de error ya son genéricos
  - "Credenciales inválidas" (en lugar de detallar qué falló)
  - "Usuario no encontrado" (genérico)
- **Mejora**: Los errores específicos se logean internamente con Application Insights
- **Recomendación**: Continuar con esta práctica

### 5. Tokens JWT (ESTADO ACTUAL)
- **Tipo**: JWT con propósito y expiración
- **Campos**: `sub` (user_id), `purpose`, `exp`
- **Algoritmo**: HS256
- **Expiración**: 60 minutos (configurable)
- **Seguridad**: Secret Key debe ser criptográficamente fuerte en producción

### 6. Contraseñas (ESTADO ACTUAL)
- **Hash**: bcrypt con salt
- **Método**: `hash_password()` y `verify_password()`
- **Contexto**: CryptContext con esquema bcrypt
- **Seguridad**: ✅ Adecuada

## Archivos Modificados/Creados

| Archivo | Cambio | Descripción |
|---------|--------|-------------|
| `app/core/rate_limiter.py` | ✨ NUEVO | Rate limiter con ventanas temporales |
| `app/middleware/security.py` | ✨ NUEVO | Security headers middleware |
| `app/middleware/__init__.py` | ✨ NUEVO | Paquete middleware |
| `app/api/auth.py` | ✏️ MODIFICADO | Agregado rate limiting a endpoints |
| `app/main.py` | ✏️ MODIFICADO | CORS restrictivo + security headers |

## Matriz de Riesgo - Antes vs. Después

| Riesgo | Antes | Después | Estado |
|--------|-------|---------|--------|
| Fuerza bruta en login | 🔴 Alto | 🟢 Mitigado | ✅ |
| MIME sniffing | 🟡 Medio | 🟢 Prevenido | ✅ |
| Clickjacking | 🟡 Medio | 🟢 Prevenido | ✅ |
| CORS no autorizado | 🔴 Alto | 🟢 Restringido | ✅ |
| XSS via headers | 🟡 Medio | 🟢 Protegido | ✅ |
| HTTP en producción | 🟡 Medio | 🟢 Forzado HTTPS | ✅ |

## Recomendaciones Futuras

### 🟠 Corto Plazo (1-2 semanas)
1. Implementar logging de intentos de acceso fallidos
2. Agregar endpoint de revocación de tokens
3. Implementar refresh tokens

### 🟡 Mediano Plazo (1-2 meses)
1. Cookies HttpOnly para tokens (reemplazar localStorage)
2. CSRF tokens con SameSite attribute
3. Auditoría de cambios de datos sensibles
4. Two-Factor Authentication (2FA)

### 🔴 Largo Plazo (3-6 meses)
1. OAuth2 con PKCE flow
2. Detección de anomalías en acceso
3. Certificate pinning
4. Monitoreo de seguridad en tiempo real

## Variables de Entorno Sensibles

Asegurarse de que estas NUNCA se commiten:

```
JWT_SECRET_KEY=your-super-secret-key
AZURE_SQL_CONNECTION_STRING=...
AZURE_STORAGE_CONNECTION_STRING=...
APPLICATIONINSIGHTS_CONNECTION_STRING=...
SMTP_PASSWORD=...
```

**Usar solo .env.example y .env.cloud.example como plantillas**

## Testing de Seguridad

Para validar los cambios:

```bash
# 1. Probar rate limiting (debe fallar en 6to intento)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}'
done

# 2. Verificar headers de seguridad
curl -I http://localhost:8000/health | grep -E "X-|Strict|Content-Security|Referrer|Permissions"

# 3. Probar CORS con origin no permitido
curl -H "Origin: http://malicious.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://localhost:8000/api/auth/login -v

# 4. Verificar que CORS permite localhost en desarrollo
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/auth/login -v
```

## Referencias de Seguridad

- [OWASP Top 10 2023](https://owasp.org/Top10/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
- [HTTP Security Headers](https://owasp.org/www-project-secure-headers/)

## Conclusión

Se han implementado mejoras de seguridad significativas:
- ✅ Protección contra fuerza bruta
- ✅ Headers de seguridad del navegador
- ✅ CORS restricitvo
- ✅ Gestión segura de errores

La aplicación está en una postura de seguridad mejorada. Se recomienda continuar con las mejoras propuestas y realizar auditorías de seguridad periódicas.

---
**Actualizado**: May 1, 2026
**Versión**: 1.0
