# Feature Document — Governance & Change Management

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-8 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

Per the Initiative Objectives ("production grade code... well documented... security compliant") and ERD reference §6, uncontrolled changes to critical fields or the schema itself can silently break downstream consumers or distort headcount calculations facility-wide. This feature implements the cross-cutting governance layer, not tied to a single entity.

## 2. Scope

### In scope

- `std_time_mins` governance workflow: dual approval (IE + Labor Planning PM), `change_log` audit table, automatic 14-day recompute trigger, manager notification within 30 minutes of resulting headcount change.
- Schema change protocol enforcement: ≥5 business days consumer notice before breaking changes; ≥24h backward compatibility for non-breaking additions; mandatory ERD doc changelog entry (version, date, author, description) on every approved schema update.
- Tie-in to this repo's own [DECISION_LOG.md](../DECISION_LOG.md) — every governed change gets a decision log entry in addition to the in-app audit trail.

### Out of scope

- Legal sign-off workflow for regulations — that's covered under Feature 02 (Shift & Compliance Configuration), though it follows the same "governed change" philosophy.

## 3. User Stories / Requirements

- As an IE, I want my approval and the PM's approval both recorded before a standard-time change takes effect, so no single person can unilaterally shift headcount facility-wide.
- As a downstream consumer/integrator, I want ≥5 business days notice before a breaking schema change, so my integration doesn't break without warning.
- As a future auditor, I want every governed change traceable end-to-end (who, when, what, why), so compliance reviews don't require reconstructing history from memory.

## 4. Data Model Impact

New entity/table: `task_type_change_log` (`task_type_id`, `old_value`, `new_value`, `changed_by`, `changed_at`, `approved_by`) — proposed in Feature 04, formalized here. **Requires ERD version bump** per schema change protocol (ERD reference §6.2) — to be applied when this feature and Feature 04 are approved together.

## 5. API / Interface Design

- `POST /task-types/{id}/std-time-change-request` — creates a pending change requiring two approvals before it applies.
- `GET /change-log?entity=task_type&id=` — audit trail read endpoint.
- Schema-change notification mechanism (e.g., changelog entry + notification to registered consumers) — exact channel TBD (see Open Questions).

## 6. Acceptance Criteria

- Given a `std_time_mins` change request with only one approval, when a second approval attempt is made by the same approver, then it is rejected (must be two distinct approvers: IE and PM).
- Given an approved change, when applied, then a `change_log` row is written and LABOR_REQUIREMENT recompute is triggered for the next 14 days in the affected zone.
- Given a breaking schema change is proposed, when scheduled, then it cannot go live until ≥5 business days after consumer notification is recorded.

## 7. Test Cases

See [testcases/08-governance-change-management.md](../testcases/08-governance-change-management.md).

## 8. Open Questions

- Notification channel for consumer notice on breaking changes (email, Slack, changelog-only)?
- Should this be a shared library/module used by any future governed field, or specific to `std_time_mins` for now?

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
