import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session as flask_session, url_for)

import db
from . import logic

bp = Blueprint("auth", __name__)


def client_ip():
    """Behind LiteSpeed the real address is in X-Forwarded-For; the first entry
    is the client, later ones are proxies."""
    fwd = request.headers.get("X-Forwarded-For", "")
    return fwd.split(",")[0].strip() if fwd else (request.remote_addr or "")


def current_user():
    """Cached per request so several template lookups do not re-query."""
    if not hasattr(g, "_user"):
        g._user = None
        if db.is_configured():
            try:
                g._user = logic.load_session(request.cookies.get(logic.SESSION_COOKIE))
            except Exception:
                # A database outage must not take the public tool pages down.
                g._user = None
    return g._user


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def _safe_next(raw):
    """Only allow same-site relative paths. An open redirect on a login form is
    a standard phishing primitive: sign in here, get bounced to a lookalike."""
    if raw and raw.startswith("/") and not raw.startswith("//"):
        return raw
    return url_for("auth.dashboard")


def _set_cookie(response, token):
    response.set_cookie(
        logic.SESSION_COOKIE, token,
        max_age=logic.SESSION_DAYS * 86400,
        httponly=True,                      # not readable from JavaScript
        secure=request.is_secure,
        samesite="Lax",                     # blocks cross-site POST/CSRF replay
        path="/",
    )
    return response


