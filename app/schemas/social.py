from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.schemas.auth import validate_bcrypt_password_length


class UserPublic(BaseModel):
    id: int
    email: str
    display_name: str | None = None
    location: str | None = None
    bio: str | None = None
    public_details: str | None = None
    businesses: str | None = None
    website_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=160)
    bio: str | None = Field(default=None, max_length=1000)
    public_details: str | None = Field(default=None, max_length=1600)
    businesses: str | None = Field(default=None, max_length=1600)
    website_url: str | None = Field(default=None, max_length=255)


class EmailUpdate(BaseModel):
    email: EmailStr
    current_password: str = Field(min_length=1)


class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=1)
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


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    body: str
    created_at: datetime
    updated_at: datetime
    author: UserPublic

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: int
    domain: str
    business_summary: str
    business_idea: str
    improvement_request: str | None = None
    photo_url: str | None = None
    created_at: datetime
    updated_at: datetime
    author: UserPublic
    comments_count: int
    likes_count: int
    liked_by_me: bool = False
    comments: list[CommentResponse] = []

    class Config:
        from_attributes = True
