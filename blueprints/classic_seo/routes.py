from flask import Blueprint, render_template, request

from utils.http import fetch, normalize_url, FetchError
from . import logic

bp = Blueprint("classic_seo", __name__)


@bp.route("/serp-preview", methods=["GET", "POST"])
def serp_preview():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            soup = logic.soup_from_html(resp.text)
            title, description = logic.get_title_and_meta(soup)
            result = {
                "url": url,
                "title": title or "(no title tag found)",
                "description": description or "(no meta description found)",
                "title_len": len(title),
                "description_len": len(description),
                "title_ok": 15 <= len(title) <= 60,
                "description_ok": 70 <= len(description) <= 160,
            }
        except FetchError as e:
            error = str(e)
    return render_template("classic_seo/serp_preview.html", result=result, error=error, url_input=url_input)


@bp.route("/keyword-density", methods=["GET", "POST"])
def keyword_density():
    result = None
    error = None
    url_input = ""
    keyword_input = ""
    text_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "").strip()
        keyword_input = request.form.get("keyword", "")
        text_input = request.form.get("text", "").strip()
        try:
            if url_input:
                url = normalize_url(url_input)
                resp = fetch(url)
                soup = logic.soup_from_html(resp.text)
                text = logic.extract_visible_text(soup)
            elif text_input:
                text = text_input
            else:
                raise FetchError("Enter a URL or paste some text to analyze.")
            result = logic.keyword_density_report(text, keyword_input)
        except FetchError as e:
            error = str(e)
    return render_template(
        "classic_seo/keyword_density.html", result=result, error=error,
        url_input=url_input, keyword_input=keyword_input, text_input=text_input,
    )


@bp.route("/redirect-checker", methods=["GET", "POST"])
def redirect_checker():
    results = []
    urls_input = ""
    if request.method == "POST":
        urls_input = request.form.get("urls", "")
        raw_urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
        for raw in raw_urls:
            try:
                url = normalize_url(raw)
                chain, status = logic.follow_redirect_chain(url)
                results.append({"input": raw, "chain": chain, "status": status})
            except FetchError as e:
                results.append({"input": raw, "chain": [], "status": "invalid", "error": str(e)})
    return render_template("classic_seo/redirect_checker.html", results=results, urls_input=urls_input)


@bp.route("/canonical-hreflang", methods=["GET", "POST"])
def canonical_hreflang():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            soup = logic.soup_from_html(resp.text)
            result = logic.parse_canonical_hreflang(soup, url)
            result["url"] = url
        except FetchError as e:
            error = str(e)
    return render_template("classic_seo/canonical_hreflang.html", result=result, error=error, url_input=url_input)


@bp.route("/header-checker", methods=["GET", "POST"])
def header_checker():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            security = logic.check_security_headers(resp.headers)
            result = {
                "url": url,
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "security": security,
            }
        except FetchError as e:
            error = str(e)
    return render_template("classic_seo/header_checker.html", result=result, error=error, url_input=url_input)


@bp.route("/domain-age", methods=["GET", "POST"])
def domain_age():
    result = None
    error = None
    domain_input = ""
    if request.method == "POST":
        domain_input = request.form.get("domain", "").strip()
        try:
            from utils.http import domain_of
            domain = domain_input
            if "//" in domain:
                domain = domain_of(normalize_url(domain))
            domain = domain.replace("www.", "", 1) if domain.startswith("www.") else domain
            result = logic.rdap_lookup(domain)
            if result is None:
                error = f"No RDAP record found for '{domain}' — it may not be registered, or its registry doesn't support RDAP."
        except FetchError as e:
            error = str(e)
        except Exception as e:
            error = f"Couldn't look up '{domain_input}': {e}"
    return render_template("classic_seo/domain_age.html", result=result, error=error, domain_input=domain_input)
