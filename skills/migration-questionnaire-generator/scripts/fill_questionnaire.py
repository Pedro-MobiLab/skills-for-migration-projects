#!/usr/bin/env python3
"""
fill_questionnaire.py — Pre-fill the MobiLab universal migration interview
questionnaire (Interview 1) for any client, one file per Application (Workload),
while PRESERVING the template's x14 dropdown data validations.

Why not openpyxl for writing? openpyxl silently drops x14 (extended) data
validations on save, destroying every dropdown. This script edits the worksheet
XML in place inside the .xlsx zip and rewrites all other parts byte-for-byte.
openpyxl is used READ-ONLY, only to locate rows by question text and to read the
Data Validator lists.

Usage:
    python fill_questionnaire.py --config workload_config.json --out OUTDIR \
        [--template assets/questionnaire_template.xlsx] \
        [--cell-map references/cell-map.json] \
        [--profile engagement-profile.yaml] [--date DD.MM.YYYY] [--strict]

Config schema: references/field-mapping.md (section "workload_config.json") and
scripts/example_config.json.
"""
import argparse
import json
import os
import re
import shutil
import sys
import warnings
import zipfile
from datetime import date
from posixpath import join as pjoin, normpath

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


# ------------------------------------------------------------------ xml helpers
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _colnum(letters):
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n


def set_cell(xml, coord, text):
    """Set an inline-string value on `coord`, preserving its style attribute."""
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    tmpl = ('<c r="%s"{style} t="inlineStr"><is><t xml:space="preserve">%s'
            '</t></is></c>' % (coord, esc(text)))
    m = re.search(r'<c r="%s"( s="\d+")?[^>]*/>' % coord, xml)
    if m:
        return xml[:m.start()] + tmpl.format(style=m.group(1) or "") + xml[m.end():]
    m = re.search(r'<c r="%s"( s="\d+")?[^>]*>.*?</c>' % coord, xml, re.S)
    if m:
        if "<f>" in m.group(0) or "<f " in m.group(0):
            raise RuntimeError("refusing to overwrite formula cell %s" % coord)
        return xml[:m.start()] + tmpl.format(style=m.group(1) or "") + xml[m.end():]
    col, rown = re.match(r"([A-Z]+)(\d+)", coord).groups()
    target = _colnum(col)
    rm = re.search(r'(<row r="%s"[^>]*>)(.*?)(</row>)' % rown, xml, re.S)
    if not rm:
        raise RuntimeError("row %s not found for %s" % (rown, coord))
    parts = re.findall(r'<c r="[A-Z]+\d+"[^>]*?(?:/>|>.*?</c>)', rm.group(2), re.S)
    newcell = tmpl.format(style="")
    out, inserted = [], False
    for p in parts:
        c = re.match(r'<c r="([A-Z]+)', p).group(1)
        if not inserted and _colnum(c) > target:
            out.append(newcell)
            inserted = True
        out.append(p)
    if not inserted:
        out.append(newcell)
    return xml[:rm.start()] + rm.group(1) + "".join(out) + rm.group(3) + xml[rm.end():]


def sheet_part(z, sheet_name):
    """Resolve the zip path of a worksheet by its visible name."""
    wb = z.read("xl/workbook.xml").decode("utf-8")
    m = re.search(r'<sheet [^>]*name="%s"[^>]*r:id="([^"]+)"' % re.escape(sheet_name), wb)
    if not m:
        raise RuntimeError("sheet %r not found in template" % sheet_name)
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    t = re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % m.group(1), rels) or \
        re.search(r'<Relationship [^>]*Target="([^"]+)"[^>]*Id="%s"' % m.group(1), rels)
    target = t.group(1)
    return target.lstrip("/") if target.startswith("/") else normpath(pjoin("xl", target))


def count_x14(xml):
    return len(re.findall(r"<x14:dataValidation[ >]", xml))


# ------------------------------------------------------------------ template map
def build_index(template, cmap):
    """Find row numbers for every anchor + read the dropdown lists."""
    import openpyxl
    warnings.filterwarnings("ignore")
    wb = openpyxl.load_workbook(template, read_only=True, data_only=True)
    ws = wb[cmap["sheet"]]
    qcol = _colnum(cmap["question_column"])
    rows = []  # (row, question text lower, col A text lower)
    for rn, r in enumerate(ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True), start=1):
        a = r[0] if len(r) > 0 else None
        q = r[qcol - 1] if len(r) >= qcol else None
        rows.append((rn, str(q or "").lower(), str(a or "").lower()))

    def find(anchor, in_col_a=False):
        hits = [row for row, q, a in rows if anchor.lower() in (a if in_col_a else q)]
        if not hits:
            raise RuntimeError("anchor not found in template: %r" % anchor)
        return hits[0]

    idx = {"workload": {k: find(v) for k, v in cmap["workload_fields"].items()},
           "server": {k: find(v["anchor"]) for k, v in cmap["server_fields"].items()},
           "notes": find(cmap["notes_anchor"], in_col_a=True) + 1}

    lists = {}
    vs = wb[cmap["validator_sheet"]]
    header = [c.value for c in next(vs.iter_rows(min_row=1, max_row=1))]
    for ci, h in enumerate(header):
        if not h:
            continue
        vals = []
        for r in vs.iter_rows(min_row=2, min_col=ci + 1, max_col=ci + 1, values_only=True):
            if r[0] not in (None, ""):
                vals.append(str(r[0]).strip())
        lists.setdefault(str(h).strip(), vals)
    wb.close()
    return idx, lists


