# DeRexi: Policy Pilot — Database Design

**Project:** DeRexi: Policy Pilot
**Institution context:** Aurum Capital Bank (fictional federally chartered private bank)
**Database:** Supabase Postgres 17
**Project ref:** `vnumvjamqtuxlctjdzoe`
**Owner:** Kiona Wilson
**Phase:** SDLC Week 3 — System Design (database design scheme)

---

## 1. Purpose

DeRexi is a policy-governance and security-assistance assistant. This document defines
the relational data model that supports the five MVP components:

1. Policy Management
2. Policy Search & Retrieval
3. Clarification & Routing
4. Incident Assistance
5. Policy Health Dashboard

The design stores approved company policies as **versioned documents**, records employee
**conversations** with DeRexi and the **policy sources** each answer is based on, routes
unanswerable questions to **policy owners**, captures **security incidents**, and collects
**feedback** for dashboard reporting.

---

## 2. Design principles

| Principle | How it is applied |
|---|---|
| **Single source of truth** | Each policy has one `policies` master record; its text lives in immutable `policy_versions` rows. |
| **Versioning over overwriting** | Policy text is never updated in place. New versions are inserted, preserving regulatory audit history. |
| **Auditability** | Timestamps (`created_at`, `effective_date`, `review_date`, `resolved_at`) support compliance and review workflows. |
| **Traceability** | `policy_citations` links every DeRexi answer to the exact policy version used. |
| **Referential integrity** | Foreign keys everywhere, with `on delete` rules chosen per relationship (cascade for owned detail rows, set null for cross-references). |
| **Least privilege** | Row Level Security is enabled on every table. |
| **Regulatory alignment** | Policy content is organized around federal banking regulations (GLBA, BSA/AML, Reg Z, Reg B/ECOA, Reg E/CC, OFAC, UDAAP). |

---

## 3. Entity relationship map

```
departments ──1:N──► users ◄──N:1── roles
                       │
                       │ (owner_id)
                       ▼
policy_categories ─1:N─► policies ──1:N──► policy_versions ──1:N──► policy_citations
                                                                        ▲
                                                                        │ (message_id)
users ──1:N──► conversations ──1:N──► messages ───────────────────────┘
                 │                      ▲
                 │                      │ (message_id)
                 └──1:N──► clarification_requests ──1:N──► clarification_replies
                                    │
                                    └──N:1── policies / users (assignee)

incident_categories ─1:N─► incident_reports ──N:1── users (reporter / assignee)

messages ──1:N──► feedback ◄──N:1── users
```

---

## 4. Table reference

### 4.1 Reference domain

#### `departments`
Business and shared-service units at Aurum Capital Bank.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `name` | text | not null, unique |
| `created_at` | timestamptz | not null, default `now()` |

Seeded: Compliance, Information Technology, Operations, Human Resources, Marketing,
Lending, Wealth Management.

#### `roles`
Application access levels.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `name` | text | not null, unique |
| `created_at` | timestamptz | not null, default `now()` |

Seeded: Employee, Policy Owner, System Administrator.

#### `users`
Employee profiles. Note: this table models the *business* user, separate from any future
Supabase Auth identity.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `first_name` | text | not null |
| `last_name` | text | not null |
| `email` | text | not null, unique (`@aurumbank.com`) |
| `department_id` | bigint | FK → `departments.id`, not null |
| `role_id` | bigint | FK → `roles.id`, not null |
| `created_at` | timestamptz | not null, default `now()` |

---

### 4.2 Policy Management (Component 1)

#### `policy_categories`
Groups related policies for browsing and dashboard reporting.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `name` | text | not null, unique |
| `description` | text | |
| `created_at` | timestamptz | not null, default `now()` |

#### `policies`
Master record for each policy and its approval lifecycle.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `title` | text | not null, unique |
| `summary` | text | |
| `category_id` | bigint | FK → `policy_categories.id` |
| `owner_id` | bigint | FK → `users.id` (accountable policy owner) |
| `status` | text | not null, default `'draft'`, check in (`draft`,`in_review`,`approved`,`retired`) |
| `created_at` | timestamptz | not null, default `now()` |
| `updated_at` | timestamptz | not null, default `now()` |

#### `policy_versions`
Immutable versioned text of a policy. The **current version** is the most recently created
version for a policy. DeRexi only answers from versions whose parent policy is `approved`.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `policy_id` | bigint | FK → `policies.id`, not null, on delete cascade |
| `version_no` | text | not null, default `'1.0'` |
| `title` | text | not null |
| `body` | text | not null (full policy text) |
| `effective_date` | date | |
| `review_date` | date | |
| `requires_review` | boolean | not null, default `false` |
| `created_by` | bigint | FK → `users.id` |
| `created_at` | timestamptz | not null, default `now()` |
| — | — | unique (`policy_id`, `version_no`) |

