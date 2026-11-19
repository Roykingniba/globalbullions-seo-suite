from flask import Blueprint, render_template, request

from . import logic

bp = Blueprint("utilities", __name__)


def _render(template, **ctx):
    return render_template(f"utilities/{template}", **ctx)


@bp.route("/word-counter", methods=["GET", "POST"])
def word_counter():
    text = request.form.get("text", "") if request.method == "POST" else ""
    stats = logic.count_text(text) if text.strip() else None
    return _render("word_counter.html", text=text, stats=stats)


@bp.route("/case-converter", methods=["GET", "POST"])
def case_converter():
    text = result = ""
    mode = "title"
    if request.method == "POST":
        text = request.form.get("text", "")
        mode = request.form.get("mode", "title")
        if text.strip():
            result = logic.convert_case(text, mode)
    return _render("case_converter.html", text=text, mode=mode, result=result)


@bp.route("/slug-generator", methods=["GET", "POST"])
def slug_generator():
    text = ""
    separator = "-"
    lowercase = True
    max_length = ""
    results = []
    if request.method == "POST":
        text = request.form.get("text", "")
        separator = request.form.get("separator", "-")
        lowercase = request.form.get("lowercase") == "on"
        max_length = request.form.get("max_length", "")
        try:
            cap = int(max_length) if max_length.strip() else 0
        except ValueError:
            cap = 0
        for line in text.splitlines():
            if line.strip():
                results.append({"source": line.strip(),
                                "slug": logic.slugify(line, separator, lowercase, cap)})
    return _render("slug_generator.html", text=text, separator=separator,
                   lowercase=lowercase, max_length=max_length, results=results)


@bp.route("/line-tools", methods=["GET", "POST"])
def line_tools():
    text = ""
    operation = "dedupe"
    case_sensitive = True
    trim = True
    result = None
    error = None
    if request.method == "POST":
        text = request.form.get("text", "")
        operation = request.form.get("operation", "dedupe")
        case_sensitive = request.form.get("case_sensitive") == "on"
        trim = request.form.get("trim") == "on"
        if text.strip():
            try:
                result = logic.process_lines(text, operation, case_sensitive, trim)
            except logic.ToolError as e:
                error = str(e)
    return _render("line_tools.html", text=text, operation=operation,
                   case_sensitive=case_sensitive, trim=trim, result=result, error=error)


@bp.route("/text-diff", methods=["GET", "POST"])
def text_diff():
    left = right = ""
    ignore_case = ignore_ws = False
    result = None
    if request.method == "POST":
        left = request.form.get("left", "")
        right = request.form.get("right", "")
        ignore_case = request.form.get("ignore_case") == "on"
        ignore_ws = request.form.get("ignore_whitespace") == "on"
        if left.strip() or right.strip():
            result = logic.diff_texts(left, right, ignore_case, ignore_ws)
    return _render("text_diff.html", left=left, right=right, result=result,
                   ignore_case=ignore_case, ignore_whitespace=ignore_ws)


@bp.route("/lorem-ipsum", methods=["GET", "POST"])
def lorem_ipsum():
    kind = "paragraphs"
    count = 3
    start_classic = True
    result = ""
    if request.method == "POST":
        kind = request.form.get("kind", "paragraphs")
        start_classic = request.form.get("start_classic") == "on"
        try:
            count = int(request.form.get("count", 3))
        except ValueError:
            count = 3
        result = logic.generate_lorem(kind, count, start_classic)
    return _render("lorem_ipsum.html", kind=kind, count=count,
                   start_classic=start_classic, result=result)


@bp.route("/base64", methods=["GET", "POST"])
def base64_tool():
    text = result = ""
    action = "encode"
    url_safe = False
    error = None
    if request.method == "POST":
        text = request.form.get("text", "")
        action = request.form.get("action", "encode")
        url_safe = request.form.get("url_safe") == "on"
        if text.strip():
            try:
                result = logic.base64_convert(text, action, url_safe)
            except logic.ToolError as e:
                error = str(e)
    return _render("base64.html", text=text, action=action,
                   url_safe=url_safe, result=result, error=error)


@bp.route("/url-encoder", methods=["GET", "POST"])
def url_encoder():
    text = result = ""
    action = "encode"
    component = True
    error = None
    if request.method == "POST":
        text = request.form.get("text", "")
        action = request.form.get("action", "encode")
        component = request.form.get("component") == "on"
        if text.strip():
            try:
                result = logic.url_convert(text, action, component)
            except logic.ToolError as e:
                error = str(e)
    return _render("url_encoder.html", text=text, action=action,
                   component=component, result=result, error=error)


