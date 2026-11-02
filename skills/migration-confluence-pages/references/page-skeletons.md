# Generic page skeletons (for page types the engagement has no template for)

Use these only when `atlassian.page_templates.<type>` is empty **and** the user agrees.
Build the page in Confluence storage format with the same conventions as the real
templates: two-column layout (main + right sidebar with Info / TOC), details tables
with *Header row OFF / Numbered rows ON*, checklists as `<ac:task-list>` so tasks can
be ticked. Once the client approves a skeleton, save the page as the engagement
template and put its id in the profile.

Every skeleton has the same backbone:

```
1. <Unit> Details        (2-column table, label | value)
2. Goal                  Goal · R-factor · Scenario · Target · Effort · Decided (Gate 0 date, by)
3. Source Environment    (table)
4. Target Environment    (table — placeholders until the SE fills it)
5. Gate 1 – Ready to plan          [tasks]
6. Gate 2 – Ready to cut over      [tasks]   (2 working days before the window)
7. Cutover                         [tasks]
8. Validation & Sign-off           [tasks]
9. Hypercare → Steady State        [tasks]
10. Special Instructions
```

**Common Gate 1 tasks:** firewall / network rules requested · cutover group built and
approved · test representative named · downtime window agreed by e-mail (link the
e-mail) · Interview 2 complete (modernization only).

**Common Gate 2 tasks:** data replication / sync finished and verified · rollback
procedure written with a named owner · engineer named · window time zone confirmed ·
owner available to test after cutover.

**Common Validation tasks:** smoke test by the test representative · owner sign-off
recorded · monitoring and backup confirmed · CMDB / inventory updated.

**Details table rows (all types):** Workload / Application Name · Status (initial
lozenge) · Owner · Technical owner · Testing representative · Environment · Business
Criticality · Data Confidentiality · Regulatory scope · Cutover date · Testing date ·
Questionnaire (`Link`) · Interview 2 (`Link`) · Jira (`Link`) · Support group ·
Migration specialist.

The sections below list only what is specific to each scenario, with the Interview 2
question IDs that feed each field.

---

## Database Modernization — `{instance} - DB Modernization`
- **Source:** instance, engine/version/edition (DBM-01), databases + sizes (DBM-02),
  HA today.
- **Target:** service + tier (DBM-03), zone redundancy / failover group (DBM-09),
  backup retention / LTR (DBM-10), maintenance window (DBM-11), private endpoint, DNS.
- **Gate 1 extra:** compatibility assessment attached and blockers resolved (DBM-04) ·
  vendor support confirmed (DBM-05) · authentication model decided (DBM-06).
- **Gate 2 extra:** migration method rehearsed with measured downtime (DBM-08) ·
  logins / users recreated · connection-string owner ready (DBM-07).
- **Cutover:** stop writes → final sync / log replay → switch connection strings / DNS
  alias → enable backups & alerts.
- **Rollback:** keep source instance read-only for N days; switch strings back.

## Fileserver Modernization — `{share} - Fileserver Modernization`
- **Source:** path, size, file count (FSM-01), DFS namespace (FSM-06), consumers (FSM-05).
- **Target:** Azure Files tier / Azure NetApp Files (FSM-02), identity-based auth
  (FSM-03), private endpoint + SMB 445 reachability (FSM-10), snapshots / backup
  (FSM-09).
- **Gate 1 extra:** permission owner named (FSM-04) · path-switch method agreed
  (DFS target swap / GPO drive map / app config) (FSM-06).
- **Gate 2 extra:** initial sync complete and delta measured (FSM-07) · open-file /
  long-path issues checked (FSM-08) · NTFS ACLs verified on target.
- **Cutover:** set source read-only → final delta → switch path → validate access with
  test users.
- **Rollback:** revert DFS target / drive map to the source share (kept read-only).

## OS Modernization — `{unit} - OS Modernization`
- **Source / target OS:** OSM-01 → OSM-02; approach in place vs rebuild (OSM-03).
- **Gate 1 extra:** vendor certification on target OS (OSM-04) · media + licence keys
  available (OSM-05) · runtime prerequisites listed (OSM-06).
- **Gate 2 extra:** snapshot / backup taken · local accounts, services, scheduled tasks
  inventoried (OSM-08) · test cases agreed (OSM-09).
- **Cutover:** upgrade or build + reinstall → restore config → test cases.
- **Rollback:** restore snapshot or keep old VM stopped for N days (OSM-10). Hostname /
  IP retention requirement (OSM-07) → Special Instructions.

## SaaS Modernization — `{app} - SaaS Modernization`
- **Details extra:** vendor / product and contract status (SAAS-01), licences (SAAS-02).
- **Target:** tenant / region and data residency (SAAS-04), SSO + provisioning
  (SAAS-05), vendor SLA & support (SAAS-07).
- **Gate 1 extra:** data migration scope agreed (SAAS-03) · integrations to rebuild
  listed with owners (SAAS-06) · coexistence plan (SAAS-08).
- **Gate 2 extra:** trial data load validated · SSO tested · user communication sent.
- **Validation:** business acceptance by the Business Workload Owner.
- **After Hypercare:** legacy data archived per retention (SAAS-09); old servers →
  Decommission cards; exit / export path documented (SAAS-10).

## Application Runtime Modernization — `{app} - App Runtime Modernization`
- **Source:** stack and versions (ART-01), code ownership (ART-02).
- **Target:** runtime (ART-03), config & secrets in Key Vault (ART-05), CI/CD (ART-06),
  scaling targets (ART-09), observability (ART-10), auth (ART-08).
- **Gate 1 extra:** state / session / local-disk writes resolved (ART-04) ·
  dependencies reachable from the target (ART-07) · test strategy (ART-11).
- **Gate 2 extra:** release rehearsed in a non-production slot · rollback via slot swap
  / previous image (ART-12).
- **Cutover:** deploy → swap / switch DNS → monitor.

## VDI Modernization — `{app} - VDI Modernization`
- **Owner:** Workplace / EUC team (not the Workload Owner).
- **Source / target:** platform, users, concurrency (VDI-01) → AVD / Windows 365
  (VDI-02); desktops vs published apps (VDI-03).
- **Gate 1 extra:** image + app packaging plan (VDI-04) · profile solution (VDI-05) ·
  licensing confirmed (VDI-10) · pilot group named (VDI-09).
- **Gate 2 extra:** pilot signed off · peripherals / printing tested (VDI-06) · access
  and conditional-access policies in place (VDI-07) · latency to back-ends checked
  (VDI-08).
- **Cutover:** in rollout waves of users, not a single window — record each user wave
  as its own cutover group.
