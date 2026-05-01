# Azure DevOps Pipeline - Backend

Este archivo contiene la configuración del pipeline CI/CD para el backend de LiveDomain.

## 📋 Contenido

- `azure-pipelines-backend.yml` - Pipeline para build y deploy del backend (FastAPI)
- `DEVOPS-TODO.md` - Guía completa de configuración paso a paso

## 🚀 Pipeline Backend

El pipeline `azure-pipelines-backend.yml` automatiza:

### Build
- Instala Python 3.12
- Valida dependencias desde `requirements.txt`
- Compila bytecode de la aplicación
- Crea artefacto ZIP para despliegue

### Deploy
- Descarga el artefacto del build
- Despliega a Azure WebApp Linux
- Configura runtime Python 3.12
- Inicia la aplicación con Uvicorn

## ⚙️ Configuración Requerida

Antes de usar el pipeline, configura estas variables:

```yaml
variables:
  azureServiceConnection: "REPLACE_AZURE_SERVICE_CONNECTION"
  webAppName: "REPLACE_BACKEND_WEBAPP_NAME"
```

**Pasos:**

1. Ve a Azure DevOps > Service Connections
2. Crea una conexión de "Azure Resource Manager"
3. Reemplaza `REPLACE_AZURE_SERVICE_CONNECTION` con el nombre exacto
4. Reemplaza `REPLACE_BACKEND_WEBAPP_NAME` con el nombre de tu Azure WebApp

## 🔄 Cómo Funciona

1. El pipeline se dispara automáticamente cuando haces push a `main` en la carpeta `backend/`
2. Se ejecuta el stage de Build
3. Si el Build es exitoso, se ejecuta el stage de Deploy
4. El backend queda disponible en la URL de tu WebApp

## 📊 Ver el Estado

- Azure DevOps > Pipelines > Pipeline runs
- Haz clic en el run para ver detalles
- Revisa los logs de cada stage

## 🔐 Notas de Seguridad

- **NUNCA** commitees secretos en el YAML
- Usa **Variable Groups** en Azure DevOps para secrets
- Los secrets deben estar marcados como "Secret" en la UI

## 📚 Más Información

Consulta `DEVOPS-TODO.md` para:
- Guía paso a paso completa
- Cómo crear Web Apps en Azure
- Cómo configurar la base de datos
- Troubleshooting

---

**Versión**: 1.0
**Última actualización**: May 1, 2026
