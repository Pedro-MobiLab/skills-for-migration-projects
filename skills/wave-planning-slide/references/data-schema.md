# Data schema — build_wave_planning.py

Worked example: `references/example-data.json` (mixed rehost + modernization wave).

```json
{
  "title": "Migration & Modernization: Wave Planning",
  "subtitle": "Cutover schedule · CW29–CW30 (13–25 July 2026)",
  "_template": "assets/cover-template.pptx",
  "_keep_cover": true,
  "cover": {"title": "Contoso Cloud Migration", "subtitle": "Wave Planning – CW29 & CW30", "date": "13 – 25 July 2026"},
  "client_name": "Contoso",
  "client_logo": "logos/contoso.png",
  "classification": "Confidential",
  "footnotes": ["* SRVERP505 – window not yet agreed by email."],
  "columns": [
    {
      "header": "CW 29",
      "meta": "14–17 July · 5 units",
      "units": [
        {"date": "14 Jul", "unit": "SRVERP505", "unit_type": "server",
         "workload": "ERP Finance", "owner": "Jane Doe", "status": "planned",
         "scenario": "Rehost", "group": "ERP-PRD", "note": "*", "missing": false}
      ]
    }
  ]
}
```

## Top level
| Field | Req. | Notes |
|---|---|---|
| `title` | yes | Slide headline. |
| `subtitle` | yes | `Cutover schedule · <weeks> (<range>)`. |
| `_template` | no | Default `assets/cover-template.pptx` (MobiLab master with all layouts + the cover). Without `_keep_cover` you get the wave slide alone. A client-specific MobiLab deck can be passed instead. Paths resolve relative to the JSON file, then the skill folder. Removed template slides are dropped from the package, not just hidden. |
| `_keep_cover` | no | `true` keeps slide 1 of the template as cover; wave slide becomes slide 2. |
| `cover` | no | `{title, subtitle, date}` written into the cover placeholders. |
| `client_name` | no | Footer text when there is no logo. Omit both → footer is `MOBILAB | Confidential`. |
| `client_logo` | no | PNG; sized by its real aspect ratio at the footer reference height (0.25"). |
| `classification` | no | Footer label, default `Confidential`. |
| `footnotes` | no | List of short lines above the legend (blocked / moved / re-prioritised units). Each line reserves ~0.25" — keep to 1–3. |
| `page_number` | no | Default 2 with cover, 1 without. |
| `columns` | yes | 1–3 columns. Three columns use slightly smaller type. |

## Column
| Field | Req. | Notes |
|---|---|---|
| `header` | yes | e.g. `CW 29`. |
| `meta` | yes | e.g. `14–17 July · 5 units`. |
| `units` | yes | Ordered list. (`servers` accepted for backward compatibility.) |

## Unit
| Field | Req. | Notes |
|---|---|---|
| `date` | yes | `DD Mon`. |
| `unit` | yes | Exact identifier. (`server` accepted for backward compatibility.) |
| `unit_type` | no | `server` / `instance` / `share` / `application` — informational. |
| `workload` | yes* | Application (Workload) name, or `null` if missing. |
| `owner` | yes* | `First Owner +N`, or `null` if missing. |
| `status` | yes | `scheduled` or `planned`. |
| `scenario` | no | Chip text (keep ≤ 26 chars). |
| `group` | no | Cutover group id — enables the one-window / never-split checks. |
| `note` | no | Marker appended to the unit name (`*`), explained in `footnotes`. |
| `missing` | no | `true` → dimmed card with `—` placeholders. |

\* may be `null` only when `missing` is `true`.

## Behaviour
- Card height/gaps adapt to the tallest column (and to the number of footnotes).
- The scenario legend entry appears only if at least one card has a chip.
- Warnings for cutover-group violations go to stderr; `--strict` exits with code 2.
