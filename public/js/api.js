/**
 * Automated Loan Approval System (ALAS) Client API Layer
 * Single Source of Truth for all frontend fetch operations
 */

const API_BASE = '/api/v1';

class AlasApi {
    constructor() {
        this.token = localStorage.getItem('alas_token') || null;
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('alas_token', token);
        } else {
            localStorage.removeItem('alas_token');
        }
    }

    getHeaders(extraHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...extraHeaders
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.headers || {})
        };

        try {
            const response = await fetch(url, config);
            const contentType = response.headers.get('content-type') || '';
            let data = null;

            if (contentType.includes('application/json') || contentType.includes('application/problem+json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                const errorMsg = data && (data.detail || data.title || data.message) 
                    ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
                    : `HTTP Error ${response.status}`;
                throw new Error(errorMsg);
            }

            return data;
        } catch (error) {
            console.error(`API Request Failed [${options.method || 'GET'} ${url}]:`, error);
            throw error;
        }
    }

    // Health
    async checkHealth() {
        return fetch('/health').then(res => res.json());
    }

    // Auth
    async login(email, password, role = 'Underwriter') {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password, role })
        });
        if (data.access_token) {
            this.setToken(data.access_token);
        }
        return data;
    }

    // Loans
    async submitLoanApplication(payload, idempotencyKey = null) {
        const headers = {};
        if (idempotencyKey) {
            headers['Idempotency-Key'] = idempotencyKey;
        }
        return this.request('/loans/applications', {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });
    }

    async getApplicationStatus(applicationId) {
        return this.request(`/loans/applications/${applicationId}`);
    }

    // Underwriter
    async getWorklist() {
        return this.request('/underwriter/worklist');
    }

    async getCaseDetails(caseId) {
        return this.request(`/underwriter/cases/${caseId}`);
    }

    async adjudicateCase(caseId, action, notes = '', approvedAmount = null, approvedRate = null, reasonCodes = []) {
        return this.request(`/underwriter/cases/${caseId}/adjudicate`, {
            method: 'POST',
            body: JSON.stringify({
                action,
                notes,
                approved_amount: approvedAmount,
                approved_rate: approvedRate,
                reason_codes: reasonCodes
            })
        });
    }

    // Analytics
    async getAnalyticsMetrics() {
        return this.request('/analytics/metrics');
    }

    // Transactions
    async submitTransaction(transactionId, tenantId, action, entityName, amount, currency = 'USD') {
        return this.request('/transactions', {
            method: 'POST',
            body: JSON.stringify({
                transaction_id: transactionId,
                tenant_id: tenantId,
                action,
                payload: {
                    entity_name: entityName,
                    amount,
                    currency
                }
            })
        });
    }

    // Audit
    async getAuditLedger(limit = 50) {
        return this.request(`/audit/ledger?limit=${limit}`);
    }
}

// Global singleton instance
window.alasApi = new AlasApi();
