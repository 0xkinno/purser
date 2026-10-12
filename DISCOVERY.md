# DISCOVERY.md

This document records the empirical discoveries made in Phase 0 of Purser development across five targeted experiments (E1 to E5). Each discovery is backed by raw committed JSON artifacts in `evidence/discovery/`.

---

## 1. Sponsor primitive

Purser integrates two external developer primitives:
1. **NeatLogs OpenTelemetry SDK and Ingestion API**:
   - Python OpenTelemetry batch tracing SDK (`neatlogs.wrap()`, `neatlogs.init()`, `neatlogs.span()`).
   - NeatLogs Prompts API (`neatlogs.create_prompt()`, `neatlogs.get_prompt()`).
   - NeatLogs Ingestion REST endpoint (`POST https://ingest.neatlogs.com/v1/trace`) using project write keys.
2. **Dodo Payments Test Mode Merchant API**:
   - Merchant REST API and Python SDK (`dodopayments`) for checkout sessions, payments, balances, ledgers, and refunds.

---

## 2. Observed constraint

Across experiments E1 through E5, five fundamental constraints were discovered:

1. **H1 (Crash Truncation and Root Loss)**: OpenTelemetry batch exporters queue span data in memory until exported on a periodic timer (`flush_interval=5.0s` by default). When a worker process terminates abruptly via uncatchable signals (`SIGKILL`, container OOM kill, hardware failure), all buffered spans in flight are permanently lost. Furthermore, because OpenTelemetry spans only serialize upon closure, the parent `WORKFLOW` span enclosing the run is never recorded, leaving fragmented orphan spans or complete trace loss.
2. **H2 (Processor Truth vs Trace Truth)**: A refund request accepted by the payment processor returns status `succeeded` or `pending` at invocation time, but subsequent settlement, disputes, or balance adjustments occur out of band. Furthermore, processor-level wallet balances and line-item configurations enforce hard rejections (`INSUFFICIENT_WALLET_FUNDS`, `LINE_ITEM_REFUND_AMOUNT_TOO_HIGH`) that naive trace status logs fail to reflect without continuous reconciliation.
3. **H3 (Processor Non-Idempotency on Retries)**: Dodo Payments refund creation endpoint does not enforce deduplication via standard `Idempotency-Key` HTTP headers. Repeated refund requests with identical payloads and identical idempotency headers generate separate and independent refund records (`ref_*`) until available line-item balance or wallet funds are exhausted. The only reliable mechanism to prevent double-refunds during crash recovery is Dead Reckoning matching against the `reason` field, which round-trips consistently.
4. **H4 (Trace Immutability and Witness Ingestion)**: The NeatLogs HTTP trace ingestion endpoint (`POST /v1/trace`) automatically issues newly minted trace IDs and span IDs. It is mathematically and architecturally impossible to append spans retroactively to an existing crashed trace. A recovery worker cannot repair a broken trace; it can only file an independent **Witness Statement** trace linked by `neatlogs.session.id` and semantic attributes.
5. **H5 (Prompt Version Drift Mid-Batch)**: Dynamically fetching prompt definitions via mutable labels (`label='production'`) creates mid-run non-determinism if a prompt version is re-tagged during an active batch run. Pinned version retrieval (`version=N`) is strictly required to guarantee batch stability.

---

## 3. Evidence

### Table 1: Crash Truncation Matrix (Experiment E1, 12 runs on Linux WSL)

| Kill Signal | Flush Interval | Step Killed | Spans Executed | Spans Received | Root Present? | Last Step Visible | Trace Integrity Status |
|:---|:---|:---|:---|:---|:---|:---|:---|
| SIGKILL | 5.0s | 3 | 3 | 0 | False | 0 | Total Trace Loss |
| SIGKILL | 5.0s | 12 | 12 | 0 | False | 0 | Total Trace Loss |
| SIGKILL | 5.0s | 19 | 19 | 0 | False | 0 | Total Trace Loss |
| SIGKILL | 1.0s | 3 | 3 | 0 | False | 0 | Total Trace Loss |
| SIGKILL | 1.0s | 12 | 12 | 9 | False | 9 | Tail-Truncated, Rootless |
| SIGKILL | 1.0s | 19 | 19 | 17 | False | 17 | Tail-Truncated, Rootless |
| SIGKILL | 0.2s | 3 | 3 | 0 | False | 0 | Total Trace Loss |
| SIGKILL | 0.2s | 12 | 12 | 11 | False | 11 | Tail-Truncated, Rootless |
| SIGKILL | 0.2s | 19 | 19 | 18 | False | 18 | Tail-Truncated, Rootless |
| SIGTERM | 5.0s | 3 | 3 | 3 | True | 3 | Clean Shutdown Drain |
| SIGTERM | 5.0s | 12 | 12 | 12 | True | 12 | Clean Shutdown Drain |
| SIGTERM | 5.0s | 19 | 19 | 19 | True | 19 | Clean Shutdown Drain |