# ── Routes ────────────────────────────────────────────────────────────────

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user():
        return redirect(_safe_next(request.args.get("next")))
    error = None
    email = display_name = ""
    if request.method == "POST":
        email = request.form.get("email", "")
        display_name = request.form.get("display_name", "")
        try:
            if not db.is_configured():
                raise logic.AuthError("Accounts are not available yet. Try again shortly.")
            user_id = logic.create_user(email, request.form.get("password", ""),
                                        display_name, ip=client_ip())
            token = logic.start_session(user_id, client_ip(),
                                        request.headers.get("User-Agent"))
            resp = redirect(_safe_next(request.args.get("next") or request.form.get("next")))
            return _set_cookie(resp, token)
        except logic.AuthError as e:
            error = str(e)
        except Exception:
            db.rollback()
            error = "Something went wrong creating your account. Try again."
    return render_template("auth/signup.html", error=error, email=email,
                           display_name=display_name, next=request.args.get("next", ""))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(_safe_next(request.args.get("next")))
    error = None
    email = ""
    if request.method == "POST":
        email = request.form.get("email", "")
        try:
            if not db.is_configured():
                raise logic.AuthError("Sign-in is not available yet. Try again shortly.")
            user = logic.authenticate(email, request.form.get("password", ""),
                                      ip=client_ip())
            token = logic.start_session(user["id"], client_ip(),
                                        request.headers.get("User-Agent"))
            resp = redirect(_safe_next(request.args.get("next") or request.form.get("next")))
            return _set_cookie(resp, token)
        except logic.AuthError as e:
            error = str(e)
        except Exception:
            db.rollback()
            error = "Something went wrong signing you in. Try again."
    return render_template("auth/login.html", error=error, email=email,
                           next=request.args.get("next", ""))


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Ask for an email and send a reset link. The reply is identical whether
    or not the address has an account."""
    sent = False
    error = None
    email = request.form.get("email", "") if request.method == "POST" else request.args.get("email", "")
    if request.method == "POST":
        try:
            if not db.is_configured():
                raise logic.AuthError("Password reset is not available yet. Try again shortly.")
            user, token = logic.request_password_reset(email, ip=client_ip())
            if user:
                from config import config
                from utils import mailer
                link = f"{config.site_url.rstrip('/')}{url_for('auth.reset_password', token=token)}"
                name = user.get("display_name") or "there"
                mailer.send(
                    user["email"],
                    "Reset your Kai SEO Suite password",
                    render_template("auth/email_reset.txt", name=name, link=link,
                                    minutes=logic.RESET_MINUTES),
                    render_template("auth/email_reset.html", name=name, link=link,
                                    minutes=logic.RESET_MINUTES),
                )
            sent = True
        except logic.AuthError as e:
            error = str(e)
        except Exception:
            db.rollback()
            error = "Something went wrong. Try again in a few minutes."
    return render_template("auth/forgot_password.html", sent=sent, error=error, email=email)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    error = None
    try:
        valid = bool(db.is_configured() and logic.check_reset_token(token))
    except Exception:
        db.rollback()
        valid = False
    if valid and request.method == "POST":
        new_pw = request.form.get("password", "")
        if new_pw != request.form.get("password2", ""):
            error = "The two passwords do not match."
        else:
            try:
                user_id = logic.reset_password(token, new_pw, ip=client_ip())
                session_token = logic.start_session(user_id, client_ip(),
                                                    request.headers.get("User-Agent"))
                flash("Your password has been changed and you are signed in.", "info")
                return _set_cookie(redirect(url_for("auth.dashboard")), session_token)
            except logic.AuthError as e:
                error = str(e)
            except Exception:
                db.rollback()
                error = "Something went wrong. Try again."
    resp = render_template("auth/reset_password.html", valid=valid, error=error)
    return resp, 200, {"Referrer-Policy": "no-referrer", "X-Robots-Tag": "noindex"}


@bp.route("/logout", methods=["POST"])
def logout():
    logic.end_session(request.cookies.get(logic.SESSION_COOKIE))
    resp = redirect(url_for("home"))
    resp.delete_cookie(logic.SESSION_COOKIE, path="/")
    return resp


@bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    accounts = db.query(
        "SELECT id, platform, display_name, username, status, token_expires_at, "
        "last_synced_at FROM social_accounts WHERE user_id = %s ORDER BY platform",
        (user["id"],),
    )
    sites = db.query(
        "SELECT id, site_url, name, status, niche, posts_published, last_audit_at, "
        "autopilot_enabled FROM wp_sites WHERE user_id = %s ORDER BY created_at DESC",
        (user["id"],),
    )
    posts = db.query(
        "SELECT p.id, p.title, p.status, p.word_count, p.scheduled_for, p.permalink, "
        "s.name AS site_name FROM wp_posts p JOIN wp_sites s ON s.id = p.wp_site_id "
        "WHERE p.user_id = %s ORDER BY p.created_at DESC LIMIT 15",
        (user["id"],),
    )
    scheduled = db.query(
        "SELECT sp.id, sp.body, sp.scheduled_for, sp.status, sa.platform "
        "FROM scheduled_posts sp JOIN social_accounts sa ON sa.id = sp.social_account_id "
        "WHERE sp.user_id = %s AND sp.status IN ('draft','scheduled') "
        "ORDER BY sp.scheduled_for LIMIT 10",
        (user["id"],),
    )
    jobs = db.query(
        "SELECT public_id, kind, status, progress, created_at FROM jobs "
        "WHERE user_id = %s ORDER BY created_at DESC LIMIT 8",
        (user["id"],),
    )
    return render_template("auth/dashboard.html", user=user, accounts=accounts,
                           sites=sites, posts=posts, scheduled=scheduled, jobs=jobs)


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = current_user()
    error = notice = None
    if request.method == "POST":
        try:
            logic.change_password(
                user["id"],
                request.form.get("current_password", ""),
                request.form.get("new_password", ""),
                keep_token=request.cookies.get(logic.SESSION_COOKIE),
            )
            notice = "Password updated. You have been signed out on other devices."
        except logic.AuthError as e:
            error = str(e)
        except Exception:
            db.rollback()
            error = "Could not update your password. Try again."
    sessions = db.query(
        "SELECT id, created_at, expires_at, user_agent FROM sessions "
        "WHERE user_id = %s AND revoked_at IS NULL AND expires_at > NOW() "
        "ORDER BY created_at DESC",
        (user["id"],),
    )
    return render_template("auth/account.html", user=user, error=error,
                           notice=notice, sessions=sessions)
