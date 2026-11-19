from flask import Blueprint, render_template, request, Response

from config import AI_CRAWLER_USER_AGENTS
from utils.http import fetch, normalize_url, FetchError
from blueprints.classic_seo.logic import extract_visible_text, soup_from_html
from . import logic

bp = Blueprint("generators", __name__)


@bp.route("/sitemap-generator", methods=["GET", "POST"])
def sitemap_generator():
    result = None
    urls_input = ""
    if request.method == "POST":
        urls_input = request.form.get("urls", "")
        urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
        if urls:
            result = logic.generate_sitemap_xml(urls)
    return render_template("generators/sitemap_generator.html", result=result, urls_input=urls_input)


@bp.route("/sitemap-generator/download.xml", methods=["POST"])
def sitemap_generator_download():
    content = request.form.get("content", "")
    return Response(content, mimetype="application/xml",
                     headers={"Content-Disposition": "attachment; filename=sitemap.xml"})


@bp.route("/robots-generator", methods=["GET", "POST"])
def robots_generator():
    result = None
    form = {"disallow": "", "sitemap_url": "", "crawl_delay": "", "blocked_agents": []}
    if request.method == "POST":
        form["disallow"] = request.form.get("disallow", "")
        form["sitemap_url"] = request.form.get("sitemap_url", "")
        form["crawl_delay"] = request.form.get("crawl_delay", "")
        form["blocked_agents"] = request.form.getlist("blocked_agents")
        disallow_paths = [p for p in form["disallow"].splitlines() if p.strip()]
        result = logic.generate_robots_txt(
            disallow_paths, form["sitemap_url"], form["crawl_delay"], set(form["blocked_agents"]),
        )
    return render_template(
        "generators/robots_generator.html", result=result, form=form,
        ai_agents=AI_CRAWLER_USER_AGENTS,
    )


@bp.route("/meta-tag-generator", methods=["GET", "POST"])
def meta_tag_generator():
    result = None
    form = {"title": "", "description": "", "url": "", "image_url": "", "site_name": "", "twitter_handle": ""}
    if request.method == "POST":
        for key in form:
            form[key] = request.form.get(key, "")
        result = logic.generate_meta_tags(
            form["title"], form["description"], form["url"],
            form["image_url"], form["site_name"], form["twitter_handle"],
        )
    return render_template("generators/meta_tag_generator.html", result=result, form=form)


@bp.route("/htaccess-generator", methods=["GET", "POST"])
def htaccess_generator():
    result = None
    pairs_input = ""
    if request.method == "POST":
        pairs_input = request.form.get("pairs", "")
        pairs = []
        for line in pairs_input.splitlines():
            if "->" in line:
                old, new = line.split("->", 1)
                pairs.append((old.strip(), new.strip()))
        if pairs:
            result = logic.generate_htaccess(pairs)
    return render_template("generators/htaccess_generator.html", result=result, pairs_input=pairs_input)


@bp.route("/duplicate-content", methods=["GET", "POST"])
def duplicate_content():
    result = None
    error = None
    url_a_input = ""
    url_b_input = ""
    if request.method == "POST":
        url_a_input = request.form.get("url_a", "")
        url_b_input = request.form.get("url_b", "")
        try:
            url_a = normalize_url(url_a_input)
            url_b = normalize_url(url_b_input)
            resp_a = fetch(url_a)
            resp_b = fetch(url_b)
            text_a = extract_visible_text(soup_from_html(resp_a.text))
            text_b = extract_visible_text(soup_from_html(resp_b.text))
            result = logic.compare_content_similarity(text_a, text_b)
        except FetchError as e:
            error = str(e)
    return render_template(
        "generators/duplicate_content.html", result=result, error=error,
        url_a_input=url_a_input, url_b_input=url_b_input,
    )
