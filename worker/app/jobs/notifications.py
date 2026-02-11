from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Iterable

import httpx

from app.config import get_settings


def send_webhook(payload: dict) -> None:
    settings = get_settings()
    if not settings.webhook_url:
        return
    httpx.post(settings.webhook_url, json=payload, timeout=10)


def send_slack(text: str) -> None:
    settings = get_settings()
    if not settings.slack_webhook_url:
        return
    httpx.post(settings.slack_webhook_url, json={"text": text}, timeout=10)


def send_email(subject: str, body: str, to: Iterable[str]) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = ", ".join(to)
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)
