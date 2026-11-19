"""Account creation, login, and session handling.

Public signup means these endpoints are reachable by anyone, so the defensive
work lives here rather than in the routes: rate limiting per IP and per account,
lockout after repeated failures, and uniform error messages that do not reveal
whether an email address is registered.
"""

import datetime
import ipaddress
import re

import db
from db import crypto

SESSION_COOKIE = "kai_session"
SESSION_DAYS = 30

# Lockout policy. Deliberately generous on attempts but long on the lock, so a
# real user who mistypes a few times is not punished while a script is.
MAX_FAILED_LOGINS = 8
LOCKOUT_MINUTES = 15

# Rate limits: (max_hits, window_seconds)
LIMITS = {
    "login": (12, 300),
    "signup": (5, 3600),
    "reset": (5, 3600),
}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[^@\s]+$")


class AuthError(Exception):
    """Shown to the user verbatim, so the message must not leak account state."""


# ── Validation ────────────────────────────────────────────────────────────

def normalise_email(raw):
    email = (raw or "").strip().lower()
    if not email or len(email) > 254 or not _EMAIL_RE.match(email):
        raise AuthError("Enter a valid email address.")
    return email


def check_password(password, email=None):
    """Length-first policy. A long passphrase beats a short one with symbols,
    so the only hard rules are a floor, bcrypt's 72-byte ceiling, and a check
    that the password is not simply the email address."""
    pw = password or ""
    if len(pw) < 10:
        raise AuthError("Password must be at least 10 characters.")
    if len(pw.encode("utf-8")) > 72:
        raise AuthError("Password is too long. Use 72 bytes or fewer.")
    if email and pw.strip().lower() == email:
        raise AuthError("Password must not be your email address.")
    if pw.strip().lower() in {"password", "password123", "letmein12345"}:
        raise AuthError("That password is too common. Choose another.")
    return pw


# ── Rate limiting ─────────────────────────────────────────────────────────

def _window_start(seconds):
    now = datetime.datetime.utcnow()
    epoch = int(now.timestamp()) // seconds * seconds
    return datetime.datetime.utcfromtimestamp(epoch)


def rate_limit(action, key):
    """Count one hit. Raises AuthError when the bucket is full.

    Uses INSERT ... ON DUPLICATE KEY UPDATE so the count is atomic; a read then
    write would let concurrent requests slip past the limit.
    """
    max_hits, window = LIMITS.get(action, (30, 300))
    bucket = f"{action}:{key}"[:120]
    start = _window_start(window)

    db.execute(
        "INSERT INTO rate_limits (bucket, window_start, hits) VALUES (%s, %s, 1) "
        "ON DUPLICATE KEY UPDATE hits = hits + 1",
        (bucket, start),
    )
    row = db.query_one(
        "SELECT hits FROM rate_limits WHERE bucket = %s AND window_start = %s",
        (bucket, start),
    )
    if row and row["hits"] > max_hits:
        raise AuthError("Too many attempts. Wait a few minutes and try again.")


def purge_rate_limits():
    """Called from the cron runner. The table is append-heavy and never read
    after its window closes."""
    db.execute(
        "DELETE FROM rate_limits WHERE window_start < %s",
        (datetime.datetime.utcnow() - datetime.timedelta(hours=6),),
    )


# ── Signup ────────────────────────────────────────────────────────────────

def create_user(email, password, display_name=None, ip=None):
    email = normalise_email(email)
    check_password(password, email)

    if ip:
        rate_limit("signup", ip)

    existing = db.query_one("SELECT id FROM users WHERE email = %s", (email,))
    if existing:
        # Deliberately the same shape as a success from the caller's point of
        # view would be better, but a public signup form has to say something.
        # This wording at least does not confirm the address is in use.
        raise AuthError(
            "That email cannot be used to sign up. If you already have an "
            "account, sign in or reset your password instead."
        )

    user_id = db.insert(
        "INSERT INTO users (email, password_hash, display_name, status, email_verified) "
        "VALUES (%s, %s, %s, 'active', 0)",
        (email, crypto.hash_password(password), (display_name or "").strip()[:120] or None),
    )
    audit(user_id, "user.signup", ip=ip)
    db.commit()
    return user_id


# ── Login ─────────────────────────────────────────────────────────────────

