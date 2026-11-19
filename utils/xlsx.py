"""Minimal .xlsx writer with no third-party dependencies.

Produces a real Excel workbook (Office Open XML) from plain Python lists, so
exports work on the host without installing openpyxl. Supports several sheets,
a bold header row with a filter, frozen header, column widths, text, numbers
and dates.
"""

import datetime
import io
import zipfile
from xml.sax.saxutils import escape

_EPOCH = datetime.datetime(1899, 12, 30)


def _col(n):
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _clean(text):
    # XML 1.0 forbids most control characters; Excel refuses files that contain them.
    return "".join(ch for ch in text if ch in "\t\n\r" or ord(ch) >= 32)


def _cell(ref, value, header=False):
    if value is None or value == "":
        style = ' s="1"' if header else ""
        return f'<c r="{ref}"{style}/>'
    if isinstance(value, bool):
        value = "Yes" if value else "No"
    if isinstance(value, datetime.datetime):
        serial = (value - _EPOCH).total_seconds() / 86400
        return f'<c r="{ref}" s="2"><v>{serial:.10f}</v></c>'
    if isinstance(value, datetime.date):
        serial = (datetime.datetime(value.year, value.month, value.day) - _EPOCH).days
        return f'<c r="{ref}" s="3"><v>{serial}</v></c>'
    if isinstance(value, (int, float)) and not header:
        return f'<c r="{ref}"><v>{value}</v></c>'
    text = escape(_clean(str(value)))
    style = ' s="1"' if header else ""
    return f'<c r="{ref}" t="inlineStr"{style}><is><t xml:space="preserve">{text}</t></is></c>'


def _sheet_xml(headers, rows, widths):
    ncols = len(headers)
    last = _col(ncols - 1)
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
           'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>']
    out.append("<cols>")
    for i in range(ncols):
        w = widths[i] if widths and i < len(widths) else 18
        out.append(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>')
    out.append("</cols><sheetData>")
    out.append('<row r="1">' + "".join(_cell(f"{_col(i)}1", h, True) for i, h in enumerate(headers)) + "</row>")
    for r, row in enumerate(rows, start=2):
        out.append(f'<row r="{r}">' + "".join(_cell(f"{_col(i)}{r}", v) for i, v in enumerate(row)) + "</row>")
    out.append("</sheetData>")
    out.append(f'<autoFilter ref="A1:{last}{max(1, len(rows) + 1)}"/>')
    out.append("</worksheet>")
    return "".join(out)


_STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<numFmts count="2"><numFmt numFmtId="164" formatCode="yyyy-mm-dd hh:mm"/>'
    '<numFmt numFmtId="165" formatCode="yyyy-mm-dd"/></numFmts>'
    '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="3"><fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFE8EEF8"/></patternFill></fill></fills>'
    '<borders count="1"><border/></borders>'
    '<cellStyleXfs count="1"><xf/></cellStyleXfs>'
    '<cellXfs count="4"><xf/>'
    '<xf fontId="1" fillId="2" applyFont="1" applyFill="1"/>'
    '<xf numFmtId="164" applyNumberFormat="1"/>'
    '<xf numFmtId="165" applyNumberFormat="1"/></cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>'
)


def build(sheets):
    """sheets: list of (name, headers, rows, widths). Returns xlsx bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        n = len(sheets)
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   + "".join(f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" '
                             'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                             for i in range(n))
                   + "</Types>")
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                   "</Relationships>")
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + "".join(f'<sheet name="{escape(s[0][:31])}" sheetId="{i + 1}" r:id="rId{i + 1}"/>'
                             for i, s in enumerate(sheets))
                   + "</sheets>"
                   + "<definedNames>"
                   + "".join(f'<definedName name="_xlnm._FilterDatabase" localSheetId="{i}" hidden="1">'
                             f"'{escape(s[0][:31])}'!$A$1:${_col(len(s[1]) - 1)}${max(1, len(s[2]) + 1)}</definedName>"
                             for i, s in enumerate(sheets))
                   + "</definedNames>"
                   + "</workbook>")
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i + 1}.xml"/>'
                             for i in range(n))
                   + f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                   "</Relationships>")
        z.writestr("xl/styles.xml", _STYLES)
        for i, (name, headers, rows, widths) in enumerate(sheets):
            z.writestr(f"xl/worksheets/sheet{i + 1}.xml", _sheet_xml(headers, rows, widths))
    return buf.getvalue()
