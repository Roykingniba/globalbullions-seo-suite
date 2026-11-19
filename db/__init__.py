"""Database access for the Kai SEO Suite foundation.

Deliberately thin. No ORM, because the query surface is small and an ORM would
add import cost to an app that already pays ~60s of cold start importing torch.

Connections are per-request and closed by teardown. There is no pool: LiteSpeed
runs a small number of processes here, and a pool that outlives a request tends
to hand out sockets MySQL has already timed out.
"""

import os
import pathlib

import pymysql
from pymysql.cursors import DictCursor

_ENV_LOADED = False


def _load_env():
    """Read ~/seo_suite/.env once.

    Credentials live in a chmod 600 file rather than in the code or in the
    Passenger .htaccess, because that .htaccess sits under the web root.
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    path = pathlib.Path(__file__).resolve().parent.parent / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            # Only fill gaps: a real environment variable should win over the file.
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    _ENV_LOADED = True


def config():
    _load_env()
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "user": os.environ.get("DB_USER", ""),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", ""),
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False,
        # Fail fast rather than hanging a web request on a wedged socket.
        "connect_timeout": 8,
        "read_timeout": 30,
        "write_timeout": 30,
    }


def is_configured():
    cfg = config()
    return bool(cfg["user"] and cfg["database"])


def connect():
    if not is_configured():
        raise RuntimeError(
            "Database is not configured. Set DB_NAME, DB_USER and DB_PASSWORD "
            "in seo_suite/.env"
        )
    return pymysql.connect(**config())


# ── Flask integration ─────────────────────────────────────────────────────

def get_conn():
    """Connection for the current request, opened lazily and reused."""
    from flask import g
    if not hasattr(g, "_db_conn"):
        g._db_conn = connect()
    return g._db_conn


def close_conn(exc=None):
    from flask import g
    conn = g.pop("_db_conn", None)
    if conn is None:
        return
    try:
        # An unhandled exception must not leave a half-finished transaction
        # to be committed by whatever runs next on this connection.
        if exc is None:
            conn.commit()
        else:
            conn.rollback()
    finally:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_conn)


# ── Query helpers ─────────────────────────────────────────────────────────
# Every helper takes parameters separately. Never build SQL with f-strings or
# concatenation: that is how a signup form becomes an injection point.

def query(sql, args=None):
    with get_conn().cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchall()


def query_one(sql, args=None):
    with get_conn().cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchone()


def execute(sql, args=None):
    """Run a write and return the affected row count."""
    with get_conn().cursor() as cur:
        return cur.execute(sql, args or ())


def insert(sql, args=None):
    """Run an INSERT and return the new auto-increment id."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.lastrowid


def commit():
    get_conn().commit()


def rollback():
    get_conn().rollback()


# ── Standalone use (cron runner, migrations) ──────────────────────────────

class standalone:
    """Context manager for code with no Flask request context.

    Commits on clean exit, rolls back on exception. The cron job runner uses
    this, since it has no request to hang a connection off.

        with standalone() as conn:
            with conn.cursor() as cur:
                cur.execute(...)
    """

    def __enter__(self):
        self.conn = connect()
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()
        return False
