#!/usr/bin/env python3
"""
build_operations_manual.py — Render the 24-field Operations Manual workbook
(one tab per unit + a shared Handover Summary tab) from a content JSON, applying
every house formatting rule so the content step never has to think about styling.

USAGE
  python build_operations_manual.py content.json [--profile engagement-profile.yaml] [--out DIR]

The content JSON carries only the mapped facts (see references/content-schema.md);
column C descriptions and option lists come from this script + the engagement
profile (Foundation scales), so every handbook of an engagement looks identical.
"""
import argparse
import json
import math
import os
import re
import sys
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# ------------------------------------------------------------------ style
NAVY, LIGHT, WHITE, BLACK = "1F3864", "D6E4F0", "FFFFFF", "000000"
STATUS_COLOR = {"Done": "2E7D32", "In Progress": "E65100", "To-Do": "C62828"}
READY_COLORS = {  # (bg, fg)
    "green": ("EBF5FB", "2E7D32"),
    "red": ("FDEDEC", "C62828"),
    "amber": ("FEF9E7", "E65100"),
}
THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
COL_WIDTHS = {"A": 5, "B": 24, "C": 42, "D": 52, "E": 10, "F": 36}
LINE_H, PADDING = 15, 6
BULLET = "›  "

DEFAULT_SCALES = {
    "environments": ["PRD", "UAT", "QAS", "INT", "TST", "DEV", "Stage"],
    "environment_labels": {"PRD": "Production", "UAT": "User Acceptance Testing",
                           "QAS": "Quality Assurance", "INT": "Integration",
                           "TST": "Test", "DEV": "Development"},
    "business_criticality": [
        {"label": "Most Critical", "impact": "Problems in core processes resulting in significant financial losses or delivery delays"},
        {"label": "Somewhat Critical", "impact": "Impacts important business processes with noticeable operational disruption"},
        {"label": "Less Critical", "impact": "Impacts individual teams or business processes with temporary loss of productivity"},
        {"label": "Not Critical", "impact": "Has little or no impact on business operations"},
    ],
    "data_classification": ["Public", "Internal", "Confidential", "Strictly Confidential"],
    "support_times": ["8x5 - Support only during client business hours",
                      "24x5 - Full support on working days", "24x7 - Full support", "Other"],
}

RTO_RPO_DEF = ("RTO (Recovery Time Objective): maximum acceptable time to restore the service after an outage.\n"
               "RPO (Recovery Point Objective): maximum acceptable data loss, measured in time.")

# (nr, title, description, option-key or None, rto_rpo_definitions)
FIELDS = [
    (1, "Application Service", "Application Service", None, False),
    (2, "System-/Service-/Application-Description", "Short description of the service, its purpose, architecture, dependencies and the migration / modernization approach used.", None, False),
    (3, "Environment Classification", "Environment the service runs in.", "environments", False),
    (4, "Business Impact Classification", "Qualitative impact on the business if the service is unavailable.", "business_criticality", False),
    (5, "Data- and Information Classification", "Classification of the data processed or stored by the service.", "data_classification", False),
    (6, "System-/Service-/Application-Owner", "Accountable owner(s) of the service, with contact details.", None, False),
    (7, "Support Process & Support Contacts", "How incidents are raised and who supports and tests the service.", None, False),
    (8, "Support Times", "Hours during which support is provided.", "support_times", False),
    (9, "Change Process", "Change management process the service follows.", None, False),
    (10, "Monitoring Process", "How the service is monitored and who is alerted.", None, False),
    (11, "Performance Indicators", "Availability, latency, capacity and other KPIs of the service.", None, False),
    (12, "Dependencies & Interfaces", "Upstream / downstream systems, file shares, databases and authentication the service depends on.", None, False),
    (13, "Maintenance Window", "Scheduled maintenance / patching window.", None, False),
    (14, "Service Level Requirements", "Agreed service levels for availability and recovery.", None, True),
    (15, "Platform Stages", "Environments (stages) of the service with their units and cutover dates.", None, False),
    (16, "User Directory", "Directory / identity provider used for users and administrators.", None, False),
    (17, "Request for Permissions", "Process for requesting access to the service.", None, False),
    (18, "Login & Access", "How users and administrators log in and from where.", None, False),
    (19, "Service Accounts", "Technical / service accounts used by the service.", None, False),
    (20, "System Architecture", "Architecture of the service: components, technology stack, connectivity.", None, False),
    (21, "Network Communication & Interfaces", "Network addresses, ports, firewall / NSG rules, private endpoints and DNS.", None, False),
    (22, "Backup & Recovery", "Backup policy, retention and recovery procedure.", None, True),
    (23, "Scheduled Activities", "Recurring scheduled activities such as patching and platform maintenance.", None, False),
    (24, "Known Problems", "Known issues that could prevent the service from working properly.", None, False),
]

