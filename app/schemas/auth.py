from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


def validate_bcrypt_password_length(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar 72 bytes.")

    return password


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    _validate_password_length = field_validator(
        "password",
        "confirm_password",
    )(validate_bcrypt_password_length)

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    _validate_password_length = field_validator(
        "new_password",
        "confirm_password",
    )(validate_bcrypt_password_length)

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden.")
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    login_messages: list[dict[str, str]] = Field(default_factory=list)


class MessageResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    display_name: str | None = None
    location: str | None = None
    bio: str | None = None
    public_details: str | None = None
    businesses: str | None = None
    website_url: str | None = None
    is_verified: bool
    is_active: bool

    class Config:
        from_attributes = True
