"use client";

import React, { useState } from "react";
import Link from "next/link";
import { CapsuleNav } from "@/components/nav/CapsuleNav";

export default function ApprovalsPage() {
  const [approved, setApproved] = useState(false);

  const navItems = [
    { href: "/", label: "Overview" },
    { href: "/app", label: "The Report" },
    { href: "/app/queue", label: "Live Queue" },
    { href: "/app/reckoning", label: "Storm Drills" },
    { href: "/verify", label: "Verify Batch" },
  ];

  return (
    <main className="min-h-screen pb-20">
      <CapsuleNav items={navItems} />

      <div className="max-w-[1240px] mx-auto pt-28 px-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="font-mono text-xs uppercase text-[--color-brass] mb-1">
              SAFETY INVARIANT P5 &middot; OPERATOR GATE
            </div>
            <h1 className="font-serif text-4xl md:text-5xl">Founder Approvals</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3.5 py-1.5 rounded-full bg-[rgba(168,121,46,0.14)] text-[--color-brass] font-mono text-xs font-semibold">
              HUMAN IN THE LOOP REQUIRED
            </span>
          </div>
        </div>

        {/* Policy rule explanation card */}
        <div className="p-6 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3] mb-8">
          <div className="font-mono text-xs text-[--color-brass] uppercase font-bold mb-2">
            Non-Negotiable Constraint P5
          </div>
          <h2 className="font-serif text-2xl text-[--color-ink] mb-2">
            The Agent Can Never Approve Itself
          </h2>
          <p className="font-mono text-sm text-[--color-ink-2] leading-relaxed">
            Refunds exceeding $100.00, or tickets flagged with confidence drift, are quarantined until an authorized operator reviews the calculated arithmetic and signs the ledger entry.
          </p>
        </div>

        {/* Approval Ticket Card */}
        <div className="rounded-xl border border-[--color-paper-3] bg-[--color-paper-2] p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-[--color-paper-3]">
            <div>
              <div className="font-mono text-xs text-[--color-signal] font-bold">tkt_074</div>
              <div className="font-mono text-lg font-bold text-[--color-ink] mt-1">marcus.v@example.com</div>
              <div className="font-mono text-xs text-[--color-ink-3]">Payment ID: pay_0NpaL8qN19ybC &middot; Dodo Payments</div>
            </div>
            <div className="text-right">
              <div className="font-mono text-xs text-[--color-ink-3] uppercase">Requested Amount</div>
              <div className="font-mono text-3xl font-bold text-[--color-ink]">$150.00</div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-sm mb-6">
            <div className="p-4 rounded-lg bg-[--color-paper]">
              <div className="text-xs text-[--color-ink-3] uppercase mb-1">Governing Rule</div>
              <div className="font-semibold text-[--color-ink]">R5_manual_review_high_value</div>
            </div>
            <div className="p-4 rounded-lg bg-[--color-paper]">
              <div className="text-xs text-[--color-ink-3] uppercase mb-1">Audit Trail</div>
              <div className="font-semibold text-[--color-brass]">Prompt Checkpoint cp-0412</div>
            </div>
            <div className="p-4 rounded-lg bg-[--color-paper]">
              <div className="text-xs text-[--color-ink-3] uppercase mb-1">Status</div>
              <div className="font-semibold text-[--color-brass]">
                {approved ? "APPROVED &middot; DISPATCHED" : "AWAITING HUMAN SIGNATURE"}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end gap-4 pt-4 border-t border-[--color-paper-3]">
            {approved ? (
              <span className="pill s font-mono text-sm py-2 px-6">
                &check; Approved and Signed by Operator
              </span>
            ) : (
              <button
                onClick={() => setApproved(true)}
                className="pill font-mono text-sm py-2 px-6 bg-[--color-settled] text-white hover:opacity-90 cursor-pointer"
              >
                Approve &amp; Release Payout ($150.00)
              </button>
            )}
          </div>
        </div>

        {/* Footer link */}
        <div className="flex items-center justify-between">
          <Link href="/app" className="font-mono text-xs text-[--color-signal] hover:underline">
            &larr; Return to The Report
          </Link>
          <Link href="/app/queue" className="font-mono text-xs text-[--color-signal] hover:underline">
            View Live Queue &rarr;
          </Link>
        </div>
      </div>
    </main>
  );
}
