"""
Deterministic rule functions implementing founder refund policy (R1..R6).
Pure Python: NO LLM, NO network.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple

POLICY_VERSION = "1.0.0"

@dataclass
class RuleEvaluation:
    rule_id: str
    allowed: bool
    amount_minor: int
    reason: str
    requires_human_approval: bool = False
    escalation_reason: Optional[str] = None

def R1_full_within_14_days(
    payment_amount_minor: int,
    payment_created_at: datetime,
    ticket_created_at: datetime,
    usage_percent: float = 0.0
) -> RuleEvaluation:
    delta_days = (ticket_created_at - payment_created_at).total_seconds() / 86400.0
    if delta_days <= 14.0 and usage_percent <= 0.8:
        return RuleEvaluation(
            rule_id="R1_full_within_14_days",
            allowed=True,
            amount_minor=payment_amount_minor,
            reason="Within 14-day money back guarantee"
        )
    return RuleEvaluation(
        rule_id="R1_full_within_14_days",
        allowed=False,
        amount_minor=0,
        reason=f"Exceeded 14 days ({delta_days:.1f} days) or high usage ({usage_percent*100:.0f}%)"
    )

def R2_prorata_annual_cancel(
    payment_amount_minor: int,
    payment_created_at: datetime,
    ticket_created_at: datetime,
    plan_interval: str = "annual"
) -> RuleEvaluation:
    if plan_interval != "annual":
        return RuleEvaluation(
            rule_id="R2_prorata_annual_cancel",
            allowed=False,
            amount_minor=0,
            reason="Rule applies exclusively to annual subscriptions"
        )
    delta_days = (ticket_created_at - payment_created_at).total_seconds() / 86400.0
    if delta_days > 180.0:
        return RuleEvaluation(
            rule_id="R2_prorata_annual_cancel",
            allowed=False,
            amount_minor=0,
            reason="Annual plan cancellation requests beyond 180 days not eligible"
        )
    elapsed_months = int(delta_days // 30)
    unused_months = max(0, 12 - elapsed_months)
    computed_minor = int((unused_months / 12.0) * payment_amount_minor)
    return RuleEvaluation(
        rule_id="R2_prorata_annual_cancel",
        allowed=True,
        amount_minor=computed_minor,
        reason=f"Pro-rata refund for {unused_months} unused months"
    )

def R3_downtime_credit(
    payment_amount_minor: int,
    outage_credit_pct: int = 100,
    days_credited: int = 1
) -> RuleEvaluation:
    # Monthly equivalent: 30 days
    daily_rate = payment_amount_minor / 30.0
    credit_amount = int(daily_rate * days_credited * (outage_credit_pct / 100.0))
    return RuleEvaluation(
        rule_id="R3_downtime_credit",
        allowed=True,
        amount_minor=min(payment_amount_minor, credit_amount),
        reason=f"Downtime credit compensation for {days_credited} day(s) at {outage_credit_pct}%"
    )

def R4_duplicate_charge(
    duplicate_payment_amount_minor: int,
    time_difference_hours: float
) -> RuleEvaluation:
    if time_difference_hours <= 24.0:
        return RuleEvaluation(
            rule_id="R4_duplicate_charge",
            allowed=True,
            amount_minor=duplicate_payment_amount_minor,
            reason="Duplicate charge within 24 hour billing window"
        )
    return RuleEvaluation(
        rule_id="R4_duplicate_charge",
        allowed=False,
        amount_minor=0,
        reason="Charges are not within duplicate transaction threshold"
    )

def R5_no_refund_after_usage_cap(
    usage_percent: float
) -> RuleEvaluation:
    if usage_percent > 0.8:
        return RuleEvaluation(
            rule_id="R5_no_refund_after_usage_cap",
            allowed=False,
            amount_minor=0,
            reason="Service usage exceeded 80% consumption threshold"
        )
    return RuleEvaluation(
        rule_id="R5_no_refund_after_usage_cap",
        allowed=True,
        amount_minor=0,
        reason="Usage within normal bounds"
    )

def R6_chargeback_risk_escalate(
    sentiment_threat: bool,
    dispute_indicated: bool
) -> RuleEvaluation:
    if sentiment_threat or dispute_indicated:
        return RuleEvaluation(
            rule_id="R6_chargeback_risk_escalate",
            allowed=False,
            amount_minor=0,
            reason="Elevated chargeback or dispute risk detected",
            requires_human_approval=True,
            escalation_reason="Customer expressed intent to dispute charge or seek regulatory action"
        )
    return RuleEvaluation(
        rule_id="R6_chargeback_risk_escalate",
        allowed=True,
        amount_minor=0,
        reason="No dispute threat flagged"
    )
