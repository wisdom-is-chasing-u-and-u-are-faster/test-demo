/**
 * Automated Loan Approval System (ALAS) Localization Dictionary
 * Supports English (en-US) and Spanish (es-US)
 */

const translations = {
    'en-US': {
        'app_title': 'Automated Loan Approval System',
        'nav_home': 'Home',
        'nav_intake': 'Apply for Loan',
        'nav_status': 'Check Status',
        'nav_worklist': 'Underwriter Worklist',
        'nav_analytics': 'Analytics',
        'nav_login': 'Login',
        'nav_logout': 'Logout',
        'hero_title': 'Enterprise Automated Lending Platform',
        'hero_subtitle': 'Straight-Through Credit Decisioning in under 15 seconds.',
        'btn_apply_now': 'Start Digital Application',
        'btn_check_status': 'Check Status',
        'btn_view_dashboard': 'Underwriter Portal',
        'lbl_stp_rate': 'Straight-Through Processing',
        'lbl_p95_latency': 'P95 Decision Latency',
        'lbl_today_volume': 'Applications Today',
        'lbl_conversion_rate': 'Conversion Rate',
        'lbl_recent_applications': 'Recent Application Stream',
        'col_app_id': 'Application ID',
        'col_applicant': 'Applicant',
        'col_amount': 'Loan Amount',
        'col_credit_score': 'Score',
        'col_status': 'Status',
        'col_action': 'Action',
        'btn_review': 'Review Case',
        'btn_submit': 'Submit Application',
        'btn_approve': 'Approve Loan',
        'btn_reject': 'Reject Loan',
        'btn_request_info': 'Request Info',
        'theme_toggle': 'Toggle Theme',
        'lang_toggle': 'Language',
        'personal_info': '1. Personal Information',
        'employment_info': '2. Employment & Income',
        'loan_parameters': '3. Loan Parameters',
        'lbl_first_name': 'First Name',
        'lbl_last_name': 'Last Name',
        'lbl_email': 'Email Address',
        'lbl_phone': 'Phone Number',
        'lbl_ssn': 'Social Security Number (SSN)',
        'lbl_dob': 'Date of Birth',
        'lbl_street': 'Street Address',
        'lbl_city': 'City',
        'lbl_state': 'State',
        'lbl_zip': 'ZIP Code',
        'lbl_employer': 'Employer Name',
        'lbl_job_title': 'Job Title',
        'lbl_income': 'Annual Income ($)',
        'lbl_emp_status': 'Employment Status',
        'lbl_years_employed': 'Years with Employer',
        'lbl_loan_amount': 'Requested Loan Amount ($)',
        'lbl_term_months': 'Term Duration (Months)',
        'lbl_loan_purpose': 'Loan Purpose'
    },
    'es-US': {
        'app_title': 'Sistema Automatizado de Aprobación de Préstamos',
        'nav_home': 'Inicio',
        'nav_intake': 'Solicitar Préstamo',
        'nav_status': 'Consultar Estado',
        'nav_worklist': 'Bandeja de Suscriptor',
        'nav_analytics': 'Analítica',
        'nav_login': 'Iniciar Sesión',
        'nav_logout': 'Cerrar Sesión',
        'hero_title': 'Plataforma Empresarial de Préstamos Digitales',
        'hero_subtitle': 'Decisiones de crédito directas en menos de 15 segundos.',
        'btn_apply_now': 'Iniciar Solicitud Digital',
        'btn_check_status': 'Consultar Estado',
        'btn_view_dashboard': 'Portal de Suscriptor',
        'lbl_stp_rate': 'Procesamiento Directo (STP)',
        'lbl_p95_latency': 'Latencia de Decisión P95',
        'lbl_today_volume': 'Solicitudes Hoy',
        'lbl_conversion_rate': 'Tasa de Conversión',
        'lbl_recent_applications': 'Flujo de Solicitudes Recientes',
        'col_app_id': 'ID de Solicitud',
        'col_applicant': 'Solicitante',
        'col_amount': 'Monto del Préstamo',
        'col_credit_score': 'Puntaje',
        'col_status': 'Estado',
        'col_action': 'Acción',
        'btn_review': 'Revisar Caso',
        'btn_submit': 'Enviar Solicitud',
        'btn_approve': 'Aprobar Préstamo',
        'btn_reject': 'Rechazar Préstamo',
        'btn_request_info': 'Solicitar Información',
        'theme_toggle': 'Cambiar Tema',
        'lang_toggle': 'Idioma',
        'personal_info': '1. Información Personal',
        'employment_info': '2. Empleo e Ingresos',
        'loan_parameters': '3. Parámetros del Préstamo',
        'lbl_first_name': 'Nombre',
        'lbl_last_name': 'Apellido',
        'lbl_email': 'Correo Electrónico',
        'lbl_phone': 'Teléfono',
        'lbl_ssn': 'Número de Seguro Social (SSN)',
        'lbl_dob': 'Fecha de Nacimiento',
        'lbl_street': 'Dirección',
        'lbl_city': 'Ciudad',
        'lbl_state': 'Estado',
        'lbl_zip': 'Código Postal',
        'lbl_employer': 'Nombre del Empleador',
        'lbl_job_title': 'Cargo / Título',
        'lbl_income': 'Ingreso Anual ($)',
        'lbl_emp_status': 'Estado Laboral',
        'lbl_years_employed': 'Años de Empleo',
        'lbl_loan_amount': 'Monto Solicitado ($)',
        'lbl_term_months': 'Plazo (Meses)',
        'lbl_loan_purpose': 'Propósito del Préstamo'
    }
};

let currentLang = localStorage.getItem('alas_lang') || 'en-US';

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    localStorage.setItem('alas_lang', lang);
    applyTranslations();
}

function t(key) {
    return (translations[currentLang] && translations[currentLang][key]) || key;
}

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang][key]) {
            el.textContent = translations[currentLang][key];
        }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[currentLang][key]) {
            el.setAttribute('placeholder', translations[currentLang][key]);
        }
    });

    const langSelect = document.getElementById('langSelect');
    if (langSelect) {
        langSelect.value = currentLang;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    applyTranslations();
});
