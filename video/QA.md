# Video Quality Assurance Report

## 1. Timing and Audio Sync
- Master Duration: 170.0s (2:50), within the 3:00 hard limit.
- Voiceover Duration: 169.64s across 10 blocks (V1 to V10).
- Voice: `en-US-ChristopherNeural` (edge-tts) at -4% rate.
- Audio Format: 48 kHz, mono, 24-bit PCM.
- Spacing: 0.4s breathing pause between blocks, no vocal fry, no overlapping audio.

## 2. Visual System and Brand Alignment
- Color Tokens: Verified against `apps/web/app/globals.css`.
  - Paper: `#F5F0E6`, `#EFE8DA`, `#E6DDCB`
  - Ink: `#16130F`, `#4A443B`, `#8A8275`
  - Signal Blue: `#2B44FF`
  - Brass: `#A8792E`
  - Settled Green: `#1F7A4D`
  - Alarm Red: `#C2361F`
- Typography: Instrument Serif 88px/64px/44px, Geist Sans, JetBrains Mono.
- Brand Mark: Pure SVG LedgerSeal 32-point compass rose geometry.
- Corner Chrome: Active live timecode HUD (`PURSER_DEMO.MP4`, timecode `00:00:00:00`).

## 3. Real Product Footage and Provenance
- W1: Real Next.js landing page at `localhost:3000` (Hero, ledger seal, stats).
- W3: Operational Ledger report (`localhost:3000/app`) with Muster passed badge.
- W4: Ticket dossier with rule R1 proration arithmetic.
- W8: Offline Verifier (`localhost:3000/verify`) with P1, P9, and P11 invariant verification.
- D04 Live Replay: Terminal log replay from `video/terminal/d04.jsonl` matching `evidence/drills/d04_live.json`.
- Partner Platforms: Explicit coverage of neatlogs (WORKFLOW root, witness statement), Entire (provenance chain), and cfo.ai (unit economics).

## 4. Verification Gates
- No em dashes in copy, code, or documentation.
- No invented figures: all numbers backed by committed evidence files (`SOURCES.md`).
- Video render artifacts gitignored.
