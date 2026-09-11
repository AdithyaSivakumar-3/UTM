# -*- coding: utf-8 -*-
"""Report plumbing on top of python-docx: one `Report` object that the chapter modules
write into. Everything a chapter needs — headings, paragraphs with inline citations,
figures with numbered captions, tables, equations, the front and back matter — lives here
so the chapters stay pure content.

Conventions (mirroring the EENX30 report): A4, numeric [n] citations in order of first
use, figures and tables numbered continuously with Word SEQ fields (so the List of
Figures / Tables are real Word fields updated on export), roman page numbers in the front
matter and arabic in the body.
"""
import os
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from refs import REFS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIGS = os.path.join(ROOT, "documentation", "figures")
LOGO_A = os.path.join(FIGS, "JTH Black", "JTH_A_sv.png")
LOGO_B = os.path.join(FIGS, "JTH Black", "JTH_B_sv.png")

INK = RGBColor(0x25, 0x34, 0x39)
TAN = RGBColor(0xB2, 0x9E, 0x84)
SAGE = RGBColor(0x6C, 0x75, 0x7D)
BODY_W_CM = 16.0                      # A4 minus 2.5 cm margins


# ------------------------------------------------------------------ low-level XML helpers
def _field(paragraph, instr, placeholder=""):
    """A complex field (fldChar begin/instr/separate/end) so Word can update it."""
    run = paragraph.add_run()
    r = run._r
    fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "begin"); r.append(fc)
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    r.append(it)
    fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "separate"); r.append(fc)
    t = OxmlElement("w:t"); t.text = placeholder; r.append(t)
    fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "end"); r.append(fc)
    return run


def _shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def _pgnum(section, fmt, start=None):
    sectPr = section._sectPr
    for old in sectPr.findall(qn("w:pgNumType")):
        sectPr.remove(old)
    p = OxmlElement("w:pgNumType"); p.set(qn("w:fmt"), fmt)
    if start is not None:
        p.set(qn("w:start"), str(start))
    sectPr.append(p)


def _footer_pagenum(section, show=True):
    section.footer.is_linked_to_previous = False
    f = section.footer
    for p in list(f.paragraphs):
        p._p.getparent().remove(p._p)
    p = f.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if show:
        run = _field(p, "PAGE")
        run.font.size = Pt(9); run.font.color.rgb = SAGE


