-- =============================================================================
-- Automated Loan Approval System (ALAS) Initial Seed Data
-- =============================================================================

-- Seed Users
INSERT OR REPLACE INTO users (user_id, email, password_hash, full_name, role)
VALUES 
    ('usr_und_001', 'underwriter@bank.com', 'scrypt_demo_hash_underwriter', 'Sarah Jenkins, Senior Underwriter', 'Underwriter'),
    ('usr_opr_001', 'operator@bank.com', 'scrypt_demo_hash_operator', 'David Miller, Loan Operator', 'Operator'),
    ('usr_adm_001', 'admin@bank.com', 'scrypt_demo_hash_admin', 'Alex Vance, System Admin', 'Admin');

-- Seed Sample Loan Applications
INSERT OR REPLACE INTO loan_applications (
    application_id, applicant_first_name, applicant_last_name, email, phone,
    ssn_masked, ssn_encrypted, date_of_birth, street, city, state, zip_code,
    employer_name, job_title, annual_income, employment_status, years_employed,
    loan_amount, term_months, loan_purpose, status, idempotency_key
) VALUES
    ('APP-2026-001', 'Marcus', 'Chen', 'marcus.chen@example.com', '555-0192',
     'XXX-XX-4891', 'enc_aes_4891', '1988-04-12', '742 Evergreen Terrace', 'Springfield', 'IL', '62704',
     'Acme Software Corp', 'Senior Engineer', 125000.00, 'Full-Time', 6,
     35000.00, 36, 'Home Improvement', 'APPROVED', 'idemp_key_001'),
    ('APP-2026-002', 'Elena', 'Rostova', 'elena.rostova@example.com', '555-0381',
     'XXX-XX-7823', 'enc_aes_7823', '1992-11-23', '124 Conch Street', 'Bikini', 'CA', '90210',
     'Apex Global Logistics', 'Operations Manager', 68000.00, 'Full-Time', 2,
     28000.00, 48, 'Debt Consolidation', 'UNDER_REVIEW', 'idemp_key_002'),
    ('APP-2026-003', 'James', 'Wilson', 'james.wilson@example.com', '555-0922',
     'XXX-XX-1194', 'enc_aes_1194', '1980-08-05', '300 Oak Avenue', 'Austin', 'TX', '78701',
     'Wilson Consulting LLC', 'Managing Partner', 180000.00, 'Self-Employed', 10,
     50000.00, 60, 'Business Expansion', 'APPROVED', 'idemp_key_003');

-- Seed Credit Reports
INSERT OR REPLACE INTO credit_reports (
    report_id, application_id, bureau_name, credit_score, delinquencies_24m,
    revolving_utilization_pct, debt_to_income_ratio, raw_response
) VALUES
    ('CR-001', 'APP-2026-001', 'Experian', 760, 0, 18.5, 0.22, '{"score": 760, "status": "PRIME"}'),
    ('CR-002', 'APP-2026-002', 'Equifax', 648, 1, 58.2, 0.42, '{"score": 648, "status": "NEAR_PRIME"}'),
    ('CR-003', 'APP-2026-003', 'Experian', 790, 0, 12.0, 0.18, '{"score": 790, "status": "SUPER_PRIME"}');

-- Seed Decision Records
INSERT OR REPLACE INTO decision_records (
    decision_id, application_id, decision, approved_amount, interest_rate,
    reason_codes, policy_trace
) VALUES
    ('DEC-001', 'APP-2026-001', 'APPROVED', 35000.00, 6.25, '["POL-PASS-PRIME"]', '{"rules_evaluated": 12, "passed": 12}'),
    ('DEC-002', 'APP-2026-002', 'MANUAL_REVIEW', 0.0, 0.0, '["POL-DTI-ELEVATED", "POL-SCORE-BORDERLINE"]', '{"rules_evaluated": 12, "flagged": ["DTI > 38%"]}'),
    ('DEC-003', 'APP-2026-003', 'APPROVED', 50000.00, 5.75, '["POL-PASS-SUPERPRIME"]', '{"rules_evaluated": 12, "passed": 12}');

-- Seed Underwriter Exceptions
INSERT OR REPLACE INTO underwriter_exceptions (
    exception_id, application_id, assigned_underwriter_id, risk_grade,
    trigger_reason, notes, action_taken
) VALUES
    ('EXC-002', 'APP-2026-002', 'usr_und_001', 'B',
     'DTI ratio 42.0% exceeds automated threshold of 38.0%', 'Requires manual verification of secondary income.', 'PENDING');

-- Seed Initial Audit Ledger Event
INSERT OR REPLACE INTO audit_ledger (
    event_id, event_type, entity_id, actor, payload_hash, payload_json
) VALUES
    ('EVT-001', 'SYSTEM_INITIALIZATION', 'SYSTEM', 'bootstrap',
     'init_sha256_hash_value_placeholder', '{"message": "Database seeded successfully"}');

-- Seed Initial Transactions
INSERT OR REPLACE INTO transactions (
    transaction_id, tenant_id, action, entity_name, amount, currency, status, tracking_id
) VALUES
    ('txn_01HZ001', 'org_481878', 'INITIATE', 'Corporate KYC Submission', 50000.00, 'USD', 'ACCEPTED', 'trk_991823');
