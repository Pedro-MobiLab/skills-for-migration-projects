---
name: wave-planning-slide
description: >-
  Build a MobiLab-branded "Wave Planning" cutover-schedule slide (with optional
  branded cover) for any client's cloud migration or modernization programme, from
  a wave-planning source (screenshot, Excel/CSV export, Jira/Cockpit list, or a
  pasted list of units with dates). Use whenever the user wants to turn a wave or
  migration schedule into a slide, mentions "wave planning", "migration schedule",
  "cutover schedule", "CW29/CW30 units", "which servers/databases/shares move when",
  or asks for the bi-weekly wave deck. Handles every unit of execution — servers,
  database instances, file shares and applications — and labels each card with its
  R-factor or modernization scenario (Rehost, OS/DB/Fileserver/SaaS/App Runtime/VDI
  Modernization). Enriches workload and owner from the engagement's source of record,
  classifies Scheduled vs Planned, enforces cutover-group rules, and renders on the
  official MobiLab template.
---

# Wave Planning Slide (customer-agnostic)

Produce one MobiLab slide showing the cutover schedule for 1–3 calendar weeks side by
side. Each **unit of execution** (server, DB instance, file share, or application) is a
card with: date chip · status marker (white/grey outline = **Scheduled**, amber =
**Planned**) · unit identifier · `Workload · Owner` · optional **scenario chip**
(R-factor or modernization scenario). Legend, footnotes and the
`MOBILAB | <client> | Confidential` footer are drawn automatically.

This is a layout skill with a fixed house design (`references/layout-spec.md`). Your
job is to gather the right data, classify it correctly and feed it to the generator.

## Before you start — engagement profile

Ask for (or locate) the client's **engagement profile** (see
`references/engagement-profile.template.yaml`). This skill uses:
`client.name`, `client.programme`, `client.logo`, `defaults.planned_marker`,
`atlassian.cloud_id`, `atlassian.confluence_space`, `atlassian.unit_page_fields`,
`naming.unit_page_title`. If there is no profile, ask only for what you need (client
name, where owner/workload data lives) and carry on.

Read `references/method-primer.md` once if you are not familiar with units, cutover
groups, Goals, R-factors and gates — the slide's rules come from there.

## Workflow

### 1. Extract units and dates from the source
Per unit, record exactly:
- **Unit identifier** — hostname, `server\instance`, share path, or application name.
  Read hostnames character by character (0/O, 1/l are common OCR traps).
- **Unit type** — `server`, `instance`, `share` or `application`.
- **Cutover date** → `DD Mon` (e.g. `14 Jul`).
- **Cutover group** (Application + Environment) if the source carries it.
- **Goal / R-factor / scenario** if the source carries it (Cockpit, Jira, inventory).
- **Planned marker** — the profile's `defaults.planned_marker` (default `-?`) on a unit
  means the slot is not confirmed.

Group units by calendar week (one column per week). Keep source order within a week,
but keep members of the same cutover group adjacent.

### 2. Classify status — exactly two states
| Evidence | Status | Marker |
|---|---|---|
| Window agreed by email and Gate 1 declared, **or** no planned marker in the source | `scheduled` | white + grey outline |
| Window only proposed, Gate 1 open, **or** planned marker present | `planned` | amber |

Never invent a third state. Blocked, rescheduled or re-prioritised units keep their
status and get a `note` marker (`*`, `**`) plus a line in `footnotes` explaining why.

### 3. Label the scenario chip (optional but recommended for mixed waves)
Use the shortest label that tells the audience what kind of move it is:

| Goal / scenario | Chip text examples |
|---|---|
| Migrate | `Rehost`, `Relocate` |
| OS Modernization | `OS Modernization` |
| Database Modernization | `DB → Azure SQL MI`, `DB → PaaS` |
| Fileserver Modernization | `Share → Azure Files` |
| SaaS Modernization | `Repurchase · SaaS` |
| Application Runtime Modernization | `App Runtime → App Service` |
| VDI Modernization | `VDI → AVD` |

If the whole wave is one scenario (e.g. pure lift & shift), omit chips and say it in
the title instead (e.g. `Lift & Shift: Wave Planning`). Never show *Retire*, *Retain*
or *Review* units on a wave slide — they are not scheduled work.

### 4. Enrich workload and owner
Look up each unit in the engagement's source of record — in this order of preference:
Application Cockpit → per-unit Confluence page → Jira card → inventory workbook.
Mechanics, field names and the owner-formatting rule (`First Owner +N`) are in
`references/enrichment-sources.md`.

If a unit has no record or blank fields, keep the card and set `"missing": true` (it
renders dimmed with `—`). Never guess a workload. Tell the user afterwards which units
were dimmed.

### 5. Check cutover-group rules
A cutover group has **one window** and is **never split** across columns/waves. The
generator warns if a group has several dates or spans columns; `--strict` makes it
fail. If it warns, ask the user which date is right rather than "fixing" it yourself.

### 6. Build the JSON and generate
Assemble the JSON from `references/data-schema.md` (worked example:
`references/example-data.json`), then:

```bash
cd <skill-dir>
python scripts/build_wave_planning.py data.json output.pptx --strict
```

- **Cover (usually wanted):** set `"_template": "assets/cover-template.pptx"`,
  `"_keep_cover": true` and a `cover` block (`title` = programme name, `subtitle`,
  `date`). The generator writes the cover text for you — see `references/cover.md`.
- **Client logo:** set `client_logo` to a PNG path; without it the client name is
  written as text. Never redraw logos as shapes.

### 7. QA before delivering (required)
```bash
python <pptx-skill>/scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 110 output.pdf slide
```
Check: no card overflows into legend/footnotes; status colours match; chips don't
collide with text; dimmed cards are the missing ones; cover text is right. Fix and
re-render, then deliver the `.pptx`.

## Defaults
- **Title:** `Migration & Modernization: Wave Planning` (or `Lift & Shift: Wave Planning`
  for pure rehost waves; follow the client's established title once it exists).
- **Subtitle:** `Cutover schedule · <weeks> (<date range>)`.
- **Column meta:** `<date range> · <N> units` (say `servers` if every unit is a server).

## Notes
- Data differs every run — never reuse a previous week's units.
- Keep client-facing text in the client's language (`client.language`, default English).
- Contract or planning-horizon constraints (e.g. "plan only until date X") are
  internal: don't put them on a client-facing slide.
