"""
Unit and Property-based tests for Kernel and Invariants P1..P12.
Exercises hypothesis properties across rule and invariant evaluations.
"""

from datetime import datetime, timezone, timedelta
import pytest
from hypothesis import given, strategies as st
from services.purser.kernel.kernel import Kernel, KernelVerdict
from services.purser.log.wal import LedgerView
from policy.rules import (
    R1_full_within_14_days,
    R2_prorata_annual_cancel,
    R3_downtime_credit,
    R4_duplicate_charge,
    R5_no_refund_after_usage_cap,
    R6_chargeback_risk_escalate
)

def test_p1_exactly_once():
    kernel = Kernel()
    # No receipt
    assert kernel.check_p1_exactly_once(None).allowed is True
    # Existing receipt
    assert kernel.check_p1_exactly_once({"receipt_id": "rcpt_1"}).allowed is False

@given(st.integers(min_value=1, max_value=10000), st.integers(min_value=0, max_value=10000))
def test_p2_refundable_ceiling_hypothesis(total, refunded):
    kernel = Kernel()
    remaining = max(0, total - refunded)
    view = LedgerView(payment_id="p1", total_amount_minor=total, refunded_minor=refunded, remaining_minor=remaining, actions_count=1)

    # Valid refund <= remaining
    if remaining > 0:
        verdict = kernel.check_p2_refundable_ceiling(remaining, view)
        assert verdict.allowed is True

    # Over-refund > remaining
    over_verdict = kernel.check_p2_refundable_ceiling(remaining + 1, view)
    assert over_verdict.allowed is False
    assert over_verdict.invariant_id == "P2"

def test_p4_identity_binding():
    kernel = Kernel()
    assert kernel.check_p4_identity_binding("user@example.com", "user@example.com").allowed is True
    assert kernel.check_p4_identity_binding("user@example.com", "different@example.com").allowed is False

def test_p5_threshold_and_flags():
    kernel = Kernel(refund_threshold_minor=5000)
    # Below threshold without flag -> allowed
    assert kernel.check_p5_no_self_approval(4000).allowed is True
    # Above threshold without human approval -> blocked
    assert kernel.check_p5_no_self_approval(6000).allowed is False
    # Above threshold with human approval -> allowed
    assert kernel.check_p5_no_self_approval(6000, human_approved=True).allowed is True

def test_rule_r1():
    now = datetime.now(timezone.utc)
    # 5 days ago -> full refund
    eval1 = R1_full_within_14_days(2898, now - timedelta(days=5), now, 0.1)
    assert eval1.allowed is True
    assert eval1.amount_minor == 2898

    # 20 days ago -> declined
    eval2 = R1_full_within_14_days(2898, now - timedelta(days=20), now, 0.1)
    assert eval2.allowed is False
    assert eval2.amount_minor == 0
