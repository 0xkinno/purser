# Purser Limitations and Honest Boundaries

Every system has architectural boundaries. In accordance with neatHack principles and honest engineering, this document details the boundaries and design trade-offs of Purser.

---

## 1. Integrations and Scope

1. **Crustdata Integration**: Crustdata is not integrated, as enrichment of company and market metadata was not required for proving the refund protocol and crash recovery thesis.
2. **Processor Environment**: Payments and refunds operate exclusively against the Dodo Payments Test Mode environment. Real HTTP requests, realistic card processing flows, real webhooks, and real refund IDs are generated, but zero real money is transacted.
3. **Synthetic Customer Helpdesk Tickets**: Customer identities, tickets, and complaint text are synthetically generated across varied scenarios (polite, angry, prompt injection attacks, chargeback threats, duplicate requests, and ambiguous references) to simulate realistic SaaS support queues.
4. **Human Decisions on Escalations**: High-risk actions (refund amounts above the configured threshold, ambiguous order matching, prompt injection detection, and potential abuse) require explicit human approval via the operator dashboard. The agent cannot self-approve payouts outside policy bounds.

---

## 2. Telemetry and System Assumptions

1. **Trace Buffering**: Telemetry spans buffered in process memory are subject to tail-truncation upon abrupt termination (`SIGKILL`). Purser explicitly treats the local write-ahead Log and the processor's ledger as the source of financial truth, utilizing Witness Statements to recover the telemetry record post-restart.
2. **Single Process Worker Execution**: Ticket leasing relies on PostgreSQL row locks (`SELECT ... FOR UPDATE`) to guarantee single-worker execution semantics per ticket during concurrent worker operation.
