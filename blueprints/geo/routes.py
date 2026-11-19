from flask import Blueprint, render_template, request, Response

from utils.http import fetch, normalize_url, FetchError
from . import logic

bp = Blueprint("geo", __name__)


@bp.route("/llms-txt-generator", methods=["GET", "POST"])
def llms_txt_generator():
    result = None
    error = None
    url_input = ""
    site_name = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        site_name = request.form.get("site_name", "").strip()
        try:
            url = normalize_url(url_input)
            result = logic.generate_llms_txt(url, site_name or None)
        except FetchError as e:
            error = str(e)
    return render_template(
        "geo/llms_txt_generator.html", result=result, error=error,
        url_input=url_input, site_name=site_name,
    )


@bp.route("/llms-txt-generator/download.txt", methods=["POST"])
def llms_txt_download():
    content = request.form.get("content", "")
    return Response(
        content, mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=llms.txt"},
    )


@bp.route("/geo-readiness", methods=["GET", "POST"])
def geo_readiness():
    result = None
    error = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "")
        try:
            url = normalize_url(url_input)
            resp = fetch(url)
            result = logic.score_geo_readiness(url, resp.text)
        except FetchError as e:
            error = str(e)
    return render_template("geo/geo_readiness.html", result=result, error=error, url_input=url_input)
