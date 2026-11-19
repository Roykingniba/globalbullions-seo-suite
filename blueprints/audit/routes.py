from flask import Blueprint, render_template, request

from utils.http import fetch, normalize_url, FetchError
from . import logic

bp = Blueprint("audit", __name__)


@bp.route("/robots-sitemap", methods=["GET", "POST"])
def robots_sitemap():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            result = logic.audit_robots_and_sitemap(url)
        except FetchError as e:
            error = str(e)
    return render_template("audit/robots_sitemap.html", result=result, error=error, url_input=url_input)


@bp.route("/schema-validator", methods=["GET", "POST"])
def schema_validator():
    results = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            results = logic.validate_schema(resp.text)
        except FetchError as e:
            error = str(e)
    return render_template("audit/schema_validator.html", results=results, error=error, url_input=url_input)


@bp.route("/mixed-content", methods=["GET", "POST"])
def mixed_content():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            result = logic.find_mixed_content(resp.text, url)
        except FetchError as e:
            error = str(e)
    return render_template("audit/mixed_content.html", result=result, error=error, url_input=url_input)


@bp.route("/js-dependency", methods=["GET", "POST"])
def js_dependency():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            result = logic.detect_js_dependency(resp.text)
        except FetchError as e:
            error = str(e)
    return render_template("audit/js_dependency.html", result=result, error=error, url_input=url_input)


@bp.route("/broken-links", methods=["GET", "POST"])
def broken_links():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            result = logic.check_broken_links(url, resp.text)
        except FetchError as e:
            error = str(e)
    return render_template("audit/broken_links.html", result=result, error=error, url_input=url_input)


@bp.route("/ai-crawler-access", methods=["GET", "POST"])
def ai_crawler_access():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            result = logic.check_ai_crawler_access(url)
        except FetchError as e:
            error = str(e)
    return render_template("audit/ai_crawler_access.html", result=result, error=error, url_input=url_input)
