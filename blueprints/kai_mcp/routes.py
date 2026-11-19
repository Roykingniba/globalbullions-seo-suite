import datetime
import os

from flask import Blueprint, Response, abort, redirect, render_template, request, send_file, url_for

from blueprints.auth.routes import client_ip, current_user, login_required
from blueprints.auth import logic as auth_logic
import db
from utils import xlsx
from . import logic

bp = Blueprint("kai_mcp", __name__)

FAQS = [
    {"q": "What is a WordPress MCP server?",
     "a": "It is a connection point that lets an AI assistant work on your WordPress site directly. MCP (Model Context Protocol) is the open standard Claude, ChatGPT, Cursor and other assistants use to connect to outside tools. KAI MCP adds an MCP server to your site, so the assistant can read content and carry out admin tasks itself instead of only telling you what to click."},
    {"q": "How do I connect Claude to my WordPress site?",
     "a": "Install KAI MCP, open KAI Vibe, Connect in your dashboard and copy your site's address for AI. In Claude go to Settings, Connectors, Add custom connector, and paste the address. Claude opens a WordPress page where you log in and press Connect. ChatGPT, Claude Code and Cursor work the same way."},
    {"q": "Which AI assistants work with KAI MCP?",
     "a": "Any app that supports MCP, including Claude, ChatGPT, Claude Code, Cursor, VS Code, Windsurf and automation tools such as n8n. It is not tied to one AI company, so you can switch assistants without changing anything on the site."},
    {"q": "Is MCP WordPress integration safe and secure?",
     "a": "With KAI MCP the assistant acts as the WordPress user who approved it, so it can never do more than that account can. Risky actions such as permanent deletes, plugin installs, file edits and site-wide search-and-replace wait for your approval, every change can be undone, all activity is logged, and connections only work over HTTPS. For content-only work, use the Content editor preset and an Editor account."},
    {"q": "Is KAI MCP free?",
     "a": "Yes. It is a free download. You only need a free Kai SEO Suite account to download it."},
    {"q": "Does it work with Elementor and other page builders?",
     "a": "Yes. Page builders store layouts outside the normal post content, so ordinary edits either do nothing or break the page. KAI MCP reads and writes Elementor, Divi, Beaver Builder, Bricks, Breakdance, Oxygen and WPBakery layouts in their own format and clears the builder cache afterwards."},
    {"q": "Can it manage a WooCommerce store?",
     "a": "Yes. It can search products, change prices, sale prices and stock, look up orders, update order status and produce sales reports. These tools only appear when WooCommerce is active, and they go through WooCommerce's own functions so totals stay correct."},
    {"q": "Will it publish things without asking?",
     "a": "New posts are saved as drafts unless you ask for them to be published. Deleting, installing and other risky actions always stop for your approval while approvals are switched on, which is the default."},
    {"q": "What if the assistant gets something wrong?",
     "a": "Open KAI Vibe, then Changes, and press Undo on the change you want reversed. The previous version is kept for every edit, including custom fields, settings, categories and theme files, which WordPress does not normally keep history for."},
    {"q": "Does my content pass through your servers?",
     "a": "No. There is no service in the middle. Your site connects straight to the assistant you chose, and the plugin collects no analytics."},
    {"q": "Do I need to be technical to set it up?",
     "a": "No. You upload the plugin like any other, paste one address into your assistant and press Connect in WordPress. There are no API keys or passwords to paste into a chat."},
    {"q": "What does my site need?",
     "a": "WordPress 6.4 or later, PHP 7.4 or later, and HTTPS. The plugin will not accept a connection over an unencrypted link."},
    {"q": "Will it slow down my website?",
     "a": "No. It does nothing for normal visitors. It only runs when a connected assistant sends a request."},
    {"q": "Can I remove it cleanly?",
     "a": "Yes. Deleting the plugin destroys every key and removes all of its data and database tables."},
]


