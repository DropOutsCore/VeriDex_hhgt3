import React from 'react';
import { Shield, Play, Download, Activity, Database, CheckCircle2, User } from 'lucide-react';

export default function TopBar({
  isHealthy,
  sessionId,
  activeStatus,
  onRunDemo,
  isLoading,
  onOpenSummary,
  hasPipelineResult,
}) {
  const isVerified = activeStatus === 'VERIFIED';
  const isFailed = activeStatus === 'FAILED';
  const isRunning = !['IDLE', 'VERIFIED', 'FAILED'].includes(activeStatus);

  return (
    <header className="px-5 py-2.5 flex items-center justify-between border-b border-[#222228] bg-[#0A0A0D] text-white shrink-0 select-none">
      {/* 1. Left Brand & Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-[#0284C7]/15 border border-[#38BDF8]/40 flex items-center justify-center text-[#38BDF8] shadow-[0_0_12px_rgba(56,189,248,0.25)]">
          <Shield className="w-4 h-4" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="font-extrabold text-base tracking-widest text-white font-mono">
            VERIDEX
          </span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[#38BDF8]/10 border border-[#38BDF8]/30 text-[#38BDF8]">
            ENGINE v2.6
          </span>
        </div>
      </div>

      {/* 2. Center Case ID Badge */}
      <div className="hidden md:flex items-center gap-2 px-4 py-1.5 rounded-lg bg-[#141419] border border-[#27272A] text-xs font-mono">
        <span className="text-zinc-500 font-medium uppercase tracking-wider">Case ID:</span>
        <span className="text-white font-bold tracking-wide">{sessionId || 'VX-2026-1102-ALPHA'}</span>
      </div>

      {/* 3. Right Network Status & Operations */}
      <div className="flex items-center gap-3 text-xs font-mono">
        <div className="hidden lg:flex items-center gap-2 text-zinc-400 text-[11px] border-r border-[#27272A] pr-3">
          <span className="text-zinc-500 font-semibold uppercase">NETWORK STATUS:</span>
          <span className="text-[#10B981] font-bold flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
            SECURE
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {hasPipelineResult && (
            <button
              onClick={onOpenSummary}
              className="px-3 py-1.5 rounded-lg bg-[#181820] hover:bg-[#22222D] text-zinc-200 text-[11px] font-bold border border-[#27272A] hover:border-zinc-500 transition-all duration-200 flex items-center gap-1.5"
              title="Export Evidence Verification Dossier"
            >
              <Download className="w-3.5 h-3.5 text-[#38BDF8]" />
              <span>Dossier</span>
            </button>
          )}

          <button
            onClick={onRunDemo}
            disabled={isLoading}
            className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-[#D97746] to-[#F08B57] hover:brightness-110 text-black text-[11px] font-extrabold border border-[#F08B57] shadow-[0_0_15px_rgba(217,119,70,0.3)] transition-all duration-200 flex items-center gap-1.5 disabled:opacity-50"
            title="Execute Full Forensic Audit"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isLoading ? 'ANALYZING...' : 'RUN AUDIT'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
