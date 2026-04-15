#!/usr/bin/env python3
"""
Email Service — SMTP-based email delivery using Python's built-in smtplib.

No third-party libraries required. Connects via STARTTLS (port 587) to the
configured SMTP host. All credentials are loaded from Settings (i.e. .env).
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Thin wrapper around smtplib for sending transactional emails.

    All methods are static — no instance state needed.
    """

    # ── Internal helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _build_message(
        to_email: str,
        subject: str,
        html_body: str,
        plain_text_url: str | None = None,
    ) -> MIMEMultipart:
        """
        Construct a MIMEMultipart email with an optional plain-text part and an HTML body.

        When plain_text_url is provided it is attached as the first (plain-text)
        part.  Most email clients (including Gmail on Android) auto-detect bare
        URLs in plain-text parts and make them tappable — even when the HTML
        <a href> for custom URI schemes is blocked.

        Args:
            to_email       (str): Recipient email address.
            subject        (str): Email subject line.
            html_body      (str): HTML content of the email.
            plain_text_url (str): Optional raw URL to embed in the plain-text part.

        Returns:
            MIMEMultipart: Ready-to-send MIME message object.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        msg["To"]      = to_email

        # Plain-text part (shown by clients that don't render HTML, and
        # auto-detected as a tappable link by Gmail mobile even for custom schemes)
        if plain_text_url:
            plain_body = (
                f"Reset your Beauty Assistant password by opening the link below on your phone:\n\n"
                f"{plain_text_url}\n\n"
                f"This link expires in 1 hour. If you didn't request this, ignore this email."
            )
            msg.attach(MIMEText(plain_body, "plain"))

        # Attach HTML part (preferred by desktop email clients)
        msg.attach(MIMEText(html_body, "html"))
        return msg

    @staticmethod
    def _send(to_email: str, msg: MIMEMultipart) -> None:
        """
        Open an SMTP connection with STARTTLS and deliver the message.

        Raises:
            smtplib.SMTPException: Re-raised after logging; lets callers decide
                                   whether to surface the error to the user.
        """
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls()          # Upgrade to TLS
                server.ehlo()
                server.login(settings.smtp_username, settings.smtp_password)
                server.sendmail(
                    from_addr=settings.smtp_from_email,
                    to_addrs=[to_email],
                    msg=msg.as_string(),
                )
            logger.info("Email sent successfully to %s", to_email)
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "SMTP authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD in .env"
            )
            raise
        except smtplib.SMTPException as exc:
            logger.error("Failed to send email to %s: %s", to_email, exc)
            raise

    # ── Public API ─────────────────────────────────────────────────────────────

    @staticmethod
    def send_reset_password_email(to_email: str, reset_link: str) -> None:
        """
        Send a branded password-reset email containing a one-time link.

        The link is valid for 1 hour (enforced by the token expiry in the DB).

        Args:
            to_email   (str): The user's registered email address.
            reset_link (str): The full URL the user clicks to reset their password.
                              e.g. http://localhost:3000/reset-password?token=<uuid>

        Raises:
            smtplib.SMTPException: If the email could not be delivered.
        """
        subject = "Reset Your Beauty Assistant Password"

        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>Password Reset</title>
            <style>
                body      {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #f9f6f2; margin: 0; padding: 0; }}
                .wrapper  {{ max-width: 560px; margin: 40px auto; background: #ffffff; border-radius: 12px;
                             box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }}
                .header   {{ background: linear-gradient(135deg, #c9946a 0%, #e8c9a8 100%);
                             padding: 36px 40px; text-align: center; }}
                .header h1{{ color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; }}
                .body     {{ padding: 36px 40px; color: #4a4a4a; line-height: 1.7; }}
                .body p   {{ margin: 0 0 16px; }}
                .cta      {{ text-align: center; margin: 32px 0; }}
                .btn      {{ display: inline-block; background: #c9946a; color: #ffffff !important;
                             text-decoration: none; padding: 14px 36px; border-radius: 8px;
                             font-size: 15px; font-weight: 600; letter-spacing: 0.3px; }}
                .link-box {{ background: #f9f6f2; border: 1px solid #e0d5cc; border-radius: 8px;
                             padding: 16px 20px; margin: 24px 0; word-break: break-all; opacity: 0.8; }}
                .link-box p {{ margin: 0 0 8px; font-size: 12px; font-weight: bold; color: #999; text-transform: uppercase; }}
                .link-box a {{ color: #c9946a; font-size: 13px; font-weight: 500;
                               text-decoration: underline; word-break: break-all; }}
                .steps    {{ background: #fff8f3; border-left: 3px solid #c9946a;
                             padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 16px 0; }}
                .steps p  {{ margin: 4px 0; font-size: 13px; color: #666; }}
                .footer   {{ background: #f9f6f2; padding: 20px 40px; text-align: center;
                             font-size: 12px; color: #aaa; }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="header">
                    <h1>Beauty Assistant</h1>
                </div>
                <div class="body">
                    <p>Hi there,</p>
                    <p>
                        We received a request to reset your <strong>Beauty Assistant</strong> account password.
                        This link is valid for <strong>1 hour</strong>.
                    </p>
                    
                    <div class="cta">
                        <a href="{reset_link}" class="btn">Reset My Password</a>
                    </div>

                    <p><strong>How it works:</strong></p>
                    <div class="steps">
                        <p>1️⃣ Tap the button above (or the link below)</p>
                        <p>2️⃣ Your browser will open and automatically launch the app</p>
                        <p>3️⃣ You will be redirected to the password reset screen</p>
                    </div>

                    <div class="link-box">
                        <p>Direct Link Fallback</p>
                        <a href="{reset_link}">{reset_link}</a>
                    </div>
                    <p>
                        If you didn't request a password reset, you can safely ignore this email —
                        your password will remain unchanged.
                    </p>
                </div>
                <div class="footer">
                    &copy; 2025 Beauty Assistant &middot; This is an automated message, please do not reply.
                </div>
            </div>
        </body>
        </html>
        """

        msg = EmailService._build_message(to_email, subject, html_body, reset_link)
        EmailService._send(to_email, msg)