@bp.route("/kai-mcp")
def landing():
    user = current_user()
    plugin = logic.plugin_info()
    # ?thanks=1 comes from get_plugin below: show the thank-you message and
    # start the download from the page, so the visitor ends up on the setup
    # steps instead of being left on the sign-in form.
    thanks = bool(user and plugin and request.args.get("thanks"))
    return render_template("kai_mcp/landing.html", plugin=plugin,
                           user=user, faqs=FAQS, thanks=thanks)


@bp.route("/kai-mcp/get")
@login_required
def get_plugin():
    """Every Download button and the sign-in/sign-up return address point
    here. It sends the visitor back to the landing page's how-to section with
    a thank-you message; that page then fetches the file itself."""
    return redirect(url_for("kai_mcp.landing", thanks=1) + "#thank-you")


@bp.route("/kai-mcp/download")
@login_required
def download():
    """Signed-in users only; login_required sends everyone else to sign in
    (or sign up) and straight back here afterwards."""
    info = logic.plugin_info()
    if not info:
        abort(404)
    user = current_user()
    try:
        auth_logic.audit(user["id"], "kai_mcp.download", "plugin", info.get("version"),
                         {"file": info["download_name"]}, ip=client_ip())
        db.commit()
    except Exception:
        # Logging must never block the download itself.
        try:
            db.rollback()
        except Exception:
            pass
    resp = send_file(info["path"], mimetype="application/zip", as_attachment=True,
                     download_name=info["download_name"], max_age=0)
    resp.headers["Cache-Control"] = "private, no-store"
    resp.headers["X-Robots-Tag"] = "noindex"
    return resp


# ── Admin: sign-ups export ────────────────────────────────────────────────

def admin_emails():
    """Accounts allowed to export sign-ups. Override with ADMIN_EMAILS in .env
    (comma-separated) without touching code."""
    db._load_env()
    raw = os.environ.get("ADMIN_EMAILS", "roykingniba@gmail.com")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def is_admin(user):
    return bool(user and (user.get("email") or "").lower() in admin_emails())


@bp.route("/admin/signups.xlsx")
@login_required
def signups_export():
    """Excel workbook of every account, plus every KAI MCP download.
    Admin only: anyone else gets a 404 so the URL reveals nothing."""
    if not is_admin(current_user()):
        abort(404)

    users = db.query(
        "SELECT u.id, u.email, u.display_name, u.status, u.email_verified, "
        "u.created_at, u.last_login_at, "
        "(SELECT COUNT(*) FROM audit_log a WHERE a.user_id = u.id AND a.action = 'kai_mcp.download') AS downloads, "
        "(SELECT MAX(a.created_at) FROM audit_log a WHERE a.user_id = u.id AND a.action = 'kai_mcp.download') AS last_download "
        "FROM users u ORDER BY u.created_at DESC"
    )
    dls = db.query(
        "SELECT a.created_at, u.email, u.display_name, a.target_id AS version "
        "FROM audit_log a LEFT JOIN users u ON u.id = a.user_id "
        "WHERE a.action = 'kai_mcp.download' ORDER BY a.created_at DESC"
    )

    signups = [[
        r["id"], r["email"], r["display_name"] or "", r["status"],
        bool(r["email_verified"]), r["created_at"], r["last_login_at"],
        int(r["downloads"] or 0), r["last_download"],
    ] for r in users]
    downloads = [[r["created_at"], r["email"] or "(deleted account)",
                  r["display_name"] or "", r["version"] or ""] for r in dls]

    data = xlsx.build([
        ("Sign-ups",
         ["ID", "Email", "Name", "Status", "Email verified", "Signed up (UTC)",
          "Last sign-in (UTC)", "KAI MCP downloads", "Last download (UTC)"],
         signups, [7, 34, 24, 11, 14, 19, 19, 18, 19]),
        ("KAI MCP downloads",
         ["Downloaded (UTC)", "Email", "Name", "Version"],
         downloads, [19, 34, 24, 10]),
    ])
    name = f"globalbullions-signups-{datetime.date.today().isoformat()}.xlsx"
    return Response(data, headers={
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Content-Disposition": f'attachment; filename="{name}"',
        "Cache-Control": "private, no-store",
        "X-Robots-Tag": "noindex",
    })
