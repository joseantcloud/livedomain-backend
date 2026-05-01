# LiveDomain Backend

> Si este proyecto te ayuda a aprender Azure, Azure DevOps y pipelines, apoya el contenido con Buy Me a Coffee: `https://buymeacoffee.com/joseantcloud`

![BMW, carro de mis suenos](./bmw.jpg)

## Apoya este curso completo

Hice este curso con mucho amor para ayudar a mas personas a aprender Azure, Azure DevOps, pipelines y despliegues reales paso a paso. He dedicado muchas horas a detallarlo, documentarlo y dejarlo lo mas claro posible para que puedas estudiar aunque no conozcas el proyecto desde antes.

Si este contenido te aporta valor, puedes apoyarlo con Buy Me a Coffee. Cada aporte me acerca a cumplir uno de mis grandes suenos: comprarme el BMW, el carro de mis suenos.

Apoya el curso aqui: `https://buymeacoffee.com/joseantcloud`

Este repositorio contiene el backend de LiveDomain. La idea es que puedas aprender, paso a paso, como una API real se ejecuta localmente, se configura por ambiente, se conecta a base de datos, guarda archivos, expone endpoints y se despliega en Azure usando Azure DevOps Pipelines.

No necesitas conocer el proyecto antes de empezar. Este README explica que hace cada pieza, que debes crear en Azure, que variables debes configurar, como funciona el pipeline y como validar que todo quedo funcionando.

## Resumen rapido

| Tema | Valor |
| --- | --- |
| Tipo de proyecto | Backend API |
| Framework | FastAPI |
| Lenguaje | Python |
| ORM | SQLAlchemy |
| Base local | SQLite |
| Base cloud | Azure SQL |
| Storage cloud | Azure Blob Storage |
| Observabilidad | Application Insights |
| Hosting recomendado | Azure App Service Linux |
| Pipeline | `azure-pipelines-backend.yml` |
| Guia del pipeline | `PIPELINE-README.md` |
| Checklist editable | `DEVOPS-CHECKLIST.xlsx` |
| Rama principal | `main` |

## Que hace este backend

El backend es la API que atiende al frontend. Su responsabilidad es recibir peticiones, validar datos, aplicar reglas de negocio y responder con JSON.

En terminos simples:

1. El frontend envia una peticion HTTP.
2. FastAPI recibe la peticion.
3. Pydantic valida datos de entrada.
4. La API consulta o modifica la base de datos con SQLAlchemy.
5. La API devuelve JSON.
6. El frontend usa esa respuesta para actualizar la pantalla.

## Funcionalidades principales

El backend se encarga de:

- Autenticacion de usuarios.
- Generacion y validacion de tokens JWT.
- Gestion de perfiles.
- Publicaciones.
- Comentarios.
- Likes.
- Carga y entrega de fotos.
- Conexion a SQLite en local.
- Conexion a Azure SQL en produccion.
- Almacenamiento local o Azure Blob Storage para fotos.
- CORS para permitir que el frontend llame la API.
- Headers de seguridad.
- Endpoint `/health` para validacion.

## Que necesita para funcionar

| Necesidad | Para que sirve | Donde se configura |
| --- | --- | --- |
| Python 3.12 | Ejecutar FastAPI | Local y Azure App Service |
| Dependencias pip | FastAPI, SQLAlchemy, Azure SDKs | `requirements.txt` |
| `JWT_SECRET_KEY` | Firmar tokens de sesion | `.env` local o App Service |
| Base de datos | Guardar usuarios y publicaciones | SQLite o Azure SQL |
| `FRONTEND_BASE_URL` | Controlar CORS | `.env` local o App Service |
| Storage | Guardar fotos | Local o Azure Blob |
| Application Insights | Ver errores y trazas | Azure |
| Service Connection | Permiso de Azure DevOps para desplegar | Azure DevOps |
| Pipeline YAML | Automatizar build y deploy | `azure-pipelines-backend.yml` |

## Estructura del repositorio

