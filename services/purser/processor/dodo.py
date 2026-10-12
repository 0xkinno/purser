"""
Dodo Payments Client with Dead Reckoning reconciliation.
Implements E3 outcome: embeds deterministic action_id inside reason field
and queries payment refunds to match prior intents without duplicate charges.
"""

import os
from typing import Optional, Dict, Any, List
from dodopayments import DodoPayments
from dodopayments.types import Refund

class DodoClient:
    def __init__(self, api_key: Optional[str] = None, environment: Optional[str] = None):
        self.api_key = api_key or os.getenv("DODO_PAYMENTS_API_KEY")
        self.environment = environment or os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")
        self.client = DodoPayments(bearer_token=self.api_key, environment=self.environment)

    def retrieve_payment(self, payment_id: str) -> Any:
        return self.client.payments.retrieve(payment_id)

    def find_refund_for_action(self, payment_id: str, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Dead Reckoning precheck per E3 outcome:
        Matches existing refunds on the payment whose reason contains action_id.
        """
        payment = self.retrieve_payment(payment_id)
        if not payment or not payment.refunds:
            return None

        prefix = f"action_id:{action_id}"
        for ref in payment.refunds:
            if ref.reason and prefix in ref.reason:
                return {
                    "refund_id": ref.refund_id,
                    "payment_id": ref.payment_id,
                    "amount_minor": ref.amount,
                    "status": ref.status,
                    "reason": ref.reason,
                    "is_partial": ref.is_partial,
                    "created_at": ref.created_at.isoformat() if ref.created_at else None
                }
        return None

    def create_refund(
        self,
        payment_id: str,
        amount_minor: int,
        reason: str,
        product_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Issues refund to Dodo Payments with embedded reason and item_id parameters.
        """
        prod_id = product_id or os.getenv("DODO_PRODUCT_ID")
        items = [{"item_id": prod_id, "amount": amount_minor}] if prod_id else None

        refund_obj = self.client.refunds.create(
            payment_id=payment_id,
            reason=reason,
            items=items
        )

        return {
            "refund_id": refund_obj.refund_id,
            "payment_id": refund_obj.payment_id,
            "amount_minor": refund_obj.amount,
            "status": refund_obj.status,
            "reason": refund_obj.reason,
            "is_partial": refund_obj.is_partial,
            "created_at": refund_obj.created_at.isoformat() if refund_obj.created_at else None
        }