*Raw data:* `evidence/discovery/e1_results.json`

### Table 2: Refund Lifecycle and Processor Constraints (Experiment E2)

| Test Case | Parameter / Payload | Observed HTTP / SDK Result | Error Code / Status | Architectural Consequence |
|:---|:---|:---|:---|:---|
| Partial Refund | amount: 1000 cents ($10.00) | 200 OK | status: `succeeded`, is_partial: True | Partial refunds update payment `refund_status` to `partial` |
| Over-Refund | amount: 2500 cents (exceeds 898 remaining) | 400 Bad Request | `LINE_ITEM_REFUND_AMOUNT_TOO_HIGH` | Processor enforces ceiling, but error occurs mid-call |
| Product Refund without Item ID | items: omitted | 409 Conflict | `INSUFFICIENT_WALLET_FUNDS` | Line item parameters required for itemized products |
| Net Merchant Wallet Depletion | refund exceeds available balance after fees | 409 Conflict | `INSUFFICIENT_WALLET_FUNDS` | Processor deducts $1.00 fee per refund; wallet can starve |

*Raw data:* `evidence/discovery/e2_refund_lifecycle.json`

### Table 3: Refund Idempotency and Dead Reckoning (Experiment E3)

| Ingestion Attempt | Header Passed | Reason String | Generated Refund ID | Status | Deduplicated? |
|:---|:---|:---|:---|:---|:---|
| Request A | None | `test partial refund` | `ref_0NpaM1zsPnunlGWyjXVD1` | succeeded | No (New refund) |
| Request B (Identical) | None | `test partial refund` | `ref_0NpaMDfHFfkiBtzfN4Fxz` | succeeded | No (Second refund issued!) |
| Request C | `Idempotency-Key: test-1` | `test idem key 1` | `ref_0NpaMa3ltU50egHQZbmRc` | succeeded | No (New refund) |
| Request D (Same Key) | `Idempotency-Key: test-1` | `test idem key 1` | `ref_0NpaMaLrkoUpVhwlv0XXC` | succeeded | No (Duplicate refund issued!) |
| List Verification | `payments.retrieve()` | Preserves embedded string | Round-trips `reason` | succeeded | Verified: reason preserves action ID |

*Raw data:* `evidence/discovery/e3_refund_idempotency.json`

### Table 4: Witness Statement Trace Ingestion (Experiment E4)

| Endpoint | Ingested Spans | Batch Session ID | Original Crashed Trace ID | HTTP Status | Response Trace ID |
|:---|:---|:---|:---|:---|:---|
| `POST /v1/trace` | 4 spans | `batch-e4-172429fb` | `d3f2a95e53a54e19b56ca7a8b37fb664` | 200 OK | `e2f9493b3077c4948065c3549f375751` |

*Raw data:* `evidence/discovery/e4_witness.json`

### Table 5: Prompt Label Drift (Experiment E5)

| Evaluation Stage | Dynamic Label (`label="production"`) | Pinned Version (`version=1`) | Drift Event |
|:---|:---|:---|:---|
| Tickets 1 to 5 | Version 1 | Version 1 | None |
| Label Repointed to V2 | Version 2 | Version 1 | Label updated dynamically in NeatLogs |
| Tickets 6 to 10 | Version 2 (DRIFT DETECTED) | Version 1 (STABLE) | Dynamic switched mid-run; pinned stayed constant |

*Raw data:* `evidence/discovery/e5_prompt_label_drift.json`

---

