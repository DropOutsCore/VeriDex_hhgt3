import React from 'react';
import { Database, Shield, Download, Sparkles, Activity } from 'lucide-react';

export default function TopBar({ 
  isHealthy, 
  sessionId, 
  activeStatus, 
  onRunDemo, 
  isLoading,
  onOpenSummary,
  hasPipelineResult 
}) {
  const statusLabel = {
    IDLE: 'STANDBY',
    SCANNING: 'SCANNING',
    ENCODING: 'ENCODING',
    SEARCHING: 'SEARCHING',
    DISCOVERING: 'DISCOVERING',
    VERIFYING: 'VERIFYING',
    FINGERPRINTING: 'FINGERPRINTING',
    ANCHORING: 'ANCHORING',
    CONFIRMING: 'CONFIRMING',
    VERIFIED: 'VERIFIED',
    FAILED: 'FAILED',
  }[activeStatus] || activeStatus;

  const isVerified = activeStatus === 'VERIFIED';
  const isFailed = activeStatus === 'FAILED';
  const isRunning = !['IDLE', 'VERIFIED', 'FAILED'].includes(activeStatus);

  return (
    <header className="px-5 py-3 flex items-center justify-between border-b border-[#222226] bg-[#0A0A0D]/90 backdrop-blur-md shrink-0">
      {/* Brand & Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-[#18181D] border border-[#2D2D35] flex items-center justify-center">
          <Shield className="w-4 h-4 text-[#D97746]" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm tracking-wider text-white">
              VERIDEX
            </span>
            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-zinc-400">
              FORENSICS
            </span>
          </div>
          <span className="text-[10px] tracking-wide text-zinc-500 font-medium hidden sm:inline">
            Zero-Trust Visual Verification Engine
          </span>
        </div>
      </div>

      {/* Center Metadata & Status Badges */}
      <div className="flex items-center gap-2 text-xs">
        {/* Health */}
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium border ${
          isHealthy 
            ? 'text-[#4ADE80] bg-[#4ADE80]/10 border-[#4ADE80]/25' 
            : 'text-[#F87171] bg-[#F87171]/10 border-[#F87171]/25'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-[#4ADE80]' : 'bg-[#F87171]'}`} />
          {isHealthy ? 'API ONLINE' : 'API OFFLINE'}
        </div>

        {/* Case ID */}
        <div className="hidden md:flex items-center gap-1 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-zinc-300 text-[11px] font-medium">
          <span className="text-zinc-500">CASE</span>
          <span className="text-[#D97746] font-semibold">{sessionId || 'VX-2026-0001'}</span>
        </div>

        {/* Network */}
        <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-zinc-400 text-[11px]">
          <Database className="w-3 h-3 text-zinc-500" />
          <span>Polygon Amoy</span>
        </div>

        {/* Pipeline Status */}
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold border ${
          isVerified 
            ? 'text-[#4ADE80] bg-[#4ADE80]/10 border-[#4ADE80]/25'
            : isFailed
            ? 'text-[#F87171] bg-[#F87171]/10 border-[#F87171]/25'
            : isRunning
            ? 'text-[#D97746] bg-[#D97746]/10 border-[#D97746]/30 animate-pulse'
            : 'text-zinc-400 bg-white/5 border-white/10'
        }`}>
          <Activity className="w-3 h-3" />
          <span>{statusLabel}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        {hasPipelineResult && (
          <button 
            onClick={onOpenSummary} 
            className="btn-secondary"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Dossier</span>
          </button>
        )}
        
        <button 
          onClick={onRunDemo} 
          disabled={isLoading} 
          className="btn-primary"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{isLoading ? 'Processing Pipeline...' : 'Run Audit'}</span>
        </button>
      </div>
    </header>
  );
}
