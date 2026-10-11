# neatHack Build Log: Purser

## Project
- **Name:** Purser
- **Purpose:** Purser clears a SaaS founder's refund queue while they sleep, and if it dies halfway, it knows exactly which customers were paid. Once.
- **Problem Addressed:** Handling refund requests is painful, slow, and risky for SaaS founders. Mistakes (refunding twice, refunding the wrong customer, or violating policy) cause irreversible financial loss. Because background agents can terminate abruptly midway through execution, traditional agents relying purely on post-hoc telemetry traces risk duplicate payments or unrecoverable state. Purser introduces a write-ahead Log, Dead Reckoning against processor ledgers, and Witness Statements to guarantee exactly-once execution.

## Team
- **Builder:** Kinnoski (@0xkinno)

## Stack
- **Agent Core & API:** Python 3.12, FastAPI, `uv`
- **Telemetry & Observability:** neatlogs Python SDK (sessions, spans, prompt labels, custom attributes, PII masking), neatlogs-cli, neatlogs HTTP ingest API (`/v1/trace`)
- **LLM Reasoning & Orchestration:** Google Gemini (`google-genai` SDK) wrapped with `neatlogs.wrap()`
- **Version Control & Session Provenance:** Entire CLI, entire-graph, Checkpoints, Sessions
- **Business & Financial Modeling:** cfo.ai (Ari model)
- **Payment Processor:** Dodo Payments (Test Mode) with Standard Webhooks signature verification
- **Persistence & Distributed Leasing:** Supabase PostgreSQL with transaction row locks
- **Frontend Dashboard & Public Verification:** Next.js (App Router), React 19, TypeScript, Tailwind CSS v4, Motion (Framer Motion)
- **Verification & Testing:** pytest, hypothesis, Playwright, client-side TypeScript offline verifier

## Build Log

### 2026-10-10: Phase 0 Setup and Discovery Initialization
- **Environment & Project Scaffolding:**
  - Initialized repository structure with MIT License and git configuration.
  - Formatted and generated `TASK.md` tracking all phases verbatim from specification.
  - Created `.gitignore` protecting `.env`, `reference/`, secrets, and build caches.
  - Created `.env.example` and `.env` template configured for neatlogs, Gemini, Dodo Payments, and Supabase.
- **Entire Integration:**
  - Installed Entire CLI v0.11.4 on system.
  - Configured Entire agent hooks for Claude Code and Antigravity.
  - Installed `entire-graph` plugin v0.4.0.
  - Executed `entire graph init-agents --repo .`, generating `.entire/graph-agent.md`, `AGENTS.md`, and `CLAUDE.md`.
  - Committed initial configuration checkpoint with clean status.
- **Reference Analysis:**
  - Cloned reference repositories and official SDK sources into `reference/`.
  - Documented architectural takeaways, benchmark comparisons, and neatlogs SDK lifecycle behavior in `reference/NOTES.md`.
- **System Documentation:**
  - Documented honest boundaries and Crustdata exclusion justification in `LIMITATIONS.md`.
  - Configured neatHack build companion log in `hackathon.md`.

## Demo
- URL and instructions will be provided upon deployment in Phase 6.

## Known Limitations and Next Steps
- **Limitations:** Detailed in `LIMITATIONS.md` (Dodo Payments operated in test mode only; customer helpdesk tickets are synthetic scenarios; operator approval required for amounts exceeding threshold).
- **Next Steps:**
  - Install and authenticate `neatlogs-cli@0.2.0`.
  - Run neatlogs SDK doctor (`--local` and `--probe`) and persist diagnostics to `evidence/discovery/`.
  - Solicit credentials from user before executing Discovery Experiment E1 (Crash Truncation).

## Submission
- **Track:** Build an agent that works (literally)
- **Mandatory Partners:** neatlogs, Entire, cfo.ai
- **Status:** Phase 0 Discovery setup in progress; pre-submission checklist pending completion of build milestones.
