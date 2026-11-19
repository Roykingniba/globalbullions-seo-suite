from flask import Blueprint, render_template, request, Response, send_file

from . import logic

bp = Blueprint("converters", __name__)


@bp.route("/csv-json", methods=["GET", "POST"])
def csv_json():
    result = None
    error = None
    input_text = ""
    direction = "csv_to_json"
    if request.method == "POST":
        direction = request.form.get("direction", "csv_to_json")
        input_text = request.form.get("input_text", "")
        try:
            if direction == "csv_to_json":
                result = logic.csv_to_json(input_text)
            else:
                result = logic.json_to_csv(input_text)
        except logic.ConversionError as e:
            error = str(e)
    return render_template(
        "converters/csv_json.html", result=result, error=error,
        input_text=input_text, direction=direction,
    )


@bp.route("/csv-json/download", methods=["POST"])
def csv_json_download():
    content = request.form.get("content", "")
    direction = request.form.get("direction", "csv_to_json")
    if direction == "csv_to_json":
        return Response(content, mimetype="application/json",
                         headers={"Content-Disposition": "attachment; filename=converted.json"})
    return Response(content, mimetype="text/csv",
                     headers={"Content-Disposition": "attachment; filename=converted.csv"})


@bp.route("/image-converter", methods=["GET", "POST"])
def image_converter():
    error = None
    target_format = request.form.get("target_format", "WEBP")
    max_width = request.form.get("max_width", "")
    if request.method == "POST":
        file = request.files.get("image")
        if not file or not file.filename:
            error = "Please choose an image file to convert."
        else:
            try:
                width = int(max_width) if max_width.strip() else None
                out, size = logic.convert_image(file, target_format, width)
                ext = target_format.lower().replace("jpeg", "jpg")
                download_name = f"converted.{ext}"
                return send_file(out, mimetype=f"image/{target_format.lower()}",
                                  as_attachment=True, download_name=download_name)
            except logic.ConversionError as e:
                error = str(e)
    return render_template(
        "converters/image_converter.html", error=error,
        target_format=target_format, max_width=max_width, formats=logic.IMAGE_FORMATS,
    )


@bp.route("/pdf-text", methods=["GET", "POST"])
def pdf_text():
    result = None
    error = None
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename:
            error = "Please choose a PDF file."
        else:
            try:
                result = logic.extract_pdf_text(file)
            except logic.ConversionError as e:
                error = str(e)
    return render_template("converters/pdf_text.html", result=result, error=error)


@bp.route("/pdf-text/download.txt", methods=["POST"])
def pdf_text_download():
    content = request.form.get("content", "")
    return Response(content, mimetype="text/plain",
                     headers={"Content-Disposition": "attachment; filename=extracted.txt"})


@bp.route("/pdf-merge", methods=["GET", "POST"])
def pdf_merge():
    error = None
    if request.method == "POST":
        files = [f for f in request.files.getlist("pdfs") if f and f.filename]
        try:
            out = logic.merge_pdfs(files)
            return send_file(out, mimetype="application/pdf", as_attachment=True, download_name="merged.pdf")
        except logic.ConversionError as e:
            error = str(e)
    return render_template("converters/pdf_merge.html", error=error)


@bp.route("/pdf-split", methods=["GET", "POST"])
def pdf_split():
    error = None
    mode = request.form.get("mode", "all")
    page_range = request.form.get("page_range", "")
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename:
            error = "Please choose a PDF file."
        else:
            try:
                out, mimetype, filename = logic.split_pdf(file, mode, page_range)
                return send_file(out, mimetype=mimetype, as_attachment=True, download_name=filename)
            except logic.ConversionError as e:
                error = str(e)
    return render_template("converters/pdf_split.html", error=error, mode=mode, page_range=page_range)


@bp.route("/pdf-compress", methods=["GET", "POST"])
def pdf_compress():
    error = None
    stats = None
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename:
            error = "Please choose a PDF file."
        else:
            try:
                out, original_size, compressed_size = logic.compress_pdf(file)
                stats = {"original": original_size, "compressed": compressed_size}
                response = send_file(out, mimetype="application/pdf", as_attachment=True, download_name="compressed.pdf")
                response.headers["X-Original-Size"] = str(original_size)
                response.headers["X-Compressed-Size"] = str(compressed_size)
                return response
            except logic.ConversionError as e:
                error = str(e)
    return render_template("converters/pdf_compress.html", error=error, stats=stats)


@bp.route("/pdf-rotate", methods=["GET", "POST"])
def pdf_rotate():
    error = None
    degrees = request.form.get("degrees", "90")
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename:
            error = "Please choose a PDF file."
        else:
            try:
                out = logic.rotate_pdf(file, int(degrees))
                return send_file(out, mimetype="application/pdf", as_attachment=True, download_name="rotated.pdf")
            except logic.ConversionError as e:
                error = str(e)
    return render_template("converters/pdf_rotate.html", error=error, degrees=degrees)


@bp.route("/pdf-watermark", methods=["GET", "POST"])
def pdf_watermark():
    error = None
    watermark_text = request.form.get("watermark_text", "CONFIDENTIAL")
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename:
            error = "Please choose a PDF file."
        else:
            try:
                out = logic.watermark_pdf(file, watermark_text or "CONFIDENTIAL")
                return send_file(out, mimetype="application/pdf", as_attachment=True, download_name="watermarked.pdf")
            except logic.ConversionError as e:
                error = str(e)
    return render_template("converters/pdf_watermark.html", error=error, watermark_text=watermark_text)


@bp.route("/pdf-to-images", methods=["GET", "POST"])
def pdf_to_images():
    error = None
    image_format = request.form.get("image_format", "PNG")
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename:
            error = "Please choose a PDF file."
        else:
            try:
                out, page_count = logic.pdf_to_images(file, image_format)
                return send_file(out, mimetype="application/zip", as_attachment=True, download_name="pages.zip")
            except logic.ConversionError as e:
                error = str(e)
    return render_template("converters/pdf_to_images.html", error=error, image_format=image_format)


@bp.route("/images-to-pdf", methods=["GET", "POST"])
def images_to_pdf():
    error = None
    if request.method == "POST":
        files = [f for f in request.files.getlist("images") if f and f.filename]
        try:
            out = logic.images_to_pdf(files)
            return send_file(out, mimetype="application/pdf", as_attachment=True, download_name="images.pdf")
        except logic.ConversionError as e:
            error = str(e)
    return render_template("converters/images_to_pdf.html", error=error)


@bp.route("/pdf-password", methods=["GET", "POST"])
def pdf_password():
    error = None
    mode = request.form.get("mode", "protect")
    if request.method == "POST":
        file = request.files.get("pdf")
        password = request.form.get("password", "")
        if not file or not file.filename:
            error = "Please choose a PDF file."
        else:
            try:
                if mode == "protect":
                    out = logic.protect_pdf(file, password)
                    name = "protected.pdf"
                else:
                    out = logic.unlock_pdf(file, password)
                    name = "unlocked.pdf"
                return send_file(out, mimetype="application/pdf", as_attachment=True, download_name=name)
            except logic.ConversionError as e:
                error = str(e)
    return render_template("converters/pdf_password.html", error=error, mode=mode)
