# DEVOPS-TODO

Guía paso a paso para el video de DevOps, SRE, Azure DevOps y despliegue de LiveDomain en Azure.

## 0. Regla de seguridad antes de publicar en GitHub

- No subir secretos reales al repositorio.
- No subir `backend/.env`.
- No subir logs.
- No subir `backend/uploads`.
- No subir `frontend/node_modules`.
- No subir `frontend/dist`.
- Revisar que `.gitignore` exista y tenga estas reglas:

```text
.env
*.env
node_modules/
dist/
*.log
backend/uploads/
frontend/config.js
```

- Usar solo archivos example:
  - `backend/.env.example`
  - `backend/.env.local.example`
  - `backend/.env.cloud.example`

- Si algun secreto ya fue subido por error:
  - Rotar el secreto en Azure.
  - Eliminarlo del repo.
  - Invalidar connection strings comprometidos.

## 1. Publicar repositorio en GitHub

- Crear repositorio en GitHub.
- Mantenerlo publico solo si no contiene secretos.
- Subir el proyecto.
- Confirmar que estos archivos NO aparecen en GitHub:
  - `backend/.env`
  - logs `*.log`
  - `backend/uploads`
  - `frontend/node_modules`
  - `frontend/dist`

Checklist:

```text
Repo publico creado
.env no publicado
Logs no publicados
Uploads no publicados
README visibles
Pipelines YAML visibles
```

## 2. Importar GitHub a Azure DevOps

- Entrar a Azure DevOps.
- Crear Organization si no existe.
- Crear Project, por ejemplo:

```text
LiveDomain
```

- Ir a `Repos`.
- Seleccionar `Import repository`.
- Pegar URL del repo GitHub:

```text
https://github.com/TU-USUARIO/TU-REPO.git
```

- Si el repo es publico, importar directamente.
- Si el repo es privado, autenticar con GitHub PAT.
- Confirmar que Azure DevOps importo:
  - Codigo backend.
  - Codigo frontend.
  - `azure-pipelines-backend.yml`.
  - `azure-pipelines-frontend.yml`.
  - `DEVOPS-TODO.md`.

## 3. Crear Azure SQL Database

- Crear Resource Group:

```text
rg-livedomain-prod
```

- Crear Azure SQL Server:

```text
sql-livedomain-prod
```

- Crear Azure SQL Database:
