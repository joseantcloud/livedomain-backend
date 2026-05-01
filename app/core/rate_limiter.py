from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import HTTPException, status


class RateLimiter:
    """Simple rate limiter basado en diccionario en memoria."""

    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_seconds = window_minutes * 60
        self.attempts: Dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Verifica si se permite un intento para la clave dada."""
        now = datetime.now(timezone.utc).timestamp()
        cutoff = now - self.window_seconds

        # Limpiar intentos antiguos
        if key in self.attempts:
            self.attempts[key] = [
                timestamp for timestamp in self.attempts[key]
                if timestamp > cutoff
            ]

        # Verificar si se excedió el límite
        if key in self.attempts and len(self.attempts[key]) >= self.max_attempts:
            return False

        # Registrar nuevo intento
        if key not in self.attempts:
            self.attempts[key] = []

        self.attempts[key].append(now)
        return True

    def check_rate_limit(
        self,
        key: str,
        max_attempts: int | None = None,
        error_message: str = "Demasiados intentos. Intenta más tarde.",
    ) -> None:
        """Lanza excepción si se excede el límite de intentos."""
        limit = max_attempts or self.max_attempts

        if not self.is_allowed(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message,
            )


# Instancia global
login_rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)
register_rate_limiter = RateLimiter(max_attempts=3, window_minutes=60)
password_reset_rate_limiter = RateLimiter(max_attempts=3, window_minutes=30)
