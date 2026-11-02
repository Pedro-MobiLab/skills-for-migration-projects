# Content schema — build_operations_manual.py

Worked example: `example-content.json` (Database Modernization unit).

```json
{
  "title": "Operations Manual - <Application Service>",
  "subtitle": "<Programme> - <Goal / scenario> - <unit(s)>",
  "workload": "Order Management",
  "client_slug": "contoso",
  "filename": "optional-explicit-name.xlsx",
  "units": [
    {
      "tab": "SRV01",
      "title": "optional per-tab title",
      "subtitle": "optional per-tab subtitle",
      "rows": {
        "1": {"value": "Order Management - DE - PRD", "status": "Done"},
        "7": {"value": "Testing Representative:\nSam Taylor - sam@client.example",
              "status": "In Progress", "open": ["Support Group name and contact"]}
      }
    }
  ],
  "handover_summary": {
    "title": "Handover Summary - <Application Service>",
    "columns": ["SRV01", "SRV02"],
    "sections": [
      {"title": "Unit Identity", "fields": [["Workload Name", ["Order Management", "Order Management"]]]},
      {"title": "Post-Migration Readiness", "traffic_light": true,
       "fields": [["Backup configured", ["Configured", "Not Configured"]]]}
    ]
  }
}
```

| Key | Notes |
|---|---|
| `rows` | Keys `"1"`…`"24"`. Missing rows render as To-Do with empty value — supply all 24. |
| `value` | Column D. Use `\n` between data points. Dashes are normalised to `-`. |
| `status` | `Done` / `In Progress` / `To-Do` (exact). |
| `open` | Column F bullets (`›` added by the builder). Ignored for `Done`. |
| `traffic_light` | Colours each value: green (configured), red (`Not …`, `No`, `Missing`), amber (`N/A`, `Platform-managed`, `Vendor-managed`, `Hypercare`). |
| `filename` | Optional; otherwise `<yyyymmdd>_MobiLab_<client_slug>_<workload>_<unit|group>_operations_manual.xlsx`. |

The builder prints a Done / In Progress / To-Do count per tab — reuse it in the reply.