## 4. Why existing approaches do not solve it

1. **Generic approach "Rely on Telemetry as Audit Log" fails**:
   - OpenTelemetry is an observability protocol, not a financial write-ahead log. When a crash occurs, buffered spans vanish. If the system treats telemetry traces as the primary ledger of actions, operations that executed at the payment gateway disappear from the telemetry audit trail.
2. **Generic approach "Retry on Error" fails**:
   - Because the payment processor does not enforce idempotency on refunds via headers, a naive worker restarting after a crash or network timeout will re-issue the refund, causing double-refunds and balance exhaustion.
3. **Generic approach "One Trace per Batch" fails**:
   - Wrapping an entire queue batch in a single OpenTelemetry root span means any unhandled crash drops the entire root span, corrupting visibility for all tickets in the batch.
4. **Generic approach "Dynamic Prompt Fetching" fails**:
   - Calling `get_prompt("planner", label="production")` per ticket exposes long-running queues to mid-batch policy mutations, causing tickets in the same overnight run to be evaluated against conflicting instructions.

---

## 5. New capability enabled

Empowered by these empirical findings, Purser implements a fault-tolerant architecture:
1. **The Log as Financial Truth**: A persistent, append-only, write-ahead PostgreSQL log with SHA-256 hash chaining. State transitions (`INTENDED` -> `DISPATCHED` -> `ACCEPTED` -> `SETTLED`) are written to disk before any external API call leaves the machine.
2. **Dead Reckoning Reconciliation**: Before issuing any refund, Purser embeds a deterministic fingerprint in the payment `reason` (`action_id:<sha256[:24]>:<rule_id>`). On recovery after a crash, Purser queries the payment's existing refunds and reconciles them against pending intents before dispatching calls.
3. **Witness Statement Reconstruction**: When an agent crash causes telemetry truncation, the recovery worker files an out-of-band Witness Statement via NeatLogs `POST /v1/trace`, binding the dead run to the batch session and restoring observability.
4. **Pinned Policy Batches**: Every batch resolves prompt labels and policy rules at initialization, commits their exact content hashes into the Log, and executes all tickets against immutable versions.

---

## 6. Invariant

The architectural findings establish the following core invariants enforced by Purser's deterministic Kernel:
- **P1 (Exactly-once per action id)**: A refund is dispatched if and only if no prior accepted receipt exists in the Log or on the processor.
- **P2 (Refundable ceiling)**: Cumulative refunds on a payment never exceed the total payment amount.
- **P3 (Deterministic amount computation)**: Refund amounts are strictly calculated by pure Python rules; LLM tool outputs never set monetary amounts.
- **P7 (Write-ahead durable logging)**: No network request to Dodo Payments is executed without a prior durable `INTENDED` record in the database.
- **P8 (Pinned policy version)**: A batch executes exclusively against pinned prompt versions and rule commits recorded in the Log at batch start.
- **P9 (Muster reconciliation)**: A batch cannot close unless processor-confirmed refunds exactly match the Log records.

---

## 7. Failure mode

Without these mechanisms, the failure modes are critical and direct:
1. **Double-Refund Storm**: A worker killed during a network acknowledgement re-runs and executes a second refund, losing merchant capital.
2. **Invisible Money Movement**: A killed process leaves behind an executed processor refund with zero traces in telemetry, creating an un-auditable discrepancy.
3. **Policy Divergence**: A mid-batch prompt edit causes later tickets to receive different refund decisions than earlier tickets in the same queue.

---

## 8. Reproducible demonstration

Every finding can be reproduced deterministically with the following commands:

```bash
# E1: Reproduce crash truncation and span loss under SIGKILL / SIGTERM
python -m experiments.e1_crash_truncation

# E2: Reproduce processor refund lifecycle, line item requirements, and wallet fee limits
uv run python experiments/e2_refund_lifecycle.py

# E3: Reproduce processor non-idempotency and verify reason field round-trip
uv run python experiments/e3_refund_idempotency.py

# E4: Reproduce Witness Statement ingestion via HTTP POST /v1/trace
uv run python experiments/e4_witness_statement.py

# E5: Reproduce mid-batch prompt label drift
uv run python experiments/e5_prompt_label_drift.py
```
