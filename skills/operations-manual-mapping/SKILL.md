---
name: operations-manual-mapping
description: >-
  Produce or update the 24-field Operations Manual (Operations Handbook) Excel workbook
  for a migrated or modernized workload of any client, mapping data from the
  handover / inventory spreadsheet, the per-unit Confluence migration pages, the
  interview questionnaires (Interview 1 and 2) and the engagement's architecture pages
  (backup, update management) into Application Service, Description, Business Impact,
  Data Classification, Owner, Support, Maintenance, SLAs, Architecture, Network, Backup
  and the other standard fields, plus a Handover Summary dashboard. Works for every
  Goal and scenario: rehosted servers, replatformed databases (Azure SQL / PaaS), file
  shares (Azure Files), OS upgrades, SaaS replacements, application runtimes and VDI.
  Use whenever the user wants to "fill the operations manual", "do the handbook for
  <workload>", "map the Confluence page", "document this server/database/share", or
  prepare the weekly handover batch.
---

# Operations Manual mapping (customer-agnostic)

Lifecycle position: **17 Signed Off → 19 Steady State** (handover to Managed
Operations). Output: one `.xlsx` per Application Group with one 24-row Operations
Manual tab per unit + one shared Handover Summary tab, built by
`scripts/build_operations_manual.py` so formatting is always identical.

## 0. Engagement profile
Load the client's engagement profile (`references/engagement-profile.template.yaml`).
Used keys: `client.*`, `cloud.target_region`, `foundation.*` (environments, criticality
tiers + impact phrases, data classes, support times), `naming.application_service`,
`naming.ops_manual_file`, `atlassian.cloud_id`, `atlassian.confluence_space`,
`atlassian.architecture_pages.*`, `sharepoint.*`, `inventory.*` (sheet and **column
header names**), `defaults.standard_processes.*`. Missing key → ask once, suggest
adding it to the profile.

## 1. Identify unit, Goal and scenario first
For every unit in the batch, establish **unit type** (server / DB instance / share /
application), **Goal**, **R-factor** and **scenario** (Cockpit → handover sheet →
Confluence Goal block → questionnaire). They decide which row variants apply — read
`references/scenario-variants.md` before mapping. Retire and Retain units get **no**
operations manual (offer a short decommission / retention note instead).

## 2. Sources and priority
1. **Handover sheet** (inventory workbook, `inventory.handover_sheet`) — highest; it is
   filled after cutover and reflects the real post-migration state.
2. **Per-unit Confluence page** + **Interview 1 questionnaire** (+ **Interview 2**
   workbook for modernized units).
3. **Architecture pages** (`atlassian.architecture_pages.backup_management`,
   `update_management`) — lowest, cross-reference only.
4. **Firewall request file** (`sharepoint.firewall_requests_folder`) — Row 21 only;
   never blocking.

Conflict rules:
- Handover sheet beats Confluence/questionnaire.
- A Confluence checklist task counts as done only if it is explicitly *Completed* **and**
  the handover sheet does not contradict it.
- Never write source references in the workbook (no "Mapped from Confluence…", no file
  names, no internal tool names). State the value.

Fetching: SharePoint search + read for the inventory / questionnaires / firewall file;
`getConfluencePage` (`contentFormat: markdown`) or CQL `title ~ "<unit>"` (partial match,
never `=`, titles carry suffixes); questionnaire attachments read locally.

## 3. Source availability checks — MANDATORY, one at a time
Never silently skip a source. Check in this order; at the first problem **stop**, alert,
and wait for the user:

| Step | Source | Blocking | If unavailable, say |
|---|---|---|---|
| 1 | Handover sheet | yes | ⚠️ *Handover spreadsheet unavailable for <unit>* — upload the row/tab, or confirm to proceed without it. |
| 2 | Confluence unit page | yes | ⚠️ *Confluence page not found for <unit>* — give the URL, or confirm none exists. |
| 3 | Interview 1 questionnaire (and Interview 2 for modernized units) | yes | ⚠️ *Questionnaire not attached for <unit>* — attach it, or confirm none exists. Flag a questionnaire that covers a different unit. |
| 4 | Architecture pages | yes | ⚠️ *<Backup / Update Management> page unavailable* — needed for rows 13/14/22/23. |

A general "go ahead" does not cover a missing source — each needs its own explicit
confirmation. Known limitation: very large inventory workbooks can exhaust the M365
connector's read budget before the Handover tab; ask the user to upload the relevant
rows instead of retrying.

## 4. Reading rules
- **Confluence:** ignore Authors, Change Log, Review Log and Signoff Log sections. Use
  only the details tables, Goal block, Source/Target, checklists and Special
  Instructions.
- **Questionnaire:** read the right server column; never use the `Example` column;
  `Status = Closed` → use, `Open` → treat as unconfirmed (row becomes In Progress);
  latest dated comment overrides. Don't pull answers that don't answer the field.

## 5. Map the 24 fields
Row-by-row rules: `references/field-mapping.md` (baseline = Rehost) plus the overrides in
`references/scenario-variants.md` for the unit's scenario. Status per row:
**Done** (complete) · **In Progress** (explicit gaps) · **To-Do** (nothing captured,
needs owner input).

Cross-cutting rules (all rows):
- **Approach always stated in Row 2**: Goal + R-factor (+ scenario) + process
  (simplified/standard interview · forced migration agreed with <names>, owner
  acknowledged risks · no interview, <name> confirmed none required). For forced /
  no-interview cases carry a short flag into rows 9, 12, 19 and 20.
- **Describe the migration event per unit of execution.** A rehosted server is a server
  move — a database that merely lives on it is configuration (rows 12/20), not a
  separate migration. A database instance moved under Database Modernization *is* the
  unit, so its move is the event.
- **Inventory maintenance window** (column `inventory.columns.maintenance_window`) goes
  into Row 13 **and** Row 23 with the identical label
  `Maintenance window (per inventory): <value>` (or `not available (#N/A)`).
- Column D: facts only, **one data point per line**, no bullets, no `|` separators —
  except the compact `RTO: … | RPO: …` line in rows 14 and 22. Every value starts with a
  capital letter. Regular hyphen `-` only, never en/em dashes (the builder enforces it).
- Contacts: Row 2 none; Row 6 only named Workload Owner + Technical Workload Owner;
  Row 7 only the named Testing Representative (no duplicates of Row 6, no interview
  participants).
- Standard-process phrases come from `defaults.standard_processes` with `{client}`
  filled in (e.g. *Backups follow the standard Contoso process*).

## 6. Build the workbook
Write the content JSON (schema: `references/content-schema.md`; worked example for a
Database Modernization unit: `references/example-content.json`), then:

```bash
python scripts/build_operations_manual.py content.json --profile <profile.yaml> --out <dir>
```
The builder adds column C descriptions and Foundation option lists (rows 3, 4, 5, 8),
RTO/RPO definitions (rows 14, 22), sections, colours, wrap/auto-height, freeze panes,
collapsed column F, and the file name from `naming.ops_manual_file`. **Never** patch an
existing workbook with `insert_rows()` — rebuild from the JSON.

Grouping: one file per Application Group (`naming.application_service` grouping), one
Operations Manual tab per unit (tab = unit id), one Handover Summary with one column per
unit.

## 7. Reply
In the user's chat language: Done / In Progress / To-Do counts per unit, the rows that
still need Workload Owner input, and whether RTO/RPO are pending client sign-off.
