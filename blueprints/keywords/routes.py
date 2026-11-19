from flask import Blueprint, render_template, request

from . import logic

bp = Blueprint("keywords", __name__)


@bp.route("/ideas", methods=["GET", "POST"])
def ideas():
    result = None
    seed_input = ""
    if request.method == "POST":
        seed_input = request.form.get("seed", "")
        if seed_input.strip():
            result = logic.generate_keyword_ideas(seed_input)
    return render_template("keywords/ideas.html", result=result, seed_input=seed_input)


@bp.route("/clustering", methods=["GET", "POST"])
def clustering():
    clusters = None
    keywords_input = ""
    if request.method == "POST":
        keywords_input = request.form.get("keywords", "")
        keywords = [k for k in keywords_input.splitlines() if k.strip()]
        if keywords:
            clusters = logic.cluster_keywords(keywords)
    return render_template("keywords/clustering.html", clusters=clusters, keywords_input=keywords_input)
