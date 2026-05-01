import os

# ================= CONFIGURACION RAPIDA =================
# Cambia solo esta linea:
# local = True  -> usa backend/app/core/local.py
# local = False -> usa backend/app/core/cloud.py
local = True
# ========================================================

os.environ.setdefault("LOCAL", str(local))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.api.auth import router as auth_router
from app.api.social import comments_router, posts_router, users_router
from app.core.config import BACKEND_DIR, settings
from app.db.session import Base, engine
from app.middleware.security import SecurityHeadersMiddleware
from app.models.social import Comment, Post, PostLike  # noqa: F401
from app.models.user import User  # noqa: F401


LOCAL = settings.LOCAL


if settings.APPLICATIONINSIGHTS_ENABLED and settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
    from azure.monitor.opentelemetry import configure_azure_monitor # pyright: ignore[reportMissingImports]

    configure_azure_monitor(
        connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING
    )


def migrate_existing_schema():
    inspector = inspect(engine)

    if "users" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }
    profile_columns = {
        "display_name": "display_name VARCHAR(120)",
        "location": "location VARCHAR(160)",
        "bio": "bio TEXT",
        "public_details": "public_details TEXT",
        "businesses": "businesses TEXT",
        "website_url": "website_url VARCHAR(255)",
    }

    with engine.begin() as connection:
        for column_name, ddl in profile_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {ddl}"))


migrate_existing_schema()
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


# Configuración de CORS más restrictiva
allowed_origins = [
    settings.FRONTEND_BASE_URL,
]

# En desarrollo, permitir localhost
if LOCAL:
    allowed_origins.extend([
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ])

local_dev_origin_regex = None
if LOCAL:
    local_dev_origin_regex = r"^http://(localhost|127\.0\.0\.1):\d+$"


# Aplicar middleware de CORS antes que otros middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=local_dev_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Agregar middleware de seguridad
app.add_middleware(SecurityHeadersMiddleware)

uploads_dir = BACKEND_DIR / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "local": LOCAL,
    }


app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(posts_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
