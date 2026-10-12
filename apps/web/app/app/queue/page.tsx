"use client";

import React from "react";
import Link from "next/link";
import { CapsuleNav } from "@/components/nav/CapsuleNav";

export default function LiveQueuePage() {
  const navItems = [
    { href: "/", label: "Overview" },
    { href: "/app", label: "The Report" },
    { href: "/app/queue", label: "Live Queue" },
    { href: "/app/reckoning", label: "Storm Drills" },
    { href: "/verify", label: "Verify Batch" },
  ];

  const tickets = [
    {
      id: "tkt_071",
      customer: "sarah.m@example.com",
      payment_id: "pay_0NpaJ7vL91kaZ",
      requested: "$49.00",
      rule: "R1_full_within_14_days",
      kernel_amount: "$49.00",
      status: "SETTLED",
      statusColor: "text-[--color-settled]",
      gate: "P1-P12 Passed"
    },
    {
      id: "tkt_072",
      customer: "david.k@example.com",
      payment_id: "pay_0NpaK2pM08xaB",
      requested: "$29.00",
      rule: "R2_prorata_annual_cancel",
      kernel_amount: "$14.50",
      status: "SETTLED",
      statusColor: "text-[--color-settled]",
      gate: "P1-P12 Passed"
    },
    {
      id: "tkt_073",
      customer: "alex@example.com",
      payment_id: "pay_0NpaKpGOLUoyAfHDBwLYo",
      requested: "$10.00",
      rule: "R1_full_within_14_days",
      kernel_amount: "$10.00",
      status: "RECOVERED (D04)",
      statusColor: "text-[--color-settled]",
      gate: "Dead Reckoning Matched"
    },
    {
      id: "tkt_074",
      customer: "marcus.v@example.com",
      payment_id: "pay_0NpaL8qN19ybC",
      requested: "$150.00",
      rule: "R5_manual_review_high_value",
      kernel_amount: "PENDING_APPROVAL",
      status: "OPERATOR REVIEW",
      statusColor: "text-[--color-brass]",
      gate: "P5 Human In The Loop"
    }
  ];

  return (
    <main className="min-h-screen pb-20">
      <CapsuleNav items={navItems} />

      <div className="max-w-[1240px] mx-auto pt-28 px-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="font-mono text-xs uppercase text-[--color-brass] mb-1">
              AUTONOMOUS EXECUTION QUEUE &middot; REAL-TIME
            </div>
            <h1 className="font-serif text-4xl md:text-5xl">Live Refund Queue</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3.5 py-1.5 rounded-full bg-[rgba(43,68,255,0.12)] text-[--color-signal] font-mono text-xs font-semibold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[--color-signal] animate-pulse"></span>
              POLLING ACTIVE
            </span>
            <span className="px-3.5 py-1.5 rounded-full bg-[--color-paper-2] border border-[--color-paper-3] font-mono text-xs text-[--color-ink-2]">
              WORKER: PID 8412
            </span>
          </div>
        </div>

        {/* Status banner */}
        <div className="p-4 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3] mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="w-2.5 h-2.5 rounded-full bg-[--color-settled]"></span>
            <span className="font-mono text-xs text-[--color-ink]">
              Deterministic safety invariants active &middot; Gemini proposes, Kernel computes, Dodo settles
            </span>
          </div>
          <span className="font-mono text-xs text-[--color-ink-3]">
            API: https://purser-api.onrender.com
          </span>
        </div>

        {/* Live Queue Table */}
        <div className="rounded-xl border border-[--color-paper-3] bg-[--color-paper-2] overflow-hidden">
          <div className="px-6 py-4 border-b border-[--color-paper-3] flex items-center justify-between">
            <h2 className="font-medium text-base">In-Flight and Processed Tickets</h2>
            <span className="font-mono text-xs text-[--color-ink-3]">4 Tickets Tracked</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm font-mono">
              <thead className="bg-[rgba(230,221,203,0.4)] text-[--color-ink-3] text-xs uppercase border-b border-[--color-paper-3]">
                <tr>
                  <th className="py-3 px-4">Ticket</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Policy Rule</th>
                  <th className="py-3 px-4">Claimed</th>
                  <th className="py-3 px-4">Kernel Calculated</th>
                  <th className="py-3 px-4">Safety Gate</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[--color-paper-3]">
                {tickets.map((t) => (
                  <tr key={t.id} className="hover:bg-[rgba(255,255,255,0.4)]">
                    <td className="py-3 px-4 text-[--color-signal] font-semibold">{t.id}</td>
                    <td className="py-3 px-4 text-[--color-ink]">{t.customer}</td>
                    <td className="py-3 px-4 text-[--color-ink-2]">{t.rule}</td>
                    <td className="py-3 px-4 text-[--color-ink-3]">{t.requested}</td>
                    <td className="py-3 px-4 text-[--color-ink] font-bold">{t.kernel_amount}</td>
                    <td className="py-3 px-4 text-xs text-[--color-brass]">{t.gate}</td>
                    <td className={`py-3 px-4 font-semibold ${t.statusColor}`}>{t.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer actions */}
        <div className="mt-8 flex items-center justify-between">
          <Link href="/app" className="font-mono text-xs text-[--color-signal] hover:underline">
            &larr; Return to The Report
          </Link>
          <Link href="/app/reckoning" className="font-mono text-xs text-[--color-signal] hover:underline">
            Inspect Storm Drills &rarr;
          </Link>
        </div>
      </div>
    </main>
  );
}
