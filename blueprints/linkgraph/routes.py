from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory, abort

from utils.http import normalize_url, FetchError
from jobs.runner import submit_job, get_job
from config import config
from . import logic

bp = Blueprint("linkgraph", __name__)


@bp.route("/site-audit", methods=["GET", "POST"])
def site_audit():
    error = None
    if request.method == "POST":
        url_input = request.form.get("url", "")
        max_pages_input = request.form.get("max_pages", "200")
        try:
            url = normalize_url(url_input)
            try:
                max_pages = int(max_pages_input)
            except ValueError:
                max_pages = 200
            max_pages = max(5, min(max_pages, config.max_crawl_pages))
            job_id = submit_job(logic.run_full_audit, url, max_pages)
            return redirect(url_for("linkgraph.site_audit_job", job_id=job_id))
        except FetchError as e:
            error = str(e)
    return render_template("linkgraph/site_audit.html", error=error, max_crawl_pages=config.max_crawl_pages)


@bp.route("/site-audit/job/<job_id>")
def site_audit_job(job_id):
    job = get_job(job_id)
    if job is None:
        abort(404)
    return render_template("linkgraph/site_audit_job.html", job=job, job_id=job_id)


@bp.route("/site-audit/job/<job_id>/status")
def site_audit_job_status(job_id):
    job = get_job(job_id)
    if job is None:
        abort(404)
    return jsonify({
        "status": job["status"],
        "progress": job["progress"],
        "error": job.get("error"),
    })


@bp.route("/site-audit/job/<job_id>/graph")
def site_audit_job_graph(job_id):
    job = get_job(job_id)
    if job is None or job["status"] != "done":
        abort(404)
    job_dir = job["result"]["job_dir"]
    return send_from_directory(job_dir, "link_graph.html")


@bp.route("/internal-links", methods=["GET", "POST"])
def internal_links():
    error = None
    if request.method == "POST":
        target_input = request.form.get("target_url", "")
        site_input = request.form.get("site_url", "")
        max_pages_input = request.form.get("max_pages", "200")
        try:
            target_url = normalize_url(target_input)
            site_url = normalize_url(site_input) if site_input.strip() else target_url
            try:
                max_pages = int(max_pages_input)
            except ValueError:
                max_pages = 200
            max_pages = max(5, min(max_pages, config.max_crawl_pages))
            job_id = submit_job(logic.run_internal_link_suggestions, target_url, site_url, max_pages)
            return redirect(url_for("linkgraph.internal_links_job", job_id=job_id))
        except FetchError as e:
            error = str(e)
    return render_template("linkgraph/internal_links.html", error=error, max_crawl_pages=config.max_crawl_pages)


@bp.route("/internal-links/job/<job_id>")
def internal_links_job(job_id):
    job = get_job(job_id)
    if job is None:
        abort(404)
    return render_template("linkgraph/internal_links_job.html", job=job, job_id=job_id)


@bp.route("/internal-links/job/<job_id>/status")
def internal_links_job_status(job_id):
    job = get_job(job_id)
    if job is None:
        abort(404)
    return jsonify({"status": job["status"], "progress": job["progress"], "error": job.get("error")})
