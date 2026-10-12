# Video Sources and Facts

Every number and claim spoken in the Purser master demo film is traced to a committed file.

| Spoken Claim | Source File | Status |
|---|---|---|
| Ticket 73, Maya | Persona | Illustrative persona, labelled on screen |
| E1 counts | `evidence/discovery/e1_results.json` | Measured crash test matrix |
| Paid twice, idempotency key | `evidence/discovery/e3_refund_idempotency.json` | Verified against Dodo API |
| Twelve invariants | `services/purser/kernel/kernel.py` | 12 protocol and safety rules in kernel |
| Fingerprint in the refund | `services/purser/log/protocol.py` | SHA-256 reason prefix round-trip |
| Kill after Dodo accepts, no second payment | `evidence/drills/d04_live.json` | Real D04 drill results |
| Witness statement | `evidence/drills/d04_live.json` | Witness statement via HTTP ingest |
| Reconciled before close, one click, never approves itself | `services/purser/muster/muster.py` | Muster reconciliation ledger |
| One trace per ticket, batch as session | `services/purser/telemetry/setup.py` | neatlogs WORKFLOW instrumentation |
| Entire rule to session | `docs/ENTIRE.md` | Entire checkpoint provenance map |
| cfo.ai pricing, margin, runway | `docs/BUSINESS_PLAN.md` | Unit economics model |
