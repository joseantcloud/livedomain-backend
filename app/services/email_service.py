import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    En local, si no configurás SMTP_HOST, el email se imprime en consola.
    En producción, configurás SMTP_HOST, SMTP_USER y SMTP_PASSWORD.
    """

    if not settings.SMTP_HOST:
        print("\n================ LIVE DOMAIN EMAIL ================")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(body)
        print("===================================================\n")
        return

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    if settings.SMTP_PORT == 465:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            smtp.send_message(message)
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()

            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            smtp.send_message(message)


def send_verification_email(to_email: str, token: str) -> None:
    verification_url = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"

    subject = "Verifica tu cuenta de LiveDomain"

    body = f"""
Hola,

Gracias por registrarte en LiveDomain.

Para verificar tu correo electrónico, abrí este enlace:

{verification_url}

Si no creaste esta cuenta, podés ignorar este correo.

LiveDomain Team
"""

    send_email(to_email, subject, body)


def send_password_reset_email(to_email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"

    subject = "Restablece tu contraseña de LiveDomain"

    body = f"""
Hola,

Recibimos una solicitud para restablecer tu contraseña.

Abrí este enlace para crear una nueva contraseña:

{reset_url}

Si no solicitaste este cambio, podés ignorar este correo.

LiveDomain Team
"""

    send_email(to_email, subject, body)