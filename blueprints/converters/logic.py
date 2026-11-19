import csv
import io
import json
import zipfile


class ConversionError(Exception):
    pass


def csv_to_json(csv_text):
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
    except csv.Error as e:
        raise ConversionError(f"Couldn't parse CSV: {e}")
    if not rows:
        raise ConversionError("No rows found — check the CSV has a header row and at least one data row.")
    return json.dumps(rows, indent=2)


def json_to_csv(json_text):
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ConversionError(f"Couldn't parse JSON: {e}")

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data or not all(isinstance(r, dict) for r in data):
        raise ConversionError("JSON must be an array of objects (or a single object) to convert to CSV.")

    fieldnames = []
    for row in data:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return buf.getvalue()


IMAGE_FORMATS = ["PNG", "JPEG", "WEBP", "GIF", "BMP"]


def convert_image(file_storage, target_format, max_width=None):
    from PIL import Image

    if target_format not in IMAGE_FORMATS:
        raise ConversionError(f"Unsupported target format: {target_format}")

    try:
        img = Image.open(file_storage.stream)
        img.load()
    except Exception as e:
        raise ConversionError(f"Couldn't read that as an image: {e}")

    if target_format in ("JPEG", "BMP") and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    if max_width and img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))

    out = io.BytesIO()
    img.save(out, format=target_format)
    out.seek(0)
    return out, img.size


def extract_pdf_text(file_storage):
    from pypdf import PdfReader

    try:
        reader = PdfReader(file_storage.stream)
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    total_pages = len(reader.pages)
    text_parts = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            text_parts.append("")

    return {
        "text": "\n\n".join(text_parts),
        "total_pages": total_pages,
        "pages_extracted": total_pages,
        "truncated": False,
    }


# ---------------------------------------------------------------------------
# PDF Merge
# ---------------------------------------------------------------------------
def merge_pdfs(file_storages):
    from pypdf import PdfWriter

    if len(file_storages) < 2:
        raise ConversionError("Upload at least two PDF files to merge.")

    writer = PdfWriter()
    for fs in file_storages:
        try:
            writer.append(fs.stream)
        except Exception as e:
            raise ConversionError(f"Couldn't read '{fs.filename}' as a PDF: {e}")

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out


# ---------------------------------------------------------------------------
# PDF Split
# ---------------------------------------------------------------------------
def split_pdf(file_storage, mode="all", page_range=""):
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(file_storage.stream)
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    total = len(reader.pages)

    if mode == "range":
        start, end = _parse_page_range(page_range, total)
        writer = PdfWriter()
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])
        out = io.BytesIO()
        writer.write(out)
        out.seek(0)
        return out, "application/pdf", "split_pages.pdf"

    # mode == "all": one PDF per page, zipped together
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in range(total):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            page_buf = io.BytesIO()
            writer.write(page_buf)
            zf.writestr(f"page_{i + 1}.pdf", page_buf.getvalue())
    zip_buf.seek(0)
    return zip_buf, "application/zip", "split_pages.zip"


def _parse_page_range(page_range, total):
    page_range = (page_range or "").strip()
    if not page_range:
        return 1, total
    try:
        if "-" in page_range:
            start_s, end_s = page_range.split("-", 1)
            start, end = int(start_s), int(end_s)
        else:
            start = end = int(page_range)
    except ValueError:
        raise ConversionError(f"Couldn't parse page range '{page_range}' — use a format like 2-5.")
    start = max(1, start)
    end = min(total, end)
    if start > end:
        raise ConversionError(f"Invalid page range '{page_range}' for a {total}-page PDF.")
    return start, end


# ---------------------------------------------------------------------------
# PDF Compress
# ---------------------------------------------------------------------------
def compress_pdf(file_storage):
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(file_storage.stream)
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    original_size = file_storage.stream.seek(0, 2)
    file_storage.stream.seek(0)

    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    compressed_size = out.tell()
    out.seek(0)
    return out, original_size, compressed_size


# ---------------------------------------------------------------------------
# PDF Rotate
# ---------------------------------------------------------------------------
def rotate_pdf(file_storage, degrees):
    from pypdf import PdfReader, PdfWriter

    if degrees not in (90, 180, 270):
        raise ConversionError("Rotation must be 90, 180, or 270 degrees.")

    try:
        reader = PdfReader(file_storage.stream)
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out


# ---------------------------------------------------------------------------
# PDF Watermark
# ---------------------------------------------------------------------------
def watermark_pdf(file_storage, watermark_text):
    from pypdf import PdfReader, PdfWriter
    from fpdf import FPDF

    try:
        reader = PdfReader(file_storage.stream)
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    first_page = reader.pages[0]
    page_w = float(first_page.mediabox.width)
    page_h = float(first_page.mediabox.height)

    overlay_pdf = FPDF(unit="pt", format=(page_w, page_h))
    overlay_pdf.add_page()
    overlay_pdf.set_font("Helvetica", size=40)
    overlay_pdf.set_text_color(160, 160, 160)
    with overlay_pdf.rotation(45, x=page_w / 2, y=page_h / 2):
        overlay_pdf.text(x=page_w / 2 - len(watermark_text) * 10, y=page_h / 2, text=watermark_text)
    overlay_bytes = bytes(overlay_pdf.output())

    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
    overlay_page = overlay_reader.pages[0]

    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(overlay_page)
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out


# ---------------------------------------------------------------------------
# PDF to Images
# ---------------------------------------------------------------------------
def pdf_to_images(file_storage, image_format="PNG", dpi=150):
    import fitz  # PyMuPDF

    try:
        doc = fitz.open(stream=file_storage.read(), filetype="pdf")
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    ext = "jpg" if image_format.upper() == "JPEG" else image_format.lower()

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix)
            zf.writestr(f"page_{i + 1}.{ext}", pix.tobytes(ext))
    zip_buf.seek(0)
    return zip_buf, len(doc)


# ---------------------------------------------------------------------------
# Images to PDF
# ---------------------------------------------------------------------------
def images_to_pdf(file_storages):
    from PIL import Image

    if not file_storages:
        raise ConversionError("Upload at least one image.")

    images = []
    for fs in file_storages:
        try:
            img = Image.open(fs.stream)
            img.load()
            images.append(img.convert("RGB"))
        except Exception as e:
            raise ConversionError(f"Couldn't read '{fs.filename}' as an image: {e}")

    out = io.BytesIO()
    images[0].save(out, format="PDF", save_all=True, append_images=images[1:])
    out.seek(0)
    return out


# ---------------------------------------------------------------------------
# PDF Password Protect / Unlock
# ---------------------------------------------------------------------------
def protect_pdf(file_storage, password):
    from pypdf import PdfReader, PdfWriter

    if not password:
        raise ConversionError("Enter a password to protect the PDF with.")
    try:
        reader = PdfReader(file_storage.stream)
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out


def unlock_pdf(file_storage, password):
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(file_storage.stream)
    except Exception as e:
        raise ConversionError(f"Couldn't read that as a PDF: {e}")

    if reader.is_encrypted:
        try:
            result = reader.decrypt(password or "")
        except Exception:
            result = 0
        if not result:
            raise ConversionError("Incorrect password, or this PDF uses an unsupported encryption method.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out
