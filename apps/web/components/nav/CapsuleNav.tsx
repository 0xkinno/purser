"use client";

import React from "react";
import { motion, useScroll, useTransform } from "motion/react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function CapsuleNav({
  items,
}: {
  items: { href: string; label: string }[];
}) {
  const pathname = usePathname();
  const { scrollY } = useScroll();
  const h = useTransform(scrollY, [0, 120], [56, 48]);

  return (
    <motion.nav
      style={{ height: h }}
      className="fixed left-1/2 top-4 z-50 -translate-x-1/2 flex items-center gap-1 rounded-[14px] border border-[--color-paper-3] bg-[--color-paper-2]/85 px-2.5 backdrop-blur-md shadow-[inset_0_1px_0_rgba(255,255,255,0.6),0_4px_24px_rgba(0,0,0,0.04)]"
    >
      {items.map((it) => {
        const isActive = pathname === it.href;
        return (
          <Link
            key={it.href}
            href={it.href}
            className={`relative rounded-[10px] px-3.5 py-1.5 text-sm font-medium transition-colors ${
              isActive
                ? "text-[--color-paper]"
                : "text-[--color-ink-2] hover:text-[--color-ink]"
            }`}
          >
            {isActive && (
              <motion.span
                layoutId="nav-active"
                className="absolute inset-0 rounded-[10px] bg-[--color-ink] shadow-[0_0_0_1px_var(--color-signal),0_0_20px_var(--color-signal-glow)]"
              />
            )}
            <span className="relative z-10">{it.label}</span>
          </Link>
        );
      })}
    </motion.nav>
  );
}
