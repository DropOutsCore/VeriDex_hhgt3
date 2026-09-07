import React from 'react';
import {
  Scan,
  Fingerprint,
  Search,
  GitCompare,
  BarChart3,
  FileCode,
  Lock,
  ShieldCheck,
  CheckCircle2,
  Clock,
  AlertTriangle,
} from 'lucide-react';

export const PIPELINE_STAGES = [
  { id: 1, key: 'SCAN',        label: 'Face Scan',      icon: Scan,        desc: 'YuNet Detection'   },
  { id: 2, key: 'SIGNATURE',   label: 'Signature',      icon: Fingerprint, desc: 'SFace 128-D'       },
  { id: 3, key: 'TRACE',       label: 'Reverse Trace',  icon: Search,      desc: 'Google Lens'       },
  { id: 4, key: 'CORRELATION', label: 'Correlation',    icon: GitCompare,  desc: 'Biometric + pHash' },
  { id: 5, key: 'EVIDENCE',    label: 'Evidence Score', icon: BarChart3,   desc: 'Multi-Signal'      },
  { id: 6, key: 'FINGERPRINT', label: 'Fingerprint',    icon: FileCode,    desc: 'RFC 8785 SHA-256'  },
  { id: 7, key: 'CHAIN',       label: 'Ledger Anchor',  icon: Lock,        desc: 'Polygon Amoy'      },
  { id: 8, key: 'PROOF',       label: 'Integrity',      icon: ShieldCheck, desc: 'Zero-Trust Audit'  },
];

const STATUS_MAP = {
  SCANNING:      { stage: 1, label: 'RUNNING' },
  ENCODING:      { stage: 2, label: 'RUNNING' },
  SEARCHING:     { stage: 3, label: 'RUNNING' },
  DISCOVERING:   { stage: 3, label: 'RUNNING' },
  VERIFYING:     { stage: 4, label: 'RUNNING' },
  FINGERPRINTING:{ stage: 6, label: 'RUNNING' },
  ANCHORING:     { stage: 7, label: 'RUNNING' },
  CONFIRMING:    { stage: 7, label: 'RUNNING' },
};

