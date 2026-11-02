# Field mapping — 24 rows (baseline: rehosted server)

This is the baseline for **Goal Migrate / Rehost or Relocate**. For any other scenario,
apply the overrides in `scenario-variants.md` on top of this table.

`{client}` = `client.name`; scales and phrases come from the engagement profile.
Column C (description + options) is written by the builder — you only supply column D
(value), E (status) and F (open points).

| Nr | Title | Primary sources | Column D rules |
|---|---|---|---|
| 1 | Application Service | Handover / questionnaire workload name + country + env | Always filled. Format with `naming.application_service` (default `<Workload> - <Country> - <ENV>`). Use the workload name **exactly** as in the source (no re-casing, expansion or prefix stripping); append the country even if the name already starts with it. |
| 2 | Description | Questionnaire notes, Confluence, handover migration type | Start with `Application Description:`; then purpose, architecture, dependencies, location. **Always state the approach** (see "Approach sentence" below). No contact names, no interview participants; don't repeat rows 5/6. |
| 3 | Environment Classification | Questionnaire / Confluence / handover | Only the selected value with label, e.g. `PRD (Production)`. |
| 4 | Business Impact Classification | Business Criticality tag | The client's tier + its impact phrase from `foundation.business_criticality`, e.g. `Less Critical - Impacts individual teams…`. Map the tier to itself — never collapse tiers. No uptime / RTO / RPO here. |
| 5 | Data- and Information Classification | Data confidentiality tag | One value from `foundation.data_classification`. |
| 6 | Owner | Questionnaire WLO + Technical WLO / Confluence | Name + email, only people explicitly named as Workload Owner / Technical Workload Owner. |
| 7 | Support Process & Contacts | Questionnaire test representative + Confluence support group | Testing Representative only (no duplicates of row 6). In Progress if the support group is empty. |
| 8 | Support Times | Not captured — infer from criticality + location | Only the inferred option. Always In Progress + "needs owner confirmation". |
| 9 | Change Process | Not captured | Note: owner to confirm whether the service follows the standard `{client}` change process. |
| 10 | Monitoring Process | Confluence post-migration tasks + handover | What is configured + note: owner to add monitoring outliers (security, data, other) if required. |
| 11 | Performance Indicators | Criticality → availability %, latency, storage, HA | Partial — application KPIs usually not captured. |
| 12 | Dependencies & Interfaces | Questionnaire (dependent workloads, authentication, file shares, DB) | All share paths, dependent apps, auth method. |
| 13 | Maintenance Window | Update Management page (env + criticality + OS) + inventory maintenance window | If the handover marks patching as not configured: `Patching Scheduled: Not Yet Configured in Azure`. Plus the applicable maintenance configuration. **Always** add `Maintenance window (per inventory): <value>` (same wording as row 23). |
| 14 | Service Level Requirements | Backup Management page (SLA catalogue) by criticality | `RTO: <x> | RPO: <y> (per SLA catalogue, pending {client} sign-off)`. |
| 15 | Platform Stages | Questionnaire env + Confluence | Every stage with unit and cutover date, e.g. `PRD - SRV01 - migrated 14/07/2026`. Describe the unit's own move only. |
| 16 | User Directory | Questionnaire AD groups, domain + Confluence | |
| 17 | Request for Permissions | Questionnaire | Without an explicit owner statement: *No service-specific deviations from the standard `{client}` IDM process were found during the migration process. Please update if required.* |
| 18 | Login & Access | Questionnaire authentication, accessibility, ports | |
| 19 | Service Accounts | Questionnaire DB login, share accounts | Partial — permissions and rotation rarely documented. |
| 20 | System Architecture | Confluence + questionnaire + handover | The 8 numbered sub-questions, each answer on its own line, blank line between blocks; unanswered → *To be completed by workload owner*. Sub-questions: (1) high-level architecture; (2) main components and interactions; (3) architecture diagram; (4) key technology stacks; (5) external / third-party dependencies; (6) file shares, storage, messaging; (7) internet connectivity in/out; (8) PIM used. Keep the closing note that the owner must fill gaps and keep the handbook up to date. |
| 21 | Network Communication & Interfaces | Confluence IPs/NSG + questionnaire ports/DNS + handover + firewall request file | Label rules as `Firewall Rules:` (never the file name). Handover `Firewall Rule Collection = No` means traffic is controlled by NSG — say so; it does not mean "no rules". |
| 22 | Backup & Recovery | Handover policy name + Backup Management page | First line: `defaults.standard_processes.backup` (e.g. *Backups follow the standard {client} process*). Policy name from the handover wins. `RTO … | RPO …` line allowed. |
| 23 | Scheduled Activities | Update Management page | Patching only. If not configured: *Patching: workload owner to schedule the patching accordingly*. **Always** add `Maintenance window (per inventory): <value>` (same wording as row 13). |
| 24 | Known Problems | — | Static: *Workload owner to fill it out*. |

## Approach sentence (Row 2)
Combine Goal, R-factor, scenario and process:

- Standard interview, rehost: *…migrated to Azure (<region>) - Goal: Migrate (Rehost) -
  via the simplified migration approach.*
- Modernization: *…modernized to Azure (<region>) - Goal: Modernize (Replatform -
  Database Modernization). <source> moved to <target> via the standard interview
  process.*
- Forced: *…forced migration agreed with <names>; the workload owner acknowledged the
  migration risks and confirmed the migration.*
- No interview: *…no interview - <name> confirmed none required.*

Forced / no-interview flags (short, factual):
Row 9 prepend *Forced migration agreed with <names>; WLO acknowledged risks.* ·
Row 12 *No questionnaire available (forced migration).* · Row 19 *Not captured (forced
migration - no interview).* · Row 20 unanswerable sub-questions → *Not captured (forced
migration).*

## Handover Summary (shared tab, one column per unit)
Sections: **Unit Identity** (unit before, workload, Goal / R-factor / scenario, target
resource after, role, domain) · **Network** · **Platform / Infrastructure** ·
**Post-Migration Readiness** (traffic light) · **Key Dates** (cutover, testing,
handover). Readiness items depend on the scenario — see `scenario-variants.md`.

Field composition:
- *Migration type*: handover value + `(simplified migration)` / `(forced migration)`
  where applicable.
- *Role*: function + context on one line — `License Server (replacing SRV010)`,
  `SQL AG node - Availability Zone 1 (Most Critical)`, `Order database (Somewhat Critical)`.
- *High Availability*: `None` for standalone; `Yes - AZ<n>` / `Zone-redundant` for HA.
- *Backup*: policy name + criticality tier in parentheses.

Readiness colours (builder): Configured / Steady State → green · Not Configured / No /
Missing → red · N/A / Platform-managed / Vendor-managed / Hypercare → amber.
