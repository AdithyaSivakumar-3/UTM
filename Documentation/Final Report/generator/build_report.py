# -*- coding: utf-8 -*-
"""Build the project report: DOCX via python-docx (two passes, so that "Figure N" /
"Table N" cross-references in the text resolve), then Word (COM) updates the TOC and
every field and exports the PDF, then pymupdf renders page thumbnails for review.

    python build_report.py            # docx + pdf + page renders
    python build_report.py --docx     # docx only (no Word needed)
"""
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from rp import Report, _footer_pagenum                        # noqa: E402
from ch import frontmatter as FM                              # noqa: E402
from ch import ch1, ch2, ch3, ch4, ch5, appendices            # noqa: E402

REPORT_DIR = os.path.dirname(HERE)        # the deliverables stay in Final Report/
OUT_DOCX = os.path.join(REPORT_DIR, "UTM_DIC_Report.docx")
OUT_PDF = os.path.join(REPORT_DIR, "UTM_DIC_Report.pdf")
PAGES = os.path.join(REPORT_DIR, "pages")
COVER = "report_cover2.png"


def compose(refmap):
    R = Report(refmap)
    # ---- cover (section 0: no page number) + inner title
    _footer_pagenum(R.doc.sections[0], show=False)
    R.cover(FM.TITLE, FM.SUBTITLE, FM.AUTHOR, FM.DEPT, FM.DATE, COVER, FM.REPORT_TYPE,
            FM.ROLE, cover_gap_pt=24, pic_w_cm=13.4, cover_top_pt=28)
    R.page_break()
    R.inner_title(FM.TITLE, FM.SUBTITLE, FM.AUTHOR, FM.DEPT, FM.DATE, FM.SUPERVISORS,
                  "%s — %s" % (FM.REPORT_TYPE, FM.ROLE), photo="JTH campus.jpg", photo_w_cm=12.6)
    # ---- front matter (roman)
    R.new_section("lowerRoman", 1)
    R.numbering(False)
    FM.abstract(R)
    R.page_break()
    FM.acknowledgments(R)
    R.page_break()
    FM.acronyms(R)
    R.page_break()
    R.toc()
    # ---- body (arabic); numbered chapters start on their own page
    R.new_section("decimal", 1)
    R.numbering(True)
    for mod in (ch1, ch2, ch3, ch4, ch5):
        mod.build(R)
    R.numbering(False)
    R.page_break()
    n = R.bibliography()
    R.appendix_mode()
    appendices.build(R)
    # ---- back page (no page number)
    R.new_section("decimal", None, pagenum=False)
    R.back_page(FM.DEPT, ["JU pic.jpg"])
    return R, n


def build_docx():
    t0 = time.time()
    first, _ = compose({})                       # pass 1: collect labels
    R, n = compose(first.labels)                 # pass 2: resolve cross-references
    missing = [k for k in first.labels if k not in R.labels]
    assert not missing, missing
    R.save(OUT_DOCX)
    print("docx: %s  (%d refs, %d figures, %d tables, %d labels, %.1f s)"
          % (OUT_DOCX, n, R._nfig, R._ntab, len(R.labels), time.time() - t0))
    return R


def export_pdf():
    import win32com.client as w
    import pythoncom
    pythoncom.CoInitialize()
    word = w.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(OUT_DOCX, ReadOnly=False, AddToRecentFiles=False)
        for toc in doc.TablesOfContents:
            toc.Update()
        doc.Fields.Update()
        for toc in doc.TablesOfContents:
            toc.UpdatePageNumbers()
        doc.Save()
        doc.ExportAsFixedFormat(OUT_PDF, 17)   # wdExportFormatPDF
        pages = doc.ComputeStatistics(2)       # wdStatisticPages
        doc.Close(False)
        print("pdf: %s  (%d pages)" % (OUT_PDF, pages))
    finally:
        word.Quit()


def render_pages(zoom=0.6):
    import pymupdf
    from PIL import Image
    os.makedirs(PAGES, exist_ok=True)
    for f in os.listdir(PAGES):
        os.remove(os.path.join(PAGES, f))
    d = pymupdf.open(OUT_PDF)
    for i, pg in enumerate(d, 1):
        pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(os.path.join(PAGES, "p%03d.png" % i))
    n = len(d)
    # contact sheets, eight pages each
    sheets = os.path.join(REPORT_DIR, "sheets")
    os.makedirs(sheets, exist_ok=True)
    for f in os.listdir(sheets):
        os.remove(os.path.join(sheets, f))
    pages = sorted(f for f in os.listdir(PAGES) if f.endswith(".png"))
    per, cols = 8, 4
    for k in range(0, len(pages), per):
        ims = [Image.open(os.path.join(PAGES, f)) for f in pages[k:k + per]]
        w, h = ims[0].size
        sw, sh = int(w * 0.75), int(h * 0.75)
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * sw + (cols + 1) * 8, rows * sh + (rows + 1) * 8), (90, 90, 90))
        for i, im in enumerate(ims):
            sheet.paste(im.resize((sw, sh)), (8 + (i % cols) * (sw + 8), 8 + (i // cols) * (sh + 8)))
        sheet.save(os.path.join(sheets, "s%02d_p%03d-%03d.png" % (k // per + 1, k + 1, min(k + per, n))))
    print("rendered %d pages -> %s (+ contact sheets)" % (n, PAGES))
    return n


if __name__ == "__main__":
    build_docx()
    if "--docx" not in sys.argv:
        export_pdf()
        render_pages()
