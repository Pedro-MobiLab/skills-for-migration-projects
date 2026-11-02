# Field mapping — inventory → Interview 1 questionnaire

## 1. Inventory columns (by header, from the engagement profile)
Never hard-code column numbers — inventories grow. Resolve each logical field with the
header text in `inventory.columns`:

```python
def col_index(header_row, wanted):
    wanted = wanted.lower()
    for i, h in enumerate(header_row):
        if h and wanted in str(h).lower():
            return i            # 0-based
    raise KeyError(wanted)
```

| Logical field | Profile key | Typical header |
|---|---|---|
| Unit / server name | `unit_name` | Server name |
| On-prem IP | `ip` | On-prem IP Address |
| Workload | `workload` | Workload Name |
| Server type | `unit_type` | Server Type |
| Environment | `environment` | Environment |
| OS | `os` | OS Version |
| Business criticality | `business_criticality` | Business Criticality |
| Data criticality | `data_classification` | Data Criticality |
| VM / SQL backup policy | `backup_policy`, `sql_backup_policy` | Backup Policy / SQL Backup Policy |
| Workload / technical owner | `workload_owner`, `technical_owner` | Workload Owner / Technical Owner |
| Target region / subscription | `target_region`, `target_subscription` | Target Azure Region / Target Subscription |
| SQL version | `sql_version` | SQL |
| Grouping | `grouping` | Grouping Proposal |
| Goal / R-factor / scenario (optional) | `goal`, `r_factor`, `scenario` | — |

If two headers match the same text, pick the exact match and tell the user.

## 2. Questionnaire cells (sheet `General`)
Rows are located by question text with `references/cell-map.json` — edit anchors there
when the template changes. Current template positions, for orientation only:

### Workload level (column G)
| Field (config key) | Anchor | Content |
|---|---|---|
| `workload` | What is the Workload / Application Name | Workload name |
| `wlo` | Who is the Workload Owner | `WLO: <name> - <email>\nData owner: same as WLO (to confirm)` |
| `tech` | Who is the Technical Workload Owner | `Full Name: <name>\nEmail Address: <email>\nApproval to contact vendor by MobiLab: Yes / No` |
| `tester` *(optional)* | responsible for executing a workload test | only if already known |
| `updater` *(optional)* | responsible for updating the application after | only if already known |
| date | `C13` | `DD.MM.YYYY` (script) |
| — | `C11`, `C12` | formulas `=G16`, `=G17` — **do not edit** |

### Per server (G = 1 … K = 5)
| Config key | Anchor | Dropdown list | Source |
|---|---|---|---|
| `name` | Which servers are used | — | unit name |
| `ot` | Operational Technology | Yes / No | only with evidence |
| `type` | What is the server type | Server Type | normalised server type |
| `env` | What type of environment | Environment | upper-case env |
| `crit` | Business Criticality does the server have | Business Criticality | normalised |
| `data` | data sensitivity | Data Sensitivity | normalised |
| `ha` | Should the server be highly available | Yes / No | only with evidence (cluster / AG) |
| `physical` | physical devices connected | Yes / No | only with evidence |
| `appliance` | vendor-specific) appliance | Yes / No | vendor OS in inventory |
| `modernize` | plans of modernizing | Yes / No | only if the inventory says so — otherwise ask |
| `facing` | internet or internal | Application Accessibility | public IP → `Public`, else `Internal` |
| `hostdb` | host any local database instances | Yes / No | DB server → `Yes` |
| `sqlcompat` | MS SQL Server Compatibility Limitation | Yes / No | SQL present, unverified → `Maybe` |
| `access` | existing AD groups | — | `defaults.admin_groups` (one per line) |

### Additional Notes (row below "Additional Notes")
Header: `Workload: … | Prepared by MA: … | Date: … | Wave … | Lifecycle: 04 Interview 1 Scheduled`
Per server: `<name>: OS <os> | Env <env> | On-prem IP <ip> | Server type <type> | Backup Policy <vm> [| SQL Backup <sql>]. <grouping, target subscription/region, risk flags, Goal signal (proposal only)>`
Optional `notes_extra` lines for workload-wide remarks.

## 3. Normalisation (inventory → dropdown)
Values must match the Data Validator **exactly**; the script lists the allowed values
when one does not match.

| Inventory value | Dropdown value |
|---|---|
| `Most critical` / `Somewhat critical` / `Less critical` / `Not critical` | Title case: `Most Critical` … |
| `Application`, `App` | `Application Server` |
| `Database`, `SQL`, `DB` | `Database Server` |
| `File Share`, `Fileserver` | `File Share Server` |
| `Proxy` | `Proxy Server` |
| `Terminal`, `RDS` | `Terminal Server` |
| `prd` | `PRD` (upper-case every environment) |
| data classes | title case to match the list |

If the client uses different tiers, fix the engagement copy of the template's Data
Validator first — don't bend the values.

## 4. Owner parsing
```python
def parse_owner(raw):
    if not raw:
        return "", ""
    parts = [p.strip() for p in str(raw).split("\n") if p.strip()]
    name = parts[0] if parts else ""
    email = next((p for p in parts if "@" in p), "")
    return name, email
```
Missing or unreachable owner → write the name you have and append
`(contact to be confirmed)`. Never invent an address.

## 5. workload_config.json
```json
[
  {
    "workload": "Order Management",
    "file": "optional explicit file name.xlsx",
    "wlo": "WLO: Jane Doe - jane.doe@client.example\nData owner: same as WLO (to confirm)",
    "tech": "Full Name: Alex Miller\nEmail Address: alex.miller@client.example\nApproval to contact vendor by MobiLab: Yes / No",
    "admin_groups": ["DOMAIN\\Server-Admins"],
    "notes_header": "Workload: Order Management | Prepared by MA: <name> | Date: 02.11.2026 | Wave 4",
    "servers": [
      {"name": "SRVORD01", "type": "Application Server", "env": "PRD",
       "crit": "Somewhat Critical", "data": "Confidential", "facing": "Internal",
       "hostdb": "", "sqlcompat": "",
       "note": "OS Windows Server 2016 | On-prem IP 10.1.2.10 | ... Goal signal (proposal only): ..."}
    ],
    "notes_extra": ["Goal signals are proposals for the System Engineer - not decisions."]
  }
]
```
- Every dropdown key takes an exact list value or `""` (empty = leave blank).
- `admin_groups` overrides `defaults.admin_groups` for this file; `[]` writes nothing.

## 6. Interview 1 catalogue alignment
`cell-map.json → interview1_catalogue` maps template rows to the M&M catalogue
(APPROVE / ASK / MARK / TECHNICAL_TRACK). Use it to tell the interviewer which rows are
pre-filled facts to confirm (APPROVE), which only the owner can answer (ASK), which are
Foundation statements (MARK), and which the System Engineer answers separately from
dependency data (TECHNICAL_TRACK) — those don't need to be asked in the owner session.
