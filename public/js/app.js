/**
 * Automated Loan Approval System (ALAS) Interactive Application Controller
 * Wires DOM events, forms, tables, and API responses dynamically
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initGlobalNav();

    // Auto-detect which page view is active
    if (document.getElementById('loanIntakeForm')) {
        initLoanIntake();
    }
    if (document.getElementById('statusCheckForm')) {
        initStatusCheck();
    }
    if (document.getElementById('loginForm')) {
        initLogin();
    }
    if (document.getElementById('worklistTable')) {
        initUnderwriterDashboard();
    }
    if (document.getElementById('caseReviewContainer')) {
        initCaseReview();
    }
    if (document.getElementById('analyticsDashboard')) {
        initAnalyticsDashboard();
    }
});

// Theme Toggle
function initTheme() {
    const savedTheme = localStorage.getItem('alas_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const next = current === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('alas_theme', next);
        });
    }
}

// Global Nav & Auth State
function initGlobalNav() {
    const user = JSON.parse(localStorage.getItem('alas_user') || 'null');
    const userDisplay = document.getElementById('userDisplay');
    const authLink = document.getElementById('authNavBtn');

    if (user && userDisplay) {
        userDisplay.textContent = `${user.name} (${user.role})`;
        if (authLink) {
            authLink.textContent = 'Logout';
            authLink.href = '#';
            authLink.onclick = (e) => {
                e.preventDefault();
                localStorage.removeItem('alas_token');
                localStorage.removeItem('alas_user');
                window.location.href = '/pages/login.html';
            };
        }
    }
}

// 1. Login Page
function initLogin() {
    const form = document.getElementById('loginForm');
    const errorBanner = document.getElementById('loginError');

    // Quick demo buttons
    document.querySelectorAll('.btn-demo-login').forEach(btn => {
        btn.addEventListener('click', async () => {
            const role = btn.getAttribute('data-role');
            const email = `${role.toLowerCase()}@bank.com`;
            await performLogin(email, 'demo123', role);
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorBanner.style.display = 'none';

        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const role = document.getElementById('loginRole').value;

        await performLogin(email, password, role);
    });

    async function performLogin(email, password, role) {
        try {
            const res = await window.alasApi.login(email, password, role);
            localStorage.setItem('alas_user', JSON.stringify(res.user));
            if (role === 'Underwriter') {
                window.location.href = '/pages/underwriter-dashboard.html';
            } else if (role === 'Operator') {
                window.location.href = '/pages/analytics-dashboard.html';
            } else {
                window.location.href = '/index.html';
            }
        } catch (err) {
            errorBanner.textContent = err.message || 'Login failed. Please check credentials.';
            errorBanner.style.display = 'block';
        }
    }
}

// 2. Loan Intake Form
function initLoanIntake() {
    const form = document.getElementById('loanIntakeForm');
    const resultCard = document.getElementById('intakeResultCard');
    const errorBanner = document.getElementById('intakeError');
    const ssnInput = document.getElementById('applicantSSN');

    // SSN format auto-masking input helper
    if (ssnInput) {
        ssnInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 9);
            if (val.length > 5) {
                e.target.value = `${val.substring(0,3)}-${val.substring(3,5)}-${val.substring(5)}`;
            } else if (val.length > 3) {
                e.target.value = `${val.substring(0,3)}-${val.substring(3)}`;
            } else {
                e.target.value = val;
            }
        });
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorBanner.style.display = 'none';
        resultCard.style.display = 'none';

        const submitBtn = document.getElementById('submitApplicationBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Evaluating Decision in Real-Time...';

        const payload = {
            applicant: {
                first_name: document.getElementById('applicantFirstName').value,
                last_name: document.getElementById('applicantLastName').value,
                email: document.getElementById('applicantEmail').value,
                phone: document.getElementById('applicantPhone').value,
                ssn: document.getElementById('applicantSSN').value,
                date_of_birth: document.getElementById('applicantDOB').value,
                address: {
                    street: document.getElementById('applicantStreet').value,
                    city: document.getElementById('applicantCity').value,
                    state: document.getElementById('applicantState').value,
                    zip_code: document.getElementById('applicantZip').value
                }
            },
            employment: {
                employer_name: document.getElementById('empName').value,
                job_title: document.getElementById('empTitle').value,
                annual_income: parseFloat(document.getElementById('empIncome').value),
                employment_status: document.getElementById('empStatus').value,
                years_employed: parseInt(document.getElementById('empYears').value || '0', 10)
            },
            loan: {
                amount: parseFloat(document.getElementById('loanAmount').value),
                term_months: parseInt(document.getElementById('loanTerm').value, 10),
                purpose: document.getElementById('loanPurpose').value
            }
        };

        const idempotencyKey = `idemp_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;

        try {
            const res = await window.alasApi.submitLoanApplication(payload, idempotencyKey);
            
            document.getElementById('resAppId').textContent = res.application_id;
            document.getElementById('resStatus').textContent = res.status;
            document.getElementById('resDecision').textContent = res.decision.decision;
            document.getElementById('resScore').textContent = res.decision.credit_score;
            document.getElementById('resApprovedAmount').textContent = `$${res.decision.max_approved_amount.toLocaleString()}`;
            document.getElementById('resRate').textContent = res.decision.interest_rate > 0 ? `${res.decision.interest_rate}%` : 'N/A';
            
            resultCard.style.display = 'block';
            resultCard.scrollIntoView({ behavior: 'smooth' });
        } catch (err) {
            errorBanner.textContent = err.message || 'Error processing application. Please review fields.';
            errorBanner.style.display = 'block';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Application';
        }
    });
}

// 3. Status Check Page
function initStatusCheck() {
    const form = document.getElementById('statusCheckForm');
    const resultArea = document.getElementById('statusResultArea');
    const errorBanner = document.getElementById('statusError');

    // Auto-search if application_id is in query param
    const urlParams = new URLSearchParams(window.location.search);
    const prefillId = urlParams.get('app_id') || urlParams.get('application_id');
    if (prefillId) {
        document.getElementById('searchAppId').value = prefillId;
        fetchStatus(prefillId);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const appId = document.getElementById('searchAppId').value.trim();
        if (appId) {
            await fetchStatus(appId);
        }
    });

    async function fetchStatus(appId) {
        errorBanner.style.display = 'none';
        resultArea.style.display = 'none';

        try {
            const res = await window.alasApi.getApplicationStatus(appId);
            document.getElementById('viewAppId').textContent = res.application_id;
            document.getElementById('viewApplicantName').textContent = res.applicant_name;
            document.getElementById('viewMaskedSSN').textContent = res.masked_ssn;
            document.getElementById('viewAmount').textContent = `$${res.amount.toLocaleString()}`;
            document.getElementById('viewStatusBadge').textContent = res.status;
            
            const timelineContainer = document.getElementById('timelineContainer');
            if (timelineContainer && res.timeline) {
                timelineContainer.innerHTML = res.timeline.map(item => `
                    <div class="timeline-item">
                        <div class="timeline-dot ${item.status === 'COMPLETED' ? 'completed' : ''}"></div>
                        <div style="font-weight: 600;">${item.stage}</div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">${item.status} — ${item.timestamp}</div>
                    </div>
                `).join('');
            }

            resultArea.style.display = 'block';
        } catch (err) {
            errorBanner.textContent = err.message || `Application '${appId}' not found.`;
            errorBanner.style.display = 'block';
        }
    }
}

// 4. Underwriter Dashboard
async function initUnderwriterDashboard() {
    const tableBody = document.querySelector('#worklistTable tbody');
    const errorBanner = document.getElementById('dashboardError');
    const totalCountEl = document.getElementById('metricTotalCases');
    const pendingCountEl = document.getElementById('metricPendingReview');
    const filterSelect = document.getElementById('riskFilterSelect');

    let allCases = [];

    async function loadWorklist() {
        try {
            const data = await window.alasApi.getWorklist();
            allCases = data.cases || [];
            if (totalCountEl) totalCountEl.textContent = data.total_cases;
            if (pendingCountEl) pendingCountEl.textContent = data.pending_review;
            renderCases(allCases);
        } catch (err) {
            if (errorBanner) {
                errorBanner.textContent = err.message || 'Error loading underwriter worklist.';
                errorBanner.style.display = 'block';
            }
        }
    }

    function renderCases(casesToRender) {
        if (!tableBody) return;
        if (casesToRender.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No cases found.</td></tr>`;
            return;
        }

        tableBody.innerHTML = casesToRender.map(c => `
            <tr>
                <td style="font-weight: 600;">${c.application_id}</td>
                <td>${c.applicant_name}</td>
                <td>$${c.loan_amount.toLocaleString()}</td>
                <td><span class="badge ${c.credit_score >= 700 ? 'badge-success' : 'badge-warning'}">${c.credit_score}</span></td>
                <td><span class="badge badge-info">Grade ${c.risk_grade}</span></td>
                <td><span class="badge ${c.status === 'Pending Review' ? 'badge-warning' : (c.status === 'Approved' ? 'badge-success' : 'badge-danger')}">${c.status}</span></td>
                <td>
                    <a href="/pages/case-review.html?case_id=${c.case_id}" class="btn btn-primary" style="padding: 0.3rem 0.75rem; font-size: 0.8rem; text-decoration: none;">Adjudicate</a>
                </td>
            </tr>
        `).join('');
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', (e) => {
            const val = e.target.value;
            if (val === 'ALL') {
                renderCases(allCases);
            } else {
                renderCases(allCases.filter(c => c.risk_grade === val || c.status.toLowerCase().includes(val.toLowerCase())));
            }
        });
    }

    await loadWorklist();
}

// 5. Case Review Screen
async function initCaseReview() {
    const urlParams = new URLSearchParams(window.location.search);
    const caseId = urlParams.get('case_id') || 'EXC-002';
    const container = document.getElementById('caseReviewContainer');
    const actionSuccessBanner = document.getElementById('actionSuccess');
    const actionErrorBanner = document.getElementById('actionError');

    try {
        const c = await window.alasApi.getCaseDetails(caseId);
        
        document.getElementById('caseAppId').textContent = c.application_id;
        document.getElementById('caseApplicantName').textContent = c.applicant.name;
        document.getElementById('caseEmail').textContent = c.applicant.email;
        document.getElementById('caseMaskedSSN').textContent = c.applicant.masked_ssn;
        document.getElementById('caseIncome').textContent = `$${c.applicant.annual_income.toLocaleString()}`;
        document.getElementById('caseDebt').textContent = `$${c.applicant.monthly_debt.toLocaleString()}`;
        
        document.getElementById('caseLoanAmount').textContent = `$${c.loan.amount.toLocaleString()}`;
        document.getElementById('caseLoanTerm').textContent = `${c.loan.term_months} Months`;
        document.getElementById('caseLoanPurpose').textContent = c.loan.purpose;

        document.getElementById('caseBureauName').textContent = c.credit_bureau_data.bureau;
        document.getElementById('caseCreditScore').textContent = c.credit_bureau_data.credit_score;
        document.getElementById('caseDelinquencies').textContent = c.credit_bureau_data.delinquencies_24m;
        document.getElementById('caseUtilization').textContent = `${c.credit_bureau_data.revolving_utilization_pct}%`;

        // Policy rule checklist
        const rulesList = document.getElementById('policyRulesList');
        if (rulesList && c.policy_evaluations) {
            rulesList.innerHTML = c.policy_evaluations.map(p => `
                <div style="padding: 0.75rem; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600;">${p.rule_name} (${p.rule_id})</div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">${p.details}</div>
                    </div>
                    <span class="badge ${p.result === 'PASS' ? 'badge-success' : 'badge-warning'}">${p.result}</span>
                </div>
            `).join('');
        }

        // Action Buttons
        document.getElementById('btnApproveCase')?.addEventListener('click', () => submitAdjudication(caseId, 'APPROVE'));
        document.getElementById('btnRejectCase')?.addEventListener('click', () => submitAdjudication(caseId, 'REJECT'));
        document.getElementById('btnRequestInfoCase')?.addEventListener('click', () => submitAdjudication(caseId, 'REQUEST_INFO'));

    } catch (err) {
        if (actionErrorBanner) {
            actionErrorBanner.textContent = err.message || 'Error loading case details.';
            actionErrorBanner.style.display = 'block';
        }
    }

    async function submitAdjudication(caseId, action) {
        const notes = document.getElementById('adjudicationNotes')?.value || `Adjudicated as ${action}`;
        actionSuccessBanner.style.display = 'none';
        actionErrorBanner.style.display = 'none';

        try {
            const res = await window.alasApi.adjudicateCase(caseId, action, notes, 35000.0, 7.5, ['ECOA-01']);
            actionSuccessBanner.textContent = `Case successfully adjudicated as ${res.action}. Adverse Action Notice / Approval Dispatch delivered.`;
            actionSuccessBanner.style.display = 'block';
        } catch (err) {
            actionErrorBanner.textContent = err.message || 'Adjudication failed.';
            actionErrorBanner.style.display = 'block';
        }
    }
}

// 6. Analytics Dashboard
async function initAnalyticsDashboard() {
    const errorBanner = document.getElementById('analyticsError');

    try {
        const metrics = await window.alasApi.getAnalyticsMetrics();
        
        document.getElementById('metricStpRate').textContent = `${metrics.stp_rate_pct}%`;
        document.getElementById('metricP95Latency').textContent = `${metrics.p95_latency_sec}s`;
        document.getElementById('metricTotalToday').textContent = metrics.total_applications_today.toLocaleString();
        document.getElementById('metricConversionRate').textContent = `${metrics.conversion_rate_pct}%`;

        document.getElementById('statApproved').textContent = metrics.approved_count.toLocaleString();
        document.getElementById('statReview').textContent = metrics.manual_review_count.toLocaleString();
        document.getElementById('statRejected').textContent = metrics.rejected_count.toLocaleString();
    } catch (err) {
        if (errorBanner) {
            errorBanner.textContent = err.message || 'Error loading telemetry metrics.';
            errorBanner.style.display = 'block';
        }
    }
}
