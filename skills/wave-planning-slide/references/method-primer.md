# Migration & Modernization method primer

Condensed from the MobiLab **Application (Workload) Lifecycle** method (M&M, working
paper Oct 2026). The method is the source of truth; this primer only carries what the
skills need to classify, label and route work. If the live method and this file
disagree, the method wins — update this file (`shared/method-primer.md`) and run
`tools/sync-shared.sh`.

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **Application (Workload)** | The unit the customer recognises and owns. Carries the Goal. |
| **Unit of execution** | What actually moves: a **server**, a **database instance**, a **file share**, or (for SaaS / runtime / VDI) the **application** itself. Effort and scenario are judged per unit, never per application. |
| **Cutover group** | Application + Environment (DEV / QA / PRD…), merged wherever a server, instance or share is shared. The unit of **downtime, sign-off and wave placement**. One window, one sign-off, **never split across waves**. |
| **Wave** | A planned batch of cutover groups. A group without Gate 1 appears in no wave. |
| **Goal** | What the application becomes (see §2). Proposed by the System Engineer, approved by the Tech Lead, confirmed by the Workload Owner (= Gate 0). |
| **Scenario row** | One modernization work item on one unit, with its R-factor and effort. Only exists when the Goal is *Modernize*. |
| **Application Cockpit** | The single record of facts, decisions, scenario rows and gate declarations, shown read-only to the owner and mirrored with Jira. |
| **Foundation** | The customer's controlled value lists (environments, criticality, confidentiality, regulatory scope). Values are stated once, not free text. |

## 2. Goals and R-factors

| Goal | Typical R-factor(s) | Notes |
|---|---|---|
| **Migrate** | Rehost, Relocate | Default outcome. Moves as-is. |
| **Modernize** | Replatform, Rebuild, Repurchase (+ Rehost for units outside scenario scope) | Carries ≥1 scenario row. A rehosted server inside a modernized application is normal. |
| **Retire** | Retire | Owner confirmation can never be skipped; needs an archive & retention answer. |
| **Retain** | Retain | Out of scope for now; a recommendation to the customer, not scheduled work. |
| **Review** | — | Undecided and visible as such (replaces "Held"). |

The method uses exactly these R-factors: **Rehost, Relocate, Replatform, Rebuild,
Repurchase, Retire, Retain.** Do not introduce Refactor / Rearchitect / Replace as
labels unless the engagement profile adds them.

## 3. Modernization scenarios

| Scenario | Unit | R-factor | Effort | Interview 2 audience |
|---|---|---|---|---|
| OS Modernization | Server | Replatform | Low | Technical Workload Owner; vendor where certified |
| Fileserver Modernization | Share | Replatform | Low–Medium | Technical Workload Owner; share permission owner |
| Database Modernization | Instance | Replatform | Medium | DBA (Technical Workload Owner if no DBA) |
| SaaS Modernization | Application | Repurchase | Medium–High | Business Workload Owner, procurement, vendor |
| Application Runtime Modernization | Application | Replatform or Rebuild | High | Developer or vendor; Technical Workload Owner |
| VDI (Desktop) Modernization | Application | Replatform | High | Workplace / EUC team (not the Workload Owner) |

**Recommendation-first** (come from *Retain*, not scheduled): Azure Local, Azure Arc,
Mainframe Modernization.

**Effort threshold** is set per engagement (worked example: *medium*), applied per
unit. Work above the line is **rehosted now** with the modernization target recorded
for a later phase.

## 4. Lifecycle — 19 steps, 3 gates

Bands: **Decide** (→ Gate 0) · **Ready** (Gate 0 → Gate 1) · **Run** (Gate 1 →).