export default function PipelineRail({
  currentStatus,
  activeStageId,
  onSelectStage,
  steps = [],
  isTampered = false,
}) {
  const isLogged = (key) => steps.some((s) => s.step?.includes(key));

  const getState = (stage) => {
    if (currentStatus === 'FAILED' && activeStageId === stage.id) return 'FAILED';
    if (isTampered && stage.id === 8) return 'TAMPERED';
    if (currentStatus === 'VERIFIED') return 'COMPLETE';

    const runningInfo = STATUS_MAP[currentStatus];
    if (runningInfo && runningInfo.stage === stage.id) return 'RUNNING';

    if (stage.id === 1 && (isLogged('SCANNING') || isLogged('ENCODING') || steps.length > 0)) return 'COMPLETE';
    if (stage.id === 2 && (isLogged('ENCODING') || isLogged('SEARCHING'))) return 'COMPLETE';
    if (stage.id === 3 && (isLogged('SEARCHING') || isLogged('DISCOVERING') || isLogged('VERIFYING'))) return 'COMPLETE';
    if (stage.id === 4 && (isLogged('VERIFYING') || isLogged('FINGERPRINTING'))) return 'COMPLETE';
    if (stage.id === 5 && (isLogged('VERIFYING') || isLogged('FINGERPRINTING'))) return 'COMPLETE';
    if (stage.id === 6 && (isLogged('FINGERPRINTING') || isLogged('ANCHORING'))) return 'COMPLETE';
    if (stage.id === 7 && (isLogged('ANCHORING') || isLogged('CONFIRMING') || isLogged('VERIFIED'))) return 'COMPLETE';
    if (stage.id === 8 && (currentStatus === 'VERIFIED' || isLogged('VERIFIED'))) return 'COMPLETE';

    return currentStatus === 'IDLE' && stage.id === 1 ? 'READY' : 'IDLE';
  };

  const getStatusBadge = (state) => {
    switch (state) {
      case 'COMPLETE':
        return (
          <span className="flex items-center gap-1 text-[10px] font-semibold text-[#4ADE80]">
            <CheckCircle2 className="w-3 h-3" />
            <span>DONE</span>
          </span>
        );
      case 'RUNNING':
        return (
          <span className="flex items-center gap-1 text-[10px] font-semibold text-[#D97746] animate-pulse">
            <Clock className="w-3 h-3" />
            <span>LIVE</span>
          </span>
        );
      case 'FAILED':
      case 'TAMPERED':
        return (
          <span className="flex items-center gap-1 text-[10px] font-semibold text-[#F87171]">
            <AlertTriangle className="w-3 h-3" />
            <span>ALERT</span>
          </span>
        );
      case 'READY':
        return (
          <span className="text-[10px] font-medium text-zinc-400">
            READY
          </span>
        );
      default:
        return (
          <span className="text-[10px] text-zinc-600">
            ---
          </span>
        );
    }
  };

  return (
    <aside className="w-64 bg-[#0A0A0D] border-r border-[#222226] flex flex-col h-full shrink-0 overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-[#222226]">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] font-semibold tracking-wider text-zinc-500 uppercase">
            Investigation Flow
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-[#D97746] font-semibold">
            8 STAGES
          </span>
        </div>
        <div className="text-sm font-bold text-white tracking-wide">
          Forensic Pipeline
        </div>
      </div>

      {/* Stages List */}
      <div className="p-3 flex-1 space-y-1.5 overflow-y-auto">
        {PIPELINE_STAGES.map((stage) => {
          const state = getState(stage);
          const isActive = activeStageId === stage.id;
          const StageIcon = stage.icon;

          return (
            <button
              key={stage.id}
              onClick={() => onSelectStage(stage.id)}
              className={`w-full text-left p-3 rounded-xl border transition-all duration-150 flex items-center justify-between gap-3 ${
                isActive
                  ? 'bg-[#18181D] border-[#D97746]/50 shadow-sm'
                  : 'bg-[#111114]/80 border-[#222226] hover:bg-[#16161B] hover:border-[#2D2D35]'
              }`}
            >
              <div className="flex items-center gap-3 min-w-0">
                {/* Number Pill / Indicator */}
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                  isActive
                    ? 'bg-[#D97746]/15 text-[#D97746] border border-[#D97746]/30'
                    : 'bg-white/5 text-zinc-400 border border-white/5'
                }`}>
                  {String(stage.id).padStart(2, '0')}
                </div>

                <div className="min-w-0">
                  <div className={`text-xs font-semibold truncate ${isActive ? 'text-white' : 'text-zinc-300'}`}>
                    {stage.label}
                  </div>
                  <div className="text-[10px] text-zinc-500 truncate">
                    {stage.desc}
                  </div>
                </div>
              </div>

              <div className="shrink-0">
                {getStatusBadge(state)}
              </div>
            </button>
          );
        })}
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-[#222226] bg-[#0C0C0F]">
        <div className="text-[10px] font-semibold tracking-wider text-zinc-500 uppercase mb-2">
          Environment
        </div>
        <div className="space-y-1.5 text-[11px] text-zinc-400">
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Engine</span>
            <span className="text-zinc-300 font-medium">YuNet + SFace</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Hash Standard</span>
            <span className="text-zinc-300 font-medium">RFC 8785 SHA-256</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Chain Network</span>
            <span className="text-[#D97746] font-medium">Amoy 80002</span>
          </div>
        </div>

        <div className="mt-3 pt-2.5 border-t border-[#222226] text-center">
          <span className="text-[10px] text-zinc-500 font-medium">
            Made by <span className="text-[#D97746] font-semibold">Team Dropouts</span>
          </span>
        </div>
      </div>
    </aside>
  );
}
