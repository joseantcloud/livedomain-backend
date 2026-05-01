from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(120), nullable=True)
    location = Column(String(160), nullable=True)
    bio = Column(Text, nullable=True)
    public_details = Column(Text, nullable=True)
    businesses = Column(Text, nullable=True)
    website_url = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    post_likes = relationship(
        "PostLike",
        back_populates="user",
        cascade="all, delete-orphan",
    )