def authenticate(email, password, ip=None):
    """Return the user row, or raise AuthError.

    Every failure path raises the same message. Distinguishing "no such user"
    from "wrong password" hands an attacker a free account-enumeration oracle.
    """
    generic = AuthError("Email or password is incorrect.")

    try:
        email = normalise_email(email)
    except AuthError:
        raise generic

    if ip:
        rate_limit("login", ip)

    user = db.query_one(
        "SELECT id, email, password_hash, status, failed_logins, locked_until "
        "FROM users WHERE email = %s",
        (email,),
    )

    if not user:
        # Hash anyway so a missing account is not measurably faster than a
        # wrong password.
        crypto.verify_password(password or "x", "$2b$12$" + "." * 53)
        raise generic

    now = datetime.datetime.utcnow()
    if user["locked_until"] and user["locked_until"] > now:
        raise AuthError(
            "This account is temporarily locked after too many failed attempts. "
            f"Try again in {LOCKOUT_MINUTES} minutes."
        )

    if not crypto.verify_password(password, user["password_hash"]):
        failed = user["failed_logins"] + 1
        lock = now + datetime.timedelta(minutes=LOCKOUT_MINUTES) if failed >= MAX_FAILED_LOGINS else None
        db.execute(
            "UPDATE users SET failed_logins = %s, locked_until = %s WHERE id = %s",
            (failed, lock, user["id"]),
        )
        audit(user["id"], "user.login_failed", ip=ip)
        db.commit()
        raise generic

    if user["status"] == "suspended":
        raise AuthError("This account has been suspended. Contact support.")

    db.execute(
        "UPDATE users SET failed_logins = 0, locked_until = NULL, last_login_at = %s "
        "WHERE id = %s",
        (now, user["id"]),
    )
    audit(user["id"], "user.login", ip=ip)
    db.commit()
    return user


# ── Sessions ──────────────────────────────────────────────────────────────

def start_session(user_id, ip=None, user_agent=None):
    """Create a session and return the raw token for the cookie.

    Only the hash is stored, so a database dump does not yield usable sessions.
    """
    token = crypto.new_token()
    db.insert(
        "INSERT INTO sessions (user_id, token_hash, ip, user_agent, expires_at) "
        "VALUES (%s, %s, %s, %s, %s)",
        (
            user_id,
            crypto.token_hash(token),
            _pack_ip(ip),
            (user_agent or "")[:255] or None,
            datetime.datetime.utcnow() + datetime.timedelta(days=SESSION_DAYS),
        ),
    )
    db.commit()
    return token


def load_session(token):
    """Return the user row for a cookie value, or None."""
    if not token:
        return None
    row = db.query_one(
        "SELECT s.id AS session_id, u.id, u.email, u.display_name, u.status "
        "FROM sessions s JOIN users u ON u.id = s.user_id "
        "WHERE s.token_hash = %s AND s.revoked_at IS NULL AND s.expires_at > %s",
        (crypto.token_hash(token), datetime.datetime.utcnow()),
    )
    if not row or row["status"] == "suspended":
        return None
    return row


def end_session(token):
    if not token:
        return
    db.execute(
        "UPDATE sessions SET revoked_at = %s WHERE token_hash = %s AND revoked_at IS NULL",
        (datetime.datetime.utcnow(), crypto.token_hash(token)),
    )
    db.commit()


def end_all_sessions(user_id, keep_token=None):
    """Sign out everywhere. Used after a password change."""
    sql = "UPDATE sessions SET revoked_at = %s WHERE user_id = %s AND revoked_at IS NULL"
    args = [datetime.datetime.utcnow(), user_id]
    if keep_token:
        sql += " AND token_hash <> %s"
        args.append(crypto.token_hash(keep_token))
    db.execute(sql, tuple(args))
    db.commit()


def purge_sessions():
    """Called from the cron runner."""
    db.execute(
        "DELETE FROM sessions WHERE expires_at < %s",
        (datetime.datetime.utcnow() - datetime.timedelta(days=7),),
    )


def change_password(user_id, current, new_password, keep_token=None):
    row = db.query_one("SELECT email, password_hash FROM users WHERE id = %s", (user_id,))
    if not row or not crypto.verify_password(current, row["password_hash"]):
        raise AuthError("Your current password is incorrect.")
    check_password(new_password, row["email"])
    db.execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (crypto.hash_password(new_password), user_id),
    )
    audit(user_id, "user.password_changed")
    # A password change should invalidate anyone else holding a session.
    end_all_sessions(user_id, keep_token=keep_token)
    db.commit()


