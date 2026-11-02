# Goal signals — inventory evidence → modernization candidate

Signals are written into the Additional Notes as **proposals for the System Engineer**
(step 07 Goal Proposed). They are never decisions: the Goal is proposed by the SE,
approved by the Tech Lead and confirmed by the Workload Owner (Gate 0). Only emit
signals for scenarios in `method.scenarios_in_scope`.

Phrase: `Goal signal (proposal only): <evidence> -> <Scenario> candidate.`

| Evidence in the inventory | Signal |
|---|---|
| OS at or near end of support (e.g. Windows Server 2012/2012 R2/2016, RHEL 7, CentOS) | OS Modernization candidate |
| SQL Server / Oracle / PostgreSQL version at or near end of support, or a dedicated DB server with a single application | Database Modernization candidate (PaaS) |
| Shared SQL server hosting many small databases | Database Modernization candidate (consolidation to Azure SQL MI / elastic pool) |
| Server type File Share / file server with no application logic | Fileserver Modernization candidate (Azure Files / ANF) |
| Commercial off-the-shelf application whose vendor offers a SaaS edition (name it only if the inventory or user says so) | SaaS Modernization candidate |
| Web / IIS / Tomcat application developed in-house with source access | Application Runtime Modernization candidate |
| Citrix / RDS / terminal servers | VDI Modernization candidate (and split at Intake Review: VDI vs jump hosts) |
| No logins / traffic in the observation window, or owner unknown and decommission noted | Retire candidate (owner confirmation mandatory) |
| Plant-floor / latency / sovereignty constraints, OT server | Retain candidate (Azure Local / Azure Arc recommendation) |
| Vendor appliance OS (FortiOS, QNAP, vCenter…) | Rehost not possible as-is — flag for Tech Lead (replacement or Retain) |

Reminders:
- Effort is judged per unit; a modernization above `method.effort_threshold` is
  **rehosted now** with the target recorded for later — mention that in the signal when
  obvious (e.g. *App Runtime Modernization candidate - likely above threshold, rehost now*).
- Do not signal on assumptions (e.g. "probably has a SaaS version") — evidence only.
