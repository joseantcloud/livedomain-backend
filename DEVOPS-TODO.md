# DEVOPS TODO - LiveDomain Backend

Guia detallada para publicar, validar y operar el backend FastAPI de LiveDomain en Azure DevOps, Azure App Service y Azure SQL.

## Estado rapido

- Proyecto: `livedomain-backend`
- Rama principal: `main`
- Pipeline esperado: `azure-pipelines-backend.yml`
- Runtime de App Service: Python 3.12
- Comando de inicio: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Artefacto de despliegue: codigo backend sin `.env`, logs, base local ni uploads
- Checklist Excel: `DEVOPS-CHECKLIST.xlsx`

## 0. Seguridad antes de publicar

Prioridad: critica.

- Confirmar que no se publiquen secretos reales.
- Revisar especialmente:
  - `.env`
  - `backend-api*.log`
  - `livedomain.db`
  - `uploads/`
  - connection strings
  - claves JWT
  - credenciales SMTP
  - credenciales Azure Storage
- Crear o corregir `.gitignore` con estas reglas minimas:

```text
.env
*.env
!*.env.example
*.log
__pycache__/
*.pyc
livedomain.db
uploads/
```

- Mantener solo archivos example:
  - `.env.example`
  - `.env.local.example`
  - `.env.cloud.example`
  - `app/.env.example`
- Si algun secreto real ya fue subido:
  - Rotar secreto en Azure o proveedor correspondiente.
  - Cambiar `JWT_SECRET_KEY`.
  - Rotar connection strings de SQL y Storage.
  - Remover el archivo del repo y evaluar limpieza de historia.

Criterio de aceptacion:

- El repo remoto no contiene `.env`, logs, SQLite local, uploads ni `__pycache__`.
- Los valores sensibles estan en App Service Configuration, Key Vault o Variable Groups.
- Los logs del pipeline no exponen connection strings.

## 1. Preparar repositorio GitHub

Prioridad: alta.

- Confirmar remoto:

```powershell
git remote -v
```

- Confirmar rama:

```powershell
git branch --show-current
```

- Verificar estado antes de cambios:

```powershell
git status --short
```

- Confirmar que el repo de GitHub corresponde a backend:

```text
https://github.com/joseantcloud/livedomain-backend.git
```

Criterio de aceptacion:

- El repo remoto apunta al proyecto correcto.
- La rama `main` tiene documentacion y pipeline actualizados.
- No hay secretos nuevos en el commit.

## 2. Corregir alcance del pipeline

Prioridad: alta.

Este repositorio tiene el backend en la raiz. Si el pipeline se ejecuta desde este repo independiente, evitar rutas tipo `backend/...`.

Revisar en `azure-pipelines-backend.yml`:

- `trigger.paths.include`
- instalacion con `pip install -r backend/requirements.txt`
- compilacion con `python -m compileall backend/app`
- `rootFolderOrFile`

Configuracion esperada si el repo es solo backend:

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - "*"
      - "app/**"
      - "azure-pipelines-backend.yml"
```

Build esperado:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m compileall app
```

Criterio de aceptacion:

- El pipeline encuentra `requirements.txt` en la raiz.
- `compileall app` finaliza sin errores.
- El ZIP no incluye `.env`, logs, SQLite local ni uploads.

## 3. Configurar Azure SQL

Prioridad: alta.

- Resource Group recomendado: `rg-livedomain-prod`
- SQL Server recomendado: `sql-livedomain-prod`
- SQL Database recomendada: `sqldb-livedomain-prod`
- Habilitar firewall solo para servicios necesarios.
- Crear usuario de aplicacion con permisos minimos.
- Guardar connection string en App Service o Key Vault.

Variables esperadas:

```text
DATABASE_URL=<connection-string-sqlserver>
ENVIRONMENT=production
```

Criterio de aceptacion:

- La aplicacion conecta a Azure SQL desde App Service.
- No se usa `livedomain.db` en produccion.
- El usuario de base de datos no es administrador global.

## 4. Configurar App Service backend

Prioridad: alta.

- Web App recomendada: `app-livedomain-backend-prod`
- Runtime: Python 3.12
- HTTPS Only: habilitado.
- Always On: habilitado en produccion si el plan lo permite.
- CORS: permitir solo dominios del frontend.

Variables de aplicacion recomendadas:

