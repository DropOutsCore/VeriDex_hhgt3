import React from 'react';
import { Play, Download } from 'lucide-react';
import VeriDexLogo from './VeriDexLogo';

export default function TopBar({
  isHealthy,
  sessionId,
  activeStatus,
  onRunDemo,
  isLoading,
  onOpenSummary,
  hasPipelineResult,
}) {
  const handleExportClick = () => {
    if (hasPipelineResult) {
      onOpenSummary();
    } else {
      onRunDemo();
    }
  };

  return (
    <header className="px-5 py-2.5 flex items-center justify-between border-b border-[#222228] bg-[#0A0A0D] text-white shrink-0 select-none">
      {/* 1. Left Brand & Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-b from-[#1C1C24] to-[#101015] border border-white/10 hover:border-[#38BDF8]/40 shadow-inner flex items-center justify-center text-[#38BDF8] transition-all duration-200 cursor-pointer hover:scale-105 group">
          <VeriDexLogo size={20} />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="font-extrabold text-base tracking-widest text-white font-mono">
            VERIDEX
          </span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-[#38BDF8]/10 border border-[#38BDF8]/30 text-[#38BDF8] font-mono">
            v2.6
          </span>
        </div>
      </div>

      {/* 2. Center Case ID Badge */}
      <div className="hidden md:flex items-center gap-2 px-4 py-1.5 rounded-xl bg-gradient-to-b from-[#16161D] to-[#0E0E14] border border-white/[0.08] text-xs font-mono shadow-inner">
        <span className="text-zinc-500 font-medium uppercase tracking-wider">Case ID:</span>
        <span className="text-white font-bold tracking-wide">{sessionId || 'VX-2026-1102-ALPHA'}</span>
      </div>

      {/* 3. Right Network Status & Operations */}
      <div className="flex items-center gap-3 text-xs font-mono">
        <div className="hidden lg:flex items-center gap-2 text-zinc-400 text-[11px] border-r border-[#27272A] pr-3">
          <span className="text-zinc-500 font-semibold uppercase">STATUS:</span>
          <span className="text-[#10B981] font-bold flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] shadow-[0_0_6px_#10B981]" />
            SECURE
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Tactile Export Dossier Button */}
          <button
            onClick={handleExportClick}
            disabled={isLoading}
            className={`group px-3.5 py-1.5 rounded-xl text-[11px] font-bold border transition-all duration-200 flex items-center gap-1.5 cursor-pointer active:scale-95 active:translate-y-0.5 ${
              hasPipelineResult
                ? 'bg-gradient-to-b from-[#1F1F2A] to-[#12121A] hover:from-[#262634] hover:to-[#171720] text-[#38BDF8] border-[#38BDF8]/50 shadow-[0_2px_8px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.08)]'
                : 'bg-gradient-to-b from-[#16161D] to-[#0E0E14] hover:from-[#1C1C24] hover:to-[#121218] text-zinc-300 border-white/10'
            }`}
            title="Export Evidence Verification Dossier"
          >
            <Download className="w-3.5 h-3.5 text-[#38BDF8] transition-transform duration-200 group-hover:translate-y-0.5" />
            <span>EXPORT DOSSIER</span>
          </button>

          {/* Tactile Run Audit Button */}
          <button
            onClick={onRunDemo}
            disabled={isLoading}
            className="group px-4 py-1.5 rounded-xl bg-gradient-to-b from-[#E28553] to-[#C86430] hover:from-[#EC9362] hover:to-[#D26E3A] text-black text-[11px] font-extrabold border border-[#FFAE80]/40 shadow-[0_2px_10px_rgba(217,119,70,0.35),inset_0_1px_0_rgba(255,255,255,0.25)] transition-all duration-200 flex items-center gap-1.5 disabled:opacity-50 active:scale-95 active:translate-y-0.5 cursor-pointer"
            title="Execute Full Forensic Audit"
          >
            <Play className="w-3.5 h-3.5 fill-current transition-transform duration-200 group-hover:translate-x-0.5 group-hover:scale-110" />
            <span>{isLoading ? 'ANALYZING...' : 'RUN AUDIT'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}