# ------------------------------------------------------------------ the report object
class Report:
    def __init__(self, refmap=None):
        self.doc = Document()
        self._cites = []                     # keys in order of first use
        self._nfig = 0
        self._ntab = 0
        self.refmap = dict(refmap or {})     # "fig:label" -> n, from the first pass
        self.labels = {}                     # collected on this pass
        self._styles()
        s = self.doc.sections[0]
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.left_margin = s.right_margin = Cm(2.5)
        s.top_margin, s.bottom_margin = Cm(2.5), Cm(2.5)

    # ---- styles
    def _styles(self):
        st = self.doc.styles
        n = st["Normal"]
        n.font.name = "Calibri"; n.font.size = Pt(11)
        n.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        n.paragraph_format.space_after = Pt(6)
        n.paragraph_format.line_spacing = 1.15
        for name, size, before in (("Heading 1", 20, 24), ("Heading 2", 14, 14),
                                   ("Heading 3", 12, 10)):
            h = st[name]
            h.font.name = "Calibri Light"; h.font.size = Pt(size); h.font.bold = True
            h.font.color.rgb = INK
            h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri Light")
            h.paragraph_format.space_before = Pt(before)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
        c = st["Caption"]
        c.font.name = "Calibri"; c.font.size = Pt(9.5); c.font.italic = False
        c.font.color.rgb = SAGE
        c.paragraph_format.space_after = Pt(10)

    # ---- structure
    def new_section(self, pgfmt="decimal", start=1, pagenum=True):
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        _pgnum(sec, pgfmt, start)
        _footer_pagenum(sec, pagenum)
        return sec

    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---- numbered headings: chapters 1, 2, ... (or A, B, ... in appendix mode)
    def numbering(self, on=True):
        self._numbered = on

    def appendix_mode(self):
        self._numbered = True
        self._appendix = True
        self._c1 = 0

    def _label1(self):
        if getattr(self, "_appendix", False):
            return "Appendix " + chr(ord("A") + self._c1 - 1)
        return str(self._c1)

    def h1(self, text):
        if getattr(self, "_numbered", False):
            self._c1 = getattr(self, "_c1", 0) + 1
            self._c2 = 0; self._c3 = 0
            lead = self.doc.add_paragraph()
            lead.paragraph_format.page_break_before = True
            lead.paragraph_format.space_before = Pt(60)
            lead.paragraph_format.space_after = Pt(0)
            lead.paragraph_format.keep_with_next = True
            r = lead.add_run(("Appendix %s" % chr(ord("A") + self._c1 - 1))
                             if getattr(self, "_appendix", False) else "Chapter %d" % self._c1)
            r.font.size = Pt(16); r.font.color.rgb = SAGE; r.font.name = "Calibri Light"
            text = "%s  %s" % (self._label1(), text)
            h = self.doc.add_heading(text, level=1)
            h.paragraph_format.space_before = Pt(4)
            h.paragraph_format.space_after = Pt(18)
            for run in h.runs:
                run.font.size = Pt(26)
            return h
        h = self.doc.add_heading(text, level=1)
        return h

    def h2(self, text):
        if getattr(self, "_numbered", False):
            self._c2 = getattr(self, "_c2", 0) + 1; self._c3 = 0
            lab = (chr(ord("A") + self._c1 - 1) if getattr(self, "_appendix", False)
                   else str(self._c1))
            text = "%s.%d  %s" % (lab, self._c2, text)
        return self.doc.add_heading(text, level=2)

    def h3(self, text):
        if getattr(self, "_numbered", False):
            self._c3 = getattr(self, "_c3", 0) + 1
            lab = (chr(ord("A") + self._c1 - 1) if getattr(self, "_appendix", False)
                   else str(self._c1))
            text = "%s.%d.%d  %s" % (lab, self._c2, self._c3, text)
        return self.doc.add_heading(text, level=3)

    # ---- citations: "[key]" tokens inside text become [n]
    def cite(self, *keys):
        nums = []
        for k in keys:
            assert k in REFS, "unknown reference key: %s" % k
            if k not in self._cites:
                self._cites.append(k)
            nums.append(self._cites.index(k) + 1)
        return "[" + ", ".join(str(n) for n in sorted(nums)) + "]"

    _TOK = re.compile(r"\[\[([a-z0-9_]+(?:\s*,\s*[a-z0-9_]+)*)\]\]|\*\*(.+?)\*\*|\*(.+?)\*"
                      r"|\{\{(fig|tab):([a-z0-9_]+)\}\}")

    def xref(self, kind, label):
        n = self.refmap.get("%s:%s" % (kind, label))
        return ("Figure %s" if kind == "fig" else "Table %s") % (n if n else "?")


    def p(self, text, *, style=None, align=None, size=None, italic=False, colour=None,
          after=None, keep=False, par=None):
        """A paragraph. Inline markup: [[key]] / [[k1, k2]] citations, **bold**, *italic*.
        `par` lets a caller fill an existing paragraph (e.g. inside a table cell)."""
        if par is None:
            par = self.doc.add_paragraph(style=style)
        if align == "center":
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align == "justify":
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if after is not None:
            par.paragraph_format.space_after = Pt(after)
        if keep:
            par.paragraph_format.keep_with_next = True
        pos = 0
        for m in self._TOK.finditer(text):
            self._run(par, text[pos:m.start()], size, italic, colour)
            if m.group(1):
                keys = [k.strip() for k in m.group(1).split(",")]
                self._cite_links(par, keys, size)
            elif m.group(2):
                self._run(par, m.group(2), size, italic, colour, bold=True)
            elif m.group(3):
                self._run(par, m.group(3), size, True, colour)
            else:
                self._run(par, self.xref(m.group(4), m.group(5)), size, italic, colour)
            pos = m.end()
        self._run(par, text[pos:], size, italic, colour)
        return par

    LINK = RGBColor(0x1F, 0x6F, 0xB4)

    def _cite_links(self, par, keys, size=None):
        """"[3, 7]" where each number is a Word hyperlink to the bookmark on its entry."""
        nums = []
        for k in keys:
            self.cite(k)
            nums.append((self._cites.index(k) + 1, k))
        nums.sort()
        self._run(par, "[", size, False, None)
        for i, (n, k) in enumerate(nums):
            if i:
                self._run(par, ", ", size, False, None)
            h = OxmlElement("w:hyperlink")
            h.set(qn("w:anchor"), "ref_" + k); h.set(qn("w:history"), "1")
            r = OxmlElement("w:r")
            rpr = OxmlElement("w:rPr")
            c = OxmlElement("w:color"); c.set(qn("w:val"), "1F6FB4"); rpr.append(c)
            if size:
                sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int(size * 2))); rpr.append(sz)
            r.append(rpr)
            t = OxmlElement("w:t"); t.text = str(n); r.append(t)
            h.append(r)
            par._p.append(h)
        self._run(par, "]", size, False, None)

    def _run(self, par, text, size, italic, colour, bold=False):
        if not text:
            return
        r = par.add_run(text)
        if size: r.font.size = Pt(size)
        if italic: r.font.italic = True
        if bold: r.font.bold = True
        if colour is not None: r.font.color.rgb = colour
        return r

    def bullets(self, items, style="List Bullet"):
        for it in items:
            self.p(it, style=style, after=3)

    def numbered(self, items):
        """A numbered list that restarts at 1 (Word's List Number style otherwise keeps
        counting across the whole document)."""
        pars = [self.p(it, style="List Number", after=3) for it in items]
        try:
            numbering = self.doc.part.numbering_part.element
            style = self.doc.styles["List Number"]
            base_id = style.element.pPr.numPr.numId.val
            base = next(n for n in numbering.findall(qn("w:num")) if n.get(qn("w:numId")) == str(base_id))
            abstract_id = base.find(qn("w:abstractNumId")).get(qn("w:val"))
            new_id = max(int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))) + 1
            num = OxmlElement("w:num"); num.set(qn("w:numId"), str(new_id))
            a = OxmlElement("w:abstractNumId"); a.set(qn("w:val"), abstract_id); num.append(a)
            lo = OxmlElement("w:lvlOverride"); lo.set(qn("w:ilvl"), "0")
            so = OxmlElement("w:startOverride"); so.set(qn("w:val"), "1"); lo.append(so); num.append(lo)
            numbering.append(num)
            for par in pars:
                ppr = par._p.get_or_add_pPr()
                npr = OxmlElement("w:numPr")
                il = OxmlElement("w:ilvl"); il.set(qn("w:val"), "0"); npr.append(il)
                ni = OxmlElement("w:numId"); ni.set(qn("w:val"), str(new_id)); npr.append(ni)
                ppr.append(npr)
        except Exception as e:                      # fall back to the style's own numbering
            print("numbered(): restart not applied:", e)

    def eq(self, text, label=None):
        """An equation line, centred; unicode maths in text. Label goes right-aligned."""
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = par.add_run(text); r.font.name = "Cambria Math"; r.font.size = Pt(12)
        if label:
            r2 = par.add_run("\t(%s)" % label); r2.font.size = Pt(10); r2.font.color.rgb = SAGE
        return par

    # ---- figures and tables (Word SEQ fields so the lists are real fields)
    def _fig_caption(self, caption):
        cap = self.doc.add_paragraph(style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run("Figure "); r.font.bold = True
        fr = _field(cap, "SEQ Figure \\* ARABIC", str(self._nfig)); fr.font.bold = True
        r2 = cap.add_run(" — "); r2.font.bold = True
        self._caption_text(cap, caption)

    def fig(self, filename, caption, width_cm=BODY_W_CM, label=None):
        path = filename if os.path.isabs(filename) else os.path.join(FIGS, filename)
        assert os.path.exists(path), "missing figure: %s" % path
        self._nfig += 1
        if label:
            self.labels["fig:" + label] = self._nfig
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = True
        par.add_run().add_picture(path, width=Cm(width_cm))
        self._fig_caption(caption)
        return self._nfig

    def fig_beside(self, texts, filename, caption, width_cm=6.0, label=None):
        """Body paragraphs in the left column, a captioned figure in the right column."""
        path = filename if os.path.isabs(filename) else os.path.join(FIGS, filename)
        assert os.path.exists(path), "missing figure: %s" % path
        self._nfig += 1
        if label:
            self.labels["fig:" + label] = self._nfig
        t = self.doc.add_table(rows=1, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        left, right = t.cell(0, 0), t.cell(0, 1)
        left.width = Cm(BODY_W_CM - width_cm - 0.6); right.width = Cm(width_cm + 0.6)
        first = True
        for txt in texts:
            par = left.paragraphs[0] if first else left.add_paragraph()
            first = False
            self.p(txt, align="justify", par=par)
            par.paragraph_format.space_after = Pt(6)
        par = right.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run().add_picture(path, width=Cm(width_cm))
        cap = right.add_paragraph(style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run("Figure "); r.font.bold = True
        fr = _field(cap, "SEQ Figure \\* ARABIC", str(self._nfig)); fr.font.bold = True
        cap.add_run(" — ").font.bold = True
        self._caption_text(cap, caption)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return self._nfig

    def fig_pair(self, files, caption, widths_cm, label=None, subcaps=("(a)", "(b)")):
        """Two pictures side by side in a borderless table, one figure number."""
        self._nfig += 1
        if label:
            self.labels["fig:" + label] = self._nfig
        t = self.doc.add_table(rows=1, cols=len(files))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, (fn, w) in enumerate(zip(files, widths_cm)):
            path = fn if os.path.isabs(fn) else os.path.join(FIGS, fn)
            assert os.path.exists(path), "missing figure: %s" % path
            cell = t.cell(0, j)
            cell.width = Cm(w + 0.4)
            par = cell.paragraphs[0]
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.keep_with_next = True
            par.add_run().add_picture(path, width=Cm(w))
            sub = cell.add_paragraph()
            sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sub.paragraph_format.keep_with_next = True
            rr = sub.add_run(subcaps[j]); rr.font.size = Pt(9); rr.font.color.rgb = SAGE
        self._fig_caption(caption)
        return self._nfig

    def tab(self, data, caption, col_widths_cm=None, font=9.5, header=True, label=None):
        self._ntab += 1
        if label:
            self.labels["tab:" + label] = self._ntab
        cap = self.doc.add_paragraph(style="Caption")
        cap.paragraph_format.keep_with_next = True
        r = cap.add_run("Table "); r.font.bold = True
        fr = _field(cap, "SEQ Table \\* ARABIC", str(self._ntab)); fr.font.bold = True
        cap.add_run(" — ").font.bold = True
        self._caption_text(cap, caption)
        t = self.doc.add_table(rows=len(data), cols=len(data[0]))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                cell = t.cell(i, j)
                cell.text = ""
                par = cell.paragraphs[0]
                par.paragraph_format.space_after = Pt(1)
                if "{{" in str(val) or "**" in str(val):
                    self.p(str(val), size=font, par=par)
                    if header and i == 0:
                        for run in par.runs:
                            run.font.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                else:
                    run = par.add_run(str(val))
                    run.font.size = Pt(font)
                    if header and i == 0:
                        run.font.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                if header and i == 0:
                    _shade(cell, "253439")
                elif i % 2 == 0:
                    _shade(cell, "F5F3EF")
        if col_widths_cm:
            for j, w in enumerate(col_widths_cm):
                for row in t.rows:
                    row.cells[j].width = Cm(w)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return self._ntab

    def _caption_text(self, cap, caption):
        pos = 0
        for m in self._TOK.finditer(caption):
            cap.add_run(caption[pos:m.start()])
            if m.group(1):
                self._cite_links(cap, [k.strip() for k in m.group(1).split(",")])
            elif m.group(2):
                cap.add_run(m.group(2)).font.bold = True
            elif m.group(3):
                cap.add_run(m.group(3)).font.italic = True
            else:
                cap.add_run(self.xref(m.group(4), m.group(5)))
            pos = m.end()
        cap.add_run(caption[pos:])

    # ---- front and back matter
    def cover(self, title, subtitle, author, dept, date, picture, report_type="", role="",
              cover_gap_pt=40, pic_w_cm=BODY_W_CM, cover_top_pt=0):
        """Cover in the EENX30 style: logo top-left, picture, then left-aligned bold title,
        the report type, the subtitle, AUTHOR in capitals with the role under it, and the
        department block."""
        d = self.doc
        p = d.add_paragraph()
        p.paragraph_format.space_before = Pt(cover_top_pt)
        p.add_run().add_picture(LOGO_B, width=Cm(7.5))
        p.paragraph_format.space_after = Pt(22)
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(os.path.join(FIGS, picture), width=Cm(pic_w_cm))
        p.paragraph_format.space_after = Pt(cover_gap_pt)
        p = d.add_paragraph()
        r = p.add_run(title); r.font.size = Pt(24); r.font.bold = True; r.font.color.rgb = INK
        r.font.name = "Arial"
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.05
        p = d.add_paragraph()
        r = p.add_run(report_type); r.font.size = Pt(11); r.font.name = "Arial"; r.font.color.rgb = INK
        p.paragraph_format.space_after = Pt(4)
        p = d.add_paragraph()
        r = p.add_run(subtitle); r.font.size = Pt(11.5); r.font.color.rgb = SAGE; r.font.name = "Arial"
        p.paragraph_format.space_after = Pt(22)
        p = d.add_paragraph()
        r = p.add_run(author.upper()); r.font.size = Pt(14); r.font.name = "Arial"; r.font.color.rgb = INK
        p.paragraph_format.space_after = Pt(3)
        p = d.add_paragraph()
        r = p.add_run(role); r.font.size = Pt(10.5); r.font.name = "Arial"; r.font.color.rgb = SAGE
        p.paragraph_format.space_after = Pt(26)
        for txt, bold, size in ((dept, True, 10), ("School of Engineering", False, 10),
                                ("JÖNKÖPING UNIVERSITY", False, 10),
                                ("Jönköping, Sweden " + date.split()[-1], False, 10),
                                ("ju.se", False, 10)):
            p = d.add_paragraph()
            r = p.add_run(txt); r.font.size = Pt(size); r.font.bold = bold; r.font.name = "Arial"
            r.font.color.rgb = INK if bold else SAGE
            p.paragraph_format.space_after = Pt(1)

    def inner_title(self, title, subtitle, author, dept, date, supervisors, report_type,
                    photo=None, photo_w_cm=14.0):
        d = self.doc
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(LOGO_B, width=Cm(8.4))
        p.paragraph_format.space_after = Pt(22)
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(report_type); r.font.size = Pt(12); r.font.color.rgb = SAGE
        p.paragraph_format.space_after = Pt(16)
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title); r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = INK
        r.font.name = "Calibri Light"
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(subtitle); r.font.size = Pt(12.5); r.font.color.rgb = SAGE
        p.paragraph_format.space_after = Pt(20)
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(author); r.font.size = Pt(14); r.font.bold = True
        p.paragraph_format.space_after = Pt(16)
        for line in supervisors + ["", dept, "Jönköping University · School of Engineering",
                                   "Jönköping, Sweden · " + date]:
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(line); r.font.size = Pt(11); r.font.color.rgb = SAGE
            p.paragraph_format.space_after = Pt(2)
        if photo:
            path = photo if os.path.isabs(photo) else os.path.join(FIGS, photo)
            assert os.path.exists(path), "missing inner-title photo: %s" % path
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(0)
            p.add_run().add_picture(path, width=Cm(photo_w_cm))

    def copyright_page(self, title, author, year, supervisors, dept, cover_note, typeset):
        d = self.doc
        for _ in range(14):
            d.add_paragraph()
        lines = [title, author, "", "© %s, %d." % (author, year), ""] + supervisors + [
            "", dept, "Jönköping University · School of Engineering",
            "Gjuterigatan 5, SE-551 11 Jönköping, Sweden", "", "Cover: " + cover_note,
            "Typeset: " + typeset, "Jönköping, Sweden %d" % year]
        for line in lines:
            p = d.add_paragraph(); r = p.add_run(line); r.font.size = Pt(10)
            r.font.color.rgb = SAGE if line and not line.startswith(title) else INK
            p.paragraph_format.space_after = Pt(1)

    def toc(self, title="Contents", switches='TOC \\o "1-3" \\h \\z \\u'):
        self.doc.add_heading(title, level=1)
        p = self.doc.add_paragraph()
        _field(p, switches, "Right-click and choose Update Field to build this list.")

    def list_of(self, what):
        self.doc.add_heading("List of %ss" % what, level=1)
        p = self.doc.add_paragraph()
        _field(p, 'TOC \\h \\z \\c "%s"' % what,
               "Right-click and choose Update Field to build this list.")

    def bibliography(self, title="Bibliography"):
        self.doc.add_heading(title, level=1)
        for n, key in enumerate(self._cites, 1):
            e = REFS[key]
            par = self.doc.add_paragraph()
            par.paragraph_format.left_indent = Cm(1.0)
            par.paragraph_format.first_line_indent = Cm(-1.0)
            par.paragraph_format.space_after = Pt(5)
            bs = OxmlElement("w:bookmarkStart"); bs.set(qn("w:id"), str(1000 + n)); bs.set(qn("w:name"), "ref_" + key)
            par._p.append(bs)
            par.add_run("[%d] " % n).font.bold = True
            be = OxmlElement("w:bookmarkEnd"); be.set(qn("w:id"), str(1000 + n))
            par._p.append(be)
            par.add_run("%s. " % e["authors"])
            par.add_run(e["title"]).font.italic = True
            par.add_run(". %s, %d. " % (e["venue"], e["year"]))
            r = par.add_run(e["url"]); r.font.color.rgb = RGBColor(0x1F, 0x6F, 0xB4)
            r.font.size = Pt(9.5)
        return len(self._cites)

    def back_page(self, dept, photos):
        d = self.doc
        for ph in photos:
            path = os.path.join(FIGS, ph)
            if os.path.exists(path):
                p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run().add_picture(path, width=Cm(11.5))
                p.paragraph_format.space_after = Pt(6)
        p = d.add_paragraph(); p.paragraph_format.space_before = Pt(14)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(LOGO_B, width=Cm(7.0))
        for line in (dept.upper(), "JÖNKÖPING UNIVERSITY · SCHOOL OF ENGINEERING",
                     "Jönköping, Sweden", "ju.se"):
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(line); r.font.size = Pt(10); r.font.color.rgb = SAGE
            p.paragraph_format.space_after = Pt(1)

    # ---- output
    def save(self, path):
        self.doc.save(path)
        return path
