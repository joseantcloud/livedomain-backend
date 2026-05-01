from datetime import timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.auth import get_current_user
from app.core.security import (
    create_token,
    hash_password,
    validate_token_purpose,
    verify_password,
)
from app.db.session import get_db
from app.models.social import Comment, Post, PostLike
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.social import (
    CommentCreate,
    CommentResponse,
    EmailUpdate,
    PasswordUpdate,
    PostResponse,
    ProfileUpdate,
    UserPublic,
)
from app.services.email_service import send_verification_email
from app.services.photo_storage import delete_photo, save_photo


posts_router = APIRouter(prefix="/posts", tags=["Posts"])
users_router = APIRouter(prefix="/users", tags=["Users"])
comments_router = APIRouter(prefix="/comments", tags=["Comments"])
optional_bearer_scheme = HTTPBearer(auto_error=False)

def clean_text(value: str | None, label: str, max_length: int) -> str:
    cleaned = (value or "").strip()

    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{label} es obligatorio.",
        )

    if len(cleaned) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{label} no puede superar {max_length} caracteres.",
        )

    return cleaned


def clean_optional_text(value: str | None, max_length: int) -> str | None:
    cleaned = (value or "").strip()

    if not cleaned:
        return None

    if len(cleaned) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El texto no puede superar {max_length} caracteres.",
        )

    return cleaned


def user_to_public(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "location": user.location,
        "bio": user.bio,
        "public_details": user.public_details,
        "businesses": user.businesses,
        "website_url": user.website_url,
        "created_at": user.created_at,
    }


def comment_to_response(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "body": comment.body,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "author": user_to_public(comment.author),
    }


def post_to_response(
    post: Post,
    include_comments: bool = False,
    current_user: User | None = None,
) -> dict:
    liked_by_me = False

    if current_user:
        liked_by_me = any(like.user_id == current_user.id for like in post.likes)

    return {
        "id": post.id,
        "domain": post.domain,
        "business_summary": post.business_summary,
        "business_idea": post.business_idea,
        "improvement_request": post.improvement_request,
        "photo_url": post.photo_url,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author": user_to_public(post.author),
        "comments_count": len(post.comments),
        "likes_count": len(post.likes),
        "liked_by_me": liked_by_me,
        "comments": [
            comment_to_response(comment)
            for comment in post.comments
        ]
        if include_comments
        else [],
    }


def get_post_or_404(db: Session, post_id: int) -> Post:
    post = (
        db.query(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.comments).selectinload(Comment.author),
            selectinload(Post.likes),
        )
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado.",
        )

    return post


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not credentials:
        return None

    try:
        payload = validate_token_purpose(credentials.credentials, "access_token")
        user_id = payload.get("sub")

        if not user_id:
            return None

        return (
            db.query(User)
            .filter(
                User.id == int(user_id),
                User.is_active.is_(True),
            )
            .first()
        )
    except Exception:
        return None


@users_router.get("/me/profile", response_model=UserPublic)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return user_to_public(current_user)


@users_router.patch("/me/profile", response_model=UserPublic)
def update_my_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.display_name = clean_optional_text(payload.display_name, 120)
    current_user.location = clean_optional_text(payload.location, 160)
    current_user.bio = clean_optional_text(payload.bio, 1000)
    current_user.public_details = clean_optional_text(payload.public_details, 1600)
    current_user.businesses = clean_optional_text(payload.businesses, 1600)
    current_user.website_url = clean_optional_text(payload.website_url, 255)

    db.commit()
    db.refresh(current_user)

    return user_to_public(current_user)


@users_router.patch("/me/email", response_model=UserPublic)
def update_my_email(
    payload: EmailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La contraseña actual no es correcta.",
        )

    new_email = payload.email.lower()

    if new_email == current_user.email:
        return user_to_public(current_user)

    existing_user = (
        db.query(User)
        .filter(func.lower(User.email) == new_email.lower())
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con este correo.",
        )

    current_user.email = new_email
    current_user.is_verified = False
    db.commit()
    db.refresh(current_user)

    verification_token = create_token(
        subject=str(current_user.id),
        purpose="email_verification",
        expires_delta=timedelta(hours=24),
    )
    send_verification_email(current_user.email, verification_token)

    return user_to_public(current_user)


