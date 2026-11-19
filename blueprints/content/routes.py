from flask import Blueprint, render_template, request, jsonify

from utils.http import fetch, normalize_url, FetchError
from . import logic

bp = Blueprint("content", __name__)


@bp.route("/grader", methods=["GET"])
def grader():
    return render_template("content/grader.html", helpful_checklist=logic.HELPFUL_CONTENT_CHECKLIST)


@bp.route("/grader/api", methods=["POST"])
def grader_api():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("content", "")
    keyword = data.get("keyword", "")
    title = data.get("title", "")
    secondary = [k for k in (data.get("secondary") or "").splitlines() if k.strip()]
    result = logic.grade_content(text, keyword, secondary, title)
    return jsonify(result)


@bp.route("/grader/fetch", methods=["POST"])
def grader_fetch():
    """Fetch a live URL's visible text so the user can grade existing content
    instead of pasting it manually."""
    url_input = request.form.get("url", "") or (request.get_json(force=True, silent=True) or {}).get("url", "")
    try:
        url = normalize_url(url_input)
        resp = fetch(url)
    except FetchError as e:
        return jsonify({"error": str(e)}), 400

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    body = soup.find("main") or soup.find("article") or soup.body or soup
    text = body.get_text(separator="\n", strip=True) if body else ""
    return jsonify({"title": title, "content": text})