---

### 4.3 Policy Search & Retrieval (Component 2)

#### `conversations`
A policy question session between an employee and DeRexi.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `user_id` | bigint | FK → `users.id`, not null |
| `topic` | text | |
| `status` | text | not null, default `'open'`, check in (`open`,`closed`) |
| `created_at` | timestamptz | not null, default `now()` |
| `updated_at` | timestamptz | not null, default `now()` |

#### `messages`
Individual turns in a conversation.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `conversation_id` | bigint | FK → `conversations.id`, not null, on delete cascade |
| `sender` | text | not null, check in (`user`,`derexi`) |
| `body` | text | not null |
| `created_at` | timestamptz | not null, default `now()` |

#### `policy_citations`
Records which policy version DeRexi based an answer on.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `message_id` | bigint | FK → `messages.id`, not null, on delete cascade |
| `policy_version_id` | bigint | FK → `policy_versions.id`, not null |
| `excerpt` | text | |
| `created_at` | timestamptz | not null, default `now()` |
| — | — | unique (`message_id`, `policy_version_id`) |

---

### 4.4 Clarification & Routing (Component 3)

#### `clarification_requests`
Questions DeRexi could not answer confidently, routed to the responsible policy owner.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `conversation_id` | bigint | FK → `conversations.id`, on delete set null |
| `message_id` | bigint | FK → `messages.id`, on delete set null |
| `user_id` | bigint | FK → `users.id`, not null (requester) |
| `policy_id` | bigint | FK → `policies.id`, on delete set null |
| `reason` | text | |
| `status` | text | not null, default `'open'`, check in (`open`,`in_progress`,`resolved`,`closed`) |
| `assigned_to` | bigint | FK → `users.id` (policy owner) |
| `resolved_at` | timestamptz | |
| `created_at` | timestamptz | not null, default `now()` |

#### `clarification_replies`
Threaded replies between the employee and the policy owner.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `request_id` | bigint | FK → `clarification_requests.id`, not null, on delete cascade |
| `sender_id` | bigint | FK → `users.id`, not null |
| `body` | text | not null |
| `created_at` | timestamptz | not null, default `now()` |

---

### 4.5 Incident Assistance (Component 4)

#### `incident_categories`
Types of reportable security incidents.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `name` | text | not null, unique |
| `description` | text | |
| `default_severity` | text | not null, default `'medium'`, check in (`low`,`medium`,`high`,`critical`) |
| `created_at` | timestamptz | not null, default `now()` |

Seeded: Phishing or Social Engineering, Malware or Ransomware, Lost or Stolen Device,
Account or Credential Compromise, Data Loss or Mishandling, Insider Threat.

#### `incident_reports`
Security incidents reported by employees and triaged by the SOC.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `reporter_id` | bigint | FK → `users.id`, not null |
| `category_id` | bigint | FK → `incident_categories.id` |
| `description` | text | not null |
| `severity` | text | not null, default `'medium'`, check in (`low`,`medium`,`high`,`critical`) |
| `status` | text | not null, default `'reported'`, check in (`reported`,`triaged`,`escalated`,`resolved`) |
| `assigned_to` | bigint | FK → `users.id` (SOC analyst) |
| `escalation_level` | integer | not null, default `1` |
| `resolution_notes` | text | |
| `created_at` | timestamptz | not null, default `now()` |
| `updated_at` | timestamptz | not null, default `now()` |

---

### 4.6 Policy Health Dashboard (Component 5)

#### `feedback`
Employee feedback on DeRexi answers.

| Column | Type | Constraints |
|---|---|---|
| `id` | bigint | PK, identity |
| `message_id` | bigint | FK → `messages.id`, on delete cascade |
| `user_id` | bigint | FK → `users.id`, on delete set null |
| `rating` | boolean | not null (`true` = helpful) |
| `comment` | text | |
| `created_at` | timestamptz | not null, default `now()` |

Dashboard metrics are **derived** from the tables above rather than stored separately:
policy counts by status, reviews due, open clarification requests, incident counts by
status/severity, feedback helpful rate, and most-cited policies.

---

## 5. Enumerated values

| Field | Allowed values |
|---|---|
| `policies.status` | `draft`, `in_review`, `approved`, `retired` |
| `conversations.status` | `open`, `closed` |
| `messages.sender` | `user`, `derexi` |
| `clarification_requests.status` | `open`, `in_progress`, `resolved`, `closed` |
| `incident_reports.severity` | `low`, `medium`, `high`, `critical` |
| `incident_reports.status` | `reported`, `triaged`, `escalated`, `resolved` |
| `feedback.rating` | boolean (`true` = helpful) |

---

## 6. Indexes and search strategy

