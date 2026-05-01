# Azure DevOps Pipeline - LiveDomain Backend

> Si este proyecto te ayuda a aprender Azure, Azure DevOps y CI/CD, apoya el contenido con Buy Me a Coffee: `https://buymeacoffee.com/joseantcloud`

Este documento explica, paso a paso, como funciona el pipeline del backend y que debes crear antes de ejecutarlo. Esta pensado para personas que estan aprendiendo Azure DevOps desde cero.

## Que es este pipeline

El archivo `azure-pipelines-backend.yml` es una receta de CI/CD para una API FastAPI.

- CI valida que Python instale dependencias y que el codigo compile.
- CD publica el ZIP generado en una Azure Web App Linux.

El backend expone endpoints HTTP, usa SQLAlchemy para datos, puede conectarse a Azure SQL, puede guardar fotos en Azure Blob Storage y puede enviar telemetria a Application Insights.

## Recursos que debes crear antes

En Azure Portal:

1. Crear un Resource Group, por ejemplo `rg-livedomain-prod`.
2. Crear un App Service Plan Linux, por ejemplo `asp-livedomain-prod`.
3. Crear una Web App Linux para el backend, por ejemplo `app-livedomain-backend-prod`.
4. Seleccionar runtime Python 3.12.
5. Crear Azure SQL Server, por ejemplo `sql-livedomain-prod`.
6. Crear Azure SQL Database, por ejemplo `sqldb-livedomain-prod`.
7. Crear Storage Account si vas a guardar fotos en Blob Storage.
8. Crear Application Insights si quieres trazas y errores centralizados.
9. Activar HTTPS Only en la Web App.

En Azure DevOps:

1. Crear una Organization.
2. Crear un Project, por ejemplo `LiveDomain`.
3. Conectar el repositorio GitHub.
4. Crear una Service Connection de Azure Resource Manager.
5. Crear el pipeline apuntando a `azure-pipelines-backend.yml`.

## Variables del pipeline

En `azure-pipelines-backend.yml` veras:

```yaml
variables:
  azureServiceConnection: "REPLACE_AZURE_SERVICE_CONNECTION"
  webAppName: "REPLACE_BACKEND_WEBAPP_NAME"
  environmentName: "production"
  pythonVersion: "3.12"
```

Debes reemplazar:

- `REPLACE_AZURE_SERVICE_CONNECTION`: nombre exacto de la Service Connection en Azure DevOps.
- `REPLACE_BACKEND_WEBAPP_NAME`: nombre exacto de la Web App del backend.

No pongas secretos en el YAML.

## Variables de la Web App

Configura estas variables en Azure Portal > Web App > Configuration > Application settings:

```text
LOCAL=False
ENVIRONMENT=production
JWT_SECRET_KEY=<clave-larga-y-segura>
FRONTEND_BASE_URL=https://<tu-frontend>.azurewebsites.net
AZURE_SQL_CONNECTION_STRING=<connection-string-de-azure-sql>
APPLICATIONINSIGHTS_ENABLED=True
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string-de-application-insights>
PHOTO_STORAGE_BACKEND=azure_blob
AZURE_STORAGE_CONNECTION_STRING=<connection-string-de-storage>
AZURE_STORAGE_CONTAINER_NAME=livedomain-photos
```

Tambien puedes configurar SMTP si vas a enviar correos:

```text
SMTP_HOST=<servidor-smtp>
SMTP_PORT=587
SMTP_USER=<usuario>
SMTP_PASSWORD=<password>
SMTP_FROM_EMAIL=no-reply@livedomain.com
SMTP_USE_TLS=True
```

## Explicacion linea por linea

### Trigger

```yaml
trigger:
  branches:
    include:
      - main
```

Esto ejecuta el pipeline cuando hay push a `main`.

```yaml
paths:
  include:
    - "*"
    - "app/**"
    - "azure-pipelines-backend.yml"
```

Esto limita el disparo a cambios relevantes del backend.

### Pool

```yaml
pool:
  vmImage: "ubuntu-latest"
```

Azure DevOps crea una maquina temporal Linux para ejecutar el pipeline.

### Stage Build

El Build valida y empaqueta el backend.

1. Selecciona Python:

```yaml
- task: UsePythonVersion@0
```