```text
.
|-- .gitignore
|-- README.md
|-- PIPELINE-README.md
|-- DEVOPS-CHECKLIST.xlsx
|-- azure-pipelines-backend.yml
|-- requirements.txt
|-- .env.example
|-- .env.local.example
|-- .env.cloud.example
`-- app/
    |-- main.py
    |-- Dockerfile
    |-- requirements.txt
    |-- api/
    |   |-- auth.py
    |   `-- social.py
    |-- core/
    |   |-- cloud.py
    |   |-- config.py
    |   |-- local.py
    |   |-- paths.py
    |   |-- rate_limiter.py
    |   `-- security.py
    |-- db/
    |   `-- session.py
    |-- middleware/
    |   `-- security.py
    |-- models/
    |   |-- social.py
    |   `-- user.py
    |-- schemas/
    |   |-- auth.py
    |   `-- social.py
    `-- services/
        |-- email_service.py
        `-- photo_storage.py
```

## Para que sirve cada archivo importante

| Archivo | Explicacion |
| --- | --- |
| `README.md` | Guia general del backend |
| `PIPELINE-README.md` | Explicacion detallada del pipeline |
| `azure-pipelines-backend.yml` | Build y deploy automatico |
| `requirements.txt` | Dependencias usadas por el pipeline |
| `.env.example` | Variables minimas para local |
| `.env.cloud.example` | Variables esperadas para Azure |
| `app/main.py` | Crea la app FastAPI, CORS, DB, routers y `/health` |
| `app/core/config.py` | Decide configuracion local/cloud |
| `app/core/local.py` | Valores por defecto para local |
| `app/core/cloud.py` | Configuracion Azure SQL, Storage, App Configuration |
| `app/db/session.py` | Conexion SQLAlchemy |
| `app/api/auth.py` | Endpoints de autenticacion |
| `app/api/social.py` | Endpoints sociales |
| `app/services/photo_storage.py` | Logica de almacenamiento de fotos |
| `app/middleware/security.py` | Headers de seguridad |

## Conceptos que vas a aprender

Este repo sirve para practicar:

- Que es una API REST.
- Que es FastAPI.
- Que es Uvicorn.
- Que es CORS.
- Que es JWT.
- Que es SQLAlchemy.
- Diferencia entre SQLite local y Azure SQL.
- Que es Azure Blob Storage.
- Que es Application Insights.
- Que es App Service.
- Que es Azure DevOps Pipelines.
- Que es un artifact.
- Que es una Service Connection.
- Como revisar logs cuando algo falla.

## Requisitos locales

Instala:

1. Git.
2. Python 3.12.
3. pip.
4. Un editor como Visual Studio Code.
5. Opcional: Azure CLI si quieres practicar comandos contra Azure.

Valida versiones:

```powershell
git --version
python --version
pip --version
```

## Instalacion local paso a paso

1. Clona el repositorio:

```powershell
git clone https://github.com/joseantcloud/livedomain-backend.git
cd livedomain-backend
```

2. Crea un entorno virtual:

```powershell
python -m venv .venv
```

3. Activa el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Instala dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. Crea un archivo `.env` basado en `.env.example`.

Ejemplo local:

```text
JWT_SECRET_KEY=replace-with-a-generated-secret
LOCAL=True
ENVIRONMENT=local
FRONTEND_BASE_URL=http://localhost:5173
LOCAL_DATABASE_URL=sqlite:///./livedomain.db
```

6. Ejecuta la API:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. Abre:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## Explicacion de variables locales

| Variable | Ejemplo | Para que sirve |
| --- | --- | --- |
| `JWT_SECRET_KEY` | `replace-with-a-generated-secret` | Firma tokens JWT |
| `LOCAL` | `True` | Activa modo local |
| `ENVIRONMENT` | `local` | Identifica ambiente |
| `FRONTEND_BASE_URL` | `http://localhost:5173` | Permite CORS desde frontend local |
| `LOCAL_DATABASE_URL` | `sqlite:///./livedomain.db` | Define SQLite local |

