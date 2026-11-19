from datetime import date
from urllib.parse import urlparse

from flask import Flask, render_template, Response, url_for

from config import config
from registry import TOOL_CATEGORIES
from seo_content import get_seo_content

from blueprints.outreach.routes import bp as outreach_bp
from blueprints.classic_seo.routes import bp as classic_seo_bp
from blueprints.audit.routes import bp as audit_bp
from blueprints.geo.routes import bp as geo_bp
from blueprints.converters.routes import bp as converters_bp
from blueprints.linkgraph.routes import bp as linkgraph_bp
from blueprints.content.routes import bp as content_bp
from blueprints.keywords.routes import bp as keywords_bp
from blueprints.generators.routes import bp as generators_bp
from blueprints.utilities.routes import bp as utilities_bp
from blueprints.auth.routes import bp as auth_bp, current_user
from blueprints.kai_mcp.routes import bp as kai_mcp_bp, is_admin as _is_admin
import db


def create_app():
    app = Flask(__name__)
    app.secret_key = config.secret_key

    app.register_blueprint(outreach_bp, url_prefix="/tools/outreach")
    app.register_blueprint(classic_seo_bp, url_prefix="/tools/classic-seo")
    app.register_blueprint(audit_bp, url_prefix="/tools/audit")
    app.register_blueprint(geo_bp, url_prefix="/tools/geo")
    app.register_blueprint(converters_bp, url_prefix="/tools/converters")
    app.register_blueprint(linkgraph_bp, url_prefix="/tools/linkgraph")
    app.register_blueprint(content_bp, url_prefix="/tools/content")
    app.register_blueprint(keywords_bp, url_prefix="/tools/keywords")
    app.register_blueprint(generators_bp, url_prefix="/tools/generators")
    app.register_blueprint(utilities_bp, url_prefix="/tools/utilities")
    app.register_blueprint(auth_bp)
    app.register_blueprint(kai_mcp_bp)

    # Per-request DB connection teardown. Registered even when the database is
    # not configured, so the public tool pages keep working either way.
    db.init_app(app)

    @app.context_processor
    def inject_globals():
        from flask import request

        active_category, active_tool = None, None
        for cat in TOOL_CATEGORIES:
            for tool in cat["tools"]:
                if tool["endpoint"] == request.endpoint:
                    active_category, active_tool = cat, tool
                    break
            if active_tool:
                break

        seo = None
        if active_category and active_tool:
            seo = get_seo_content(active_category["slug"], active_tool["slug"])

        return {
            "categories": TOOL_CATEGORIES,
            "site_url": config.site_url,
            "active_category": active_category,
            "active_tool": active_tool,
            "seo": seo,
            # Drives the header Sign in / Dashboard link. Returns None when the
            # visitor is anonymous or the database is unreachable, so a DB
            # outage degrades to "signed out" rather than a 500 on every page.
            "current_user": current_user(),
            "is_admin": _is_admin(current_user()),
        }

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/robots.txt")
    def robots_txt():
        # NOTE: this app is mounted at a subdirectory (config.site_url's path,
        # e.g. /seo-suite), so this route is only ever reachable at
        # <site_url>/robots.txt — NOT the domain root. Crawlers only ever
        # fetch /robots.txt at the true domain root, so this file is not
        # self-discovering here; the real root robots.txt (owned by whatever
        # else runs on the domain) needs a line added pointing at this app's
        # sitemap. Paths below are still written root-relative (including the
        # subdirectory prefix) so they're correct if pasted into that root file.
        site_path = urlparse(config.site_url).path.rstrip("/")
        lines = [
            "User-agent: *",
            "Allow: /",
            # Per-run job result pages are ephemeral and user-specific, not
            # evergreen content worth indexing.
            f"Disallow: {site_path}/tools/linkgraph/site-audit/job/",
            f"Disallow: {site_path}/tools/linkgraph/internal-links/job/",
            f"Disallow: {site_path}/kai-mcp/download",
            f"Disallow: {site_path}/kai-mcp/get",
            f"Disallow: {site_path}/admin/",
            f"Disallow: {site_path}/forgot-password",
            f"Disallow: {site_path}/reset-password/",
            f"Sitemap: {config.site_url}/sitemap.xml",
        ]
        return Response("\n".join(lines) + "\n", mimetype="text/plain")

    @app.route("/sitemap.xml")
    def sitemap_xml():
        today = date.today().isoformat()
        urls = [(url_for("home"), "1.0"), (url_for("kai_mcp.landing"), "0.9")]
        for cat in TOOL_CATEGORIES:
            for tool in cat["tools"]:
                urls.append((url_for(tool["endpoint"]), "0.8"))

        entries = "".join(
            f"<url><loc>{config.site_url}{path}</loc>"
            f"<lastmod>{today}</lastmod><priority>{priority}</priority></url>"
            for path, priority in urls
        )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{entries}</urlset>"
        )
        return Response(xml, mimetype="application/xml")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