**Foreign-key / filter indexes**

| Index | Table |
|---|---|
| `policies_category_id_idx`, `policies_owner_id_idx`, `policies_status_idx` | `policies` |
| `policy_versions_policy_id_idx` | `policy_versions` |
| `conversations_user_id_idx` | `conversations` |
| `messages_conversation_id_idx` | `messages` |
| `policy_citations_message_id_idx`, `policy_citations_policy_version_id_idx` | `policy_citations` |
| `clarification_requests_user_id_idx`, `clarification_requests_assigned_to_idx`, `clarification_requests_status_idx` | `clarification_requests` |
| `clarification_replies_request_id_idx` | `clarification_replies` |
| `incident_reports_reporter_id_idx`, `incident_reports_category_id_idx`, `incident_reports_status_idx`, `incident_reports_assigned_to_idx` | `incident_reports` |
| `feedback_message_id_idx`, `feedback_rating_idx` | `feedback` |

**Search indexes** — the `pg_trgm` extension (installed in the `extensions` schema) provides
trigram GIN indexes used for natural-language retrieval:

- `policies_title_trgm_idx`
- `policy_versions_title_trgm_idx`
- `policy_versions_body_trgm_idx`

**Retrieval ranking.** The MVP ranks current approved policy versions with a blended score:

```
score = 0.6 * word_similarity(question, body) + 0.4 * similarity(question, title)
```

`word_similarity` finds the best-matching passage inside the long policy body, while
`similarity` rewards title matches. Results below the confidence threshold are not treated
as authoritative and instead trigger **Clarification & Routing**. This is a deterministic
retrieval baseline; semantic/embedding search is a future enhancement.

---

## 7. Security model

- Row Level Security is **enabled on all 14 tables**.
- The Python backend connects with a direct Postgres connection string (service role), so it
  operates with full access for MVP development.
- `authenticated` users have `SELECT` access to policy/catalog data and reference data; write
  policies are intentionally deferred until Supabase Auth is integrated.
- RLS policies are the mechanism, not permissions grants, so the posture can be tightened
  table-by-table as the app matures without schema changes.
- Secrets (`DATABASE_URL`) are kept in `backend/.env`, which is git-ignored.

---

## 8. Seed data (Aurum Capital Bank)

The database is seeded with a realistic federal banking handbook so retrieval and the
dashboard can be tested end to end.

| Item | Count | Notes |
|---|---|---|
| Departments | 7 | incl. Lending and Wealth Management |
| Roles | 3 | Employee, Policy Owner, System Administrator |
| Users | 11 | all 5 personas + admin staff |
| Policy categories | 7 | Privacy, AML & Financial Crime, Lending & Credit, Wealth Management, InfoSec & Ops, Acceptable Use, HR & Conduct |
| Policies | 16 | 17 versions (Wealth policy has v1.0 and v2.0) |
| Incident categories | 6 | phishing, malware, lost device, compromise, data loss, insider threat |
| Demo conversations / messages | 4 / 7 | incl. citations and one routed escalation |
| Demo incidents | 2 | phishing click, lost device |
| Demo feedback | 3 | 2 helpful, 1 not helpful |

**Regulations represented in policy content:** GLBA / Regulation P, GLBA Safeguards Rule
(16 CFR 314), BSA/AML (31 CFR Ch. X), CIP/KYC (31 CFR 1020.220), SAR (31 CFR 1020.320),
OFAC sanctions, UDAAP (Dodd-Frank §1031 / 12 CFR 1014), Regulation Z (TILA), Regulation B
(ECOA), Regulation E, Regulation CC.

---

## 9. Migration history

| # | Migration | Summary |
|---|---|---|
| 1 | `baseline_reference_tables` | Captured the original dashboard tables; added Lending + Wealth Management; aligned users to personas |
| 2 | `policy_management_schema` | `policy_categories`, `policies`, `policy_versions` + indexes + RLS |
| 3 | `conversation_and_retrieval_schema` | `conversations`, `messages`, `policy_citations` + indexes + RLS |
| 4 | `clarification_and_incident_schema` | `clarification_requests`, `clarification_replies`, `incident_categories`, `incident_reports` + RLS |
| 5 | `feedback_and_search_support` | `feedback` + `pg_trgm` + trigram GIN indexes + RLS |
| 6 | `seed_banking_policy_handbook` | The full Aurum Capital Bank handbook and demo data |
| 7 | `rename_bank_to_aurum_capital` | Renamed institution in policy text; moved emails to `@aurumbank.com` |

---

## 10. Week 4 handoff

The backend (`backend/`) implements this design with SQLAlchemy models, a FastAPI service
layer, trigram-backed policy search, the ask/citation workflow, clarification routing,
incident reporting, feedback capture, and dashboard aggregation.
