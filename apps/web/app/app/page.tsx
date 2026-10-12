import React from "react";
import Link from "next/link";
import { CapsuleNav } from "@/components/nav/CapsuleNav";

export default function ReportPage() {
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
              BATCH REPORT · BATCH B-0412
            </div>
            <h1 className="font-serif text-4xl md:text-5xl">The Operational Ledger</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3.5 py-1.5 rounded-full bg-[rgba(31,122,77,0.12)] text-[--color-settled] font-mono text-xs font-semibold">
              MUSTER PASSED
            </span>
            <span className="px-3.5 py-1.5 rounded-full bg-[--color-paper-2] border border-[--color-paper-3] font-mono text-xs text-[--color-ink-2]">
              OPERATOR: READ-ONLY
            </span>
          </div>
        </div>

        {/* Metric cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="p-5 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
            <div className="font-mono text-xs text-[--color-ink-3] uppercase mb-1">Total Evaluated</div>
            <div className="font-mono text-3xl font-bold">138</div>
          </div>
          <div className="p-5 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
            <div className="font-mono text-xs text-[--color-ink-3] uppercase mb-1">Settled Refunds</div>
            <div className="font-mono text-3xl font-bold">$4,212.50</div>
          </div>
          <div className="p-5 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
            <div className="font-mono text-xs text-[--color-ink-3] uppercase mb-1">Duplicate Refunds</div>
            <div className="font-mono text-3xl font-bold text-[--color-settled]">0</div>
          </div>
          <div className="p-5 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
            <div className="font-mono text-xs text-[--color-ink-3] uppercase mb-1">Escalations</div>
            <div className="font-mono text-3xl font-bold text-[--color-brass]">1</div>
          </div>
        </div>

        {/* Live Ledger Table */}
        <div className="rounded-xl border border-[--color-paper-3] bg-[--color-paper-2] overflow-hidden">
          <div className="px-6 py-4 border-b border-[--color-paper-3] flex items-center justify-between">
            <h2 className="font-medium text-base">Settled Actions in Batch</h2>
            <Link href="/verify" className="text-xs font-mono text-[--color-signal] hover:underline">
              Verify Batch Manifest &rarr;
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm font-mono">
              <thead className="bg-[rgba(230,221,203,0.4)] text-[--color-ink-3] text-xs uppercase border-b border-[--color-paper-3]">
                <tr>
                  <th className="py-3 px-4">Ticket</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Rule</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Processor Ref</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[--color-paper-3]">
                <tr>
                  <td className="py-3 px-4 text-[--color-signal]">tkt_seed_001</td>
                  <td className="py-3 px-4">test_customer_1@example.com</td>
                  <td className="py-3 px-4">R1_full_within_14_days</td>
                  <td className="py-3 px-4">$28.98</td>
                  <td className="py-3 px-4">ref_0NpaM1zsPnunlGWyjXVD1</td>
                  <td className="py-3 px-4 text-[--color-settled] font-semibold">SETTLED</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 text-[--color-signal]">tkt_seed_002</td>
                  <td className="py-3 px-4">jordan_lee@example.com</td>
                  <td className="py-3 px-4">R2_prorata_annual_cancel</td>
                  <td className="py-3 px-4">$24.98</td>
                  <td className="py-3 px-4">ref_0NpaO6hD0oppZRCVw7F8N</td>
                  <td className="py-3 px-4 text-[--color-settled] font-semibold">SETTLED</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 text-[--color-signal]">tkt_seed_004</td>
                  <td className="py-3 px-4">test_customer_1@example.com</td>
                  <td className="py-3 px-4">R4_duplicate_charge</td>
                  <td className="py-3 px-4">$28.98</td>
                  <td className="py-3 px-4">ref_0NpaT5FHGnoaXcjRj2iHC</td>
                  <td className="py-3 px-4 text-[--color-settled] font-semibold">SETTLED</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 text-[--color-signal]">tkt_seed_003</td>
                  <td className="py-3 px-4">attacker@suspicious.net</td>
                  <td className="py-3 px-4">R6_chargeback_risk_escalate</td>
                  <td className="py-3 px-4">$0.00</td>
                  <td className="py-3 px-4">Blocked</td>
                  <td className="py-3 px-4 text-[--color-alarm] font-semibold">ESCALATED</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
