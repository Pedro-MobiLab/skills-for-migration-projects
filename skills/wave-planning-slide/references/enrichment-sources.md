# Enrichment — where workload and owner come from

Use the first source that has the unit. Load the Atlassian / Microsoft 365 tools via
tool search first if they are deferred. Take `cloud_id`, space and field labels from
the engagement profile; if a value is missing, find it once (e.g.
`getAccessibleAtlassianResources` for the cloudId) and suggest adding it to the profile.

## 1. Application Cockpit (preferred, when the engagement runs the M&M method)
The Cockpit record is the single source of facts and decisions. Read the
application's name, Workload Owner, the unit's cutover group, Goal, R-factor and
scenario row. If the Cockpit and Confluence disagree, the Cockpit wins.

## 2. Per-unit Confluence page
Most engagements keep one child page per unit, titled after the unit
(`naming.unit_page_title`, default `{unit}`), in `atlassian.confluence_space`.

1. Search for the exact identifier (Atlassian search or CQL `title ~ "<unit>"`).
   Accept only a page whose **title equals the identifier** (or starts with it for
   suffixed pages such as `<unit> - DB Migration`). Ignore Jira issues, IPAM pages,
   checklist templates and personal copies.
2. Fetch the page and read the details table:

| Card field | Confluence label (profile key) | Default label |
|---|---|---|
| Workload | `atlassian.unit_page_fields.workload` | `Workload / Application Name` |
| Owner | `atlassian.unit_page_fields.owner` | `Application / Workload Owner Name & Email` |

Search units one at a time; one fetch returns the whole page.

## 3. Jira card
If there is no page, the migration card (`naming.jira_card_title`) usually carries
the workload in its title: `DD/MM - <Workload> - <Country> - <Env> - <unit>`.

## 4. Inventory workbook
Last resort: the inventory's workload and owner columns (header names in
`inventory.columns`). Inventory owners are often `Name\nemail` — keep the name.

## Owner formatting (all sources)
- First owner's display name, then `+N` for the others:
  `Jane Doe`, `Jane Doe +1`, `Maria Garcia-Lopez +3`.
- Abbreviate a long first name if the line would wrap: `M. Garcia-Lopez +3`.
- Drop e-mail addresses.

## Missing data
No record anywhere, or blank fields → `"missing": true`, `workload`/`owner` = `null`.
List the dimmed units in your reply so the PM can chase them.
