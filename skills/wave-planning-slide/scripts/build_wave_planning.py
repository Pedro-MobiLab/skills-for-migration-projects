#!/usr/bin/env python3
"""
build_wave_planning.py — Generate a MobiLab-branded "Wave Planning" cutover
schedule slide (optionally preceded by the branded cover) for any client and any
mix of migration / modernization scenarios.

Renders 1–3 columns (normally calendar weeks) side by side. Each unit of
execution (server, database instance, file share or application) is a card:
date chip + left status marker (white/grey outline = Scheduled, amber = Planned)
+ unit identifier + "Workload · Owner" line + optional scenario chip
(e.g. "Rehost", "Replatform · DB"). Units with missing data render dimmed.

USAGE
  python build_wave_planning.py data.json output.pptx [--strict]

  --strict   exit with code 2 if any cutover-group rule is violated
             (a group with different dates, or a group spread over columns).

INPUT — see references/data-schema.md for the full schema. Minimal example:
{
  "title": "Migration & Modernization: Wave Planning",
  "subtitle": "Cutover schedule · CW29–CW30 (13–25 July 2026)",
  "client_name": "Contoso",              # footer text if no client_logo
  "client_logo": "path/to/logo.png",     # optional
  "columns": [
    {"header": "CW 29", "meta": "14–17 July · 3 units",
     "units": [
       {"date": "14 Jul", "unit": "SRVAPP01", "workload": "Navision",
        "owner": "Jane Doe +1", "status": "scheduled",
        "scenario": "Rehost", "group": "Navision-PRD"}
     ]}
  ]
}
Legacy input ("servers" list, "server" key) is still accepted.
"""
import json
import os
import sys
from collections import defaultdict

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- MobiLab palette ----------------
TEAL      = RGBColor(0x00, 0xA8, 0x9D)   # week header band
DARK      = RGBColor(0x19, 0x28, 0x32)   # headlines / body
SUBTITLE  = RGBColor(0x3D, 0x62, 0x7B)
CARD_BG   = RGBColor(0xF2, 0xF2, 0xF2)
CARD_DIM  = RGBColor(0xE8, 0xE8, 0xE8)
GREY_TX   = RGBColor(0x6B, 0x6B, 0x6B)
DIM_TX    = RGBColor(0xA6, 0xA6, 0xA6)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
STATUS_AMBER = RGBColor(0xFB, 0xBB, 0x33)  # Planned
BAR_BORDER   = RGBColor(0xB0, 0xB0, 0xB0)  # Scheduled outline
CHIP_BG      = RGBColor(0xE0, 0xF4, 0xF2)  # scenario chip fill
CHIP_TX      = RGBColor(0x00, 0x75, 0x6D)  # scenario chip text
DIVIDER      = RGBColor(0xC8, 0xC8, 0xC8)

FONT_HEAD = "Aeonik Semibold"
FONT_MED  = "Aeonik Medium"
FONT_BODY = "Inter"
FONT_SEMI = "Inter SemiBold"

EMU = 914400               # per inch
SLIDE_W = 16271875         # 45.2 cm
SLIDE_H = 9144000          # 25.4 cm


# ---------------------------------------------------------------- helpers
def _resolve(path, base_dir):
    """Resolve a path from the JSON: absolute, relative to the JSON file, or to the skill."""
    if not path:
        return None
    if os.path.isabs(path) and os.path.exists(path):
        return path
    for root in (base_dir, SKILL_DIR, os.getcwd()):
        cand = os.path.join(root, path)
        if os.path.exists(cand):
            return cand
    return None


def _set_fill(shape, rgb):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb
    shape.line.fill.background()


def _add_text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT,
              anchor=MSO_ANCHOR.TOP, margin=0):
    tb = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = margin
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    for text, font, size, color, bold in runs:
        r = p.add_run()
        r.text = text
        r.font.name = font
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = bold
    return tb


def _rounded(slide, x, y, w, h, fill, radius=0.06):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(x), Emu(y), Emu(w), Emu(h))
    _set_fill(sp, fill)
    try:
        sp.adjustments[0] = radius
    except Exception:
        pass
    sp.shadow.inherit = False
    return sp


def _rect(slide, x, y, w, h, fill):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x), Emu(y), Emu(w), Emu(h))
    _set_fill(sp, fill)
    sp.shadow.inherit = False
    return sp


def _aspect(path, fallback):
    try:
        from PIL import Image
        im = Image.open(path)
        return im.width / im.height
    except Exception:
        return fallback


def _units(col):
    """Accept both the new ('units'/'unit') and legacy ('servers'/'server') keys."""
    items = col.get("units", col.get("servers", []))
    for u in items:
        if "unit" not in u and "server" in u:
            u["unit"] = u["server"]
    return items


