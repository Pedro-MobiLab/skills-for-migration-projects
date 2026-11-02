# Page-type catalogue

One row per page type. `template key` is the key under `atlassian.page_templates` in
the engagement profile. Titles use `naming.unit_page_title` (default `{unit}`) plus the
suffix. Card titles use `naming.jira_card_title`
(default `{dd_mm} - {workload} - {country} - {env} - {unit}{suffix}`).

| Page type | When | Template key | Page title | Jira cards (suffix → labels) |
|---|---|---|---|---|
| Server – Rehost (Windows) | Goal Migrate, R-factor Rehost/Relocate, Windows | `server_rehost_windows` | `{unit}` | `` → migration · ` - FW` → firewall |
| Server – Rehost (Linux) | as above, Linux | `server_rehost_linux` | `{unit}` | same |
| Database – joint effort | DB moves **with** a rehosted server or from a shared SQL server to a target SQL VM (DBA involved) | `database_joint_effort` | `{unit} - DB Migration` | ` - DB Migration` → migration |
| Database Modernization | DB **instance** → PaaS (Azure SQL MI / SQL DB / PostgreSQL / MySQL flexible) | `database_modernization` | `{instance} - DB Modernization` | ` - DB Modernization` → migration, modernization · ` - FW` → firewall |
| Fileserver Modernization | **Share** → Azure Files / Azure NetApp Files | `fileshare_modernization` | `{share} - Fileserver Modernization` | ` - Fileserver Modernization` → migration, modernization · ` - FW` → firewall |
| OS Modernization | Server keeps its role, OS upgraded (in place or rebuild + app reinstall) | `os_modernization` | `{unit} - OS Modernization` | ` - OS Modernization` → modernization (+ ` - FW` if host/IP changes) |
| SaaS Modernization | Application → vendor SaaS (Repurchase) | `saas_modernization` | `{app} - SaaS Modernization` | ` - SaaS Modernization` → modernization · ` - FW` (egress / allow-list) · ` - Decommission` per old server |
| Application Runtime Modernization | Application → App Service / AKS / Container Apps / Functions (Replatform or Rebuild) | `app_runtime_modernization` | `{app} - App Runtime Modernization` | ` - App Runtime Modernization` → modernization · ` - FW` · ` - Decommission` per old server |
| VDI Modernization | Desktop / app delivery → Azure Virtual Desktop / Windows 365 | `vdi_modernization` | `{app} - VDI Modernization` | ` - VDI Modernization` → modernization · ` - FW` · ` - Decommission` |

## Rules
- A modernized application often still contains **rehosted servers** (units outside
  scenario scope or above the effort threshold). Those get normal server pages.
- One unit = one page. A shared database instance used by several applications gets
  **one** page; reference it from each application's pages.
- Units above the effort threshold that are rehosted now: create the Rehost page and
  record the deferred target in Special Instructions (`Modernization target recorded
  for a later phase: <scenario> → <target>`).
- `Decommission` cards: create them up front in status Backlog with the old server
  names, so they are not forgotten; they are worked only after the replacement has
  passed Hypercare.
- Retire / Retain / Review → no pages, no cards from this skill.
