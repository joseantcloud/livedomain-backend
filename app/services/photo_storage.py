from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import BACKEND_DIR, settings


UPLOAD_DIR = BACKEND_DIR / "uploads" / "posts"
MAX_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def validate_photo_file(photo: UploadFile) -> str:
    suffix = Path(photo.filename or "").suffix.lower()

    if suffix not in ALLOWED_PHOTO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La foto debe ser JPG, PNG, WEBP o GIF.",
        )

    if photo.content_type and not photo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser una imagen.",
        )

    return suffix


def validate_photo_size(data: bytes) -> None:
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La foto no puede superar 5 MB.",
        )


def get_blob_service_client():
    from azure.storage.blob import BlobServiceClient

    if settings.AZURE_STORAGE_CONNECTION_STRING:
        return BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )

    if settings.AZURE_STORAGE_ACCOUNT_URL:
        from azure.identity import DefaultAzureCredential

        return BlobServiceClient(
            account_url=settings.AZURE_STORAGE_ACCOUNT_URL,
            credential=DefaultAzureCredential(),
        )

    raise RuntimeError(
        "Azure Blob Storage requiere AZURE_STORAGE_CONNECTION_STRING "
        "o AZURE_STORAGE_ACCOUNT_URL."
    )


def build_blob_url(blob_name: str) -> str:
    if settings.AZURE_STORAGE_PUBLIC_BASE_URL:
        return (
            f"{settings.AZURE_STORAGE_PUBLIC_BASE_URL.rstrip('/')}/"
            f"{blob_name}"
        )

    if settings.AZURE_STORAGE_ACCOUNT_URL:
        return (
            f"{settings.AZURE_STORAGE_ACCOUNT_URL.rstrip('/')}/"
            f"{settings.AZURE_STORAGE_CONTAINER_NAME}/{blob_name}"
        )

    client = get_blob_service_client()
    return client.get_blob_client(
        container=settings.AZURE_STORAGE_CONTAINER_NAME,
        blob=blob_name,
    ).url


async def save_photo(photo: UploadFile | None) -> str | None:
    if not photo or not photo.filename:
        return None

    suffix = validate_photo_file(photo)
    data = await photo.read()
    validate_photo_size(data)

    filename = f"{uuid4().hex}{suffix}"

    if settings.PHOTO_STORAGE_BACKEND == "azure_blob":
        from azure.core.exceptions import ResourceExistsError
        from azure.storage.blob import ContentSettings

        service_client = get_blob_service_client()
        container_client = service_client.get_container_client(
            settings.AZURE_STORAGE_CONTAINER_NAME
        )

        try:
            container_client.create_container()
        except ResourceExistsError:
            pass

        container_client.upload_blob(
            name=filename,
            data=data,
            overwrite=False,
            content_settings=ContentSettings(
                content_type=photo.content_type or "application/octet-stream"
            ),
        )

        return build_blob_url(filename)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / filename
    path.write_bytes(data)

    return f"/uploads/posts/{filename}"


def delete_photo(photo_url: str | None) -> None:
    if not photo_url:
        return

    if photo_url.startswith("/uploads/posts/"):
        filename = Path(photo_url).name
        path = UPLOAD_DIR / filename

        if path.exists():
            path.unlink()

        return

    if settings.PHOTO_STORAGE_BACKEND != "azure_blob":
        return

    blob_name = photo_url.rstrip("/").split("/")[-1]

    if not blob_name:
        return

    service_client = get_blob_service_client()
    blob_client = service_client.get_blob_client(
        container=settings.AZURE_STORAGE_CONTAINER_NAME,
        blob=blob_name,
    )
    try:
        blob_client.delete_blob(delete_snapshots="include")
    except Exception:
        return
