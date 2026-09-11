# -*- coding: utf-8 -*-
"""Build MASTER_README.pdf at the repository root, with folder flowcharts drawn from the tree.

Three parts:

  1. THE FLOWCHARTS. Drawn by matplotlib from the ACTUAL directory tree, not from a hand-kept
     list, so they cannot drift from the repository: one for the whole repo to depth 2, one
     for Documentation/ to depth 3, one for Software/ to depth 3. Each folder box carries its
     own file count so the shape of the repository is visible at a glance.
  2. THE DOCUMENT. MASTER_README.md is converted to DOCX with python-docx -- headings,
     tables, bullets, block quotes, inline code and bold -- with the flowcharts inserted
     after the opening section.
  3. THE PDF. Word exports it, the same route the project report uses.

Rerun after any reorganisation: python Documentation/Scripts/master_readme_pdf.py
"""
import io
import os
import re
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                        # noqa: E402
from matplotlib.patches import FancyBboxPatch                          # noqa: E402
import docx                                                            # noqa: E402
from docx.enum.section import WD_ORIENT                                # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT                         # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH                          # noqa: E402
from docx.oxml.ns import qn                                            # noqa: E402
from docx.shared import Cm, Pt, RGBColor                               # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
SRC = "MASTER_README.md"
OUT_DOCX = os.path.abspath("MASTER_README.docx")
OUT_PDF = os.path.abspath("MASTER_README.pdf")
FIGS = os.path.join("Documentation", "Figures", "readme")

SKIP = {".git", "__pycache__", ".venv", ".pytest_cache", ".pio", ".vscode", ".claude",
        ".local_baselines", ".idea"}
INK, GREY, LINE = "#253439", "#5A636B", "#B9C2C7"
FILL = {0: "#253439", 1: "#1F6FB2", 2: "#DCE9F2", 3: "#F1F3F5"}
TEXT = {0: "white", 1: "white", 2: INK, 3: INK}


# --------------------------------------------------------------------------- the tree
def children(path):
    try:
        entries = sorted(os.listdir(path), key=str.lower)
    except OSError:
        return []
    return [e for e in entries if os.path.isdir(os.path.join(path, e)) and e not in SKIP]


def n_files(path):
    try:
        return sum(1 for e in os.listdir(path) if os.path.isfile(os.path.join(path, e)))
    except OSError:
        return 0


def build(path, label, depth, maxd):
    node = {"label": label, "files": n_files(path), "kids": []}
    if depth < maxd:
        for c in children(path):
            node["kids"].append(build(os.path.join(path, c), c, depth + 1, maxd))
    return node


# --------------------------------------------------------------------------- the drawing
def layout(node, depth, y, rows):
    """Assign each node a row, depth-first, and return the row it sits on."""
    mine = y[0]
    rows.append((depth, node, mine))
    y[0] += 1
    for k in node["kids"]:
        layout(k, depth + 1, y, rows)
    return mine


MAX_ROWS = 20                 # what fits on one landscape page at a readable size


def draw_chunked(path, label, out_stem, title, maxd=2):
    """Draw a tree, split into as many figures as it takes to stay page-sized."""
    root = build(path, label, 0, maxd)
    groups, cur, n = [], [], 0
    for kid in root["kids"]:
        rows = 1 + len(kid["kids"])
        if cur and n + rows > MAX_ROWS - 1:
            groups.append(cur); cur, n = [], 0
        cur.append(kid); n += rows
    if cur:
        groups.append(cur)
    out = []
    for i, g in enumerate(groups, 1):
        part = dict(root)
        part["kids"] = g
        suffix = "" if len(groups) == 1 else " (%d of %d)" % (i, len(groups))
        name = out_stem + ("" if len(groups) == 1 else "_%d" % i) + ".png"
        out.append((title + suffix, draw(part, name, title + suffix)))
    return out


