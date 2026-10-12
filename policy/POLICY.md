# Purser Founder Refund Policy

Version: 1.0.0
Status: ACTIVE
Owner: Kingsley (0xkinno)

Purser executes autonomous refund operations for SaaS products powered by Dodo Payments in test mode.
Every refund must satisfy the rules below. All amount calculations are deterministic functions of the rule, payment history, and verified incidents. The language model never sets or modifies an amount.

---

## Rules

### Rule R1: Full Refund Within 14 Days
- **Rule ID**: `R1_full_within_14_days`
- **Condition**: Request submitted within 14 calendar days of payment date, customer states dissatisfaction or accidental purchase, and subscription usage is below cap.
- **Refund Amount**: 100% of the payment total (`payment.total_amount`).

### Rule R2: Pro-rata Annual Cancellation
- **Rule ID**: `R2_prorata_annual_cancel`
- **Condition**: Customer on an annual plan requests cancellation after 14 days but before 180 days.
- **Refund Amount**: Pro-rated remaining unused full months calculated deterministically:
  `remaining_months / 12 * payment.total_amount`.

### Rule R3: Downtime Credit
- **Rule ID**: `R3_downtime_credit`
- **Condition**: Customer claims service disruption matching an official verified incident record in `incidents.json` during their billing window.
- **Refund Amount**: Daily equivalent multiplied by outage credit percentage defined in the incident record.

### Rule R4: Duplicate Charge
- **Rule ID**: `R4_duplicate_charge`
- **Condition**: Customer was billed twice for the same product within a 24-hour window on the same customer record.
- **Refund Amount**: 100% refund of the duplicate payment (`payment.total_amount`).

### Rule R5: No Refund After Usage Cap
- **Rule ID**: `R5_no_refund_after_usage_cap`
- **Condition**: Customer has exceeded 80% usage of the active plan quota or passed 30 days.
- **Decision**: Decline refund (`amount = 0`), reply politely citing policy.

### Rule R6: Chargeback and Dispute Risk Escalation
- **Rule ID**: `R6_chargeback_risk_escalate`
- **Condition**: Ticket tone indicates severe chargeback threat, regulatory complaint, or suspicious abuse/fraud flag.
- **Decision**: Escalate immediately to human operator review packet; automated processing halted.
