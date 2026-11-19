"""Outgoing email.

Uses SMTP when SMTP_HOST is set in .env (SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
SMTP_SSL=true/false), otherwise the server's own sendmail, which shared
hosting provides for PHP's mail() and needs no credentials.

Failures are written to data/mail.log so a reset email that never arrives can
be diagnosed from the file manager.
"""

import datetime
import os
import smtplib
import subprocess
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

import db

_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mail.log")


def _log(line):
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S} {line}\n")
    except OSError:
        pass


def send(to, subject, text, html=None):
    """Send one email. Returns True on success; never raises."""
    db._load_env()
    sender_addr = os.environ.get("MAIL_FROM", "no-reply@globalbullions.com")
    sender_name = os.environ.get("MAIL_FROM_NAME", "Kai SEO Suite")

    msg = EmailMessage()
    msg["From"] = formataddr((sender_name, sender_addr))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=sender_addr.split("@")[-1])
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    host = os.environ.get("SMTP_HOST", "").strip()
    try:
        if host:
            port = int(os.environ.get("SMTP_PORT", "465"))
            use_ssl = os.environ.get("SMTP_SSL", "true").lower() != "false"
            cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
            with cls(host, port, timeout=20) as s:
                if not use_ssl:
                    s.starttls()
                user = os.environ.get("SMTP_USER", "")
                if user:
                    s.login(user, os.environ.get("SMTP_PASSWORD", ""))
                s.send_message(msg)
        else:
            binary = next((p for p in ("/usr/sbin/sendmail", "/usr/lib/sendmail", "/usr/bin/sendmail")
                           if os.path.exists(p)), None)
            if not binary:
                raise RuntimeError("no sendmail binary found and SMTP_HOST is not set")
            proc = subprocess.run([binary, "-t", "-i", "-f", sender_addr],
                                  input=msg.as_bytes(), capture_output=True, timeout=30)
            if proc.returncode != 0:
                raise RuntimeError(f"sendmail exit {proc.returncode}: {proc.stderr.decode(errors='replace')[:300]}")
        _log(f"sent '{subject}' to {to}")
        return True
    except Exception as e:  # noqa: BLE001 - mail must never take a page down
        _log(f"FAILED '{subject}' to {to}: {e!r}")
        return False