@users_router.patch("/me/password", response_model=MessageResponse)
def update_my_password(
    payload: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La contraseña actual no es correcta.",
        )

    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Contraseña actualizada correctamente."}


@users_router.get("/{user_id}/profile", response_model=UserPublic)
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    return user_to_public(user)


@posts_router.get("", response_model=list[PostResponse])
def list_posts(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    posts = (
        db.query(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.comments),
            selectinload(Post.likes),
        )
        .order_by(func.random())
        .all()
    )

    return [post_to_response(post, current_user=current_user) for post in posts]


@posts_router.get("/mine", response_model=list[PostResponse])
def list_my_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = (
        db.query(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.comments),
            selectinload(Post.likes),
        )
        .filter(Post.user_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    return [post_to_response(post, current_user=current_user) for post in posts]


@posts_router.post("", response_model=PostResponse)
async def create_post(
    domain: str = Form(...),
    business_summary: str = Form(...),
    business_idea: str = Form(...),
    improvement_request: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(
        user_id=current_user.id,
        domain=clean_text(domain, "El dominio", 255),
        business_summary=clean_text(business_summary, "Que hace", 1200),
        business_idea=clean_text(business_idea, "La idea de negocio", 1600),
        improvement_request=clean_optional_text(improvement_request, 1200),
        photo_url=await save_photo(photo),
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post_to_response(get_post_or_404(db, post.id), current_user=current_user)


@posts_router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return post_to_response(
        get_post_or_404(db, post_id),
        include_comments=True,
        current_user=current_user,
    )


@posts_router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    domain: str = Form(...),
    business_summary: str = Form(...),
    business_idea: str = Form(...),
    improvement_request: str | None = Form(None),
    remove_photo: bool = Form(False),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = get_post_or_404(db, post_id)

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes editar tus propios posts.",
        )

    post.domain = clean_text(domain, "El dominio", 255)
    post.business_summary = clean_text(business_summary, "Que hace", 1200)
    post.business_idea = clean_text(business_idea, "La idea de negocio", 1600)
    post.improvement_request = clean_optional_text(improvement_request, 1200)

    new_photo_url = await save_photo(photo)

    if remove_photo or new_photo_url:
        delete_photo(post.photo_url)
        post.photo_url = new_photo_url

    db.commit()

    return post_to_response(
        get_post_or_404(db, post.id),
        include_comments=True,
        current_user=current_user,
    )


@posts_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = get_post_or_404(db, post_id)

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes borrar tus propios posts.",
        )

    delete_photo(post.photo_url)
    db.delete(post)
    db.commit()


@posts_router.post("/{post_id}/like", response_model=PostResponse)
def toggle_post_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_post_or_404(db, post_id)

    existing_like = (
        db.query(PostLike)
        .filter(
            PostLike.post_id == post_id,
            PostLike.user_id == current_user.id,
        )
        .first()
    )

    if existing_like:
        db.delete(existing_like)
    else:
        db.add(PostLike(post_id=post_id, user_id=current_user.id))

    db.commit()

    return post_to_response(
        get_post_or_404(db, post_id),
        include_comments=True,
        current_user=current_user,
    )


@posts_router.post("/{post_id}/comments", response_model=CommentResponse)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_post_or_404(db, post_id)
    body = clean_text(payload.body, "El comentario", 1000)

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        body=body,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment_to_response(
        db.query(Comment)
        .options(selectinload(Comment.author))
        .filter(Comment.id == comment.id)
        .first()
    )


@comments_router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = (
        db.query(Comment)
        .options(selectinload(Comment.author))
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado.",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes editar tus propios comentarios.",
        )

    comment.body = clean_text(payload.body, "El comentario", 1000)
    db.commit()
    db.refresh(comment)

    return comment_to_response(comment)


@comments_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado.",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes borrar tus propios comentarios.",
        )

    db.delete(comment)
    db.commit()
