# Field mapping — questionnaire → Confluence page

Default for the MobiLab universal migration interview questionnaire (sheet `General`).
**Locate rows by question text** (column D, case-insensitive substring) — row numbers
drift between template versions. Single-value answers are in column G (`Response`);
per-server answers in G (server 1) … K (server 5); column M holds comments.

Always read column M: the latest dated comment (`DD.MM: …`) overrides the cell value.
Ignore column F (`Example`) — it holds placeholders, never answers.

## Interview 1 (all page types)
| Page field | Question text anchor | Notes |
|---|---|---|
| Workload / Application Name | `Workload / Application Name` | Then format with `naming.application_service`. |
| Owner | `Who is the Workload Owner` | `Name - email`. |
| Technical owner (if the template has it) | `Technical Workload Owner` | |
| Testing representative | `responsible for executing a workload test` | Gate 1 item. |
| Post-migration updater | `responsible for updating the application after` | Connection strings / config. |
| Data Confidentiality | `data sensitivity` | Foundation value. |
| Environment | `type of environment` | Foundation value. |
| Business Criticality | `Business Criticality` | Foundation value. |
| High Availability | `highly available` | |
| Cutover date | user's date > `suggested date ideal for Migration` > DB details `Proposed migration date` | |
| Same-day rollback | `rollback on the same day` | → Special Instructions if Yes. |
| OS | value in the OS row of the server header, or `OS Version` from inventory | Empty if absent. |
| Shutdown / power-on steps | `steps required before the server gets shutdown`, `after powering-on` | → Special Instructions. |
| Ports | `communication ports are in use` | Unknown → "Ports unknown – risk accepted by WLO" only if stated. |
| DNS alias | `internal DNS alias record` | → Special Instructions. |
| Fileshare path / updater | `path of the fileshare`, `updating the fileshare path` | |
| Modernization plans | `plans of modernizing` | Context for the Goal block, never the Goal itself. |

## Database pages (`DB details` sheet, if present)
| Page field | Source |
|---|---|
| On-prem instance | `Shared SQL server` / instance column |
| Database name(s) | `Database name` |
| Target | `Target Azure Server` (joint effort) or the Goal target (modernization) |
| SQL login | General: `Which SQL Login is used` |
| DB connection method | General: `How does the application connect to the Database` (Alias / IP / FQDN) |
| Compatibility limit | General: `MS SQL Server Compatibility Limitation` |

## Interview 2 (modernization pages)
Map the Interview 2 workbook of the matching scenario (produced by the
`migration-questionnaire-generator` skill, question IDs `OSM-*`, `FSM-*`, `DBM-*`,
`SAAS-*`, `ART-*`, `VDI-*`). The page skeletons list which IDs feed which field.
