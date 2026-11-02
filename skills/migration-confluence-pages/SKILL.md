---
name: migration-confluence-pages
description: >-
  FALLBACK for engagements where the Application Cockpit (Axium) does not create the
  Confluence pages and Jira cards itself.
  Create the per-unit migration / modernization checklist pages in Confluence
  (server, database, file share, OS, SaaS, application-runtime or VDI) and the
  matching Jira cards (unit, firewall, database, scenario) for any client engagement,
  from the workload's interview questionnaire and the engagement profile. Use when
  the user gives a unit name (server, DB instance, share, application) plus a
  questionnaire and a parent Confluence page and wants "the migration pages",
  "checklist pages", "Confluence child pages", "Jira cards for the migration" or
  "the DB page" created — for rehost (lift & shift) or for any modernization
  scenario (Replatform, Rebuild, Repurchase).
---

# Migration / modernization Confluence pages + Jira cards (customer-agnostic)

> **Status: fallback / pre-Axium.** First check whether the engagement's Application
> Cockpit (Axium) already creates these pages and cards. If it does, don't duplicate
> them — tell the user. If Axium is live but does not create them, use the Cockpit
> record (Goal, scenario rows, cutover group, owners, gate declarations) as the source
> instead of the questionnaire, and create only what the method keeps in Confluence:
> the execution checklist, Gate 1 / Gate 2 evidence and the handover material.

Creates, for one Application (Workload) and its units of execution, the Confluence
checklist child pages and the Jira cards that track them, filled from the interview
questionnaire. Lifecycle position: **11 Readiness → 14 Pre-Migration**; the pages
hold the Gate 1 and Gate 2 evidence (see `references/method-primer.md`).

## 0. Engagement profile (read first)
Load the client's engagement profile (`references/engagement-profile.template.yaml`).
This skill uses: `atlassian.cloud_id`, `atlassian.confluence_space`,
`atlassian.page_templates.*`, `atlassian.jira.*`, `naming.application_service`,
`naming.jira_card_title`, `naming.unit_page_title`, `naming.ad_domain`, `defaults.dba`,
`sharepoint.questionnaire_folder`. Missing keys → ask once, then suggest adding them.

## 1. Inputs (ask only for what is missing)
1. The Application (Workload) and its **units**: server hostnames, DB instances, file
   shares, or the application itself for SaaS / runtime / VDI.
