"""
Agent tools exposed to the Gemini model per Section 4.5.
All tools are strictly READ-ONLY or PROPOSAL tools.
Effectful operations (execute_refund, post_reply) are NOT model tools.
"""

from typing import Dict, Any, List, Optional
from dodopayments import DodoPayments

class AgentTools:
    def __init__(self, dodo_client: DodoPayments, incidents: List[Dict[str, Any]]):
        self.dodo = dodo_client
        self.incidents = incidents

    def find_customer(self, query: str) -> List[Dict[str, Any]]:
        """Finds customer by email, name, or order reference."""
        try:
            customers = self.dodo.customers.list(page_size=20)
            q = query.strip().lower()
            matches = []
            for c in customers.items:
                if (c.email and q in c.email.lower()) or (c.name and q in c.name.lower()) or (c.customer_id and q in c.customer_id.lower()):
                    matches.append({
                        "customer_id": c.customer_id,
                        "email": c.email,
                        "name": c.name
                    })
            return matches
        except Exception as e:
            return [{"error": str(e)}]

    def list_payments(self, customer_id: str) -> List[Dict[str, Any]]:
        """Lists payments associated with a customer."""
        try:
            payments = self.dodo.payments.list(customer_id=customer_id, page_size=10)
            return [
                {
                    "payment_id": p.payment_id,
                    "total_amount": p.total_amount,
                    "currency": p.currency,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "refund_status": p.refund_status
                }
                for p in payments.items
            ]
        except Exception as e:
            return [{"error": str(e)}]

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """Retrieves single payment details."""
        try:
            p = self.dodo.payments.retrieve(payment_id)
            return {
                "payment_id": p.payment_id,
                "total_amount": p.total_amount,
                "currency": p.currency,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "refund_status": p.refund_status,
                "refunds_count": len(p.refunds) if p.refunds else 0
            }
        except Exception as e:
            return {"error": str(e)}

    def list_refunds(self, payment_id: str) -> List[Dict[str, Any]]:
        """Lists prior refunds on a payment."""
        try:
            p = self.dodo.payments.retrieve(payment_id)
            if not p.refunds:
                return []
            return [
                {
                    "refund_id": r.refund_id,
                    "amount": r.amount,
                    "status": r.status,
                    "reason": r.reason
                }
                for r in p.refunds
            ]
        except Exception as e:
            return [{"error": str(e)}]

    def get_incidents(self, window_hours: int = 72) -> List[Dict[str, Any]]:
        """Returns verified service incidents from the app status log."""
        return self.incidents

    def propose_resolution(
        self,
        resolution_type: str, # refund_full, refund_partial, decline, ask_customer, escalate
        payment_id: str,
        rule_id: str,
        claimed_reason: str,
        evidence: str
    ) -> Dict[str, Any]:
        """
        The model proposes a resolution.
        NOTE: It never proposes an amount!
        The kernel computes the amount from the rule.
        """
        return {
            "type": resolution_type,
            "payment_id": payment_id,
            "rule_id": rule_id,
            "claimed_reason": claimed_reason,
            "evidence": evidence
        }

    def request_clarification(self, message: str) -> Dict[str, Any]:
        """Requests clarification from the customer."""
        return {"action": "request_clarification", "message": message}

    def escalate(self, reason: str, packet: Dict[str, Any]) -> Dict[str, Any]:
        """Escalates ticket to human review queue."""
        return {"action": "escalate", "reason": reason, "packet": packet}