# ---------------------------------------------------------------- checks
def check_cutover_groups(cols):
    """A cutover group has ONE window and is never split across waves/columns."""
    issues = []
    dates, columns = defaultdict(set), defaultdict(set)
    for ci, col in enumerate(cols):
        for u in _units(col):
            g = u.get("group")
            if g:
                dates[g].add(u.get("date", ""))
                columns[g].add(ci)
    for g in sorted(dates):
        if len(dates[g]) > 1:
            issues.append("cutover group '%s' has several dates %s (one window per group)"
                          % (g, sorted(dates[g])))
        if len(columns[g]) > 1:
            issues.append("cutover group '%s' is spread over several columns "
                          "(a group is never split)" % g)
    return issues


# ---------------------------------------------------------------- cover
def fill_cover(slide, cover):
    """Write title/subtitle/date into the cover placeholders, keeping formatting."""
    mapping = {
        "main cover title": cover.get("title"),
        "subtitle": cover.get("subtitle"),
        "location - date": cover.get("date"),
    }
    for sh in slide.shapes:
        key = (sh.name or "").strip().lower()
        val = mapping.get(key)
        if val is None or not sh.has_text_frame:
            continue
        runs = [r for p in sh.text_frame.paragraphs for r in p.runs]
        if runs:
            runs[0].text = val
            for r in runs[1:]:
                r.text = ""
        else:
            sh.text_frame.text = val