def draw(node, out, title, colw=3.05, rowh=0.42):
    rows = []
    layout(node, 0, [0], rows)
    n = len(rows)
    maxd = max(d for d, _, _ in rows)
    fig_w = 1.05 + colw * (maxd + 1)
    fig, ax = plt.subplots(figsize=(fig_w, max(2.2, n * rowh + 0.9)))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, n * rowh + 0.8)
    ax.axis("off")
    ax.set_title(title, fontsize=11.5, color=INK, loc="left", x=0.01, pad=10)

    pos = {}
    for depth, nd, r in rows:
        x = 0.35 + depth * colw
        yy = (n - r - 0.5) * rowh + 0.25
        pos[id(nd)] = (x, yy)

    # connectors first, so boxes sit on top
    for depth, nd, r in rows:
        x, yy = pos[id(nd)]
        for k in nd["kids"]:
            kx, ky = pos[id(k)]
            ax.plot([x + 0.22, x + 0.22], [yy, ky], color=LINE, lw=1.0, zorder=1)
            ax.plot([x + 0.22, kx], [ky, ky], color=LINE, lw=1.0, zorder=1)

    for depth, nd, r in rows:
        x, yy = pos[id(nd)]
        label = nd["label"] if depth == 0 else nd["label"] + "/"
        if nd["files"]:
            label += "   (%d)" % nd["files"]
        w = min(colw - 0.16, 0.13 * len(label) + 0.28)
        ax.add_patch(FancyBboxPatch((x, yy - rowh * 0.36), w, rowh * 0.72,
                                    boxstyle="round,pad=0.02,rounding_size=0.05",
                                    fc=FILL[min(depth, 3)], ec=INK, lw=0.7, zorder=2))
        ax.text(x + 0.12, yy, label, fontsize=8.6 if depth else 9.6, va="center",
                color=TEXT[min(depth, 3)], zorder=3,
                fontweight="bold" if depth <= 1 else "normal")

    fig.tight_layout()
    p = os.path.join(FIGS, out)
    fig.savefig(p, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("   %-28s %d boxes" % (out, n))
    return p


# --------------------------------------------------------------------------- markdown -> docx
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def add_runs(par, text):
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            r = par.add_run(piece[2:-2]); r.bold = True
        elif piece.startswith("`") and piece.endswith("`"):
            r = par.add_run(piece[1:-1]); r.font.name = "Consolas"
            r.font.size = Pt(9); r.font.color.rgb = RGBColor(0x1F, 0x6F, 0xB2)
        elif piece.startswith("["):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", piece)
            r = par.add_run(m.group(1)); r.font.color.rgb = RGBColor(0x1F, 0x6F, 0xB2)
            r.underline = True
        else:
            par.add_run(piece)


def shade(cell, hexcolor):
    el = cell._tc.get_or_add_tcPr()
    sh = el.makeelement(qn("w:shd"), {qn("w:fill"): hexcolor})
    el.append(sh)


def md_table(doc, rows):
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, row in enumerate(rows):
        cells = t.add_row().cells
        for c, val in zip(cells, row):
            c.text = ""
            par = c.paragraphs[0]
            par.paragraph_format.space_before = Pt(1)
            par.paragraph_format.space_after = Pt(1)
            add_runs(par, val)
            for r in par.runs:
                r.font.size = Pt(8.5)
                if i == 0:
                    r.bold = True
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            if i == 0:
                shade(c, "253439")
    return t


def convert(md, doc, figures):
    lines = md.split("\n")
    i = 0
    inserted = False
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):                        # code block
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            par = doc.add_paragraph()
            par.paragraph_format.left_indent = Cm(0.5)
            par.paragraph_format.space_before = Pt(4)
            r = par.add_run("\n".join(buf))
            r.font.name = "Consolas"; r.font.size = Pt(8.5)
        elif ln.startswith("|") and i + 1 < len(lines) and set(lines[i + 1]) <= set("|-: "):
            rows = []
            head = [c.strip() for c in ln.strip("|").split("|")]
            rows.append(head)
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            md_table(doc, rows)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue
        elif ln.startswith("#"):
            level = len(ln) - len(ln.lstrip("#"))
            text = ln.lstrip("# ").strip()
            h = doc.add_heading("", level=min(level, 4))
            add_runs(h, text)
            for r in h.runs:
                r.font.color.rgb = RGBColor(0x25, 0x34, 0x39)
            # the flowcharts go straight after the first section's intro
            if not inserted and level == 2:
                pass
        elif ln.startswith("> "):
            par = doc.add_paragraph()
            par.paragraph_format.left_indent = Cm(0.6)
            add_runs(par, ln[2:])
            for r in par.runs:
                r.font.size = Pt(9.5); r.italic = True
        elif ln.strip() in ("---", "***"):
            doc.add_paragraph()
        elif ln.startswith(("- ", "* ")):
            par = doc.add_paragraph(style="List Bullet")
            add_runs(par, ln[2:])
            for r in par.runs:
                r.font.size = Pt(10)
        elif ln.strip():
            par = doc.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_runs(par, ln)
            for r in par.runs:
                r.font.size = Pt(10)
        i += 1
        # insert the diagrams once, right before the first "## `CAD/`" section
        if not inserted and i < len(lines) and lines[i].startswith("## `CAD/`"):
            doc.add_page_break()
            h = doc.add_heading("", level=2)
            add_runs(h, "The folder tree")
            for r in h.runs:
                r.font.color.rgb = RGBColor(0x25, 0x34, 0x39)
            par = doc.add_paragraph()
            add_runs(par, "Drawn from the directory tree itself by "
                          "`Documentation/Scripts/master_readme_pdf.py`, so it cannot drift "
                          "from the repository. The number after each folder is how many "
                          "files sit directly in it.")
            for r in par.runs:
                r.font.size = Pt(10)
            from PIL import Image as _I
            for fi, (cap, p) in enumerate(figures):
                cp = doc.add_paragraph()
                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cp.paragraph_format.keep_with_next = True     # caption stays with its figure
                cp.paragraph_format.space_after = Pt(2)
                iw, ih = _I.open(p).size
                w_cm = min(24.4, 14.9 * iw / ih)      # leaves room for the caption line
                cp.add_run().add_picture(p, width=Cm(w_cm))
                c2 = doc.add_paragraph()
                c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = c2.add_run(cap)
                r.font.size = Pt(9); r.italic = True
                r.font.color.rgb = RGBColor(0x5A, 0x63, 0x6B)
                c2.paragraph_format.space_after = Pt(10)      # each diagram fills a page
                                                              # on its own; an explicit break
                                                              # here would leave a blank one
            doc.add_page_break()
            inserted = True


