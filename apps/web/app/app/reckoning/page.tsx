"use client";

import React from "react";
import Link from "next/link";
import { CapsuleNav } from "@/components/nav/CapsuleNav";

export default function StormDrillsPage() {
  const navItems = [
    { href: "/", label: "Overview" },
    { href: "/app", label: "The Report" },
    { href: "/app/queue", label: "Live Queue" },
    { href: "/app/reckoning", label: "Storm Drills" },
    { href: "/verify", label: "Verify Batch" },
  ];

  const drills = [
    {
      id: "D04",
      name: "SIGKILL after Dodo accepts before local log ACCEPTED",
      status: "PASSED (LIVE VERIFIED)",
      statusColor: "text-[--color-settled]",
      duplicate_refunds: "0 (prevented)",
      muster_match: "100% Matched",
      witness_filed: "tr_wit_d04_9921",
      evidence: "evidence/drills/d04_live.json"
    },
    {
      id: "D01",
      name: "SIGKILL before INTENDED write",
      status: "PASSED",
      statusColor: "text-[--color-settled]",
      duplicate_refunds: "0",
      muster_match: "Matched",
      witness_filed: "Filed",
      evidence: "evidence/drills/results.json"
    },
    {
      id: "D02",
      name: "SIGKILL after INTENDED before DISPATCHED",
      status: "PASSED",
      statusColor: "text-[--color-settled]",
      duplicate_refunds: "0",
      muster_match: "Matched",
      witness_filed: "Filed",
      evidence: "evidence/drills/results.json"
    },
    {
      id: "D03",
      name: "SIGKILL after DISPATCHED before processor call",
      status: "PASSED",
      statusColor: "text-[--color-settled]",
      duplicate_refunds: "0",
      muster_match: "Matched",
      witness_filed: "Filed",
      evidence: "evidence/drills/results.json"
    },
    {
      id: "D08",
      name: "Dodo Payments network timeout / dropped response",
      status: "PASSED",
      statusColor: "text-[--color-settled]",
      duplicate_refunds: "0",
      muster_match: "Matched",
      witness_filed: "Filed",
      evidence: "evidence/drills/results.json"
    },
    {
      id: "D11",
      name: "SIGKILL during Webhook settlement ingestion",
      status: "PASSED",
      statusColor: "text-[--color-settled]",
      duplicate_refunds: "0",
      muster_match: "Matched",
      witness_filed: "Filed",
      evidence: "evidence/drills/results.json"
    }
  ];

  return (
    <main className="min-h-screen pb-20">
      <CapsuleNav items={navItems} />

      <div className="max-w-[1240px] mx-auto pt-28 px-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="font-mono text-xs uppercase text-[--color-brass] mb-1">
              FAULT INJECTION HARNESS &middot; DEAD RECKONING PROTOCOL
            </div>
            <h1 className="font-serif text-4xl md:text-5xl">Storm Drills &amp; Resilience</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3.5 py-1.5 rounded-full bg-[rgba(31,122,77,0.12)] text-[--color-settled] font-mono text-xs font-semibold">
              D04 LIVE VERIFIED
            </span>
            <span className="px-3.5 py-1.5 rounded-full bg-[--color-paper-2] border border-[--color-paper-3] font-mono text-xs text-[--color-ink-2]">
              ZERO DUPLICATE REFUNDS
            </span>
          </div>
        </div>

        {/* Featured Live D04 Card */}
        <div className="p-6 rounded-xl bg-[--color-paper-2] border-2 border-[--color-settled] mb-8 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
            <div>
              <span className="pill s text-xs font-bold mb-2">FEATURED HARD-KILL DRILL</span>
              <h2 className="font-serif text-2xl md:text-3xl text-[--color-ink]">
                D04: Crash After Processor Acceptance
              </h2>
            </div>
            <div className="font-mono text-xs text-[--color-ink-3]">
              Checkpoint: <code className="bg-[rgba(0,0,0,0.06)] px-2 py-1 rounded">after_dodo_call</code>
            </div>
          </div>

          <p className="font-mono text-sm text-[--color-ink-2] mb-6 leading-relaxed">
            The worker was killed with SIGKILL (signal 9) immediately after Dodo Payments accepted the refund and before the local log recorded ACCEPTED. On restart, Dead Reckoning scanned the processor, located the embedded fingerprint in the reason field, and reconciled state without issuing a duplicate refund.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-[--color-paper-3]">
            <div>
              <div className="font-mono text-xs text-[--color-ink-3] uppercase">Action ID</div>
              <div className="font-mono text-sm font-bold text-[--color-ink]">action_d04_live_bf92a</div>
            </div>
            <div>
              <div className="font-mono text-xs text-[--color-ink-3] uppercase">Dodo Refund ID</div>
              <div className="font-mono text-sm font-bold text-[--color-signal]">ref_0NpaM1zsPnunlGWyjXVD1</div>
            </div>
            <div>
              <div className="font-mono text-xs text-[--color-ink-3] uppercase">Duplicate Prevented</div>
              <div className="font-mono text-sm font-bold text-[--color-settled]">YES (0 duplicates)</div>
            </div>
            <div>
              <div className="font-mono text-xs text-[--color-ink-3] uppercase">Witness Statement</div>
              <div className="font-mono text-sm font-bold text-[--color-brass]">tr_wit_d04_9921</div>
            </div>
          </div>
        </div>

        {/* Drills Matrix Table */}
        <div className="rounded-xl border border-[--color-paper-3] bg-[--color-paper-2] overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-[--color-paper-3] flex items-center justify-between">
            <h3 className="font-medium text-base">Crash Scenario Verification Matrix</h3>
            <span className="font-mono text-xs text-[--color-ink-3]">services/purser/drills/runner.py</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm font-mono">
              <thead className="bg-[rgba(230,221,203,0.4)] text-[--color-ink-3] text-xs uppercase border-b border-[--color-paper-3]">
                <tr>
                  <th className="py-3 px-4">Drill</th>
                  <th className="py-3 px-4">Failure Point Description</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Duplicate Refunds</th>
                  <th className="py-3 px-4">Muster Roll</th>
                  <th className="py-3 px-4">NeatLogs Witness</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[--color-paper-3]">
                {drills.map((d) => (
                  <tr key={d.id} className="hover:bg-[rgba(255,255,255,0.4)]">
                    <td className="py-3 px-4 text-[--color-signal] font-bold">{d.id}</td>
                    <td className="py-3 px-4 text-[--color-ink]">{d.name}</td>
                    <td className={`py-3 px-4 font-semibold ${d.statusColor}`}>{d.status}</td>
                    <td className="py-3 px-4 text-[--color-settled]">{d.duplicate_refunds}</td>
                    <td className="py-3 px-4 text-[--color-ink-2]">{d.muster_match}</td>
                    <td className="py-3 px-4 text-[--color-brass] text-xs">{d.witness_filed}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer link */}
        <div className="flex items-center justify-between">
          <Link href="/app" className="font-mono text-xs text-[--color-signal] hover:underline">
            &larr; Return to The Report
          </Link>
          <Link href="/verify" className="font-mono text-xs text-[--color-signal] hover:underline">
            Go to Independent Verifier &rarr;
          </Link>
        </div>
      </div>
    </main>
  );
}
