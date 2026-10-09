-- =============================================================================
-- Automated Loan Approval System (ALAS) Relational Database Schema
-- Standard SQL DDL compatible with PostgreSQL 16 and SQLite 3
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Underwriter', 'Operator', 'Admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_applications (
    application_id VARCHAR(64) PRIMARY KEY,
    applicant_first_name VARCHAR(100) NOT NULL,
    applicant_last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    ssn_masked VARCHAR(20) NOT NULL,
    ssn_encrypted VARCHAR(255) NOT NULL,
    date_of_birth VARCHAR(20) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    employer_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    annual_income NUMERIC(12, 2) NOT NULL,
    employment_status VARCHAR(50) NOT NULL,
    years_employed INT NOT NULL DEFAULT 0,
    loan_amount NUMERIC(12, 2) NOT NULL,
    term_months INT NOT NULL,
    loan_purpose VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED' CHECK (status IN ('SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED')),
    idempotency_key VARCHAR(128) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_reports (
    report_id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    bureau_name VARCHAR(50) NOT NULL,
    credit_score INT NOT NULL,
    delinquencies_24m INT NOT NULL DEFAULT 0,
    revolving_utilization_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    debt_to_income_ratio NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    raw_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
);

CREATE TABLE IF NOT EXISTS decision_records (
    decision_id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('APPROVED', 'REJECTED', 'MANUAL_REVIEW')),
    approved_amount NUMERIC(12, 2) DEFAULT 0.0,
    interest_rate NUMERIC(5, 2) DEFAULT 0.0,
    reason_codes TEXT,
    policy_trace TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
);

CREATE TABLE IF NOT EXISTS underwriter_exceptions (
    exception_id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    assigned_underwriter_id VARCHAR(64),
    risk_grade VARCHAR(10) NOT NULL DEFAULT 'B',
    trigger_reason VARCHAR(255) NOT NULL,
    notes TEXT,
    action_taken VARCHAR(50) CHECK (action_taken IN ('APPROVE', 'REJECT', 'REQUEST_INFO', 'PENDING')),
    fcra_notice_sent BOOLEAN DEFAULT FALSE,
    adjudicated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id),
    FOREIGN KEY (assigned_underwriter_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS audit_ledger (
    event_id VARCHAR(64) PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    payload_hash VARCHAR(128) NOT NULL,
    payload_json TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_name VARCHAR(255) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    status VARCHAR(50) NOT NULL DEFAULT 'ACCEPTED',
    tracking_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_loan_apps_status ON loan_applications(status);
CREATE INDEX IF NOT EXISTS idx_loan_apps_idempotency ON loan_applications(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_credit_app_id ON credit_reports(application_id);
CREATE INDEX IF NOT EXISTS idx_decision_app_id ON decision_records(application_id);
CREATE INDEX IF NOT EXISTS idx_exceptions_app_id ON underwriter_exceptions(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_ledger(entity_id);