## Modo local vs modo cloud

El proyecto tiene dos formas de configurarse:

| Modo | Valor | Uso |
| --- | --- | --- |
| Local | `LOCAL=True` | Desarrollo con SQLite y archivos locales |
| Cloud | `LOCAL=False` | Produccion con Azure SQL, Blob Storage y Application Insights |

En `app/main.py` existe una linea de configuracion rapida:

```python
local = True
```

Para una demo de produccion real, cambia a:

```python
local = False
```

Tambien puedes controlar el modo con variables de ambiente. En Azure App Service debes configurar `LOCAL=False`.

## Configuracion cloud

Usa `.env.cloud.example` como guia. No subas un `.env` real.

Variables principales para Azure:

```text
LOCAL=False
ENVIRONMENT=production
JWT_SECRET_KEY=<clave-larga-y-segura>
FRONTEND_BASE_URL=https://<frontend>.azurewebsites.net
AZURE_SQL_CONNECTION_STRING=<connection-string>
APPLICATIONINSIGHTS_ENABLED=True
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
PHOTO_STORAGE_BACKEND=azure_blob
AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_STORAGE_CONTAINER_NAME=livedomain-photos
```

Variables SMTP opcionales:

```text
SMTP_HOST=<servidor-smtp>
SMTP_PORT=587
SMTP_USER=<usuario>
SMTP_PASSWORD=<password>
SMTP_FROM_EMAIL=no-reply@livedomain.com
SMTP_USE_TLS=True
```

## Comandos del proyecto

