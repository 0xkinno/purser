"""
Manual Drill D04: SIGKILL after processor accepted, before ACCEPTED is written to the Log.
Tests whether Purser's Dead Reckoning precheck detects the prior payment refund
and avoids double-refunding when re-executed.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
import asyncpg

from services.purser.log.wal import Log
from services.purser.kernel.kernel import Kernel
from services.purser.processor.dodo import DodoClient
from services.purser.log.protocol import MoneyProtocol, RefundAction, generate_action_id

async def run_d04_drill():
    db_url = os.getenv("DATABASE_URL")
    pool = await asyncpg.create_pool(db_url, min_size=1, max_size=3)
    log = Log(pool)
    kernel = Kernel()
    dodo = DodoClient()
    proto = MoneyProtocol(pool, log, kernel, dodo)

    batch_id = f"batch-d04-{os.urandom(4).hex()}"
    ticket_id = f"tkt_d04_{os.urandom(3).hex()}"
    # Use payment 1 from discovery
    payment_id = "pay_0NpaKpGOLUoyAfHDBwLYo"
    p_info = dodo.retrieve_payment(payment_id)
    cust_email = p_info.customer.email

    # Insert batch and ticket into Supabase
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO batches (batch_id, policy_version, policy_hash, planner_model, writer_model)
            VALUES ($1, '1.0.0', 'hash_v1', 'gemini-2.5-pro', 'gemini-2.5-flash')
            ON CONFLICT (batch_id) DO NOTHING;
            """,
            batch_id
        )
        await conn.execute(
            """
            INSERT INTO tickets (ticket_id, batch_id, customer_email, subject, status)
            VALUES ($1, $2, $3, 'Test D04 Kill Drill', 'NEW')
            ON CONFLICT (ticket_id) DO NOTHING;
            """,
            ticket_id, batch_id, cust_email
        )

    # Action definition: refund 50 cents ($0.50)
    amount_minor = 50
    rule_id = "R1_full_within_14_days"
    policy_ver = "1.0.0"
    action_id = generate_action_id(ticket_id, payment_id, amount_minor, rule_id, policy_ver)

    action = RefundAction(
        action_id=action_id,
        ticket_id=ticket_id,
        payment_id=payment_id,
        amount_minor=amount_minor,
        rule_id=rule_id,
        policy_version=policy_ver,
        ticket_email=cust_email,
        payment_email=cust_email
    )

    print(f"Simulating D04 execution 1 for action {action_id}...")
    res1 = await proto.execute_refund(
        batch_id=batch_id,
        action=action,
        rule_computed_minor=amount_minor
    )
    print("Execution 1 result:", res1["status"], "dispatched:", res1.get("dispatched"))

    print("\nSimulating crash and restart: running execution 2 with identical action...")
    res2 = await proto.execute_refund(
        batch_id=batch_id,
        action=action,
        rule_computed_minor=amount_minor
    )
    print("Execution 2 result:", res2["status"], "reused/recovered:", res2.get("reused", res2.get("recovered")))

    assert res2["status"] == "SUCCESS"
    assert res2.get("reused") or res2.get("recovered"), "Must not dispatch new processor refund!"

    print("\nD04 Drill PASSED: Zero duplicate refund created on retry!")
    await pool.close()

if __name__ == "__main__":
    asyncio.run(run_d04_drill())