| # | Step | Owner | Gate |
|---|---|---|---|
| 01 | Backlog | Lead Migration Analyst | |
| 02 | Intake Review (scope · unit · programme · route) | Lead System Engineer | |
| 03 | Pipeline | Lead Migration Analyst | |
| 04–06 | Interview 1 Scheduled / In Progress / Complete | Migration Analyst | |
| 07 | Goal Proposed | System Engineer | |
| 08 | Goal Approved | Tech Lead | |
| 09 | Goal Accepted | Workload Owner | **Gate 0** — Goal set; scenario rows recorded if Modernize; servers/instances/shares confirmed; environments identified |
| 10 | Scenario Review (Modernize only) — Interview 2 per scenario row | Migration Analyst | |
| 11 | Readiness | Migration Analyst + SE | |
| 12 | Wave Planning | Migration Analyst | **Gate 1** — firewall rules requested; cutover group built & approved; test representative named; downtime window agreed **by email** |
| 13 | Ready for Migration | Lead System Engineer | |
| 14 | Pre-Migration | System Engineer | **Gate 2** (2 working days before window) — replication finished & verified; rollback procedure with named owner; engineer named; time zone matches window; owner available to test |
| 15 | Migrating | System Engineer | |
| 16 | Migrated | System Engineer | |
| 17 | Signed Off | Project Manager | |
| 18 | Hypercare (~10 working days) | Hypercare | |
| 19 | Steady State | Managed Operations | |

Exceptions (enterable from any step, return to where they left): **Blocked** (reason
mandatory) · **Rejected by Owner** (→ Goal Proposed) · **Escalated** · **Rolled Back**
(→ Pre-Migration).

**Fast path:** if Intake Review finds a known target, the Analyst recommends it at
the end of Interview 1 and *Goal Proposed* is skipped.

## 5. Interview 1 — approve, ask, mark

- **Approve (7, pre-filled from systems):** SERVER_LIST, DEPENDENCIES, ENVIRONMENT,
  LOCAL_DATABASE, FILESHARE_CONNECTED, OPERATING_SYSTEM (vendor appliance),
  PHYSICAL_DEVICES.
- **Ask (10, only the Workload Owner can answer):** USE_CASE, USER_COUNT,
  DOWNTIME_TOLERANCE, BUSINESS_IMPACT, MODERNIZATION_PLANS, REPLACEMENT_PLANNED,
  WORKLOAD_OWNER, TEST_REPRESENTATIVE, POST_MIGRATION_CHANGES, OWNER_ABSENCE.
- **Mark (3, once per application, Foundation values):** BUSINESS_CRITICALITY,
  CONFIDENTIALITY, REGULATORY_SCOPE. Carried per cutover group as ENV_CRITICALITY /
  ENV_CONFIDENTIALITY (inherited unless stated; ENV_SOURCE mandatory once stated).
- **Technical track (9, System Engineer from dependency data):** COMMUNICATION_PORTS,
  TRAFFIC_ENDPOINTS, ADDRESS_DEPENDENCY, DNS_ALIAS, OUTBOUND_INTERNET,
  THIRD_PARTY_WHITELIST, WEB_PUBLIC_ADDRESS, WEB_DOMAIN_AND_PATH, LICENSE_DONGLE.

Every approved item records who approved it, when, and the source.

## 6. Downtime & sensitivity

Downtime window in three moments: owner states a constraint (Interview 1) → Analyst
proposes a concrete window per cutover group (Wave Planning) → owner agrees by email
(before Gate 1). **Cutover Sensitivity** band per group (from environment, business
criticality, impact/user count, scenario mix) drives wave order (lowest first),
approval depth, mandatory rollback plan and hypercare length.

## 7. How the skills use this

| Skill | Lifecycle position | What it relies on |
|---|---|---|
| `migration-questionnaire-generator` | 04–06 (Interview 1), 10 (Interview 2) | §5, §3 audiences |
| `migration-confluence-pages` | 11–14 (Readiness → Pre-Migration) | §1 units, §3 scenarios, Gate 1/2 evidence |
| `wave-planning-slide` | 12 (Wave Planning) | cutover groups, Gate 1 → Scheduled vs Planned |
| `operations-manual-mapping` | 17–19 (Signed Off → Steady State) | Goal + R-factor + scenario per unit |
