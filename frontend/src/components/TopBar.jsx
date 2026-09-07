import React from 'react';
import { Shield, Play, Download } from 'lucide-react';

export default function TopBar({
  isHealthy,
  sessionId,
  activeStatus,
  onRunDemo,
  isLoading,
  onOpenSummary,
  hasPipelineResult,
}) {
  return (
    <header className="px-5 py-2.5 flex items-center justify-between border-b border-[#222228] bg-[#0A0A0D] text-white shrink-0 select-none">
      {/* 1. Left Brand & Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-[#38BDF8]/10 border border-[#38BDF8]/30 flex items-center justify-center text-[#38BDF8] transition-colors duration-200">
          <Shield className="w-4 h-4" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="font-extrabold text-base tracking-widest text-white font-mono">
            VERIDEX
          </span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[#38BDF8]/10 border border-[#38BDF8]/30 text-[#38BDF8]">
            v2.6
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
          <span className="text-zinc-500 font-semibold uppercase">STATUS:</span>
          <span className="text-[#10B981] font-bold flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
            SECURE
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Always-visible Export Dossier Button */}
          <button
            onClick={hasPipelineResult ? onOpenSummary : undefined}
            disabled={!hasPipelineResult}
            className={`px-3.5 py-1.5 rounded-lg text-[11px] font-bold border transition-all duration-200 flex items-center gap-1.5 ${
              hasPipelineResult
                ? 'bg-[#181820] hover:bg-[#22222E] text-[#38BDF8] border-[#38BDF8]/40 hover:border-[#38BDF8] cursor-pointer hover:scale-[1.02]'
                : 'bg-[#141418] text-zinc-600 border-[#222226] cursor-not-allowed opacity-50'
            }`}
            title={hasPipelineResult ? 'Export Evidence Verification Dossier' : 'Run audit first to export dossier'}
          >
            <Download className={`w-3.5 h-3.5 ${hasPipelineResult ? 'text-[#38BDF8]' : 'text-zinc-600'}`} />
            <span>EXPORT DOSSIER</span>
          </button>

          <button
            onClick={onRunDemo}
            disabled={isLoading}
            className="px-4 py-1.5 rounded-lg bg-[#D97746] hover:bg-[#E08352] text-black text-[11px] font-extrabold border border-[#D97746] transition-all duration-200 flex items-center gap-1.5 disabled:opacity-50 hover:scale-[1.02] cursor-pointer"
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

