#!/usr/bin/env python3
"""
build_interview2.py — Create an Interview 2 (Scenario Review) workbook for one
Application (Workload) and one modernization scenario, with one answer column per
unit (server / instance / share / application) and native dropdowns.

This builds a NEW workbook with openpyxl (no template, so no x14 issue).

Usage:
    python build_interview2.py --config interview2_config.json --out OUTDIR \
        [--sets references/interview2-question-sets.json] [--profile profile.yaml]

Config (JSON list, one object per file):
[
  {"workload": "Order Management", "scenario": "Database Modernization",
   "units": ["SQLPRD01\\\\ORDERS"],
   "interviewee": "Alex Miller - alex.miller@contoso.example",
   "prefill": {"SQLPRD01\\\\ORDERS": {"DBM-01": "SQL Server 2014 Enterprise",
                                     "DBM-02": "ORDERS 120 GB, +2 GB/month"}}}
]
"""
import argparse
import json
import os
import re
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVY, LIGHT, TEAL = "1F3864", "D6E4F0", "00A89D"
THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
YESNO = ["Yes", "No", "Maybe"]
STATUS = ["Open", "Closed", "Need Tech Lead Clarification"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", re.sub(r"[()\[\]]", "", str(s).lower())).strip("_")


def cell(ws, r, c, v, bold=False, fill=None, color="000000", wrap=True):
    x = ws.cell(row=r, column=c, value=v)
    x.font = Font(name="Arial", size=10, bold=bold, color=color)
    if fill:
        x.fill = PatternFill("solid", fgColor=fill)
    x.alignment = Alignment(vertical="top", wrap_text=wrap)
    x.border = BORDER
    return x


def build(cfg, sets, profile, out_dir, today):
    scen = sets["scenarios"].get(cfg["scenario"])
    if not scen:
        raise SystemExit("Unknown scenario %r. Known: %s" % (cfg["scenario"], ", ".join(sets["scenarios"])))
    units = cfg["units"]
    prefill = cfg.get("prefill", {})
    wb = Workbook()
    ws = wb.active
    ws.title = "Interview 2"
    ws.sheet_view.showGridLines = False

    fixed = ["ID", "Kind", "Category", "Question", "Guidance"]
    widths = [10, 10, 16, 48, 40]
    ucols = len(units)
    last = len(fixed) + ucols + 2
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last)
    cell(ws, 1, 1, "Interview 2 - %s - %s" % (cfg["scenario"], cfg["workload"]), bold=True, fill=NAVY, color="FFFFFF")
    ws.row_dimensions[1].height = 24
    meta = [
        ("Client", ((profile or {}).get("client") or {}).get("name", cfg.get("client", ""))),
        ("Application (Workload)", cfg["workload"]),
        ("Scenario / R-factor", "%s / %s" % (cfg["scenario"], scen["r_factor"])),
        ("Unit type", scen["unit"]),
        ("Audience", scen["audience"]),
        ("Interviewee", cfg.get("interviewee", "")),
        ("Date", today),
        ("Lifecycle", "10 Scenario Review (Goal = Modernize, after Gate 0)"),
    ]
    r = 2
    for k, v in meta:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        cell(ws, r, 1, k, bold=True, fill=LIGHT)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=last)
        cell(ws, r, 4, v)
        r += 1
    r += 1
    head_row = r
    headers = fixed + units + ["Status", "Comment"]
    for i, h in enumerate(headers, start=1):
        cell(ws, r, i, h, bold=True, fill=TEAL, color="FFFFFF")
    for i, w in enumerate(widths + [28] * ucols + [16, 36], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=head_row + 1, column=len(fixed) + 1)

    status_dv = DataValidation(type="list", formula1='"%s"' % ",".join(STATUS), allow_blank=True)
    ws.add_data_validation(status_dv)
    r += 1
    for q in scen["questions"]:
        cell(ws, r, 1, q["id"], bold=True)
        cell(ws, r, 2, q["kind"])
        cell(ws, r, 3, q["category"])
        cell(ws, r, 4, q["question"])
        cell(ws, r, 5, q.get("help", ""), color="555555")
        opts = None
        if q["answer"] == "yesno":
            opts = YESNO
        elif q["answer"].startswith("list:"):
            opts = q["answer"][5:].split("|")
        if opts:
            dv = DataValidation(type="list", formula1='"%s"' % ",".join(opts), allow_blank=True)
            dv.error = "Pick a value from the list (or use the Comment column)."
            ws.add_data_validation(dv)
        for ui, u in enumerate(units):
            col = len(fixed) + 1 + ui
            val = (prefill.get(u) or {}).get(q["id"], "")
            c = cell(ws, r, col, val)
            if opts:
                dv.add(c)
        st = cell(ws, r, len(fixed) + ucols + 1, "Open")
        status_dv.add(st)
        cell(ws, r, len(fixed) + ucols + 2, "")
        ws.row_dimensions[r].height = max(30, 15 * (1 + len(q["question"]) // 48))
        r += 1

    rd = wb.create_sheet("Readme")
    notes = [
        "Interview 2 runs per scenario row, only when the Goal is Modernize (after Gate 0).",
        "Kind = approve: pre-filled from systems; the interviewee confirms or corrects. Kind = ask: only the interviewee can answer.",
        "Status: Open = not answered / not confirmed; Closed = confirmed; Need Tech Lead Clarification = escalate.",
        "Answers feed the scenario's Confluence page (migration-confluence-pages skill) and the operations manual overrides.",
        "Question set: %s" % sets.get("_status", ""),
    ]
    rd.column_dimensions["A"].width = 120
    for i, n in enumerate(notes, start=1):
        x = rd.cell(row=i, column=1, value=n)
        x.font = Font(name="Arial", size=10)
        x.alignment = Alignment(wrap_text=True)

    client = ((profile or {}).get("client") or {}).get("slug") or cfg.get("client_slug", "client")
    fname = cfg.get("file") or "%s_MobiLab_interview2_%s_%s_%s.xlsx" % (
        today[-4:], client, slug(cfg["scenario"]), slug(cfg["workload"]))
    path = os.path.join(out_dir, fname)
    wb.save(path)
    return path, len(scen["questions"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sets", default=os.path.join(SKILL_DIR, "references", "interview2-question-sets.json"))
    ap.add_argument("--profile")
    ap.add_argument("--date", default=date.today().strftime("%d.%m.%Y"))
    a = ap.parse_args()
    with open(a.sets, encoding="utf-8") as f:
        sets = json.load(f)
    profile = None
    if a.profile:
        import yaml
        with open(a.profile, encoding="utf-8") as f:
            profile = yaml.safe_load(f)
    with open(a.config, encoding="utf-8") as f:
        cfgs = json.load(f)
    os.makedirs(a.out, exist_ok=True)
    for cfg in cfgs:
        p, n = build(cfg, sets, profile, a.out, a.date)
        print("OK  %s  (%d questions x %d units)" % (p, n, len(cfg["units"])))


if __name__ == "__main__":
    main()
