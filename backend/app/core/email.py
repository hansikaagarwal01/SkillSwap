import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional
from app.core.config import settings

logger = logging.getLogger("skillswap.email")

def send_marketplace_inquiry_email(
    seller_email: str,
    seller_name: str,
    buyer_name: str,
    buyer_roll_no: str,
    buyer_email: str,
    product_title: str,
    inquiry_message: str,
) -> Tuple[bool, str, Optional[str]]:
    """
    Sends an email notification to the seller regarding a new buyer inquiry.
    Uses authentic stored emails from the STUDENT table.
    
    Returns:
        (success: bool, delivery_status: str, error_message: Optional[str])
        delivery_status is one of: 'SENT', 'FAILED', 'SKIPPED'
    """
    subject = f"New Inquiry for Your Product on SkillSwap JKLU - {product_title}"

    body = f"""Hello {seller_name},

You have received a new inquiry about your marketplace listing.

Product: {product_title}
Buyer: {buyer_name}
Buyer Roll_No: {buyer_roll_no}
Buyer Email: {buyer_email}

Message:
{inquiry_message}

Please log in to SkillSwap JKLU to view and respond to this inquiry.

Regards,
SkillSwap JKLU
"""

    # If SMTP is not configured (typical for local dev/testing), log safely and mark SKIPPED
    if not settings.SMTP_HOST:
        logger.info(
            "[DEV EMAIL DISPATCH (SMTP not configured)] To: %s | Subject: %s | Content: %s",
            seller_email,
            subject,
            body.replace("\n", " "),
        )
        return True, "SKIPPED", None

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = seller_email

        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            if settings.SMTP_PORT == 587:
                server.starttls()
                server.ehlo()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, [seller_email], msg.as_string())

        logger.info("Successfully dispatched inquiry notification email to %s", seller_email)
        return True, "SENT", None
    except Exception as exc:
        err_msg = f"SMTP dispatch failed: {str(exc)}"
        logger.warning(err_msg)
        return False, "FAILED", err_msg[:255]


def send_verification_email(
    email: str,
    name: str,
    roll_no: str,
    raw_token: str,
) -> Tuple[bool, str, Optional[str]]:
    """
    Sends an account verification email containing a secure single-use token link.
    When SMTP_HOST is not configured, logs to console in development and returns SKIPPED.

    Returns:
        (success: bool, delivery_status: str, error_message: Optional[str])
    """
    verify_url = f"{settings.FRONTEND_ORIGIN}/verify-email?token={raw_token}"
    subject = "Verify Your SkillSwap JKLU Account"

    body = f"""Hello {name},

Thank you for registering on SkillSwap JKLU (Roll No: {roll_no}).

Please verify your university student email address by opening the link below:
{verify_url}

This verification link is valid for 24 hours and can only be used once.

If you did not register for SkillSwap JKLU, please ignore this email.

Best regards,
SkillSwap JKLU Team
JK Lakshmipat University, Jaipur
"""

    if not settings.SMTP_HOST:
        logger.info(
            "[DEV EMAIL DISPATCH (SMTP not configured)] Verification To: %s | URL: %s",
            email,
            verify_url,
        )
        return True, "SKIPPED", None

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = email

        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            if settings.SMTP_PORT == 587:
                server.starttls()
                server.ehlo()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, [email], msg.as_string())

        logger.info("Successfully dispatched verification email to %s", email)
        return True, "SENT", None
    except Exception as exc:
        err_msg = f"SMTP dispatch failed: {str(exc)}"
        logger.warning(err_msg)
        return False, "FAILED", err_msg[:255]
