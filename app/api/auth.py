from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_login_messages, settings
from app.core.rate_limiter import (
    login_rate_limiter,
    password_reset_rate_limiter,
    register_rate_limiter,
)
from app.core.security import (
    create_token,
    hash_password,
    validate_token_purpose,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.services.email_service import (
    send_password_reset_email,
    send_verification_email,
)


router = APIRouter(prefix="/auth", tags=["Auth"])

bearer_scheme = HTTPBearer()


def get_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .filter(func.lower(User.email) == email.lower())
        .first()
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    payload = validate_token_purpose(token, "access_token")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    return user


@router.post("/register", response_model=MessageResponse)
def register(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Rate limiting por IP
    client_ip = request.client.host if request.client else "unknown"
    register_rate_limiter.check_rate_limit(
        client_ip,
        error_message="Demasiados intentos de registro. Intenta más tarde.",
    )

    existing_user = get_user_by_email(db, payload.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con este correo.",
        )

    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        is_verified=False,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    verification_token = create_token(
        subject=str(user.id),
        purpose="email_verification",
        expires_delta=timedelta(hours=24),
    )

    send_verification_email(user.email, verification_token)

    return {
        "message": "Usuario registrado. Revisa tu correo para verificar la cuenta."
    }


@router.get("/verify-email", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = validate_token_purpose(token, "email_verification")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido.",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    if user.is_verified:
        return {"message": "El correo ya estaba verificado."}

    user.is_verified = True
    db.commit()

    return {"message": "Correo verificado correctamente. Ya puedes iniciar sesión."}


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Rate limiting por IP
    client_ip = request.client.host if request.client else "unknown"
    login_rate_limiter.check_rate_limit(
        client_ip,
        error_message="Demasiados intentos de inicio de sesión. Intenta más tarde.",
    )

    user = get_user_by_email(db, payload.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar tu correo antes de iniciar sesión.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    access_token = create_token(
        subject=str(user.id),
        purpose="access_token",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "login_messages": get_login_messages(),
    }


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Rate limiting por IP
    client_ip = request.client.host if request.client else "unknown"
    password_reset_rate_limiter.check_rate_limit(
        client_ip,
        error_message="Demasiados intentos de restablecimiento. Intenta más tarde.",
    )

    user = get_user_by_email(db, payload.email)

    if user:
        reset_token = create_token(
            subject=str(user.id),
            purpose="password_reset",
            expires_delta=timedelta(minutes=30),
        )

        send_password_reset_email(user.email, reset_token)

    return {
        "message": "Si el correo existe, se enviará un enlace para restablecer la contraseña."
    }


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_payload = validate_token_purpose(payload.token, "password_reset")

    user_id = token_payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido.",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    user.hashed_password = hash_password(payload.new_password)

    db.commit()

    return {
        "message": "Contraseña actualizada correctamente. Ya puedes iniciar sesión."
    }


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