# ---------------------------------------------------------------- build
def build(data, out_path, base_dir):
    template = _resolve(data.get("_template", "assets/cover-template.pptx"), base_dir)
    if not template:
        sys.exit("Template not found: %s" % data.get("_template"))
    keep_cover = bool(data.get("_keep_cover", False))
    prs = Presentation(template)

    blank = None
    for layout in prs.slide_layouts:
        if layout.name and layout.name.strip().lower() in ("empty slide", "main slide + empty"):
            blank = layout
            break
    if blank is None:
        blank = prs.slide_layouts[17] if len(prs.slide_layouts) > 17 else prs.slide_layouts[-1]

    slide = prs.slides.add_slide(blank)

    # Keep only our slide (+ the cover if requested). Drop the relationship too, so
    # the removed template slides are not shipped as hidden orphan parts.
    xml_slides = prs.slides._sldIdLst
    sldIds = list(xml_slides)
    keep = {sldIds[0], sldIds[-1]} if keep_cover else {sldIds[-1]}
    for sldId in sldIds:
        if sldId not in keep:
            rId = sldId.rId
            xml_slides.remove(sldId)
            prs.part.drop_rel(rId)

    if keep_cover and data.get("cover"):
        fill_cover(prs.slides[0], data["cover"])

    bg = _rect(slide, 0, 0, SLIDE_W, SLIDE_H, WHITE)
    slide.shapes._spTree.remove(bg._element)
    slide.shapes._spTree.insert(2, bg._element)

    MARGIN = int(0.6 * EMU)

    _add_text(slide, MARGIN, int(0.45 * EMU), SLIDE_W - 2 * MARGIN, int(0.9 * EMU),
              [(data.get("title", "Migration & Modernization: Wave Planning"),
                FONT_HEAD, 34, DARK, True)])
    _add_text(slide, MARGIN, int(1.35 * EMU), SLIDE_W - 2 * MARGIN, int(0.5 * EMU),
              [(data.get("subtitle", ""), FONT_MED, 18, SUBTITLE, False)])

    # ---- Columns ----
    cols = data["columns"]
    if not 1 <= len(cols) <= 3:
        sys.exit("1 to 3 columns are supported, got %d" % len(cols))
    n = len(cols)
    gutter = int(0.4 * EMU)
    col_w = (SLIDE_W - 2 * MARGIN - (n - 1) * gutter) // n
    top0 = int(2.05 * EMU)
    header_h = int(0.55 * EMU)

    footnotes = data.get("footnotes") or []
    max_units = max(1, max(len(_units(c)) for c in cols))
    reserve = 1.15 + (0.25 * len(footnotes))
    bottom_limit = SLIDE_H - int(reserve * EMU)
    avail = bottom_limit - (top0 + header_h + int(0.12 * EMU))
    card_gap = int(0.12 * EMU)
    card_h = (avail - (max_units - 1) * card_gap) // max_units
    max_card_h, min_card_h = int(0.62 * EMU), int(0.42 * EMU)
    if card_h > max_card_h:
        card_h = max_card_h
    if card_h < min_card_h:
        card_gap = int(0.08 * EMU)
        card_h = max(min_card_h, (avail - (max_units - 1) * card_gap) // max_units)

    narrow = n == 3
    date_w = int((0.8 if narrow else 0.95) * EMU)
    text_x_off = int((1.05 if narrow else 1.25) * EMU)
    name_pt = 11.5 if narrow else 12.5
    sub_pt = 9.5 if narrow else 10.5

    for ci, col in enumerate(cols):
        cx = MARGIN + ci * (col_w + gutter)
        _rounded(slide, cx, top0, col_w, header_h, TEAL, radius=0.12)
        _add_text(slide, cx + int(0.25 * EMU), top0, int(col_w * 0.5), header_h,
                  [(col["header"], FONT_MED, 20, WHITE, True)], anchor=MSO_ANCHOR.MIDDLE)
        _add_text(slide, cx + int(col_w * 0.45), top0,
                  int(col_w * 0.55) - int(0.25 * EMU), header_h,
                  [(col.get("meta", ""), FONT_BODY, 12, WHITE, False)],
                  align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

        cy = top0 + header_h + card_gap
        for u in _units(col):
            missing = u.get("missing", False)
            card_fill = CARD_DIM if missing else CARD_BG
            name_tx = DIM_TX if missing else DARK
            sub_tx = DIM_TX if missing else GREY_TX
            status = str(u.get("status", "planned")).lower()

            _rounded(slide, cx, cy, col_w, card_h, card_fill, radius=0.10)

            bar_w = int(0.07 * EMU)
            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                         Emu(cx), Emu(cy), Emu(bar_w), Emu(card_h))
            bar.fill.solid()
            if status == "scheduled":
                bar.fill.fore_color.rgb = WHITE
                bar.line.color.rgb = BAR_BORDER
                bar.line.width = Pt(0.75)
            else:
                bar.fill.fore_color.rgb = STATUS_AMBER
                bar.line.fill.background()
            try:
                bar.adjustments[0] = 0.30
            except Exception:
                pass
            bar.shadow.inherit = False

            _add_text(slide, cx + int(0.22 * EMU), cy, date_w, card_h,
                      [(u.get("date", ""), FONT_SEMI, 12 if not narrow else 11, name_tx, True)],
                      anchor=MSO_ANCHOR.MIDDLE)

            # Scenario chip (right side)
            chip_w = 0
            scen = u.get("scenario")
            if scen:
                chip_w = int(min(2.0, 0.25 + 0.085 * len(scen)) * EMU)
                chip_h = int(0.28 * EMU)
                chip_x = cx + col_w - chip_w - int(0.15 * EMU)
                chip_y = cy + (card_h - chip_h) // 2
                _rounded(slide, chip_x, chip_y, chip_w, chip_h,
                         CARD_DIM if missing else CHIP_BG, radius=0.5)
                _add_text(slide, chip_x, chip_y, chip_w, chip_h,
                          [(scen, FONT_SEMI, 9, DIM_TX if missing else CHIP_TX, True)],
                          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
                chip_w += int(0.25 * EMU)

            tx = cx + text_x_off
            tw = col_w - text_x_off - int(0.2 * EMU) - chip_w
            tb = slide.shapes.add_textbox(Emu(tx), Emu(cy), Emu(tw), Emu(card_h))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p1 = tf.paragraphs[0]
            r1 = p1.add_run()
            r1.text = u.get("unit", "")
            r1.font.name, r1.font.size, r1.font.bold = FONT_SEMI, Pt(name_pt), True
            r1.font.color.rgb = name_tx
            if u.get("note"):
                rn = p1.add_run()
                rn.text = " " + str(u["note"])
                rn.font.name, rn.font.size, rn.font.bold = FONT_SEMI, Pt(name_pt), True
                rn.font.color.rgb = STATUS_AMBER if not missing else DIM_TX
            p2 = tf.add_paragraph()
            r2 = p2.add_run()
            r2.text = "%s  ·  %s" % (u.get("workload") or "—", u.get("owner") or "—")
            r2.font.name, r2.font.size = FONT_BODY, Pt(sub_pt)
            r2.font.color.rgb = sub_tx

            cy += card_h + card_gap

    # ---- Footnotes ----
    fy = SLIDE_H - int((0.95 + 0.25 * len(footnotes)) * EMU)
    for fn in footnotes:
        _add_text(slide, MARGIN, fy, SLIDE_W - 2 * MARGIN, int(0.25 * EMU),
                  [(fn, FONT_BODY, 10, GREY_TX, False)], anchor=MSO_ANCHOR.MIDDLE)
        fy += int(0.25 * EMU)

    # ---- Legend ----
    leg_y = SLIDE_H - int(0.95 * EMU)
    lx = MARGIN
    dot = int(0.14 * EMU)
    d1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Emu(lx), Emu(leg_y + int(0.03 * EMU)), Emu(dot), Emu(dot))
    d1.fill.solid(); d1.fill.fore_color.rgb = WHITE
    d1.line.color.rgb = BAR_BORDER; d1.line.width = Pt(0.75)
    d1.shadow.inherit = False
    _add_text(slide, lx + int(0.24 * EMU), leg_y, int(1.6 * EMU), int(0.3 * EMU),
              [("Scheduled", FONT_BODY, 12, DARK, False)], anchor=MSO_ANCHOR.MIDDLE)
    lx2 = lx + int(1.9 * EMU)
    d2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Emu(lx2), Emu(leg_y + int(0.03 * EMU)), Emu(dot), Emu(dot))
    _set_fill(d2, STATUS_AMBER); d2.shadow.inherit = False
    _add_text(slide, lx2 + int(0.24 * EMU), leg_y, int(1.6 * EMU), int(0.3 * EMU),
              [("Planned", FONT_BODY, 12, DARK, False)], anchor=MSO_ANCHOR.MIDDLE)
    if any(u.get("scenario") for c in cols for u in _units(c)):
        lx3 = lx2 + int(1.7 * EMU)
        _rounded(slide, lx3, leg_y + int(0.02 * EMU), int(0.45 * EMU), int(0.2 * EMU), CHIP_BG, radius=0.5)
        _add_text(slide, lx3 + int(0.55 * EMU), leg_y, int(3 * EMU), int(0.3 * EMU),
                  [("R-factor / scenario", FONT_BODY, 12, DARK, False)], anchor=MSO_ANCHOR.MIDDLE)

    # ---- Footer: [MOBILAB] | [client logo or name] | Confidential ...... page# ----
    logo_mobilab = os.path.join(SKILL_DIR, "assets", "logo-mobilab.png")
    logo_client = _resolve(data.get("client_logo"), base_dir)
    client_name = data.get("client_name", "")

    foot_y = SLIDE_H - int(0.5 * EMU)
    foot_h = int(0.3 * EMU)
    x = MARGIN
    vcenter = foot_y + foot_h // 2
    gap = int(0.20 * EMU)

    def _divider(px):
        _add_text(slide, px, foot_y, int(0.14 * EMU), foot_h,
                  [("|", FONT_BODY, 12, DIVIDER, False)],
                  align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    ref_h = int(0.25 * EMU)            # client logo height = reference unit
    mb_h = int(ref_h * 0.55)           # MOBILAB wordmark ≈ 0.55 × reference
    mb_w = int(mb_h * _aspect(logo_mobilab, 6.9))
    if os.path.exists(logo_mobilab):
        slide.shapes.add_picture(logo_mobilab, Emu(x), Emu(vcenter - mb_h // 2), Emu(mb_w), Emu(mb_h))
    x += mb_w + gap
    if logo_client or client_name:
        _divider(x); x += int(0.14 * EMU) + gap
        if logo_client:
            cl_w = int(ref_h * _aspect(logo_client, 2.0))
            slide.shapes.add_picture(logo_client, Emu(x), Emu(vcenter - ref_h // 2), Emu(cl_w), Emu(ref_h))
            x += cl_w + gap
        else:
            w = int((0.085 * len(client_name) + 0.1) * EMU)
            _add_text(slide, x, foot_y, w, foot_h,
                      [(client_name, FONT_SEMI, 11, DARK, True)], anchor=MSO_ANCHOR.MIDDLE)
            x += w + gap
    _divider(x); x += int(0.14 * EMU) + gap
    _add_text(slide, x, foot_y, int(2 * EMU), foot_h,
              [(data.get("classification", "Confidential"), FONT_SEMI, 11, DARK, True)],
              anchor=MSO_ANCHOR.MIDDLE)
    _add_text(slide, SLIDE_W - MARGIN - int(0.6 * EMU), foot_y, int(0.6 * EMU), foot_h,
              [(str(data.get("page_number", 2 if keep_cover else 1)), FONT_BODY, 11, GREY_TX, False)],
              align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    prs.save(out_path)
    print("Saved %s" % out_path)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    strict = "--strict" in argv
    if len(args) != 2:
        print("usage: build_wave_planning.py data.json output.pptx [--strict]")
        return 1
    with open(args[0], encoding="utf-8") as f:
        data = json.load(f)
    issues = check_cutover_groups(data["columns"])
    for i in issues:
        print("WARNING: " + i, file=sys.stderr)
    if issues and strict:
        return 2
    build(data, args[1], os.path.dirname(os.path.abspath(args[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
