"""
Money Protocol: execute_refund and Dead Reckoning crash recovery.
Implements Section 4.3 with write-ahead durable logging (INTENDED -> DISPATCHED -> ACCEPTED -> SETTLED).
"""

import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import asyncpg

from services.purser.log.wal import Log, LedgerView
from services.purser.kernel.kernel import Kernel, KernelVerdict
from services.purser.processor.dodo import DodoClient

def generate_action_id(
    ticket_id: str,
    payment_id: str,
    amount_minor: int,
    rule_id: str,
    policy_version: str
) -> str:
    raw = f"refund|{ticket_id}|{payment_id}|{amount_minor}|{rule_id}|{policy_version}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

@dataclass
class RefundAction:
    action_id: str
    ticket_id: str
    payment_id: str
    amount_minor: int
    rule_id: str
    policy_version: str
    ticket_email: str
    payment_email: str
    attempt: int = 1

    def fingerprint_reason(self) -> str:
        return f"action_id:{self.action_id}:{self.rule_id}:{self.policy_version}"

class MoneyProtocol:
    def __init__(self, pool: asyncpg.Pool, log: Log, kernel: Kernel, dodo: DodoClient):
        self.pool = pool
        self.log = log
        self.kernel = kernel
        self.dodo = dodo

    async def execute_refund(
        self,
        batch_id: str,
        action: RefundAction,
        rule_computed_minor: int,
        injection_flag: bool = False,
        dispute_flag: bool = False,
        human_approved: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the exact 5-step money protocol from Section 4.3:
        0. Return existing receipt if already committed.
        1. Pure deterministic kernel verdict.
        2. Write-ahead durable INTENDED record.
        3. Dead Reckoning precheck at processor.
        4. DISPATCHED record -> processor call -> ACCEPTED receipt.
        """
        # Step 0: Already done?
        if receipt := await self.log.receipt_for(action.action_id):
            return {"status": "SUCCESS", "receipt": receipt, "reused": True}

        # Step 1: Kernel decision (pure Python, NO LLM)
        payment_info = self.dodo.retrieve_payment(action.payment_id)
        payment_total = payment_info.total_amount
        ledger = await self.log.ledger_view(action.payment_id, payment_total)

        verdict = self.kernel.check_refund(
            action_id=action.action_id,
            proposed_minor=action.amount_minor,
            rule_computed_minor=rule_computed_minor,
            ticket_email=action.ticket_email,
            payment_email=action.payment_email,
            ledger_view=ledger,
            existing_receipt=receipt,
            injection_flag=injection_flag,
            dispute_flag=dispute_flag,
            human_approved=human_approved
        )

        if not verdict.allowed:
            # Record denial in Log
            await self.log.append(batch_id, action.action_id, "DENIED", {
                "reason": verdict.reason,
                "invariant_id": verdict.invariant_id,
                "requires_human_approval": verdict.requires_human_approval
            })
            return {"status": "DENIED", "verdict": asdict(verdict)}

        # Step 2: Write-ahead INTENDED record
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO refund_actions (action_id, ticket_id, payment_id, amount_minor, rule_id, policy_version, state, attempt)
                VALUES ($1, $2, $3, $4, $5, $6, 'INTENDED', $7)
                ON CONFLICT (action_id) DO UPDATE SET attempt = refund_actions.attempt + 1;
                """,
                action.action_id, action.ticket_id, action.payment_id, action.amount_minor,
                action.rule_id, action.policy_version, action.attempt
            )
        await self.log.append(batch_id, action.action_id, "INTENDED", asdict(action))

        # Step 3: Dead Reckoning precheck (processor already processed this in a prior crashed life?)
        if existing_refund := self.dodo.find_refund_for_action(action.payment_id, action.action_id):
            receipt_id = f"rcpt_{action.action_id}"
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO receipts (receipt_id, action_id, ticket_id, payment_id, refund_id, amount_minor, rule_id, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, 'ACCEPTED')
                    ON CONFLICT (receipt_id) DO NOTHING;
                    """,
                    receipt_id, action.action_id, action.ticket_id, action.payment_id,
                    existing_refund["refund_id"], action.amount_minor, action.rule_id
                )
            await self.log.append(batch_id, action.action_id, "ACCEPTED", existing_refund)
            return {"status": "SUCCESS", "receipt": existing_refund, "recovered": True}

        # Step 4: Dispatch
        await self.log.append(batch_id, action.action_id, "DISPATCHED", {"attempt": action.attempt})
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE refund_actions SET state = 'DISPATCHED' WHERE action_id = $1;", action.action_id)

        # Call Processor
        created_refund = self.dodo.create_refund(
            payment_id=action.payment_id,
            amount_minor=action.amount_minor,
            reason=action.fingerprint_reason()
        )

        receipt_id = f"rcpt_{action.action_id}"
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO receipts (receipt_id, action_id, ticket_id, payment_id, refund_id, amount_minor, rule_id, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, 'ACCEPTED')
                ON CONFLICT (receipt_id) DO NOTHING;
                """,
                receipt_id, action.action_id, action.ticket_id, action.payment_id,
                created_refund["refund_id"], action.amount_minor, action.rule_id
            )
            await conn.execute("UPDATE refund_actions SET state = 'ACCEPTED' WHERE action_id = $1;", action.action_id)

        await self.log.append(batch_id, action.action_id, "ACCEPTED", created_refund)
        return {"status": "SUCCESS", "receipt": created_refund, "dispatched": True}