def main():
    if not os.path.isdir(FIGS):
        os.makedirs(FIGS)
    t0 = time.time()
    print("flowcharts:")
    figures = []
    figures += draw_chunked(".", "UTM-main current  (repository root)", "readme_tree_repo",
                            "The repository, two levels deep")
    figures += draw_chunked("Documentation", "Documentation", "readme_tree_documentation",
                            "Documentation/, expanded")
    figures += draw_chunked("Software", "Software", "readme_tree_software",
                            "Software/, expanded")
    figures = [("Figure %d — %s" % (i, cap), p)
               for i, (cap, p) in enumerate(figures, 1)]

    doc = docx.Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE                 # the tables and diagrams are wide
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    for m in ("left_margin", "right_margin"):
        setattr(sec, m, Cm(2.0))
    sec.top_margin, sec.bottom_margin = Cm(1.6), Cm(1.6)
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)
    style.paragraph_format.space_after = Pt(4)

    md = io.open(SRC, encoding="utf-8").read()
    convert(md, doc, figures)
    doc.save(OUT_DOCX)
    print("docx: %s" % OUT_DOCX)

    import win32com.client as win32
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    try:
        d = word.Documents.Open(OUT_DOCX, ReadOnly=False, AddToRecentFiles=False)
        d.ExportAsFixedFormat(OUT_PDF, 17)
        d.Close(False)
    finally:
        word.Quit()
    import pymupdf
    pages = pymupdf.open(OUT_PDF).page_count
    print("pdf:  %s  (%d pages, %.1f s)" % (OUT_PDF, pages, time.time() - t0))


if __name__ == "__main__":
    main()
