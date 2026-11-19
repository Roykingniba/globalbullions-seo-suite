from flask import Blueprint, render_template, request, jsonify

from . import logic
from .logic import DEFAULT_KEYWORDS, process_domains, scan_domain

bp = Blueprint("outreach", __name__)


MAX_KEYWORDS = 150


def _parse_keywords(text):
    kws = [k.strip().lower() for k in (text or "").splitlines() if k.strip()]
    return kws[:MAX_KEYWORDS] or list(DEFAULT_KEYWORDS)


@bp.route("/email-finder", methods=["GET", "POST"])
def email_finder():
    """The page itself. With JavaScript on, the browser scans the list one
    domain at a time through email_finder_scan below and never posts this
    form. The POST branch only runs for visitors without JavaScript, so it is
    capped to keep a single request inside the host's time limit."""
    results, domains, notice = [], [], None
    keywords_text = "\n".join(DEFAULT_KEYWORDS)

    if request.method == "POST":
        domains = [d.strip() for d in request.form.get("domains", "").splitlines() if d.strip()]
        keywords_text = request.form.get("keywords", keywords_text)
        if len(domains) > NOJS_LIMIT:
            notice = (f"Without JavaScript only the first {NOJS_LIMIT} domains are scanned. "
                      "Turn JavaScript on to scan the full list with live progress.")
        results = list(process_domains(domains[:NOJS_LIMIT], _parse_keywords(keywords_text)))

    return render_template(
        "outreach/email_finder.html",
        results=results, domains=domains, notice=notice,
        keywords_text=keywords_text, default_keywords=DEFAULT_KEYWORDS,
        submitted=request.method == "POST",
    )


NOJS_LIMIT = 5


@bp.route("/email-finder/scan", methods=["POST"])
def email_finder_scan():
    """Scan exactly one domain and return JSON. Called once per domain by the
    page's script, which is what makes an accurate progress bar possible."""
    data = request.get_json(silent=True) or {}
    domain = str(data.get("domain", "")).strip()[:253]
    if not domain:
        return jsonify({"error": "No domain given"}), 400
    keywords = data.get("keywords") or []
    if not isinstance(keywords, list):
        keywords = []
    keywords = [str(k).strip().lower() for k in keywords if str(k).strip()][:MAX_KEYWORDS]
    return jsonify(scan_domain(domain, keywords or None))


@bp.route("/broken-link-finder", methods=["GET", "POST"])
def broken_link_finder():
    results = None
    pages_input = ""
    if request.method == "POST":
        pages_input = request.form.get("pages", "")
        pages = [p.strip() for p in pages_input.splitlines() if p.strip()]
        if pages:
            results = logic.find_broken_link_opportunities(pages)
    return render_template("outreach/broken_link_finder.html", results=results, pages_input=pages_input)


@bp.route("/social-profile-finder", methods=["GET", "POST"])
def social_profile_finder():
    results = None
    domains_input = ""
    if request.method == "POST":
        domains_input = request.form.get("domains", "")
        domains = [d.strip() for d in domains_input.splitlines() if d.strip()]
        if domains:
            results = logic.find_social_profiles(domains)
    return render_template("outreach/social_profile_finder.html", results=results, domains_input=domains_input)


DEFAULT_PITCH_TEMPLATE = """Hi {{site_name}} team,

I came across your site and think your readers would enjoy a guest contribution on a related topic. Would you be open to a pitch?

Thanks,
[Your name]"""


@bp.route("/pitch-personalizer", methods=["GET", "POST"])
def pitch_personalizer():
    results = None
    domains_input = ""
    template_input = DEFAULT_PITCH_TEMPLATE
    if request.method == "POST":
        domains_input = request.form.get("domains", "")
        template_input = request.form.get("template", DEFAULT_PITCH_TEMPLATE)
        domains = [d.strip() for d in domains_input.splitlines() if d.strip()]
        if domains and template_input.strip():
            results = logic.personalize_pitches(domains, template_input)
    return render_template(
        "outreach/pitch_personalizer.html", results=results,
        domains_input=domains_input, template_input=template_input,
    )