# ------------------------------------------------------------------ naming
def slug(s):
    s = re.sub(r"[()\[\]]", "", str(s).lower())
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def file_name(wl, profile, today):
    if wl.get("file"):
        return wl["file"]
    pattern = (((profile or {}).get("naming") or {}).get("questionnaire_file")
               or "{year}_MobiLab_universal_migration_interview_questionaire_{client_slug}_{app_slug}.xlsx")
    client = ((profile or {}).get("client") or {}).get("slug") or wl.get("client_slug", "client")
    return pattern.format(year=today[-4:], client_slug=client, app_slug=slug(wl["workload"]))


# ------------------------------------------------------------------ fill
def fill_one(template, wl, out_dir, today, cmap, idx, lists, profile, strict):
    dst = os.path.join(out_dir, file_name(wl, profile, today))
    shutil.copy(template, dst)
    with zipfile.ZipFile(dst) as z:
        names = z.namelist()
        infos = {n: z.getinfo(n) for n in names}
        data = {n: z.read(n) for n in names}
        part = sheet_part(z, cmap["sheet"])
    xml = data[part].decode("utf-8")
    baseline = count_x14(xml)
    warnings_out = []

    rc = cmap["response_column"]
    xml = set_cell(xml, cmap["date_cell"], today)
    for key, row in idx["workload"].items():
        if wl.get(key):
            xml = set_cell(xml, "%s%d" % (rc, row), wl[key])

    cols = cmap["server_columns"]
    if len(wl["servers"]) > len(cols):
        raise RuntimeError("template supports max %d servers per file; %r has %d — split the "
                           "workload by environment / cutover group" % (len(cols), wl["workload"], len(wl["servers"])))
    admin = wl.get("admin_groups")
    if admin is None:
        admin = ((profile or {}).get("defaults") or {}).get("admin_groups") or []
    for i, srv in enumerate(wl["servers"]):
        col = cols[i]
        if admin and not srv.get("access"):
            srv = dict(srv, access="\n".join(admin))
        for key, spec in cmap["server_fields"].items():
            val = srv.get(key, "")
            if not val:
                continue
            lst = spec.get("list")
            if lst and lists.get(lst) and val not in lists[lst]:
                warnings_out.append("%s / %s: %r is not in the '%s' dropdown %s"
                                    % (wl["workload"], srv.get("name"), val, lst, lists[lst]))
            xml = set_cell(xml, "%s%d" % (col, idx["server"][key]), val)

    header = wl.get("notes_header") or ("Workload: %s  |  Date: %s" % (wl["workload"], today))
    lines = [header]
    for srv in wl["servers"]:
        note = srv.get("note", "")
        lines.append("%s: %s" % (srv["name"], note) if note else srv["name"])
    for extra in wl.get("notes_extra", []):
        lines.append(extra)
    xml = set_cell(xml, "A%d" % idx["notes"], "\n".join(lines))

    after = count_x14(xml)
    if after != baseline:
        raise RuntimeError("DROPDOWNS CHANGED in %s: %d -> %d x14 validations" % (dst, baseline, after))
    for c in cmap.get("protected_cells", []):
        if not re.search(r'<c r="%s"[^>]*>\s*<f>' % c, xml):
            warnings_out.append("formula in %s not found (template changed?)" % c)

    data[part] = xml.encode("utf-8")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            z.writestr(infos[n], data[n])
    for w in warnings_out:
        print("WARNING: " + w, file=sys.stderr)
    if strict and warnings_out:
        raise SystemExit(2)
    return dst, after


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=os.path.join(SKILL_DIR, "assets", "questionnaire_template.xlsx"))
    ap.add_argument("--cell-map", default=os.path.join(SKILL_DIR, "references", "cell-map.json"))
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile")
    ap.add_argument("--date", default=date.today().strftime("%d.%m.%Y"))
    ap.add_argument("--strict", action="store_true", help="fail on off-list dropdown values")
    a = ap.parse_args()

    with open(a.cell_map, encoding="utf-8") as f:
        cmap = json.load(f)
    profile = None
    if a.profile:
        import yaml
        with open(a.profile, encoding="utf-8") as f:
            profile = yaml.safe_load(f)
    with open(a.config, encoding="utf-8") as f:
        workloads = json.load(f)

    idx, lists = build_index(a.template, cmap)
    os.makedirs(a.out, exist_ok=True)
    for wl in workloads:
        dst, dv = fill_one(a.template, wl, a.out, a.date, cmap, idx, lists, profile, a.strict)
        print("OK  %s  (dropdowns preserved: %d)" % (dst, dv))
    print("Done. %d file(s) written." % len(workloads))


if __name__ == "__main__":
    main()
