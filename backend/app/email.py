import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from .config import get_settings

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, html_content: str, text_content: str | None = None) -> bool:
    """Send an email using SMTP configuration."""
    settings = get_settings()

    if not settings.smtp_host:
        logger.warning(f"SMTP not configured. Would send email to {to_email}: {subject}")
        # In development, log the email content for testing
        logger.info(f"Email content:\n{text_content or html_content}")
        return True  # Return True in dev mode so registration works

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        message["To"] = to_email

        # Add plain text and HTML versions
        if text_content:
            message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        # Connect and send
        context = ssl.create_default_context()

        if settings.smtp_use_tls:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls(context=context)
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from_email, to_email, message.as_string())
        else:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from_email, to_email, message.as_string())

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def send_verification_email(to_email: str, verification_token: str, user_name: str | None = None) -> bool:
    """Send email verification email with a verification link."""
    settings = get_settings()

    verification_url = f"{settings.app_url}/verify-email?token={verification_token}"
    greeting = f"Hi {user_name}" if user_name else "Hi"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Clarynt</h1>
        </div>
        <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">Verify your email address</h2>
            <p>{greeting},</p>
            <p>Thanks for signing up for Clarynt! Please verify your email address by clicking the button below:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block;">Verify Email Address</a>
            </div>
            <p style="color: #666; font-size: 14px;">Or copy and paste this link into your browser:</p>
            <p style="color: #667eea; font-size: 14px; word-break: break-all;">{verification_url}</p>
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
            <p style="color: #999; font-size: 12px; margin-bottom: 0;">This link will expire in 24 hours. If you didn't create an account with Clarynt, you can safely ignore this email.</p>
        </div>
    </body>
    </html>
    """

    text_content = f"""{greeting},

Thanks for signing up for Clarynt! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account with Clarynt, you can safely ignore this email.

- The Clarynt Team
"""

    return await send_email(
        to_email=to_email,
        subject="Verify your Clarynt email address",
        html_content=html_content,
        text_content=text_content
    )
