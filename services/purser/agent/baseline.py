"""
Baseline v1-naive agent implementation for Storm Drill comparison.
Implements Section 6 requirements:
- Amount computed by LLM / heuristics (not pure deterministic kernel)
- Naive retry-on-error without WAL or Dead Reckoning precheck
- No Muster verification
"""

import os
import asyncio
from typing import Dict, Any
from services.purser.processor.dodo import DodoClient

class BaselineNaiveAgent:
    def __init__(self):
        self.dodo = DodoClient()

    async def handle_ticket_naive(self, ticket: Dict[str, Any], simulated_error: bool = False) -> Dict[str, Any]:
        """
        Naive implementation: calls create_refund directly without durable INTENDED,
        without checking prior processor receipts, and retries naively on failure.
        """
        payment_id = ticket.get("payment_id", "pay_0NpaKpGOLUoyAfHDBwLYo")
        amount = ticket.get("requested_amount", 1000)

        # Naive attempt 1
        try:
            if simulated_error:
                # Simulates network crash after call dispatched
                self.dodo.create_refund(payment_id=payment_id, amount_minor=amount, reason="naive refund attempt 1")
                raise ConnectionResetError("Simulated network timeout during processor call")

            res = self.dodo.create_refund(payment_id=payment_id, amount_minor=amount, reason="naive refund")
            return {"status": "SUCCESS", "refund": res}
        except Exception as e:
            # Naive retry without Dead Reckoning check!
            # Creates duplicate refund if first call succeeded on processor!
            res_retry = self.dodo.create_refund(payment_id=payment_id, amount_minor=amount, reason="naive retry refund")
            return {"status": "RECOVERED_NAIVE", "refund": res_retry, "duplicate_created": True}
