# Purser TASK.md

## Phase 0: Setup and Discovery
- [ ] 0.1 Create public GitHub repo `purser`, MIT license, `.gitignore` incl. `reference/`
- [ ] 0.2 Enable Entire for Claude Code in the repo; first checkpoint committed; `entire status` clean
- [ ] 0.3 Install entire-graph; `entire graph init-agents --repo .`; commit generated files
- [ ] 0.4 Clone all reference repos into `reference/` (Section 13); write `reference/NOTES.md` (gitignored): strengths, weaknesses, ideas to exceed
- [ ] 0.5 Read every official source in Section 1; write `hackathon.md` header
- [ ] 0.6 neatlogs project created; SDK Doctor local + probe pass (save JSON)
- [ ] 0.7 E1 crash truncation experiment run in WSL/Docker; results JSON + dashboard screenshots
- [ ] 0.8 E2 refund lifecycle in Dodo test mode (incl. automated test checkout)
- [ ] 0.9 E3 refund idempotency and fingerprint round-trip
- [ ] 0.10 E4 Witness Statement in same session
- [ ] 0.11 E5 prompt label drift
- [ ] 0.12 DISCOVERY.md written; final gate checklist all true

## Phase 1: Mechanism (prove the hardest claim first)
- [ ] 1.1 Supabase schema + migrations
- [ ] 1.2 Log with hash chain + tests (P7, P11)
- [ ] 1.3 Kernel: rules R1..Rn from POLICY.md + P1..P12 checks + unit + property tests
- [ ] 1.4 Dodo client + reconciliation (`find_refund_for_action`) per E3 outcome
- [ ] 1.5 Money protocol `execute_refund` + Dead Reckoning
- [ ] 1.6 Webhook receiver with signature verification; settlement updates (P6)
- [ ] 1.7 Muster + manifest export + offline verifier CLI + tamper tests
- [ ] 1.8 Witness Statement builder + completeness audit via neatlogs MCP/API (P10)
- [ ] 1.9 First real refund issued and settled in test mode; D04 kill test passes manually

## Phase 2: The agent
- [ ] 2.1 Telemetry setup (wrap Anthropic, spans, sessions, mask)
- [ ] 2.2 Tools + planner loop + propose_resolution + clarification + escalation
- [ ] 2.3 Prompts in neatlogs Prompts with labels; pin per batch
- [ ] 2.4 Seed: real test payments (Playwright checkout) + synthetic tickets set (varied, incl. injection, duplicates, ambiguity)
- [ ] 2.5 Batch runner + ticket leasing (row locks) + Report generation
- [ ] 2.6 v1-naive baseline agent implemented for comparison
- [ ] 2.7 Detections configured in neatlogs dashboard (screenshots)

## Phase 3: Storm Drills and improvement loop
- [ ] 3.1 Drill harness + fault proxy + SIGKILL points D01..D17
- [ ] 3.2 Run full matrix for v1 and v2, seeds ≥ 3; results.json + summary.json
- [ ] 3.3 Use neatlogs Investigate/Fixes/MCP on v1 failures; record Fix ids and the changes made
- [ ] 3.4 Before/after trace pair for the same ticket; numbers generated
- [ ] 3.5 Impact-scoped drills via entire graph impact; output committed
- [ ] 3.6 Provenance: rule → commit → checkpoint resolved for every rule id

## Phase 4: Product UI
- [ ] 4.1 Design tokens, fonts, paper grain, capsule nav
- [ ] 4.2 Hero image generated or sourced; Ledger Seal SVG; Dead Reckoning SVG
- [ ] 4.3 Landing page sections 1..8 with real data
- [ ] 4.4 Dashboard routes (all in 7.7) wired to the API, judge read-only mode, operator passcode
- [ ] 4.5 /verify TS port + /support + /r/[ticket]
- [ ] 4.6 Playwright responsive matrix all green; screenshots saved
- [ ] 4.7 Lighthouse ≥ 90 performance, 100 accessibility on landing (save report)

## Phase 5: Business and evidence
- [ ] 5.1 export_cfo_inputs.py; cfo.ai model built; BUSINESS_PLAN.md; /app/economics
- [ ] 5.2 generate_readme.py; README complete per template; all md docs written
- [ ] 5.3 CLAIMS.json complete; every claim has evidence + command + status
- [ ] 5.4 ENTIRE.md and NEATLOGS.md complete with links

## Phase 6: Ship
- [ ] 6.1 Deploy API + worker (Render), web (Vercel), with human approval
- [ ] 6.2 smoke_live.py all PASS
- [ ] 6.3 Clean-room reproduction from a fresh clone (credential-free path) passes
- [ ] 6.4 Demo video ≤ 3:00 covering all three partners
- [ ] 6.5 Building-in-public posts drafted for the human; links recorded
- [ ] 6.6 Pre-submission checklist (Section 14) all true
- [ ] 6.7 Human posts the quote-post submission in the official window