@bp.route("/html-entities", methods=["GET", "POST"])
def html_entities():
    text = result = ""
    action = "encode"
    quotes = True
    if request.method == "POST":
        text = request.form.get("text", "")
        action = request.form.get("action", "encode")
        quotes = request.form.get("quotes") == "on"
        if text.strip():
            result = logic.html_convert(text, action, quotes)
    return _render("html_entities.html", text=text, action=action,
                   quotes=quotes, result=result)


@bp.route("/hash-generator", methods=["GET", "POST"])
def hash_generator():
    text = ""
    hashes = []
    if request.method == "POST":
        text = request.form.get("text", "")
        chosen = request.form.getlist("algos") or logic.HASH_ALGOS
        if text:
            hashes = logic.hash_text(text, chosen)
    return _render("hash_generator.html", text=text, hashes=hashes,
                   algos=logic.HASH_ALGOS)


@bp.route("/uuid-generator", methods=["GET", "POST"])
def uuid_generator():
    count = 10
    uppercase = braces = False
    hyphens = True
    results = []
    if request.method == "POST":
        try:
            count = int(request.form.get("count", 10))
        except ValueError:
            count = 10
        uppercase = request.form.get("uppercase") == "on"
        braces = request.form.get("braces") == "on"
        hyphens = request.form.get("hyphens") == "on"
        results = logic.generate_uuids(count, 4, uppercase, braces, hyphens)
    return _render("uuid_generator.html", count=count, uppercase=uppercase,
                   braces=braces, hyphens=hyphens, results=results)


@bp.route("/password-generator", methods=["GET", "POST"])
def password_generator():
    length, count = 20, 5
    lower = upper = digits = symbols = True
    exclude_ambiguous = False
    result = None
    error = None
    if request.method == "POST":
        try:
            length = int(request.form.get("length", 20))
            count = int(request.form.get("count", 5))
        except ValueError:
            length, count = 20, 5
        lower = request.form.get("lower") == "on"
        upper = request.form.get("upper") == "on"
        digits = request.form.get("digits") == "on"
        symbols = request.form.get("symbols") == "on"
        exclude_ambiguous = request.form.get("exclude_ambiguous") == "on"
        try:
            result = logic.generate_passwords(length, count, lower, upper,
                                              digits, symbols, exclude_ambiguous)
        except logic.ToolError as e:
            error = str(e)
    return _render("password_generator.html", length=length, count=count,
                   lower=lower, upper=upper, digits=digits, symbols=symbols,
                   exclude_ambiguous=exclude_ambiguous, result=result, error=error)


@bp.route("/json-formatter", methods=["GET", "POST"])
def json_formatter():
    text = ""
    indent = "2"
    sort_keys = minify = False
    result = None
    error = None
    if request.method == "POST":
        text = request.form.get("text", "")
        indent = request.form.get("indent", "2")
        sort_keys = request.form.get("sort_keys") == "on"
        minify = request.form.get("minify") == "on"
        try:
            result = logic.format_json(text, indent, sort_keys, minify)
        except logic.ToolError as e:
            error = str(e)
    return _render("json_formatter.html", text=text, indent=indent,
                   sort_keys=sort_keys, minify=minify, result=result, error=error)


@bp.route("/utm-builder", methods=["GET", "POST"])
def utm_builder():
    base_url = ""
    params = {k: "" for k in logic.UTM_FIELDS}
    lowercase = True
    result = None
    error = None
    if request.method == "POST":
        base_url = request.form.get("base_url", "")
        params = {k: request.form.get(k, "") for k in logic.UTM_FIELDS}
        lowercase = request.form.get("lowercase") == "on"
        try:
            result = logic.build_utm(base_url, params, lowercase)
        except logic.ToolError as e:
            error = str(e)
    return _render("utm_builder.html", base_url=base_url, params=params,
                   lowercase=lowercase, result=result, error=error,
                   fields=logic.UTM_FIELDS)


@bp.route("/color-converter", methods=["GET", "POST"])
def color_converter():
    value = ""
    color = None
    error = None
    if request.method == "POST":
        value = request.form.get("value", "")
        try:
            color = logic.parse_color(value)
        except logic.ToolError as e:
            error = str(e)
    return _render("color_converter.html", value=value, color=color, error=error)
