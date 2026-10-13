# Identity & Access Management

**Bank:** Aurum Capital Bank
**Policy ID:** ACB-IT-002
**Department:** Information Technology
**Policy Owner:** Chris Tanaka, Information Security (SOC)
**Version:** 1.0
**Effective Date:** 2026-10-01
**Review Date:** 2027-09-30
**Approval Status:** Approved

---

## 1. Purpose

This policy defines how Aurum Capital Bank grants, changes, and removes access to bank systems and information. It protects client and bank data by ensuring that every employee receives only the access their job requires, that a manager approves every access decision, and that access is removed promptly when it is no longer needed. It also establishes how employees request access, how managers approve it, and how administrators administer accounts.

This is an internal Aurum Capital Bank policy. It supports the bank's obligations under the GLBA Safeguards Rule to control access to customer information; where a legal or regulatory requirement is stricter, the stricter requirement applies.

## 2. Scope

This policy applies to all Aurum Capital Bank employees, contractors, interns, and temporary staff, and to every bank system, application, database, network, and shared resource that requires a login. It covers new employee access requests, permission modification requests, account troubleshooting, and employee account deactivation.

## 3. Policy Requirements

### 3.1 New employee access requests
- Access is granted only in response to an approved access request. There is no automatic right to system access based on job title.
- Every new employee access request must require, at minimum: the requesting manager's approval and the approval of the system or application owner.
- Access must be granted using the least-privilege principle: the minimum permissions needed to perform the role, and no more.
- Elevated or privileged access (for example, administrator or production access) requires additional approval from Information Security or the IT Service Desk manager.

### 3.2 Manager approval requirements
- A manager must approve access before it is provisioned. Managers are accountable for confirming that the requested access is appropriate for the employee's duties.
- Managers must review and confirm their team's access at least annually and when an employee changes roles.
- Managers must notify the IT Service Desk immediately when an employee leaves, transfers, or no longer needs access.

### 3.3 Role-based access control (RBAC)
- Access is assigned through defined roles rather than being granted individually where a role exists.
- Each role is documented and mapped to a set of permissions. New permissions are added to roles, not to individuals, unless a documented exception exists.
- Separation-of-duties rules must be respected; employees must not hold combinations of access that allow them to both initiate and approve the same transaction.

### 3.4 Least-privilege access
- Default access is read-only or none. Additional access is added only when a documented business need exists.
- Standing privileged access is discouraged. Where possible, elevated access is granted just-in-time and expires automatically.
- Access that has not been used for ninety (90) days may be reviewed and removed.

### 3.5 Account troubleshooting
- If an employee cannot log in, is locked out, or believes their account is compromised, they must contact the IT Service Desk.
- A suspected compromise (unexpected login prompts, password reset emails the employee did not request, or unusual account activity) must be treated as a security incident and reported under the Information Security & Acceptable Technology Use policy.
- Administrators must never ask an employee for their password. Passwords are never shared, including with IT.

### 3.6 Permission modification requests
- To change an employee's access, submit a permission modification request to the IT Service Desk with the current access, the access requested, the business justification, and manager approval.
- Access changes for privileged roles additionally require Information Security approval.
- On a role change, existing access must be removed and re-provisioned to match the new role (no "stacking" of old and new permissions).

### 3.7 Employee account deactivation
- Account deactivation must begin on the employee's last working day, or immediately if the employee is terminated for cause.
- Managers must notify the IT Service Desk in advance of a departure so deactivation can be completed on time.
- Deactivation includes disabling the account, revoking access tokens and sessions, recovering bank devices, and reassigning or suspending access to shared resources.
- For privileged accounts, credentials must be rotated, and access to production systems must be removed first.

### 3.8 Administrator responsibilities
- System administrators are accountable for provisioning, modifying, and deactivating access accurately and promptly, based on approved requests only.
- Administrators must keep an auditable record of every access grant, change, and removal.
- Administrators must review privileged accounts and service accounts on a regular schedule and report exceptions to Information Security.

## 4. Employee Procedures

### 4.1 To request access for a new employee
1. The manager submits an access request to the IT Service Desk identifying the systems and roles required.
2. The manager approves the request; the system owner approves the specific system access.
3. Information Security reviews and approves any privileged access.
4. The IT Service Desk provisions least-privilege access and confirms completion to the manager.
5. The manager verifies the employee can access what they need and nothing more.

### 4.2 To change an employee's permissions
1. Submit a permission modification request stating current and requested access and the business reason.
2. Obtain manager approval and, for privileged access, Information Security approval.
3. The IT Service Desk adjusts access and records the change.
4. Confirm that unnecessary access was removed, not merely added.

### 4.3 To deactivate an employee account
1. The manager notifies the IT Service Desk of the departure date.
2. On the last working day (or immediately for cause), access is disabled and sessions are revoked.
3. Privileged credentials are rotated and production access removed first.
4. Bank devices are recovered, and shared-resource access is reassigned.
5. The administrator records the deactivation for audit.

### 4.4 If your account is compromised or locked
1. Contact the IT Service Desk immediately.
2. If you suspect compromise, report it as a security incident to security@aurumbank.com.
3. Change your password from a trusted device and enable multi-factor authentication.
4. Do not attempt to investigate the compromise yourself.

## 5. Responsibilities

| Role | Responsibility |
|---|---|
| Employee | Use only assigned access; protect credentials; report suspected compromise. |
| Manager | Approve access; review team access annually; notify IT of departures and role changes. |
| System Owner | Approve access to their specific system; define roles and permissions. |
| IT Service Desk / Administrators | Provision, modify, and deactivate accounts accurately; maintain audit records. |
| Information Security (SOC) | Approve privileged access; monitor for access anomalies. |
| Policy Owner (Chris Tanaka) | Maintain this policy; review it annually; answer access questions. |

## 6. Exceptions & Escalation

Exceptions to least-privilege or separation-of-duties requirements require written approval from the Chief Information Security Officer, with a documented business justification and an expiration date. Escalate to Information Security if an access request is urgent, if a privileged action is required, or if you believe access has been granted improperly. Suspected account compromise is always escalated to Information Security immediately.

## 7. Related Policies

- Information Security & Acceptable Technology Use
- Data Classification & Handling
- Cloud Services, SaaS & Software Approval
- Incident Response & Breach Reporting
- Confidentiality & Employee Data Privacy

## 8. Frequently Asked Questions

**What approvals are needed to give a new employee system access?**
A new employee access request requires the manager's approval and the approval of the system or application owner before access is provisioned. If the request includes privileged or administrator access, Information Security must also approve it. Access is granted using least privilege.

**How do I request a change to an employee's permissions?**
Submit a permission modification request to the IT Service Desk with the current access, the access requested, and the business justification, along with manager approval. Privileged changes also need Information Security approval.

**How do I deactivate a departing employee's account?**
Notify the IT Service Desk of the departure date. Deactivation begins on the last working day (or immediately for cause) and includes disabling the account, revoking sessions, rotating privileged credentials, and recovering bank devices.

**My account is locked. What do I do?**
Contact the IT Service Desk. If you suspect the account was compromised, report it to security@aurumbank.com as a security incident.

**Can I share my password with IT to speed up a fix?**
No. Passwords are never shared. Administrators must never ask for your password and will not need it.