2. Actualiza pip:

```bash
python -m pip install --upgrade pip
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Compila Python:

```bash
python -m compileall app
```

Esto no ejecuta pruebas funcionales, pero detecta errores de sintaxis e imports basicos.

5. Crea un ZIP del backend.
6. Publica el ZIP como artifact llamado `backend`.

### Stage Deploy

El Deploy descarga el artifact y lo publica en App Service.

La tarea clave es:

```yaml
- task: AzureWebApp@1
```

Usa:

- `azureSubscription`: Service Connection.
- `appName`: nombre de la Web App.
- `package`: ZIP generado en Build.
- `runtimeStack`: Python 3.12.
- `startUpCommand`: comando que inicia Uvicorn.

## Como crear Azure SQL para principiantes

1. En Azure Portal buscar SQL databases.
2. Seleccionar Create.
3. Elegir Resource Group.
4. Escribir Database name: `sqldb-livedomain-prod`.
5. Crear o seleccionar SQL Server: `sql-livedomain-prod`.
6. Elegir autenticacion y guardar usuario/password en un lugar seguro.
7. Elegir un compute pequeno para aprendizaje.
8. Crear la base de datos.
9. Ir al SQL Server > Networking.
10. Permitir acceso desde Azure services si App Service necesita conectarse.
11. Copiar connection string ODBC.
12. Guardarla en la Web App como `AZURE_SQL_CONNECTION_STRING`.

## Como crear Storage Account para fotos

1. Crear Storage Account, por ejemplo `stlivedomainprod`.
2. Crear container `livedomain-photos`.
3. Definir acceso segun el caso:
   - privado si las fotos se sirven por backend;
   - publico solo si entiendes el impacto.
4. Copiar connection string.
5. Guardarla como `AZURE_STORAGE_CONNECTION_STRING`.

## Como crear la Service Connection

1. Entrar a Azure DevOps.
2. Ir a Project Settings.
3. Ir a Service connections.
4. Seleccionar New service connection.
5. Elegir Azure Resource Manager.
6. Elegir Service principal automatic.
7. Seleccionar suscripcion y Resource Group.
8. Dar nombre, por ejemplo `sc-livedomain-prod`.
9. Autorizar el pipeline.

## Como crear el pipeline

1. Ir a Azure DevOps > Pipelines.
2. Seleccionar New pipeline.
3. Elegir GitHub.
4. Seleccionar el repo `livedomain-backend`.
5. Elegir Existing Azure Pipelines YAML file.
6. Seleccionar `/azure-pipelines-backend.yml`.
7. Revisar variables.
8. Guardar y ejecutar.

## Validaciones despues del despliegue

1. Abrir `https://<backend>.azurewebsites.net/health`.
2. Confirmar respuesta:

```json
{
  "status": "ok"
}
```

3. Abrir logs de App Service.
4. Probar login o registro desde el frontend.
5. Confirmar que la base usada es Azure SQL, no SQLite local.
6. Revisar Application Insights si esta habilitado.

## Errores comunes

- `requirements.txt not found`: el pipeline esta usando una ruta incorrecta.
- Error de ODBC: falta driver, connection string incorrecto o firewall de SQL.
- Error de CORS: `FRONTEND_BASE_URL` no coincide con la URL real del frontend.
- Error 500 al iniciar: falta `JWT_SECRET_KEY` o variables de produccion.
- Uploads fallan: Storage Account o container mal configurados.
- Deploy falla por permisos: revisar Service Connection.

## Checklist de aprendizaje

| Paso | Que debes entender | Resultado esperado |
| --- | --- | --- |
| 1 | Que es App Service | Hosting administrado para la API |
| 2 | Que es Azure SQL | Base de datos administrada |
| 3 | Que es Storage Account | Almacenamiento de archivos |
| 4 | Que es Application Insights | Observabilidad y errores |
| 5 | Que es Service Connection | Permiso de Azure DevOps hacia Azure |
| 6 | Que es Build | Validar y empaquetar codigo |
| 7 | Que es Deploy | Publicar artifact en App Service |

## Relacion con el README principal

El README principal contiene la guia completa del proyecto: que hace, como correrlo localmente, que recursos necesita y el checklist general. Este archivo se enfoca solo en el pipeline.