SECTIONS = [
    ("General Information", [1, 2]),
    ("Classification", [3, 4, 5]),
    ("Ownership & Support", [6, 7, 8]),
    ("Processes", [9, 10, 11, 12]),
    ("Maintenance & SLAs", [13, 14]),
    ("Platform & Access", [15, 16, 17, 18, 19]),
    ("Architecture & Network", [20, 21]),
    ("Backup, Patching & Known Problems", [22, 23, 24]),
]


# ------------------------------------------------------------------ helpers
def clean(text):
    """House character rule: regular hyphen only, never en/em dashes."""
    if text is None:
        return None
    s = str(text).replace("–", "-").replace("—", "-")
    return s


def load_scales(profile_path):
    scales = dict(DEFAULT_SCALES)
    if not profile_path:
        return scales, {}
    import yaml
    with open(profile_path, encoding="utf-8") as f:
        prof = yaml.safe_load(f) or {}
    found = prof.get("foundation", {}) or {}
    for k in DEFAULT_SCALES:
        if found.get(k):
            scales[k] = found[k]
    return scales, prof


def options_block(key, scales):
    if key == "environments":
        labels = scales.get("environment_labels", {}) or {}
        items = ["%s (%s)" % (e, labels[e]) if e in labels else e for e in scales["environments"]]
    elif key == "business_criticality":
        items = ["%s - %s" % (c["label"], c["impact"]) if isinstance(c, dict) else str(c)
                 for c in scales["business_criticality"]]
    else:
        items = [str(x) for x in scales[key]]
    return "Options:\n" + "\n".join(BULLET + i for i in items)


def count_lines(text, width):
    if not text:
        return 1
    total = 0
    for para in str(text).split("\n"):
        total += max(1, math.ceil(len(para) / width)) if para else 1
    return total


def auto_height(ws, r, widths):
    lines = 1
    for col, w in widths.items():
        v = ws["%s%d" % (col, r)].value
        if v:
            lines = max(lines, count_lines(v, w))
    return max(22, lines * LINE_H + PADDING)


def put(ws, coord, value, bold=False, color=BLACK, fill=WHITE, center=False, size=10):
    c = ws[coord]
    c.value = clean(value)
    c.font = Font(name="Arial", size=size, bold=bold, color=color)
    c.fill = PatternFill("solid", fgColor=fill)
    c.alignment = Alignment(horizontal="center" if center else "left", vertical="top", wrap_text=True)
    c.border = BORDER
    return c


def band(ws, row, text, fill, color, height, bold=True, last="F"):
    ws.merge_cells("A%d:%s%d" % (row, last, row))
    c = put(ws, "A%d" % row, text, bold=bold, color=color, fill=fill)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = height


def safe_tab(name, used):
    t = re.sub(r"[\[\]\*\?/\\:]", "-", str(name))[:31] or "Unit"
    base, i = t, 2
    while t in used:
        t = (base[:28] + "-%d" % i)
        i += 1
    used.add(t)
    return t


# ------------------------------------------------------------------ sheets
def build_manual(ws, unit, title, subtitle, scales):
    ws.sheet_view.showGridLines = False
    for col, w in COL_WIDTHS.items():
        ws.column_dimensions[col].width = w
    band(ws, 1, title, NAVY, WHITE, 26)
    band(ws, 2, subtitle, LIGHT, NAVY, 15, bold=False)
    for col, h in zip("ABCDEF", ["Nr", "Title", "Description", "Value / Content", "Status", "Open / Pending Points"]):
        put(ws, "%s3" % col, h, bold=True, color=WHITE, fill=NAVY)
    ws.freeze_panes = "A4"

    rows = {str(k): v for k, v in (unit.get("rows") or {}).items()}
    fields = {f[0]: f for f in FIELDS}
    r = 4
    summary = {"Done": 0, "In Progress": 0, "To-Do": 0}
    for sec_title, nrs in SECTIONS:
        band(ws, r, sec_title, LIGHT, NAVY, 18)
        r += 1
        for nr in nrs:
            _, ftitle, fdesc, optkey, rto = fields[nr]
            data = rows.get(str(nr), {})
            desc = fdesc
            if optkey:
                desc += "\n" + options_block(optkey, scales)
            if rto:
                desc += "\n\n" + RTO_RPO_DEF
            status = data.get("status", "To-Do")
            if status not in STATUS_COLOR:
                sys.exit("Row %d: status must be Done / In Progress / To-Do, got %r" % (nr, status))
            summary[status] += 1
            opens = data.get("open") or []
            if status == "Done":
                opens = []
            put(ws, "A%d" % r, nr, bold=True, center=True)
            put(ws, "B%d" % r, ftitle)
            put(ws, "C%d" % r, desc)
            put(ws, "D%d" % r, data.get("value", ""))
            put(ws, "E%d" % r, status, bold=True, color=STATUS_COLOR[status])
            put(ws, "F%d" % r, "\n".join(BULLET + clean(o) for o in opens) if opens else "")
            ws.row_dimensions[r].height = auto_height(ws, r, {k: v for k, v in COL_WIDTHS.items() if k != "A"})
            r += 1
    ws.column_dimensions.group("F", "F", outline_level=1, hidden=True)
    return summary


