# Scenario variants — row overrides on top of the Rehost baseline

Rows not mentioned keep the baseline rule from `field-mapping.md`. Use the Interview 2
answers (question IDs in brackets) for modernized units.

## Migrate — Rehost / Relocate
Baseline applies unchanged.

## Modernize — OS Modernization (server, Replatform)
| Row | Override |
|---|---|
| 2 | Approach: *OS modernized from <old OS> to <new OS> (<in-place upgrade / rebuild and reinstall>)* (OSM-01..03). |
| 15 | `PRD - SRV01 - OS modernized 14/07/2026 (Windows Server 2016 -> 2022)`. |
| 20 (4) | Target OS and runtime prerequisites (OSM-06). |
| 24 | Keep the static text, and add vendor-certification caveats if OSM-04 was "not certified". |
| Readiness | Backup · Monitoring · Patching schedule · Firewall · Old VM snapshot removed · Hypercare. |

## Modernize — Database Modernization (instance, Replatform → PaaS)
| Row | Override |
|---|---|
| 1 | Same format; the unit is the database / managed instance. |
| 2 | Approach: *<instance> (<engine/version>) moved to <service> (<tier>)* (DBM-01..03). |
| 11 | Service tier, vCores / DTU, storage, availability SLA of the service. |
| 12 | Consumers (application servers), connection method, authentication (DBM-06, DBM-07). |
| 13 | *Platform maintenance: Azure-managed, maintenance window <config>* (DBM-11) + the inventory line. No OS patching statement. |
| 14 | RTO / RPO from the service capabilities (PITR, geo-restore, failover group) and the SLA catalogue; pending client sign-off. |
| 15 | `PRD - <instance> - modernized to <service> <date>` — the instance move **is** the event. |
| 16 | Entra admin / Entra authentication status (DBM-06). |
| 19 | SQL logins / contained users / managed identities. |
| 20 | Service, compatibility level, features in use (DBM-04). |
| 21 | Private endpoint IP + FQDN, port (1433 / redirect range), public endpoint state, firewall rules. |
| 22 | Automated backups: PITR retention, LTR policy (DBM-10). Baseline first line still applies. |
| 23 | *Patching: platform-managed by Azure (no OS patching required)* + inventory line. |
| Readiness | Backup (native) · Monitoring / alerts · Patching = Platform-managed · Network rules / private endpoint · Entra authentication · Hypercare. |

## Modernize — Fileserver Modernization (share, Replatform → Azure Files / ANF)
| Row | Override |
|---|---|
| 2 | Approach: *share <path> moved to <Azure Files tier / Azure NetApp Files>; path switched via <DFS / GPO / app config>* (FSM-01, 02, 06). |
| 11 | Size, file count, performance tier / IOPS. |
| 12 | Consumers: applications, mapped drives, DFS namespace (FSM-05, 06). |
| 13 / 23 | Platform-managed maintenance; no patching; inventory line still added. |
| 15 | `PRD - <share> - modernized to <target> <date>`. |
| 16 / 17 | Identity-based authentication (AD DS / Entra Kerberos) and the permission owner (FSM-03, 04). |
| 19 | Accounts used by applications to access the share. |
| 21 | Private endpoint, SMB 445 reachability, firewall rules (FSM-10). |
| 22 | Share snapshots / Azure Backup for Files retention (FSM-09). |
| Readiness | Backup / snapshots · Monitoring · Patching = Platform-managed · Private endpoint · ACLs verified · Hypercare. |

## Modernize — SaaS Modernization (application, Repurchase)
| Row | Override |
|---|---|
| 2 | Approach: *replaced by <vendor product> (SaaS); data migrated: <scope>* (SAAS-01, 03). |
| 7 | Vendor support model and contacts + internal testing representative (SAAS-07). |
| 8 | Vendor support hours from the contract (not inferred). |
| 9 | Vendor release / change notifications; internal configuration-change process. |
| 13 / 23 | *Vendor-managed maintenance* + vendor notification channel. No inventory line if no server remains (write `not applicable (SaaS)`). |
| 14 | Vendor SLA from the contract (SAAS-07). |
| 16 / 18 | SSO (Entra ID SAML / OIDC), provisioning (SCIM) (SAAS-05). |
| 21 | Egress / allow-list requirements and integration endpoints (SAAS-06). |
| 22 | Vendor backup responsibility, data export / exit path, legacy archive (SAAS-09, 10). |
| Readiness | SSO · Provisioning · Integrations live · Legacy data archived · Old servers decommissioned · Hypercare. |

## Modernize — Application Runtime Modernization (application, Replatform / Rebuild)
| Row | Override |
|---|---|
| 2 | Approach: *re-platformed to <App Service / Container Apps / AKS / Functions>* (ART-03). |
| 9 | CI/CD pipeline and release approval (ART-06). |
| 10 | Application Insights / Log Analytics (ART-10). |
| 11 | Scaling and performance targets (ART-09). |
| 13 / 23 | Platform patching by Azure; image / runtime update responsibility; deployment slots. |
| 19 | Managed identities, Key Vault secrets (ART-05). |
| 20 | Components, stack, state handling (ART-01, 04, 07). |
| 22 | Code and configuration in the repository; data backups of dependent stores; rollback via slot swap / previous image (ART-12). |
| Readiness | Pipeline · Monitoring · Secrets in Key Vault · Network / private access · Backups of data stores · Hypercare. |

## Modernize — VDI Modernization (application, Replatform → AVD / Windows 365)
| Row | Override |
|---|---|
| 6 | Owner is the Workplace / EUC team. |
| 11 | Users, concurrency, session density (VDI-01). |
| 13 / 23 | Image update cadence, host-pool scaling plan, patching of session hosts. |
| 16 / 18 | Entra ID, conditional access, MFA, client access paths (VDI-07). |
| 20 | Host pools, app groups, image and packaging (VDI-02..04). |
| 22 | Profile storage (FSLogix) backup (VDI-05); images versioned in the gallery. |
| Readiness | Host pools · Images · Profiles · Conditional access · Printing / peripherals · Hypercare. |

## Retire / Retain / Review
No operations manual. For **Retire**, offer a short decommission note: archive location,
retention period, owner confirmation (date, by whom), servers decommissioned. For
**Retain**, nothing — the recommendation lives in the Cockpit.