```text
ENVIRONMENT=production
JWT_SECRET_KEY=<secret>
DATABASE_URL=<connection-string>
FRONTEND_URL=https://<frontend-webapp>.azurewebsites.net
SMTP_HOST=<smtp-host>
SMTP_USER=<smtp-user>
SMTP_PASSWORD=<secret>
AZURE_STORAGE_CONNECTION_STRING=<secret>
AZURE_STORAGE_CONTAINER=<container>
```

Criterio de aceptacion:

- `/docs` o endpoint de health responde si esta permitido.
- Login/registro funcionan contra la base de produccion.
- CORS no permite origenes abiertos en produccion.

## 5. Configurar Azure DevOps

Prioridad: alta.

- Crear Service Connection de Azure Resource Manager.
- Autorizar el pipeline para usar la conexion.
- Configurar variables no secretas:

```yaml
azureServiceConnection: "<NOMBRE_SERVICE_CONNECTION>"
webAppName: "<NOMBRE_BACKEND_WEBAPP>"
environmentName: "production"
pythonVersion: "3.12"
```

- Configurar secretos en Variable Group, App Service o Key Vault.

Criterio de aceptacion:

- El pipeline puede desplegar al App Service correcto.
- Las variables secretas no aparecen en YAML.
- El ambiente `production` queda protegido con aprobaciones si aplica.

## 6. Validaciones locales

Prioridad: media.

Ejecutar antes de merge o push:

```powershell
python -m pip install -r requirements.txt
python -m compileall app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Validar:

- La API inicia sin errores.
- Endpoints de auth responden.
- Endpoints sociales responden.
- Rate limiting y headers de seguridad siguen activos.

Criterio de aceptacion:

- La compilacion no falla.
- La API responde localmente.
- No se generan archivos versionados inesperados.

## 7. Despliegue CI/CD

Prioridad: alta.

- Hacer push a `main`.
- Confirmar que Azure DevOps inicia el pipeline.
- Revisar stage Build:
  - Python 3.12
  - instalacion de dependencias
  - compilacion
  - publicacion de artefacto
- Revisar stage Deploy:
  - descarga del artefacto
  - despliegue a App Service
  - startup command

Criterio de aceptacion:

- Build y Deploy quedan en verde.
- La API responde por HTTPS.
- La app usa Azure SQL y no SQLite local.

## 8. Observabilidad y soporte

Prioridad: media.

- Habilitar Application Insights.
- Revisar logs de App Service despues del despliegue.
- Configurar alerta por 5xx, latencia alta o fallos de disponibilidad.
- Documentar URL, Resource Group, App Service, SQL Server y responsable.

Criterio de aceptacion:

- Se pueden consultar trazas y errores.
- Existe una alerta minima para incidentes.
- Hay procedimiento documentado para revisar logs.

## 9. Rollback

Prioridad: media.

- Mantener artefactos historicos del pipeline.
- Para rollback rapido:
  - redeploy del ultimo artefacto exitoso, o
  - revert commit y push a `main`.
- Si hubo migracion o cambio de esquema:
  - validar plan de rollback de base de datos antes del despliegue.

Criterio de aceptacion:

- Existe artefacto anterior estable.
- El rollback de aplicacion esta probado.
- Los cambios de base de datos tienen plan de recuperacion.

## Checklist resumido

| ID | Item | Prioridad | Estado |
| --- | --- | --- | --- |
| BE-001 | Crear/corregir `.gitignore` | Critica | Pendiente |
| BE-002 | Remover `.env`, logs, SQLite, uploads y cache del tracking | Critica | Pendiente |
| BE-003 | Rotar secretos si ya fueron publicados | Critica | Pendiente |
| BE-004 | Ajustar rutas del pipeline al repo independiente | Alta | Pendiente |
| BE-005 | Crear Azure SQL y usuario de aplicacion | Alta | Pendiente |
| BE-006 | Configurar App Service Python 3.12 | Alta | Pendiente |
| BE-007 | Configurar variables secretas fuera del YAML | Alta | Pendiente |
| BE-008 | Ejecutar compileall y smoke test local | Media | Pendiente |
| BE-009 | Validar despliegue en Azure | Alta | Pendiente |
| BE-010 | Habilitar logs, trazas y alertas | Media | Pendiente |
| BE-011 | Probar rollback | Media | Pendiente |