def build_summary(ws, hs, title):
    cols = hs.get("columns", [])
    n = len(cols)
    last = chr(ord("A") + n)  # field col + n unit cols
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 30
    for i in range(n):
        ws.column_dimensions[chr(ord("B") + i)].width = 42
    band(ws, 1, title, NAVY, WHITE, 26, last=last)
    put(ws, "A2", "Field", bold=True, color=WHITE, fill=NAVY)
    for i, c in enumerate(cols):
        put(ws, "%s2" % chr(ord("B") + i), c, bold=True, color=WHITE, fill=NAVY)
    ws.freeze_panes = "B3"
    r = 3
    for sec in hs.get("sections", []):
        band(ws, r, sec["title"], LIGHT, NAVY, 18, last=last)
        r += 1
        traffic = sec.get("traffic_light", False)
        for field, values in sec.get("fields", []):
            put(ws, "A%d" % r, field, bold=True)
            for i in range(n):
                v = values[i] if i < len(values) else ""
                cell = "%s%d" % (chr(ord("B") + i), r)
                if traffic:
                    tone = readiness_tone(v)
                    bg, fg = READY_COLORS[tone]
                    put(ws, cell, v, bold=True, color=fg, fill=bg, center=True)
                else:
                    put(ws, cell, v)
            widths = {"A": 30}
            widths.update({chr(ord("B") + i): 42 for i in range(n)})
            ws.row_dimensions[r].height = auto_height(ws, r, widths)
            r += 1


def readiness_tone(v):
    s = str(v or "").strip().lower()
    if s in ("n/a", "na", "not applicable", "platform-managed", "vendor-managed", "hypercare", "in progress"):
        return "amber"
    if re.match(r"^(not|no)\b", s) or s in ("missing", "open", "pending"):
        return "red"
    return "green"


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("--profile")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()

    with open(a.content, encoding="utf-8") as f:
        spec = json.load(f)
    scales, prof = load_scales(a.profile or spec.get("profile"))

    wb = Workbook()
    wb.remove(wb.active)
    used = set()
    totals = {"Done": 0, "In Progress": 0, "To-Do": 0}
    for unit in spec["units"]:
        ws = wb.create_sheet(safe_tab(unit["tab"], used))
        s = build_manual(ws, unit, unit.get("title", spec["title"]),
                         unit.get("subtitle", spec.get("subtitle", "")), scales)
        for k in totals:
            totals[k] += s[k]
        print("%-20s Done %2d | In Progress %2d | To-Do %2d" % (ws.title, s["Done"], s["In Progress"], s["To-Do"]))

    if spec.get("handover_summary"):
        ws = wb.create_sheet(safe_tab("Handover Summary", used))
        build_summary(ws, spec["handover_summary"], spec["handover_summary"].get("title", "Handover Summary"))

    fname = spec.get("filename")
    if not fname:
        client = (prof.get("client", {}) or {}).get("slug") or spec.get("client_slug", "client")
        wl = re.sub(r"[^a-z0-9]", "", spec.get("workload", "workload").lower())
        unit = spec["units"][0]["tab"] if len(spec["units"]) == 1 else "group"
        pattern = ((prof.get("naming", {}) or {}).get("ops_manual_file")
                   or "{yyyymmdd}_MobiLab_{client_slug}_{workload_slug}_{unit}_operations_manual.xlsx")
        fname = pattern.format(yyyymmdd=date.today().strftime("%Y%m%d"), client_slug=client,
                               workload_slug=wl, unit=re.sub(r"[\\/:*?\"<>|]", "-", unit))
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, fname)
    wb.save(path)
    print("TOTAL                Done %2d | In Progress %2d | To-Do %2d" % (totals["Done"], totals["In Progress"], totals["To-Do"]))
    print("Saved %s" % path)


if __name__ == "__main__":
    main()
