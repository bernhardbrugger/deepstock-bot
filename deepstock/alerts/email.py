"""Email alert delivery via SMTP."""

from __future__ import annotations

import logging
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    to_address: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None,
) -> bool:
    """Send an email alert via SMTP.

    Args:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port.
        smtp_user: SMTP username.
        smtp_password: SMTP password.
        to_address: Recipient email address.
        subject: Email subject.
        body_html: HTML body content.
        body_text: Plain text fallback (auto-generated if not provided).

    Returns:
        True if email was sent successfully.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_address

    if not body_text:
        body_text = re.sub(r"<[^>]+>", "", body_html)

    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Sent email alert to %s: %s", to_address, subject)
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check credentials.")
        return False
    except smtplib.SMTPException as e:
        logger.error("SMTP error: %s", e)
        return False
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False
