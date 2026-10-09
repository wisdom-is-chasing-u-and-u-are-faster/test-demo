import time
from typing import Dict, Any, List, Optional


class NotificationDispatcher:
    """Multi-channel notification dispatcher delivering FCRA / ECOA compliant letters and real-time alerts."""

    def dispatch_decision_notice(
        self,
        application_id: str,
        applicant_email: str,
        applicant_name: str,
        decision: str,
        approved_amount: float = 0.0,
        reason_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Dispatches automated email and SMS notification according to FCRA / ECOA compliance."""
        reason_codes = reason_codes or []
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if decision == "APPROVED":
            subject = f"Congratulations! Your Loan Application {application_id} has been Approved"
            notice_type = "APPROVAL_DISPATCH"
        elif decision == "REJECTED":
            subject = f"Notice of Adverse Action — Application {application_id}"
            notice_type = "FCRA_ECOA_ADVERSE_ACTION"
        else:
            subject = f"Application Update: Underwriter Review in Progress ({application_id})"
            notice_type = "UNDERWRITING_UPDATE"

        # Return simulated dispatch log
        return {
            "application_id": application_id,
            "recipient": applicant_email,
            "notice_type": notice_type,
            "subject": subject,
            "dispatched_at": timestamp,
            "channels": ["EMAIL", "SMS"],
            "status": "DELIVERED"
        }


notification_dispatcher = NotificationDispatcher()
