---
name: migration-questionnaire-generator
description: >-
  FALLBACK for engagements where the Application Cockpit (Axium) is not used for
  interviews, or when an offline Excel questionnaire is explicitly requested.
  Generate pre-filled migration interview questionnaires for any client: the
  Interview 1 workbook (one .xlsx per Application/Workload, one column per server,
  filled from the client's migration inventory with the MobiLab universal template)
  and, when the Goal is Modernize, the Interview 2 / Scenario Review workbook per
  modernization scenario (OS, Fileserver, Database, SaaS, Application Runtime, VDI).
  Use whenever the user wants to create, pre-fill or prepare interview questionnaires
  or interview sheets before a Workload Owner interview — "make questionnaires for
  these servers", "pre-fill the questionnaire for <workload>", "prep the interview
  sheets for wave X", "prepare Interview 2 for the database modernization" — or gives
  an inventory file plus the template and asks to map one into the other. Preserves the
  template's Excel dropdowns (x14 data validations), which openpyxl silently destroys
  on save, so always use this skill instead of editing the template directly.
---

# Migration interview questionnaire generator (customer-agnostic)

> **Status: fallback / pre-Axium.** If the engagement runs interviews in the
> Application Cockpit (Axium), do **not** generate an Excel questionnaire — it would
> create a second source of truth. Tell the user that and stop, unless they confirm
> they need the offline workbook (no Axium on this engagement, client requires a file,
> or Axium not yet writing data). The question content (Interview 1 catalogue mapping
> in `references/cell-map.json`, Interview 2 sets in
> `references/interview2-question-sets.json`) remains valid input for Axium.

Lifecycle position: **04 Interview 1 Scheduled** (prepare Interview 1) and **10 Scenario
Review** (prepare Interview 2, only when the Goal is *Modernize*). See
`references/method-primer.md` §5 for the approve / ask / mark logic.

| Output | Script | When |
|---|---|---|
| Interview 1 workbook — one per Application (Workload), servers as columns G–K | `scripts/fill_questionnaire.py` | Before every first interview |
| Interview 2 workbook — one per Application × scenario, units as columns | `scripts/build_interview2.py` | After Gate 0 for each scenario row |

## Why the Interview 1 script exists (read first)
The template's dropdowns are stored as Microsoft *x14 extended data validations*.
`openpyxl` drops all of them on save — the file looks fine but every dropdown is gone.
`fill_questionnaire.py` edits the sheet XML inside the zip and copies every other part
byte-for-byte; it compares the x14 count before and after and fails loudly if it
changed. **Never** open the template in openpyxl and `save()`.

## 0. Engagement profile
Load the client's engagement profile (`references/engagement-profile.template.yaml`).
Used keys: `client.slug`, `client.name`, `inventory.*` (file, sheet, **column header
names**), `foundation.*` (to check that values exist in the template's Data Validator),
`naming.questionnaire_file`, `defaults.admin_groups`, `method.scenarios_in_scope`,
`method.effort_threshold`. Missing key → ask once, then suggest adding it.

**Per-engagement template copy.** Before the first interview of a new engagement, copy
`assets/questionnaire_template.xlsx`, align its *Data Validator* sheet with the client's
Foundation (environments, criticality tiers, data classes, backup / update policies,
domains, network segments) and store it in the engagement space. Edit the Data
Validator in Excel (not openpyxl), then run this skill with `--template <that copy>`.

## 1. Interview 1 workflow

### 1.1 Read the inventory
- Prefer the inventory the user uploads now; inventories are living files. If you must
  use an older copy, say so.
- Open with `openpyxl(read_only=True, data_only=True)` and locate columns **by header
  text** from `inventory.columns` (case-insensitive substring) — never by position.
- Match the requested servers on the unit-name column; group them per Application
  (user's grouping > workload column > grouping-proposal column). Owners are often
  `Name\nemail` — see `references/field-mapping.md` for the parser.
- Large inventories (3 MB+) are fine locally; do not fetch them through the SharePoint
  connector (they fail).

### 1.2 Map fields
`references/field-mapping.md` lists every mapping and normalisation. In short:
- **Workload level:** workload name, WLO (+ data owner), technical owner; date in C13.
  C11/C12 are formulas — never touch them.
- **Per server (G = server 1 … K = server 5):** server name, type, environment, business
  criticality, data sensitivity, accessibility, OT / HA / physical / appliance flags when
  the inventory has evidence, hosts-local-DB + MSSQL compatibility for DB servers, AD
  admin groups from `defaults.admin_groups`.
- **Additional Notes:** a header line + one line per server: OS, IP, backup policy, SQL
  instance, grouping, target subscription / region, risk flags (Tier 0, public IP →
  certificate re-issue, physical devices, vendor appliance) and **Goal signals**.

Dropdown cells must receive an **exact Data Validator value**; the script warns (and
`--strict` fails) on off-list values. Anything not in the inventory stays blank — those
are interview questions, not facts to invent.

### 1.3 Goal signals (modernization awareness)
Interview 1 is where MODERNIZATION_PLANS and REPLACEMENT_PLANNED are asked, and the
System Engineer proposes the Goal right after (step 07). Help them by adding **signals**
(never decisions) to the server note when the inventory shows them — rules in
`references/goal-signals.md` (e.g. OS out of support → *OS Modernization candidate*;
SQL version out of support → *Database Modernization candidate*; dedicated file server
→ *Fileserver Modernization candidate*; commercial off-the-shelf app with a SaaS
edition → *SaaS candidate*). Only signal scenarios listed in
`method.scenarios_in_scope`.

### 1.4 Generate
Build the config (schema in `references/field-mapping.md`; example:
`scripts/example_config.json`), then:
```bash
python scripts/fill_questionnaire.py --config workload_config.json --out <dir> \
  --profile <profile.yaml> [--template <engagement copy>] [--strict]
```
More than 5 servers in one Application → split by environment or cutover group (one
file each); the template has 5 server columns.

### 1.5 Name the files
`naming.questionnaire_file` (default
`<year>_MobiLab_universal_migration_interview_questionaire_<client>_<application>.xlsx`,
lower-case, spaces → `_`, parentheses removed). "questionaire" is the established
MobiLab spelling — keep it.

## 2. Interview 2 workflow (Goal = Modernize)
1. For each **scenario row** (scenario × units) take the units from the Cockpit / Gate 0
   record.
2. Pre-fill the `approve` questions from systems (inventory, discovery, assessment) in a
   `prefill` block; leave `ask` questions empty.
3. Run:
   ```bash
   python scripts/build_interview2.py --config interview2_config.json --out <dir> --profile <profile.yaml>
   ```
   Example: `scripts/example_interview2_config.json`. Question sets live in
   `references/interview2-question-sets.json` (IDs `OSM-`, `FSM-`, `DBM-`, `SAAS-`,
   `ART-`, `VDI-`). They are a **draft starter set** — tell the user so on first use and
   record client-agreed changes in that file.
4. Address the workbook to the scenario's audience (DBA for databases, EUC team for VDI,
   procurement + vendor for SaaS…), not automatically to the Workload Owner.

## 3. Verify before presenting
Each Interview 1 file: opens; sheets `General`, `Data Validator`, `Readme`; x14 count
unchanged (script prints it); workload cells filled; C11/C12 still formulas; no
off-list dropdown warnings (or each explained). Each Interview 2 file: one column per
unit, dropdowns on list questions, Status = Open.

## 4. Present and report gaps
Send the files, then list per Application what was filled and **what still needs
confirmation**: missing owner contacts, servers not found in the inventory, assumed
`data owner = WLO`, unconfirmed IPs/ports, Goal signals for the System Engineer, and
risk flags (Tier 0, public IP, physical dependencies, vendor appliances) as candidate
exceptions for the Tech Lead — without blocking delivery. Client-facing content in the
workbook stays in the client language (default English).