| Comando | Cuando usarlo | Que hace |
| --- | --- | --- |
| `python -m pip install -r requirements.txt` | Instalacion local o pipeline | Instala dependencias |
| `python -m compileall app` | Validacion rapida | Detecta errores de sintaxis |
| `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | Desarrollo local | Ejecuta API con recarga |
| `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` | Produccion | Ejecuta API sin recarga |

## Recursos que debes crear en Azure

Crea estos recursos en este orden recomendado:

1. Resource Group.
2. App Service Plan Linux.
3. Web App Linux para backend.
4. Azure SQL Server.
5. Azure SQL Database.
6. Storage Account.
7. Blob Container.
8. Application Insights.
9. Application settings en Web App.
10. Azure DevOps Project.
11. Service Connection.
12. Pipeline desde YAML.

Nombres sugeridos:

```text
Resource Group: rg-livedomain-prod
App Service Plan: asp-livedomain-prod
Backend Web App: app-livedomain-backend-prod
SQL Server: sql-livedomain-prod
SQL Database: sqldb-livedomain-prod
Storage Account: stlivedomainprod
Blob Container: livedomain-photos
Application Insights: ai-livedomain-prod
Azure DevOps Project: LiveDomain
Service Connection: sc-livedomain-prod
```

## Crear Resource Group

Un Resource Group agrupa todos los recursos del proyecto.

En Azure Portal:

1. Buscar `Resource groups`.
2. Seleccionar `Create`.
3. Elegir la suscripcion.
4. Nombre: `rg-livedomain-prod`.
5. Elegir region.
6. Crear.

## Crear App Service Plan

El App Service Plan define la capacidad donde corre la API.

1. Buscar `App Service plans`.
2. Seleccionar `Create`.
3. Resource Group: `rg-livedomain-prod`.
4. Nombre: `asp-livedomain-prod`.
5. Sistema operativo: Linux.
6. Elegir un plan pequeno para aprendizaje.
7. Crear.

## Crear Web App backend

1. Buscar `App Services`.
2. Seleccionar `Create`.
3. Elegir `Web App`.
4. Resource Group: `rg-livedomain-prod`.
5. Nombre: `app-livedomain-backend-prod`.
6. Publish: Code.
7. Runtime stack: Python 3.12.
8. Operating System: Linux.
9. App Service Plan: `asp-livedomain-prod`.
10. Crear.

## Crear Azure SQL

1. Buscar `SQL databases`.
2. Seleccionar `Create`.
3. Resource Group: `rg-livedomain-prod`.
4. Database name: `sqldb-livedomain-prod`.
5. Crear o seleccionar SQL Server: `sql-livedomain-prod`.
6. Guardar usuario y password de administrador en un lugar seguro.
7. Elegir compute pequeno para aprendizaje.
8. Crear.
9. Ir al SQL Server.
10. Abrir `Networking`.
11. Permitir acceso desde servicios de Azure si App Service debe conectarse.
12. Copiar connection string.
13. Guardarla en App Service como `AZURE_SQL_CONNECTION_STRING`.

## Crear Storage Account

1. Buscar `Storage accounts`.
2. Seleccionar `Create`.
3. Resource Group: `rg-livedomain-prod`.
4. Nombre: `stlivedomainprod` o uno disponible.
5. Crear.
6. Entrar al Storage Account.
7. Crear container `livedomain-photos`.
8. Copiar connection string.
9. Guardarla como `AZURE_STORAGE_CONNECTION_STRING`.

## Crear Application Insights

1. Buscar `Application Insights`.
2. Crear recurso.
3. Resource Group: `rg-livedomain-prod`.
4. Nombre: `ai-livedomain-prod`.
5. Copiar connection string.
6. Guardarla como `APPLICATIONINSIGHTS_CONNECTION_STRING`.

## Configurar App Service

En la Web App backend:

1. Ir a `Settings`.
2. Entrar en `Environment variables` o `Configuration`.
3. Agregar variables:

```text
LOCAL=False
ENVIRONMENT=production
JWT_SECRET_KEY=<clave-larga-y-segura>
FRONTEND_BASE_URL=https://<frontend-webapp>.azurewebsites.net
AZURE_SQL_CONNECTION_STRING=<connection-string>
APPLICATIONINSIGHTS_ENABLED=True
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
PHOTO_STORAGE_BACKEND=azure_blob
AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_STORAGE_CONTAINER_NAME=livedomain-photos
```

4. Guardar.
5. Reiniciar la Web App.

## Azure DevOps: que debes crear

Necesitas:

1. Organization.
2. Project.
3. Service Connection.
4. Pipeline.

## Crear Service Connection

En Azure DevOps:

1. Entrar al Project.
2. Ir a `Project settings`.
3. Ir a `Service connections`.
4. Crear una nueva.
5. Elegir `Azure Resource Manager`.
6. Usar `Service principal automatic`.
7. Seleccionar la suscripcion.
8. Seleccionar el Resource Group.
9. Nombre sugerido: `sc-livedomain-prod`.
10. Guardar.

Ese nombre debe coincidir con `azureServiceConnection` en el YAML.

## Configurar el pipeline

Archivo:

```text
azure-pipelines-backend.yml
```

Variables que debes reemplazar:

```yaml
azureServiceConnection: "REPLACE_AZURE_SERVICE_CONNECTION"
webAppName: "REPLACE_BACKEND_WEBAPP_NAME"
```

Ejemplo:

```yaml
azureServiceConnection: "sc-livedomain-prod"
webAppName: "app-livedomain-backend-prod"
```

## Que hace el pipeline

1. Se ejecuta cuando haces push a `main`.
2. Usa una maquina Ubuntu temporal.
3. Instala Python 3.12.
4. Actualiza pip.
5. Instala dependencias desde `requirements.txt`.
6. Ejecuta `python -m compileall app`.
7. Empaqueta el repo en un ZIP.
8. Publica el ZIP como artifact.
9. Despliega el ZIP en Azure App Service.
10. Configura el comando de inicio con Uvicorn.

## Despliegue completo paso a paso

1. Ejecuta la API localmente.
2. Valida `/health`.
3. Crea los recursos de Azure.
4. Configura variables en App Service.
5. Crea Service Connection.
6. Ajusta variables del YAML.
7. Haz commit.
8. Haz push a `main`.
9. Abre Azure DevOps > Pipelines.
10. Revisa el stage Build.
11. Revisa el stage Deploy.
12. Abre `/health` en Azure.
13. Prueba login desde el frontend.
14. Revisa Application Insights.

## Validacion despues del despliegue

Endpoint:

```text
https://<backend>.azurewebsites.net/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "app": "LiveDomain API",
  "environment": "production",
  "local": false
}
```

## Seguridad y archivos que no deben subirse

Este repo incluye `.gitignore`. Aun asi, revisa siempre antes de commit:

```powershell
git status --short
```

No subas:

```text
.env
*.env
*.log
__pycache__/
*.pyc
livedomain.db
uploads/
```

Si algun secreto real ya fue publicado:

1. Rota `JWT_SECRET_KEY`.
2. Rota connection strings de Azure SQL.
3. Rota connection strings de Storage.
4. Cambia passwords SMTP.
5. Quita archivos sensibles del repo.
6. Evalua limpiar la historia de Git.

## Checklist principal

| ID | Item | Prioridad | Estado |
| --- | --- | --- | --- |
| BE-001 | Crear recursos base en Azure | Alta | Pendiente |
| BE-002 | Crear Web App Linux Python | Alta | Pendiente |
| BE-003 | Crear Azure SQL | Alta | Pendiente |
| BE-004 | Crear Storage Account | Media | Pendiente |
| BE-005 | Crear Application Insights | Media | Pendiente |
| BE-006 | Configurar variables de App Service | Alta | Pendiente |
| BE-007 | Crear Service Connection | Alta | Pendiente |
| BE-008 | Ajustar variables del pipeline | Alta | Pendiente |
| BE-009 | Ejecutar validacion local | Media | Pendiente |
| BE-010 | Ejecutar pipeline | Alta | Pendiente |
| BE-011 | Validar `/health` publicado | Alta | Pendiente |
| BE-012 | Validar CORS desde frontend | Alta | Pendiente |
| BE-013 | Revisar logs y Application Insights | Media | Pendiente |
| BE-014 | Probar rollback | Media | Pendiente |

El archivo `DEVOPS-CHECKLIST.xlsx` sirve para marcar avance, responsable, fecha objetivo y notas.

## Troubleshooting

| Problema | Causa probable | Como revisarlo |
| --- | --- | --- |
| API no inicia | Falta variable obligatoria | Revisar logs de App Service |
| Error JWT | `JWT_SECRET_KEY` ausente o cambiado | Revisar Application settings |
| Error SQL | Connection string o firewall | Revisar Azure SQL Networking |
| Error CORS | `FRONTEND_BASE_URL` incorrecto | Comparar URL real del frontend |
| Upload falla | Storage mal configurado | Revisar container y connection string |
| Pipeline no inicia | Trigger o rama incorrecta | Confirmar push a `main` |
| Deploy falla | Service Connection sin permisos | Revisar Azure DevOps Project Settings |
| `/health` muestra local true | `LOCAL` no esta en `False` | Revisar variables de App Service |

## Relacion con el frontend

El frontend espera que este backend:

- Responda por HTTPS.
- Exponga endpoints bajo `/api`.
- Permita CORS desde la URL del frontend.
- Devuelva JSON.
- Sirva fotos o URLs de fotos correctamente.

El backend espera que el frontend tenga una URL conocida, porque esa URL se configura en `FRONTEND_BASE_URL` para CORS.

## Documentacion adicional

Lee tambien:

- `PIPELINE-README.md` para entender cada parte del pipeline.
- `SECURITY_IMPROVEMENTS.md` para mejoras de seguridad implementadas.
- `DEVOPS-CHECKLIST.xlsx` para seguimiento operativo.

## Siguiente practica recomendada

Ejecuta la API localmente, abre `/docs`, prueba un endpoint y luego despliega a Azure. Despues revisa el mismo endpoint en la URL publica y compara logs locales contra logs de App Service.