# ── Password reset ────────────────────────────────────────────────────────

RESET_MINUTES = 60

_AUTH_TOKENS_DDL = (
    "CREATE TABLE IF NOT EXISTS auth_tokens ("
    " id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,"
    " user_id BIGINT UNSIGNED NOT NULL,"
    " purpose ENUM('verify_email','reset_password') NOT NULL,"
    " token_hash CHAR(64) NOT NULL,"
    " created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    " expires_at DATETIME NOT NULL,"
    " used_at DATETIME NULL,"
    " PRIMARY KEY (id),"
    " UNIQUE KEY uq_auth_tokens_token (token_hash),"
    " KEY idx_auth_tokens_user (user_id, purpose),"
    " CONSTRAINT fk_auth_tokens_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
)


def request_password_reset(email, ip=None):
    """Create a single-use reset token and return (user_row, token), or
    (None, None) when there is no active account for that address.

    The caller must show the same message either way, so the form cannot be
    used to find out which emails have accounts.
    """
    try:
        email = normalise_email(email)
    except AuthError:
        return None, None
    if ip:
        rate_limit("reset", ip)
    rate_limit("reset", "email:" + email)

    user = db.query_one(
        "SELECT id, email, display_name, status FROM users WHERE email = %s", (email,)
    )
    if not user or user["status"] == "suspended":
        db.commit()
        return None, None

    db.execute(_AUTH_TOKENS_DDL)
    now = datetime.datetime.utcnow()
    # Only the newest link works: older unused ones are retired.
    db.execute(
        "UPDATE auth_tokens SET used_at = %s WHERE user_id = %s "
        "AND purpose = 'reset_password' AND used_at IS NULL",
        (now, user["id"]),
    )
    token = crypto.new_token()
    db.execute(
        "INSERT INTO auth_tokens (user_id, purpose, token_hash, expires_at) "
        "VALUES (%s, 'reset_password', %s, %s)",
        (user["id"], crypto.token_hash(token), now + datetime.timedelta(minutes=RESET_MINUTES)),
    )
    audit(user["id"], "user.password_reset_requested", ip=ip)
    db.commit()
    return user, token


def check_reset_token(token):
    """Return the token row (with the user's email) if the link is still
    valid, else None."""
    if not token or len(token) > 200:
        return None
    return db.query_one(
        "SELECT t.id, t.user_id, u.email FROM auth_tokens t JOIN users u ON u.id = t.user_id "
        "WHERE t.token_hash = %s AND t.purpose = 'reset_password' AND t.used_at IS NULL "
        "AND t.expires_at > %s AND u.status <> 'suspended'",
        (crypto.token_hash(token), datetime.datetime.utcnow()),
    )


def reset_password(token, new_password, ip=None):
    """Set a new password from a reset link. Returns the user id."""
    row = check_reset_token(token)
    if not row:
        raise AuthError("This reset link has expired or has already been used. Request a new one.")
    check_password(new_password, row["email"])
    now = datetime.datetime.utcnow()
    db.execute(
        "UPDATE users SET password_hash = %s, failed_logins = 0, locked_until = NULL "
        "WHERE id = %s",
        (crypto.hash_password(new_password), row["user_id"]),
    )
    db.execute("UPDATE auth_tokens SET used_at = %s WHERE id = %s", (now, row["id"]))
    audit(row["user_id"], "user.password_reset", ip=ip)
    db.commit()
    # Anyone holding an old session (possibly whoever guessed the old
    # password) is signed out.
    end_all_sessions(row["user_id"])
    return row["user_id"]


# ── Audit ─────────────────────────────────────────────────────────────────

def audit(user_id, action, target_type=None, target_id=None, detail=None, ip=None):
    import json
    db.insert(
        "INSERT INTO audit_log (user_id, action, target_type, target_id, detail, ip) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, action[:80], target_type, str(target_id) if target_id else None,
         json.dumps(detail) if detail else None, _pack_ip(ip)),
    )


def _pack_ip(ip):
    """Store as packed bytes so IPv4 and IPv6 share one column."""
    if not ip:
        return None
    try:
        return ipaddress.ip_address(ip.split(",")[0].strip()).packed
    except ValueError:
        return None
