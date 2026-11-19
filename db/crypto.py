"""Encryption for stored OAuth tokens, and password hashing.

Why tokens are encrypted rather than just stored in a private table:
a database dump is the most common way credentials leak, via a stray backup,
a misconfigured phpMyAdmin, or a support export. With the key held outside the
database, a dump on its own cannot post to anybody's social account.

Key material lives in seo_suite/.env (chmod 600), never in the repo and never
in the Passenger .htaccess, which sits under the web root.
"""

import base64
import hashlib
import hmac
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from . import _load_env

# Bump when introducing a new key. Old rows record the version that encrypted
# them, so both can be read while re-encryption happens in the background.
CURRENT_KEY_VERSION = 1

_NONCE_BYTES = 12   # AES-GCM standard nonce size
_KEY_BYTES = 32     # AES-256


class CryptoNotConfigured(RuntimeError):
    pass


def _key(version=CURRENT_KEY_VERSION):
    _load_env()
    raw = os.environ.get(f"TOKEN_KEY_V{version}") or (
        os.environ.get("TOKEN_KEY") if version == 1 else None
    )
    if not raw:
        raise CryptoNotConfigured(
            f"TOKEN_KEY_V{version} is not set. Generate one with "
            "`python -m db.crypto --generate-key` and put it in seo_suite/.env"
        )
    try:
        key = base64.urlsafe_b64decode(raw)
    except Exception as exc:
        raise CryptoNotConfigured(f"TOKEN_KEY_V{version} is not valid base64") from exc
    if len(key) != _KEY_BYTES:
        raise CryptoNotConfigured(
            f"TOKEN_KEY_V{version} must decode to {_KEY_BYTES} bytes, got {len(key)}"
        )
    return key


def encrypt(plaintext, aad=None, version=CURRENT_KEY_VERSION):
    """Encrypt a token. Returns bytes for a BLOB column.

    `aad` is authenticated but not encrypted. Passing something that binds the
    ciphertext to its row, such as f"social:{account_id}", means a value copied
    into a different row fails to decrypt instead of silently working.
    """
    if plaintext is None:
        return None
    if isinstance(plaintext, str):
        plaintext = plaintext.encode("utf-8")
    nonce = secrets.token_bytes(_NONCE_BYTES)
    ct = AESGCM(_key(version)).encrypt(nonce, plaintext, _aad(aad))
    return nonce + ct


def decrypt(blob, aad=None, version=CURRENT_KEY_VERSION):
    """Decrypt a token blob back to str. Returns None for NULL columns."""
    if blob is None:
        return None
    if len(blob) <= _NONCE_BYTES:
        raise ValueError("ciphertext too short to contain a nonce")
    nonce, ct = blob[:_NONCE_BYTES], blob[_NONCE_BYTES:]
    return AESGCM(_key(version)).decrypt(nonce, ct, _aad(aad)).decode("utf-8")


def _aad(aad):
    if aad is None:
        return None
    return aad.encode("utf-8") if isinstance(aad, str) else aad


def generate_key():
    """A new base64 key suitable for TOKEN_KEY_V1."""
    return base64.urlsafe_b64encode(secrets.token_bytes(_KEY_BYTES)).decode("ascii")


# ── Passwords ─────────────────────────────────────────────────────────────

def hash_password(password):
    """bcrypt hash. Deliberately slow, which is the point."""
    import bcrypt
    if not password:
        raise ValueError("password must not be empty")
    # bcrypt silently truncates beyond 72 bytes, so reject rather than let a
    # long passphrase be quietly shortened.
    pw = password.encode("utf-8")
    if len(pw) > 72:
        raise ValueError("password must be 72 bytes or fewer")
    return bcrypt.hashpw(pw, bcrypt.gensalt(rounds=12)).decode("ascii")


def verify_password(password, hashed):
    import bcrypt
    if not password or not hashed:
        return False
    pw = password.encode("utf-8")
    if len(pw) > 72:
        return False
    try:
        return bcrypt.checkpw(pw, hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


# ── Opaque tokens (sessions, email verification, password reset) ──────────

def new_token():
    """A URL-safe random token. This is the value the user receives."""
    return secrets.token_urlsafe(32)


def token_hash(token):
    """What gets stored. Only the hash goes in the database, so a dump does
    not hand over a set of usable sessions or reset links."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def token_matches(token, stored_hash):
    """Constant-time compare, so timing cannot be used to guess a token."""
    return hmac.compare_digest(token_hash(token), stored_hash or "")


if __name__ == "__main__":
    import sys
    if "--generate-key" in sys.argv:
        print(f"TOKEN_KEY_V{CURRENT_KEY_VERSION}={generate_key()}")
    else:
        print("usage: python -m db.crypto --generate-key")
