from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable

from logging_config import setup_logger

log = setup_logger()


def send_mail(
    subject: str,
    body: str,
    to: Iterable[str],
    attachments: Iterable[Path] = (),
    sender: str = "",
    smtp_server: str = "",
    smtp_port: int = 587,
    smtp_user: str = "",
    smtp_pass: str = "",
):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.set_content(body)

    for path in attachments:
        if path and path.exists():
            msg.add_attachment(
                path.read_bytes(),
                maintype="text",
                subtype="plain",
                filename=path.name,
            )

    with smtplib.SMTP(smtp_server, smtp_port) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)

    log.info("Mail enviado | subject=%s | to=%s", subject, to)