2. The **Goal** and, per unit, the **R-factor / scenario** (from the Cockpit, the
   questionnaire's modernization answers, or the user). Default when nothing says
   otherwise: Goal *Migrate*, R-factor *Rehost*.
3. Questionnaire `.xlsx` (Interview 1; plus the Interview 2 workbook per scenario row
   when the Goal is *Modernize*).
4. Parent Confluence page URL (usually `<App> - <Country> - <Env>`).
5. Questionnaire link (SharePoint) for the page field and the Jira card.
6. Optional: DB details table/screenshot, migration date, support group, specialist.

## 2. Decide which pages and cards to create
Use `references/page-types.md`: it maps each unit + R-factor/scenario to a page type,
its template key in the profile, its title pattern and its Jira card set. Summary:

| Unit / scenario | Page | Cards |
|---|---|---|
| Server — Rehost / Relocate | `<UNIT>` (server checklist, Windows or Linux) | unit + FW |
| DB on a shared/standalone SQL server moved with it (Rehost) | `<UNIT> - DB Migration` | DB |
| DB instance — Database Modernization | `<INSTANCE> - DB Modernization` | unit + FW |
| Share — Fileserver Modernization | `<SHARE> - Fileserver Modernization` | unit + FW |
| Server — OS Modernization | `<UNIT> - OS Modernization` | unit (+ FW if IP/host changes) |
| Application — SaaS / App Runtime / VDI | `<APP> - <Scenario>` | unit + FW (+ decommission card for the old servers) |

Retire, Retain and Review units get **no** pages. If the profile has no template for a
type, offer the generic skeleton from `references/page-skeletons.md` and create the
page from it only after the user agrees.

## 3. Conventions (apply exactly)
- Page titles from `naming.unit_page_title` (default `{unit}`) plus the type suffix;
  all pages are children of the given parent page.
- Workload / Application Name and the Application Services tag use
  `naming.application_service` (default `<App> - <Country> - <Env>`), with no extra
  prefixes.
- Status cell: keep only the initial lozenge from the template (e.g.
  `AWAITING MIGRATION`); do not add others.
- Keep the template layout (columns, sidebars, Info/Authors/Change Log/TOC) and every
  checklist table untouched. **Only fill data cells.**
- **Details tables (Unit Details, Source, Target): Header row OFF, Numbered rows ON.**
  Templates often put the first row in `<thead>`, which Confluence renders as a header
  row. Move that `<tr>` into `<tbody>` (no `<thead>`), keep the label as `<th>`, make
  the value cell a `<td>`, keep `data-number-column="true"` on the `<table>`.
- People: `Name - email`, one person per paragraph.
- DBA: questionnaire value, else `defaults.dba`; never write "default:".
- Dates: `<time datetime="YYYY-MM-DD">`; testing date = cutover date unless stated.
- Questionnaire / Jira fields: hyperlink with text `Link`.
- **Goal block** (all modernization pages, and server pages when the profile's template
  has the field): `Goal: <Goal> · R-factor: <R> · Scenario: <scenario>` and the target
  (e.g. `Azure SQL Managed Instance`, `Azure Files premium`), as recorded at Gate 0.
- **Special Instructions**: short, technical, cutover-relevant only — DB dependency +
  link to the other page; units out of scope / decommissioned; who updates connection
  strings or share paths; unknown ports / accepted risk; internal URL / DNS alias;
  same-day rollback requirement; shutdown / power-on steps from the questionnaire;
  for modernization: the data-sync method, the coexistence period and the cut-over
  switch (DNS / connection string / share path). Do not include sales text ("MobiLab
  will perform…"), e-mail logistics or business-usage remarks.
- **Source Environment**: identifier, OS / engine version; domain from
  `naming.ad_domain` only if evidenced (e.g. AD groups in that domain) — flag it as
  inferred. Leave IP / vCPU / RAM / storage and the Target Environment as template
  placeholders unless the source gives them.
- Leave Support Group / Migration Specialist empty unless given.

## 4. Field mapping from the questionnaire (or the Cockpit)
Default mapping for the MobiLab universal questionnaire is in
`references/field-mapping.md` (anchor rows by **question text**, not row number;
server columns G–K, comment column M). Always read the comment column: the latest
dated comment (e.g. `22.09: …`) overrides older values. For modernization pages, also
map the Interview 2 answers listed per scenario in `references/page-skeletons.md`.

## 5. Procedure
1. Read the questionnaire with openpyxl (`data_only=True`, suppress the
   data-validation warning).
2. Fetch the needed templates with `getConfluencePage` (`contentFormat: html`). The
   result is big → saved to file; extract the body with `jq`.
3. **Create the Jira cards first** (profile: project, issue type, epic, priority;
   description copied from `template_issue_key`; `Confluence Link` left without URL):
   titles from `naming.jira_card_title`, labels from `atlassian.jira.labels`
   (unit/DB/scenario → `migration` (+ `modernization` for modernization), FW → `firewall`).
   Replace the generic "Questionnaires" link with this workload's questionnaire link.
4. Build each body with BeautifulSoup: in the first layout column, for each 2-cell row
   match the label text and replace the value cell (including the Questionnaire and
   Jira links). Unwrap `span.annotation` (template inline comments).
5. Apply the details-table settings (step 3 rule).
6. Shrink before sending (token budget): drop `data-local-id` attributes; drop
   `style="background-color…"` where `data-background` exists; for `nested-table`
   extensions parse `data-parameters`, drop `cxhtml`/`reason`, strip `localId` from the
   inner ADF and re-emit with a single-quoted attribute. Content after the Target
   Environment table is static — keep it byte-identical.
7. Paste the HTML (print in chunks with `head -c`/`tail -c`; mind multibyte
   characters at the split) into `createConfluencePage` (parentId, space from profile).
   Order when pages link to each other: create the dependent page (e.g. DB) first, then
   the main page with the link, then update the small page with the back-link.
8. Verify: `<ac:task>` count in the returned storage equals the template's count; key
   headings and values present; details tables have no header row.
9. Edit the Jira cards (markdown) to set `Confluence Link`; verify labels/parent with
   a JQL `key in (...)` search.

## 6. Safety — never overwrite the user's edits
- Before any `updateConfluencePage`, re-fetch and compare with what you last wrote. If
  it changed, build the update from the **current** body, or ask.
- If the version number jumps by more than 1, stop and tell the user (Page history can
  restore it).
- For small changes on a large page the user is editing, give them the exact links /
  text to paste instead.

## 7. Final reply
In the user's chat language, short: links to pages and cards, what was inferred, what
was left empty, and which Gate 1 items the pages still miss (firewall request, test
representative, downtime window e-mail).
