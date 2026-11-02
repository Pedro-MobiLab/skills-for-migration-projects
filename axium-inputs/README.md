# Inputs for the Axium question catalogue and templates

Reusable content produced while generalising the migration skills. It is kept in place
inside the skills (so the fallback skills keep working) and indexed here so the Axium /
Application Cockpit owners can take it over. When Axium adopts a piece, note it in the
table and treat Axium as the source from then on.

| Content | File | Method assignment | Status |
|---|---|---|---|
| Interview 1 catalogue ↔ universal questionnaire rows (APPROVE / ASK / MARK / TECHNICAL_TRACK) | [`cell-map.json` → `interview1_catalogue`](../skills/migration-questionnaire-generator/references/cell-map.json) | A2 (done) — cross-check | Mapping |
| Interview 2 question sets for 6 scenarios (OSM, FSM, DBM, SAAS, ART, VDI — 63 questions, answer types, audience, approve/ask) | [`interview2-question-sets.json`](../skills/migration-questionnaire-generator/references/interview2-question-sets.json) | D3 (to build) | Draft v0.1 — Tech Lead review |
| Goal signals: inventory evidence → modernization candidate | [`goal-signals.md`](../skills/migration-questionnaire-generator/references/goal-signals.md) | "What the rules propose" (Cockpit) | Draft |
| Page-type catalogue per unit and scenario (titles, Jira card sets) | [`page-types.md`](../skills/migration-confluence-pages/references/page-types.md) | C2 (scenario execution workflows) | Draft |
| Modernization page skeletons with Gate 1 / Gate 2 / cutover / rollback items per scenario | [`page-skeletons.md`](../skills/migration-confluence-pages/references/page-skeletons.md) | C2 / Confluence gate checklists | Draft |
| Operations-manual overrides per scenario (what changes for PaaS DB, Azure Files, SaaS, runtime, VDI) and readiness items | [`scenario-variants.md`](../skills/operations-manual-mapping/references/scenario-variants.md) | Handover packs | Draft |

Question IDs (`OSM-01`, `DBM-04`, …) are referenced by the page skeletons and the
operations-manual variants — keep them stable if Axium imports the sets.
