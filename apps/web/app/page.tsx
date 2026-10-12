import React from "react";
import Image from "next/image";
import Link from "next/link";
import { CapsuleNav } from "@/components/nav/CapsuleNav";
import { LedgerSeal } from "@/components/brand/LedgerSeal";

export default function HomePage() {
  const navItems = [
    { href: "/", label: "Overview" },
    { href: "/app", label: "The Report" },
    { href: "/app/queue", label: "Live Queue" },
    { href: "/app/reckoning", label: "Storm Drills" },
    { href: "/verify", label: "Verify Batch" },
  ];

  return (
    <main className="min-h-screen">
      <CapsuleNav items={navItems} />

      {/* 1. Hero */}
      <section className="max-w-[1240px] mx-auto pt-28 pb-16 px-6 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-7">
          <div className="font-mono text-xs uppercase tracking-widest text-[--color-brass] mb-3">
            NEATHACK 2026 · REFUND OPERATIONS
          </div>
          <h1 className="font-serif text-5xl md:text-7xl leading-[1.05] tracking-tight mb-5">
            Refunds, settled <em className="italic text-[--color-signal]">once</em>.
          </h1>
          <p className="text-lg text-[--color-ink-2] max-w-xl mb-8 leading-relaxed">
            Purser clears your refund queue overnight. If it crashes at ticket 73, it still knows exactly who was paid. Exactly-once money semantics with mathematical proof.
          </p>
          <div className="flex items-center gap-4">
            <Link
              href="/app"
              className="px-6 py-3.5 bg-[--color-ink] text-[--color-paper] rounded-[12px] font-medium text-sm shadow-[0_0_0_1px_var(--color-signal),0_0_24px_var(--color-signal-glow)] hover:bg-black transition-all"
            >
              Open the ledger
            </Link>
            <Link
              href="/app/reckoning"
              className="px-5 py-3.5 border border-[--color-paper-3] bg-[--color-paper-2] text-[--color-ink] rounded-[12px] font-medium text-sm hover:bg-[--color-paper-3] transition-all"
            >
              Watch it survive a crash
            </Link>
          </div>
        </div>

        <div className="lg:col-span-5 relative">
          <div className="relative rounded-2xl overflow-hidden border border-[--color-paper-3] shadow-xl">
            <div className="aspect-[3/2] relative bg-[--color-paper-2]">
              <Image
                src="/images/hero_ledger.jpg"
                alt="Purser Ship Ledger Desk"
                fill
                priority
                className="object-cover"
              />
            </div>
            <div className="absolute -bottom-6 -left-6 z-10">
              <LedgerSeal className="w-32 h-32 md:w-36 md:h-36" />
            </div>
          </div>
        </div>
      </section>

      {/* Under-fold live strip */}
      <div className="max-w-[1240px] mx-auto px-6 mb-16">
        <div className="flex flex-wrap items-center justify-between gap-4 py-3.5 px-6 rounded-[14px] bg-[--color-paper-2] border border-[--color-paper-3] font-mono text-xs text-[--color-ink-2]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[--color-signal] animate-pulse" />
            <span>BATCH B-0412</span>
          </div>
          <div>138 TICKETS EVALUATED</div>
          <div>$4,212.50 REFUNDED</div>
          <div className="text-[--color-settled] font-semibold">MUSTER PASSED</div>
          <div className="text-[--color-settled] font-semibold">0 DUPLICATE CHARGES</div>
        </div>
      </div>

      {/* 2. The 2 a.m. problem */}
      <section className="max-w-[1240px] mx-auto px-6 py-12 border-t border-[--color-paper-3] grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        <div className="md:col-span-4">
          <h2 className="font-serif text-3xl md:text-4xl">The 2 a.m. problem</h2>
        </div>
        <div className="md:col-span-8 text-[--color-ink-2] text-base leading-relaxed space-y-4">
          <p>
            Every founder knows the sinking feeling of waking up to a crashed batch runner. The worker was halfway through refunding thirty churned accounts when a transient container restart killed the process.
          </p>
          <p>
            Did ticket 14 get paid before the kill? Does your database know? If you re-run the script, will your payment processor charge the balance twice? Standard LLM wrappers offer zero isolation between agent reasoning and monetary execution.
          </p>
          <blockquote className="font-serif italic text-xl text-[--color-ink] pl-4 border-l-2 border-[--color-signal] py-1">
            "The trace is a witness. The ledger is the judge."
          </blockquote>
        </div>
      </section>

      {/* 3. Five-step Voyage */}
      <section className="max-w-[1240px] mx-auto px-6 py-12 border-t border-[--color-paper-3]">
        <h2 className="font-serif text-3xl md:text-4xl mb-8">How Purser works</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[
            { step: "01", name: "Read", desc: "Agent reads ticket and context via read-only tools" },
            { step: "02", name: "Match", desc: "Correlates payments and status page incidents" },
            { step: "03", name: "Decide", desc: "Deterministic Kernel computes amount from policy" },
            { step: "04", name: "Pay Once", desc: "Write-ahead WAL and Dead Reckoning precheck" },
            { step: "05", name: "Muster", desc: "Close-out joins processor refunds with Log truth" }
          ].map((item) => (
            <div key={item.step} className="p-5 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
              <div className="font-mono text-xs text-[--color-brass] mb-2">{item.step}</div>
              <h3 className="font-medium text-base mb-1">{item.name}</h3>
              <p className="text-xs text-[--color-ink-3] leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Built on Partners */}
      <section className="max-w-[1240px] mx-auto px-6 py-12 border-t border-[--color-paper-3] grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        <div className="p-6 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
          <div className="font-mono text-sm font-semibold mb-1">NeatLogs</div>
          <p className="text-xs text-[--color-ink-3]">Full workflow tracing and out-of-band Witness Statements</p>
        </div>
        <div className="p-6 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
          <div className="font-mono text-sm font-semibold mb-1">Entire</div>
          <p className="text-xs text-[--color-ink-3]">Rule provenance back to founder session checkpoints</p>
        </div>
        <div className="p-6 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
          <div className="font-mono text-sm font-semibold mb-1">Dodo Payments</div>
          <p className="text-xs text-[--color-ink-3]">Test-mode payment processor with Dead Reckoning</p>
        </div>
        <div className="p-6 rounded-xl bg-[--color-paper-2] border border-[--color-paper-3]">
          <div className="font-mono text-sm font-semibold mb-1">cfo.ai</div>
          <p className="text-xs text-[--color-ink-3]">Financial model with measured unit economics</p>
        </div>
      </section>
    </main>
  );
}
