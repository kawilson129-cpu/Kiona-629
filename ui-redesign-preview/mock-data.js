/* DeRexi "The Ledger" — mock dataset for the UI redesign preview.
   Mirrors the live FastAPI response shapes 1:1 so the preview can be promoted
   by swapping the data adapter only. Numbers marked REAL match the production
   database on Sep 24, 2026; the rest is plausible sample content. */
(function () {
  'use strict';

  var N = 40; // simulated network latency (ms)
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };

  /* ----------------------------------------------------------------- roles */
  var ROLES = [
    { id: 1, name: 'Employee' },
    { id: 2, name: 'Policy Owner' },
    { id: 3, name: 'System Administrator' }
  ];

  var DEPARTMENTS = [
    { id: 1, name: 'Information Technology' },
    { id: 2, name: 'Human Resources' },
    { id: 3, name: 'Lending' },
    { id: 4, name: 'Wealth Management' },
    { id: 5, name: 'Compliance & Risk' },
    { id: 6, name: 'Operations' },
    { id: 7, name: 'Security Operations' }
  ];

  /* ------------------------------------------------------- users (REAL) */
  var USERS = [
    { id: 1, full_name: 'Dana Brooks', email: 'dana.brooks@aurum.bank', department_id: 7, department: 'Security Operations', role_id: 3, role: 'System Administrator' },
    { id: 2, full_name: 'Lucy Chen', email: 'lucy.chen@aurum.bank', department_id: 7, department: 'Security Operations', role_id: 3, role: 'System Administrator' },
    { id: 3, full_name: 'Tom Bennett', email: 'tom.bennett@aurum.bank', department_id: 3, department: 'Lending', role_id: 1, role: 'Employee' },
    { id: 4, full_name: 'Maya Patel', email: 'maya.patel@aurum.bank', department_id: 5, department: 'Compliance & Risk', role_id: 2, role: 'Policy Owner' },
    { id: 5, full_name: 'Elena Rodriguez', email: 'elena.rodriguez@aurum.bank', department_id: 3, department: 'Lending', role_id: 1, role: 'Employee' },
    { id: 6, full_name: 'Alex Chen', email: 'alex.chen@aurum.bank', department_id: 1, department: 'Information Technology', role_id: 1, role: 'Employee' },
    { id: 7, full_name: 'Chris Tanaka', email: 'chris.tanaka@aurum.bank', department_id: 7, department: 'Security Operations', role_id: 2, role: 'Policy Owner' },
    { id: 8, full_name: 'Sam Okonkwo', email: 'sam.okonkwo@aurum.bank', department_id: 6, department: 'Operations', role_id: 1, role: 'Employee' },
    { id: 9, full_name: 'Jordan Rivera', email: 'jordan.rivera@aurum.bank', department_id: 2, department: 'Human Resources', role_id: 2, role: 'Policy Owner' },
    { id: 10, full_name: 'Gabrielle Fontaine', email: 'gabrielle.fontaine@aurum.bank', department_id: 3, department: 'Lending', role_id: 2, role: 'Policy Owner' },
    { id: 11, full_name: 'Marcus Webb', email: 'marcus.webb@aurum.bank', department_id: 5, department: 'Compliance & Risk', role_id: 2, role: 'Policy Owner' },
    { id: 12, full_name: 'Rachel Sampson', email: 'rachel.sampson@aurum.bank', department_id: 4, department: 'Wealth Management', role_id: 2, role: 'Policy Owner' }
  ];

  function user(id) {
    for (var i = 0; i < USERS.length; i++) if (USERS[i].id === id) return USERS[i];
    return USERS[7];
  }

  /* ------------------------------------------------------ categories (REAL) */
  var CATEGORIES = [
    { id: 1, name: 'Privacy & Consumer Protection', count: 2 },
    { id: 2, name: 'Anti-Money Laundering & Financial Crime', count: 4 },
    { id: 3, name: 'Lending & Credit', count: 5 },
    { id: 4, name: 'Wealth Management & Private Banking', count: 1 },
    { id: 5, name: 'Information Security & Operations', count: 10 },
    { id: 6, name: 'Human Resources & Conduct', count: 16 },
    { id: 7, name: 'Acceptable Use & Technology', count: 5 }
  ];

  /* --------------------------------------------------- policies (shapes REAL) */
  function P(id, title, summary, cat, owner, status, ver, review, requiresReview) {
    return {
      id: id,
      title: title,
      summary: summary,
      status: status || 'approved',
      category_id: cat,
      category: catName(cat),
      owner_id: owner,
      owner: user(owner).full_name,
      latest_version: ver || '1.0',
      review_date: review || '2026-11-15',
      requires_review: requiresReview === undefined ? false : requiresReview,
      created_at: '2026-05-04T09:00:00+00:00',
      updated_at: '2026-08-20T14:30:00+00:00'
    };
  }

  function catName(id) {
    for (var i = 0; i < CATEGORIES.length; i++) if (CATEGORIES[i].id === id) return CATEGORIES[i].name;
    return 'Policy';
  }

  var POLICIES = [
    /* Privacy & Consumer Protection */
    P(1, 'Customer Information Privacy (GLBA / Regulation P)', 'How the Bank collects, uses, shares, and protects nonpublic personal information.', 1, 4, 'approved', '2.1'),
    P(2, 'Unfair, Deceptive, or Abusive Acts or Practices (UDAAP)', 'Consumer protection standards for every customer-facing practice.', 1, 4, 'approved', '1.3'),

    /* AML & Financial Crime */
    P(3, 'Anti-Money Laundering (BSA/AML) Program', 'The Bank Secrecy Act program, its four pillars, and employee obligations.', 2, 11, 'approved', '1.0'),
    P(4, 'Customer Identification Program (CIP / KYC)', 'Identity verification requirements for new customers under the USA PATRIOT Act.', 2, 11, 'approved', '1.2'),
    P(5, 'Suspicious Activity Reporting (SAR)', 'How and when to report suspicious transactions to FinCEN.', 2, 11, 'approved', '1.4'),
    P(6, 'OFAC Sanctions Compliance', 'Screening for and blocking transactions involving sanctioned persons.', 2, 11, 'approved', '1.1'),

    /* Lending & Credit */
    P(7, 'Loan Origination & Truth in Lending (Regulation Z)', 'Required disclosures and advertising rules for consumer and mortgage lending.', 3, 10, 'approved', '1.5'),
    P(8, 'Fair Lending & Equal Credit Opportunity (Regulation B / ECOA)', 'Prohibited bases for credit decisions and adverse action requirements.', 3, 10, 'approved', '1.1'),
    P(9, 'Electronic Fund Transfers & Deposit Services (Regulation E & CC)', 'Consumer rights for electronic transfers and funds availability.', 3, 10, 'approved', '1.0'),
    P(10, 'Lending Adviser & Third-Party Origination', 'Qualification and monitoring of third-party loan originators.', 3, 10, 'approved', '1.0'),
    P(11, 'Credit Decision Documentation', 'Record-keeping for credit decisions and adverse action notice files.', 3, 10, 'approved', '1.0', '2026-12-01', true),

    /* Wealth Management */
    P(12, 'Wealth Management & Private Banking Suitability', 'Suitability, confidentiality, and conflict-of-interest standards for private clients.', 4, 12, 'in_review', '1.0', '2026-09-30', true),

    /* Information Security & Operations */
    P(13, 'Information Security Program (GLBA Safeguards Rule)', 'The written information security program protecting customer information.', 5, 7, 'approved', '1.2'),
    P(14, 'Incident Response & Breach Reporting', 'How to report, triage, escalate, and document security incidents.', 5, 7, 'approved', '1.1'),
    P(15, 'Data Retention & Secure Disposal', 'Retention schedules and approved disposal methods for records and media.', 5, 7, 'approved', '1.0'),
    P(16, 'Password & Multi-Factor Authentication', 'Credential standards, MFA enrollment, and shared-credential prohibitions.', 5, 7, 'approved', '1.0'),
    P(17, 'Phishing & Social Engineering Awareness', 'Recognizing and reporting suspicious email, calls, and messages.', 5, 7, 'approved', '1.0'),
    P(18, 'Third-Party Vendor Risk Management', 'Risk assessments, contracts, and monitoring for vendors with bank data.', 5, 7, 'approved', '1.0', '2027-01-10', true),

    /* Human Resources & Conduct */
    P(19, 'Paid Time Off & Vacation', 'Annual PTO accrual, scheduling, and payout for full-time employees.', 6, 9, 'approved', '1.0'),
    P(20, 'Paid Holidays & Floating Holidays', 'The annual holiday calendar and floating holiday policy.', 6, 9, 'approved', '1.0'),
    P(21, 'Family & Medical Leave of Absence', 'FMLA-eligible leave and parental leave of up to 16 weeks.', 6, 9, 'approved', '1.0'),
    P(22, 'Sick Leave & Medical Absence', 'Paid sick leave accrual, use, and documentation.', 6, 9, 'approved', '1.0'),
    P(23, 'Code of Conduct', 'Ethical standards, conflicts of interest, and personal accountability.', 6, 9, 'approved', '2.3'),
    P(24, 'Workplace Harassment Prevention', 'Prohibited conduct, reporting channels, and investigation process.', 6, 9, 'approved', '1.1'),
    P(25, 'Whistleblower Protection', 'Good-faith reporting of misconduct and protection from retaliation.', 6, 9, 'approved', '1.0'),
    P(26, 'Gifts & Entertainment', 'Permitted business courtesies and the $100 threshold.', 6, 9, 'approved', '1.0'),
    P(27, 'Business Travel & Expense', 'Travel booking, reimbursement, and per-diem guidance.', 6, 9, 'approved', '1.0'),
    P(28, 'Recruitment & Hiring', 'Fair hiring practices and records retention for applicants.', 6, 9, 'approved', '1.0', '2026-11-20', true),
    P(29, 'Payroll & Timekeeping', 'Timesheet submission, payroll schedule, and error correction.', 6, 9, 'approved', '1.0'),

    /* Acceptable Use & Technology */
    P(30, 'Acceptable Use of Bank Systems', 'Appropriate personal use of bank computers, email, and the network.', 7, 7, 'approved', '1.4'),
    P(31, 'Remote Work & Connectivity', 'Approved remote locations, VPN requirements, and secure home setup.', 7, 7, 'approved', '1.0'),
    P(32, 'Clean Desk & Screen Lock', 'Measures to protect information when stepping away from your desk.', 7, 7, 'approved', '1.0'),
    P(33, 'Bring Your Own Device (BYOD)', 'Personal device eligibility, enrollment, and data separation.', 7, 7, 'approved', '1.0'),
    P(34, 'Artificial Intelligence Acceptable Use & Governance', 'Approved AI tools, data boundaries, and human oversight.', 7, 7, 'approved', '1.0', '2026-10-25', true)
  ];

  /* Selected policy bodies + version history for the detail drawer. */
  var BODIES = {
    8: 'Fair Lending & Equal Credit Opportunity (Regulation B / ECOA). Policy Statement: The Bank will not discriminate against any applicant on a prohibited basis, including race, color, religion, national origin, sex, marital status, or age. Every credit decision must be supported by documented, legitimate business reasons. Application Processing: If an application is missing documents or has not provided all required information, the Bank will notify the applicant what information is needed to complete the application and allow a reasonable period to provide it. When the Bank must notify the applicant of incomplete information, it will identify specifically the additional information needed and provide applicant notice as required by regulation. Adverse Action: If the Bank takes an adverse action, it will provide the applicant a written adverse-action notice that states the specific reasons or advises the applicant of the right to a statement of reasons within 30 days, per the requirements of the Equal Credit Opportunity Act.',
    19: 'Paid Time Off & Vacation. Policy Statement: Full-time employees receive 20 paid vacation days per year, accrued monthly on the last pay period at a rate of 1.667 days per month. Vacation requests are scheduled with at least two weeks of notice where practicable, subject to department coverage, and must not be banked beyond 40 accrued days without leadership approval. Unused accrued vacation is paid out on separation in accordance with state law.',
    20: 'Paid Holidays & Floating Holidays. Policy Statement: The Bank observes 11 paid holidays each calendar year, published in January on the internal holiday calendar. In addition, each full-time employee receives three floating holidays, which may be used with manager approval and do not require a stated reason. Unused floating holidays expire at the end of the calendar year and are not paid out.',
    21: 'Family & Medical Leave of Absence. Policy Statement: Eligible employees may take up to 12 weeks of unpaid, job-protected leave under the Family and Medical Leave Act for qualifying medical and family reasons. In addition, the Bank provides up to 16 weeks of paid parental leave for the birth, adoption, or placement of a child. Employees should submit a leave request to Human Resources at least 30 days before the anticipated start date where foreseeable.',
    22: 'Sick Leave & Medical Absence. Policy Statement: Full-time employees accrue 12 paid sick days per year. Sick leave may be used for personal illness, medical appointments, or care of a dependent, and must be reported to a supervisor before the start of the scheduled shift. When a leave of three or more consecutive days is taken, the Bank may require appropriate documentation.',
    5: 'Suspicious Activity Reporting (SAR). Policy Statement: Any employee who observes a transaction or activity that may be suspicious - including unusual size, frequency, pattern, or structuring that appears intended to evade reporting thresholds - must promptly refer it to the Compliance department. The Bank will file a Suspicious Activity Report with FinCEN within 30 calendar days of detecting the activity. Employees must not disclose the existence or filing of a SAR, as disclosure is prohibited by law.'
  };

  var VERSIONS = {
    8: [
      { version_no: '1.1', effective_date: '2026-09-24', review_date: '2027-09-24', requires_review: false, created_at: '2026-09-24T00:00:00+00:00', body: BODIES[8] },
      { version_no: '1.0', effective_date: '2026-05-04', review_date: '2026-09-30', requires_review: true, created_at: '2026-05-04T00:00:00+00:00', body: 'Fair Lending & Equal Credit Opportunity (Regulation B / ECOA). The Bank will not discriminate against any applicant on a prohibited basis. Adverse action notices will state reasons in writing as required by the Equal Credit Opportunity Act.' }
    ],
    19: [
      { version_no: '1.0', effective_date: '2026-05-04', review_date: '2027-05-04', requires_review: false, created_at: '2026-05-04T00:00:00+00:00', body: BODIES[19] }
    ],
    20: [
      { version_no: '1.0', effective_date: '2026-05-04', review_date: '2027-05-04', requires_review: false, created_at: '2026-05-04T00:00:00+00:00', body: BODIES[20] }
    ],
    21: [
      { version_no: '1.0', effective_date: '2026-05-04', review_date: '2027-05-04', requires_review: false, created_at: '2026-05-04T00:00:00+00:00', body: BODIES[21] }
    ],
    22: [
      { version_no: '1.0', effective_date: '2026-05-04', review_date: '2027-05-04', requires_review: false, created_at: '2026-05-04T00:00:00+00:00', body: BODIES[22] }
    ],
    5: [
      { version_no: '1.4', effective_date: '2026-06-01', review_date: '2027-06-01', requires_review: false, created_at: '2026-06-01T00:00:00+00:00', body: BODIES[5] },
      { version_no: '1.0', effective_date: '2026-05-04', review_date: '2026-09-15', requires_review: true, created_at: '2026-05-04T00:00:00+00:00', body: 'Suspicious Activity Reporting (SAR). Employees who observe suspicious activity must report it to Compliance. The Bank files SARs with FinCEN within 30 days.' }
    ]
  };

  function policyDetail(id) {
    for (var i = 0; i < POLICIES.length; i++) {
      if (POLICIES[i].id === id) {
        var p = POLICIES[i];
        var out = {};
        for (var k in p) out[k] = p[k];
        out.versions = (VERSIONS[id] || [{
          version_no: p.latest_version,
          effective_date: p.review_date,
          review_date: p.review_date,
          requires_review: p.requires_review,
          created_at: p.created_at,
          body: p.summary
        }]);
        return out;
      }
    }
    throw new Error('Policy not found');
  }

  /* ------------------------------------------------------- incidents (REAL) */
  var INCIDENT_CATEGORIES = [
    { id: 1, name: 'Phishing or Social Engineering', description: 'Suspicious email, message, or phone contact attempting to obtain credentials or information.', default_severity: 'high' },
    { id: 2, name: 'Malware or Ransomware', description: 'Malicious software detected or suspected on a bank device or system.', default_severity: 'critical' },
    { id: 3, name: 'Lost or Stolen Device', description: 'A bank-issued laptop, phone, or storage device is lost or stolen.', default_severity: 'high' },
    { id: 4, name: 'Account or Credential Compromise', description: 'Suspected unauthorized access to a bank account or employee credentials.', default_severity: 'critical' },
    { id: 5, name: 'Data Loss or Mishandling', description: 'Accidental or improper exposure of customer or bank information.', default_severity: 'high' },
    { id: 6, name: 'Insider Threat', description: 'Suspected malicious or negligent activity by an employee or contractor.', default_severity: 'critical' }
  ];

  var INCIDENTS = [
    {
      id: 2, reporter_id: 5, reporter: 'Elena Rodriguez', category_id: 3, category: 'Lost or Stolen Device',
      description: 'Bank-issued laptop left in a rideshare vehicle; device is encrypted and was remotely locked within the hour. Rideshare company contacted, vehicle located.',
      severity: 'high', status: 'escalated', assigned_to: 7, assignee: 'Chris Tanaka', escalation_level: 3,
      resolution_notes: 'Device recovered. Forensic imaging ordered; risk of exposure assessed as low given full disk encryption.',
      created_at: '2026-09-17T11:55:43+00:00', updated_at: '2026-09-18T09:12:00+00:00'
    },
    {
      id: 1, reporter_id: 8, reporter: 'Sam Okonkwo', category_id: 1, category: 'Phishing or Social Engineering',
      description: 'Clicked a link in a spoofed invoice email and entered credentials before realizing the sender address was fraudulent. Password rotated immediately; MFA prompt anomaly flagged.',
      severity: 'high', status: 'triaged', assigned_to: 7, assignee: 'Chris Tanaka', escalation_level: 2,
      resolution_notes: null,
      created_at: '2026-09-15T19:55:43+00:00', updated_at: '2026-09-16T08:40:00+00:00'
    }
  ];

  /* ------------------------------------------------- clarifications (REAL-ish) */
  var CLARIFICATIONS = [
    { id: 26, user_id: 8, requester: 'Sam Okonkwo', policy_id: 34, reason: 'No approved policy confidently matched the question about approved AI tools for personal research.', status: 'open', assigned_to: 6, assignee: 'Alex Chen', created_at: '2026-09-23T18:10:31+00:00', resolved_at: null },
    { id: 25, user_id: 8, requester: 'Sam Okonkwo', policy_id: 34, reason: 'Question about whether customer data may be entered into third-party AI assistants.', status: 'open', assigned_to: 6, assignee: 'Alex Chen', created_at: '2026-09-23T18:10:30+00:00', resolved_at: null },
    { id: 24, user_id: 8, requester: 'Sam Okonkwo', policy_id: 17, reason: 'Asked whether forwarding a suspicious bank-branded email to personal email violates policy.', status: 'in_progress', assigned_to: 7, assignee: 'Chris Tanaka', created_at: '2026-09-23T18:10:28+00:00', resolved_at: null },
    { id: 23, user_id: 5, requester: 'Elena Rodriguez', policy_id: 11, reason: 'Requested clarification on how long adverse-action documentation must be retained.', status: 'open', assigned_to: 10, assignee: 'Gabrielle Fontaine', created_at: '2026-09-22T13:02:11+00:00', resolved_at: null },
    { id: 22, user_id: 3, requester: 'Tom Bennett', policy_id: 7, reason: 'Asked whether promotional APR language requires the same disclosure as standard offers.', status: 'in_progress', assigned_to: 10, assignee: 'Gabrielle Fontaine', created_at: '2026-09-20T16:44:00+00:00', resolved_at: null },
    { id: 21, user_id: 6, requester: 'Alex Chen', policy_id: 31, reason: 'Asked whether guest networks in approved remote locations are permitted with VPN.', status: 'resolved', assigned_to: 7, assignee: 'Chris Tanaka', created_at: '2026-09-18T10:20:00+00:00', resolved_at: '2026-09-19T09:05:00+00:00' },
    { id: 20, user_id: 8, requester: 'Sam Okonkwo', policy_id: 19, reason: 'Asked whether PTO can be used in half-day increments for appointments.', status: 'resolved', assigned_to: 9, assignee: 'Jordan Rivera', created_at: '2026-09-16T08:30:00+00:00', resolved_at: '2026-09-17T14:12:00+00:00' },
    { id: 19, user_id: 6, requester: 'Alex Chen', policy_id: 13, reason: 'Asked whether personal file-sync services may hold bank data.', status: 'resolved', assigned_to: 7, assignee: 'Chris Tanaka', created_at: '2026-09-14T11:00:00+00:00', resolved_at: '2026-09-15T10:30:00+00:00' }
  ];

  /* ------------------------------------------------------ dashboard (REAL) */
  var DASHBOARD = {
    totals: { policies: 43, conversations: 77, messages: 153, incidents: 2 },
    policies_by_status: [{ status: 'approved', count: 42 }, { status: 'in_review', count: 1 }],
    reviews_due: 2,
    clarifications_by_status: [{ status: 'open', count: 25 }, { status: 'in_progress', count: 1 }],
    incidents_by_status: [{ status: 'triaged', count: 1 }, { status: 'escalated', count: 1 }],
    incidents_by_severity: [{ severity: 'high', count: 2 }],
    feedback: { total: 3, helpful: 2, not_helpful: 1, helpful_rate: 0.667 },
    top_cited_policies: [
      { id: 17, title: 'Phishing & Social Engineering Awareness', citation_count: 21 },
      { id: 8, title: 'Fair Lending & Equal Credit Opportunity (Regulation B / ECOA)', citation_count: 14 },
      { id: 7, title: 'Loan Origination & Truth in Lending (Regulation Z)', citation_count: 12 },
      { id: 5, title: 'Suspicious Activity Reporting (SAR)', citation_count: 8 },
      { id: 15, title: 'Data Retention & Secure Disposal', citation_count: 6 }
    ]
  };

  /* ------------------------------------------------------ conversations */
  var CONVERSATIONS = [
    {
      id: 1, user_id: 8, topic: 'How much paid time off do I get each year?', status: 'open', created_at: '2026-09-24T09:15:00+00:00',
      messages: [
        { id: 1, sender: 'user', body: 'How much paid time off do I get each year?', created_at: '2026-09-24T09:15:00+00:00', citations: [] },
        { id: 2, sender: 'derexi', body: "Here's what you should do: Full-time employees receive 20 paid vacation days per year, accrued monthly on the last pay period at a rate of 1.667 days per month. Vacation requests are scheduled with at least two weeks of notice where practicable.\nReference: Paid Time Off & Vacation (v1.0)", created_at: '2026-09-24T09:15:01+00:00', citations: [{ policy_id: 19, policy_version_id: 1, title: 'Paid Time Off & Vacation', version_no: '1.0', excerpt: 'Full-time employees receive 20 paid vacation days per year, accrued monthly...' }] }
      ]
    },
    {
      id: 2, user_id: 8, topic: 'Can I use ChatGPT for work tasks?', status: 'open', created_at: '2026-09-23T18:09:53+00:00',
      messages: [
        { id: 3, sender: 'user', body: 'Can I use ChatGPT for work tasks?', created_at: '2026-09-23T18:09:53+00:00', citations: [] },
        { id: 4, sender: 'derexi', body: 'The policy library does not contain enough information to answer this confidently, so I have routed it to a policy owner for clarification rather than guess.', created_at: '2026-09-23T18:09:53+00:00', citations: [] }
      ]
    }
  ];

  /* -------------------------------------------------------------- /ask */
  var TOPIC_MAP = [
    { rx: /pto|vacation|paid time|holiday|sick/, policy: 19, score: 0.3229 },
    { rx: /parental|maternity|paternity|16 weeks|leave of absence|fmla/, policy: 21, score: 0.2977 },
    { rx: /phishing|social engineering|suspicious email/, policy: 17, score: 0.2368 },
    { rx: /password|mfa|multi-factor/, policy: 16, score: 0.2812 },
    { rx: /reg b|fair lending|credit application|incomplete application|missing document|ecoa/, policy: 8, score: 0.4465 },
    { rx: /reg z|truth in lending|loan origination|april|disclosure/, policy: 7, score: 0.2731 },
    { rx: /sar|suspicious activity|finCEN/, policy: 5, score: 0.2604 }
  ];

  function mockAsk(payload) {
    var q = String(payload.question || '').toLowerCase();
    var hit = null;
    for (var i = 0; i < TOPIC_MAP.length; i++) {
      if (TOPIC_MAP[i].rx.test(q)) { hit = TOPIC_MAP[i]; break; }
    }
    var convId = 100 + (CONVERSATIONS.length + 1);
    if (hit) {
      var det = policyDetail(hit.policy);
      var guidance = det.versions[0].body.split('. ').slice(0, 2).join('. ') + '.';
      var answer = "Here's what you should do: " + guidance + "\nReference: " + det.title + ' (v' + det.latest_version + ')';
      return {
        conversation_id: convId,
        answer: answer,
        citations: [{ policy_id: det.id, policy_version_id: 1, title: det.title, version_no: det.latest_version, score: hit.score, excerpt: guidance }],
        needs_clarification: false,
        confidence: hit.score
      };
    }
    var closest = 17; // fallback routed policy
    var reason = 'The policy library does not contain enough information to answer this confidently, so I have routed it to a policy owner for clarification rather than guess.';
    return {
      conversation_id: convId,
      answer: reason,
      citations: [],
      needs_clarification: true,
      clarification_request_id: CLARIFICATIONS.length + 1,
      assigned_to: user(POLICIES[closest - 1].owner_id || 4).id,
      confidence: 0.17
    };
  }

  /* ------------------------------------------------------------ adapter */
  var API = {};
  API['/users'] = function () { return USERS; };
  API['/roles'] = function () { return ROLES; };
  API['/departments'] = function () { return DEPARTMENTS; };
  API['/categories'] = function () { return CATEGORIES; };
  API['/policies'] = function () { return POLICIES; };
  API['/dashboard/policy-health'] = function () { return DASHBOARD; };
  API['/clarifications'] = function () { return CLARIFICATIONS; };
  API['/incidents'] = function () { return INCIDENTS; };
  API['/incident-categories'] = function () { return INCIDENT_CATEGORIES; };
  API['/conversations/1'] = function () { return CONVERSATIONS[0]; };
  API['/conversations/2'] = function () { return CONVERSATIONS[1]; };

  API['/policies/search'] = function (q) {
    var term = String(q || '').toLowerCase();
    var out = [];
    POLICIES.forEach(function (p) {
      var hay = (p.title + ' ' + p.summary).toLowerCase();
      if (hay.indexOf(term) !== -1) {
        out.push({ policy_id: p.id, policy_version_id: 1, title: p.title, version_no: p.latest_version, score: 0.3 + ((p.id % 10) / 100), excerpt: p.summary });
      }
    });
    return out.slice(0, 5);
  };

  API['/ask'] = function (body) { return mockAsk(body); };
  API['/feedback'] = function () { return { id: 99, message_id: 99, rating: true }; };
  API['/clarifications/resolve'] = function (body) {
    for (var i = 0; i < CLARIFICATIONS.length; i++) {
      if (CLARIFICATIONS[i].id === body.id) {
        CLARIFICATIONS[i].status = 'resolved';
        CLARIFICATIONS[i].resolved_at = '2026-09-24T15:00:00+00:00';
        return { id: body.id, status: 'resolved', resolved_at: CLARIFICATIONS[i].resolved_at };
      }
    }
    throw new Error('Clarification request not found');
  };
  API['/clarifications/reply'] = function (body) {
    return { id: body.id, request_id: body.requestId, status: 'in_progress' };
  };

  function call(path, opts) {
    opts = opts || {};
    var method = opts.method || 'GET';
    var body = null;
    if (opts.body) { try { body = JSON.parse(opts.body); } catch (e) { body = null; } }
    var q = null;
    var m = path.match(/policies\/search\?q=([^&]+)/);
    if (m) q = decodeURIComponent(m[1]);

    var route = path.split('?')[0];
    var pm = route.match(/^\/policies\/(\d+)$/);

    return wait(N).then(function () {
      if (method === 'POST') {
        if (route === '/ask') return API['/ask'](body);
        if (route === '/feedback') return API['/feedback'](body);
        if (/\/resolve$/.test(route)) return API['/clarifications/resolve'](body);
        if (/\/replies$/.test(route)) return API['/clarifications/reply'](body);
        return { ok: true };
      }
      if (route === '/policies/search') return API[route](q);
      if (pm) return policyDetail(parseInt(pm[1], 10));
      return API[route]();
    });
  }

  window.DEREXI_MOCK = {
    call: call,
    latency: N
  };
})();