"use client";

import React from "react";
import { motion } from "motion/react";

export function LedgerSeal({ className }: { className?: string }) {
  return (
    <div className={`relative ${className || "w-36 h-36"}`}>
      <motion.svg
        viewBox="0 0 200 200"
        className="w-full h-full filter drop-shadow-[0_8px_16px_rgba(168,121,46,0.15)]"
        animate={{ rotate: 360 }}
        transition={{ duration: 120, repeat: Infinity, ease: "linear" }}
      >
        <circle cx="100" cy="100" r="92" fill="none" stroke="#A8792E" strokeWidth="2.5" />
        <circle cx="100" cy="100" r="82" fill="none" stroke="#A8792E" strokeWidth="1" strokeDasharray="3 3" />
        <circle cx="100" cy="100" r="68" fill="none" stroke="#A8792E" strokeWidth="1" />
        
        {/* 32-point compass rose points */}
        <polygon points="100,20 106,85 100,95 94,85" fill="#A8792E" />
        <polygon points="100,180 106,115 100,105 94,115" fill="#A8792E" opacity="0.8" />
        <polygon points="20,100 85,106 95,100 85,94" fill="#A8792E" />
        <polygon points="180,100 115,106 105,100 115,94" fill="#A8792E" opacity="0.8" />

        {/* Diagonal points */}
        <polygon points="43,43 88,92 92,88" fill="#A8792E" opacity="0.6" />
        <polygon points="157,43 112,88 108,92" fill="#A8792E" opacity="0.6" />
        <polygon points="43,157 88,108 92,112" fill="#A8792E" opacity="0.6" />
        <polygon points="157,157 112,112 108,108" fill="#A8792E" opacity="0.6" />

        <circle cx="100" cy="100" r="10" fill="#A8792E" />
      </motion.svg>
    </div>
  );
}
