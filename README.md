# MobiLab Migration & Modernization skills

Customer-agnostic Claude skills for Cloud Adoption engagements, covering rehost
(lift & shift) **and** modernization (Replatform, Rebuild, Repurchase) along the
MobiLab **Application (Workload) Lifecycle** method.

They were generalised 1:1 from the skills built on a large Azure migration programme;
everything client-specific now lives in an **engagement profile** you fill once per
project.

## Skills

| Skill | Lifecycle step | Produces |
|---|---|---|
| [`migration-questionnaire-generator`](skills/migration-questionnaire-generator/SKILL.md) | 04 Interview 1 · 10 Scenario Review | Pre-filled Interview 1 workbook per application (dropdowns preserved) + Interview 2 workbook per modernization scenario |
| [`migration-confluence-pages`](skills/migration-confluence-pages/SKILL.md) | 11 Readiness → 14 Pre-Migration | Per-unit Confluence checklist pages (server, DB, share, OS, SaaS, runtime, VDI) + Jira cards |
| [`wave-planning-slide`](skills/wave-planning-slide/SKILL.md) | 12 Wave Planning | MobiLab-branded cutover-schedule slide (+ cover) with scenario chips and cutover-group checks |
| [`operations-manual-mapping`](skills/operations-manual-mapping/SKILL.md) | 17 Signed Off → 19 Steady State | 24-field Operations Manual workbook + Handover Summary, with per-scenario row variants |

### What changed versus the original client-specific skills (1:1)

| Generic skill | Main changes |
|---|---|
| `migration-questionnaire-generator` | Template sanitised; rows located by question text (fixes hard-coded row drift); inventory columns by header; dropdown values validated against the Data Validator; Goal signals; new Interview 2 builder with draft question sets for 6 scenarios |
| `migration-confluence-pages` | Template IDs, Jira project/epic, DBA, domain and naming from the profile; page-type catalogue per unit and scenario; generic page skeletons for modernization; Gate 1 / Gate 2 evidence |
| `wave-planning-slide` | Any unit type (server, instance, share, application); scenario chips; cutover-group validation (`--strict`); client logo / name from input; cover text filled by the generator; footnotes; up to 3 columns |
| `operations-manual-mapping` | Foundation scales from the profile; scenario-variants reference (PaaS DB, Azure Files, OS upgrade, SaaS, runtime, VDI); new `build_operations_manual.py` that enforces every formatting rule; header-based inventory columns |

## Repository layout

```
shared/method-primer.md                    # condensed M&M method (source of truth: the live method page)
profiles/_template.engagement-profile.yaml # copy per client; never commit real client profiles here
skills/<skill>/SKILL.md                    # entry point Claude reads
skills/<skill>/references/                 # detail loaded on demand (+ synced copies of shared files)
skills/<skill>/scripts/                    # deterministic generators
skills/<skill>/assets/                     # MobiLab templates (no client data)
tools/sync-shared.sh                       # copies shared/ + profile template into every skill
```

## Using the skills on a new engagement
1. Copy `profiles/_template.engagement-profile.yaml` to the engagement space (private)
   and fill it in: client name, Atlassian cloudId / space / template page IDs, Jira
   project / epic, inventory header names, Foundation value lists, naming conventions.
2. Make an engagement copy of the questionnaire template and align its *Data Validator*
   sheet with the client's Foundation (see the questionnaire skill).
3. Install the skills (zip each `skills/<name>` folder, or add the repo as a plugin
   source) and attach the profile when you run one.

## Maintaining
- Edit `shared/method-primer.md` or the profile template → run `tools/sync-shared.sh`.
- Python dependencies: `python-pptx`, `openpyxl`, `Pillow`, `PyYAML`, `beautifulsoup4`.
- Smoke tests (each writes to a temp folder):
  ```bash
  python skills/wave-planning-slide/scripts/build_wave_planning.py skills/wave-planning-slide/references/example-data.json /tmp/wave.pptx --strict
  python skills/operations-manual-mapping/scripts/build_operations_manual.py skills/operations-manual-mapping/references/example-content.json --profile profiles/_template.engagement-profile.yaml --out /tmp
  python skills/migration-questionnaire-generator/scripts/fill_questionnaire.py --config skills/migration-questionnaire-generator/scripts/example_config.json --profile profiles/_template.engagement-profile.yaml --out /tmp --strict
  python skills/migration-questionnaire-generator/scripts/build_interview2.py --config skills/migration-questionnaire-generator/scripts/example_interview2_config.json --out /tmp
  ```
- Open items inherited from the method: Interview 2 question sets (draft here), Cutover
  Sensitivity weights, and scenario execution workflows are still being defined — keep
  the skills in step when the method page changes.

## Data hygiene
No client names, people, hostnames, page IDs or URLs belong in this repo. Examples use
the fictitious "Contoso". Keep real profiles, client logos and filled outputs in the
engagement's own SharePoint / Confluence space.
