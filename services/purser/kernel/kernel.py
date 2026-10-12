"""
Deterministic Kernel implementing Invariants P1 to P12.
Pure Python: NO LLM, NO network.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from services.purser.log.wal import LedgerView

@dataclass
class KernelVerdict:
    allowed: bool
    invariant_id: Optional[str]
    reason: str
    requires_human_approval: bool = False

class Kernel:
    def __init__(self, refund_threshold_minor: int = 5000):
        self.refund_threshold_minor = refund_threshold_minor

    def check_p1_exactly_once(self, existing_receipt: Optional[Dict[str, Any]]) -> KernelVerdict:
        """P1: Exactly-once per action id."""
        if existing_receipt is not None:
            return KernelVerdict(
                allowed=False,
                invariant_id="P1",
                reason=f"Action already has recorded receipt: {existing_receipt.get('receipt_id')}"
            )
        return KernelVerdict(allowed=True, invariant_id="P1", reason="No prior receipt exists")

    def check_p2_refundable_ceiling(self, proposed_minor: int, ledger_view: LedgerView) -> KernelVerdict:
        """P2: Refundable ceiling: sum of refunds on a payment <= payment amount."""
        if proposed_minor <= 0:
            return KernelVerdict(
                allowed=False,
                invariant_id="P2",
                reason=f"Proposed refund amount must be positive: {proposed_minor}"
            )
        if proposed_minor > ledger_view.remaining_minor:
            return KernelVerdict(
                allowed=False,
                invariant_id="P2",
                reason=(
                    f"Over-refund blocked: proposed {proposed_minor} exceeds remaining "
                    f"refundable balance {ledger_view.remaining_minor} (total: {ledger_view.total_amount_minor}, refunded: {ledger_view.refunded_minor})"
                )
            )
        return KernelVerdict(allowed=True, invariant_id="P2", reason="Amount within refundable ceiling")

    def check_p3_amount_determinism(self, proposed_minor: int, rule_computed_minor: int) -> KernelVerdict:
        """P3: Amount is a pure function of rule; model output never sets an amount."""
        if proposed_minor != rule_computed_minor:
            return KernelVerdict(
                allowed=False,
                invariant_id="P3",
                reason=f"Amount mismatch: proposed {proposed_minor} does not match rule calculated {rule_computed_minor}"
            )
        return KernelVerdict(allowed=True, invariant_id="P3", reason="Amount matches deterministic rule computation")

    def check_p4_identity_binding(self, ticket_customer_email: str, payment_customer_email: str) -> KernelVerdict:
        """P4: Identity binding: refunded payment belongs to the customer bound to ticket."""
        if not ticket_customer_email or not payment_customer_email:
            return KernelVerdict(
                allowed=False,
                invariant_id="P4",
                reason="Customer email missing on ticket or payment"
            )
        if ticket_customer_email.strip().lower() != payment_customer_email.strip().lower():
            return KernelVerdict(
                allowed=False,
                invariant_id="P4",
                reason=f"Identity mismatch: ticket email '{ticket_customer_email}' != payment email '{payment_customer_email}'"
            )
        return KernelVerdict(allowed=True, invariant_id="P4", reason="Customer identity verified")

    def check_p5_no_self_approval(
        self,
        amount_minor: int,
        injection_flag: bool = False,
        dispute_flag: bool = False,
        human_approved: bool = False
    ) -> KernelVerdict:
        """P5: No self-approval: amounts above threshold or flags require human decision."""
        needs_human = (amount_minor > self.refund_threshold_minor) or injection_flag or dispute_flag
        if needs_human and not human_approved:
            return KernelVerdict(
                allowed=False,
                invariant_id="P5",
                reason=f"High-stakes payout or risk flag requires human approval (amount: {amount_minor}, threshold: {self.refund_threshold_minor})",
                requires_human_approval=True
            )
        return KernelVerdict(allowed=True, invariant_id="P5", reason="Threshold check passed")

    def check_p6_settlement_truth(self, processor_status: str) -> KernelVerdict:
        """P6: Settlement truth: refund counts as done only on processor status succeeded."""
        if processor_status == "succeeded":
            return KernelVerdict(allowed=True, invariant_id="P6", reason="Processor status succeeded")
        return KernelVerdict(
            allowed=False,
            invariant_id="P6",
            reason=f"Refund is not settled: processor status is '{processor_status}'"
        )

    def check_refund(
        self,
        action_id: str,
        proposed_minor: int,
        rule_computed_minor: int,
        ticket_email: str,
        payment_email: str,
        ledger_view: LedgerView,
        existing_receipt: Optional[Dict[str, Any]] = None,
        injection_flag: bool = False,
        dispute_flag: bool = False,
        human_approved: bool = False
    ) -> KernelVerdict:
        """Comprehensive pre-flight check evaluating invariants P1 to P5."""
        # P1
        v1 = self.check_p1_exactly_once(existing_receipt)
        if not v1.allowed: return v1

        # P3
        v3 = self.check_p3_amount_determinism(proposed_minor, rule_computed_minor)
        if not v3.allowed: return v3

        # P4
        v4 = self.check_p4_identity_binding(ticket_email, payment_email)
        if not v4.allowed: return v4

        # P2
        v2 = self.check_p2_refundable_ceiling(proposed_minor, ledger_view)
        if not v2.allowed: return v2

        # P5
        v5 = self.check_p5_no_self_approval(proposed_minor, injection_flag, dispute_flag, human_approved)
        if not v5.allowed: return v5

        return KernelVerdict(allowed=True, invariant_id=None, reason="All kernel checks passed")
