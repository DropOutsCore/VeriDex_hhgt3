import React from 'react';
import {
  Scan,
  Fingerprint,
  Globe,
  GitCompare,
  Gauge,
  Binary,
  Link2,
  ShieldCheck,
  Check,
} from 'lucide-react';

export const PIPELINE_CHEVRONS = [
  { id: 1, key: 'SCAN', label: '1. SCAN', icon: Scan, anim: 'group-hover:scale-110 group-hover:rotate-6' },
  { id: 2, key: 'SIGNATURE', label: '2. SIGNATURE', icon: Fingerprint, anim: 'group-hover:scale-110 group-hover:-translate-y-0.5' },
  { id: 3, key: 'TRACE', label: '3. REVERSE TRACE', icon: Globe, anim: 'group-hover:rotate-45 duration-500' },
  { id: 4, key: 'CORRELATION', label: '4. CORRELATION', icon: GitCompare, anim: 'group-hover:scale-110 group-hover:rotate-12' },
  { id: 5, key: 'EVIDENCE', label: '5. SCORE', icon: Gauge, anim: 'group-hover:-rotate-12 group-hover:scale-110' },
  { id: 6, key: 'FINGERPRINT', label: '6. FINGERPRINT', icon: Binary, anim: 'group-hover:scale-110 group-hover:translate-x-0.5' },
  { id: 7, key: 'CHAIN', label: '7. BLOCKCHAIN', icon: Link2, anim: 'group-hover:rotate-45 group-hover:scale-110' },
  { id: 8, key: 'PROOF', label: '8. INTEGRITY', icon: ShieldCheck, anim: 'group-hover:scale-115' },
];

const STATUS_MAP = {
  SCANNING: { stage: 1 },
  ENCODING: { stage: 2 },
  SEARCHING: { stage: 3 },
  DISCOVERING: { stage: 3 },
  VERIFYING: { stage: 4 },
  FINGERPRINTING: { stage: 6 },
  ANCHORING: { stage: 7 },
  CONFIRMING: { stage: 7 },
};

export default function PipelineChevronNav({
  currentStatus,
  activeStageId,
  onSelectStage,
  steps = [],
  isTampered = false,
}) {
  const isLogged = (key) => steps.some((s) => s.step?.includes(key));

  const getStageState = (stageId) => {
    if (currentStatus === 'FAILED' && activeStageId === stageId) return 'FAILED';
    if (isTampered && stageId === 8) return 'TAMPERED';
    if (currentStatus === 'VERIFIED') return 'COMPLETED';

    const running = STATUS_MAP[currentStatus];
    if (running && running.stage === stageId) return 'ACTIVE';

    if (stageId === 1 && (isLogged('SCANNING') || isLogged('ENCODING') || steps.length > 0)) return 'COMPLETED';
    if (stageId === 2 && (isLogged('ENCODING') || isLogged('SEARCHING'))) return 'COMPLETED';
    if (stageId === 3 && (isLogged('SEARCHING') || isLogged('DISCOVERING') || isLogged('VERIFYING'))) return 'COMPLETED';
    if (stageId === 4 && (isLogged('VERIFYING') || isLogged('FINGERPRINTING'))) return 'COMPLETED';
    if (stageId === 5 && (isLogged('VERIFYING') || isLogged('FINGERPRINTING'))) return 'COMPLETED';
    if (stageId === 6 && (isLogged('FINGERPRINTING') || isLogged('ANCHORING'))) return 'COMPLETED';
    if (stageId === 7 && (isLogged('ANCHORING') || isLogged('CONFIRMING') || isLogged('VERIFIED'))) return 'COMPLETED';
    if (stageId === 8 && (currentStatus === 'VERIFIED' || isLogged('VERIFIED'))) return 'COMPLETED';

    return activeStageId === stageId ? 'ACTIVE' : 'UPCOMING';
  };

  return (
    <div className="w-full bg-[#0B0B0E] border-b border-[#1E1E24] px-4 py-2 flex flex-col gap-1.5 shrink-0 select-none">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold tracking-widest text-zinc-400 uppercase font-mono">
          PIPELINE STAGE NAVIGATION
        </span>
        <div className="flex items-center gap-3 text-[10px] font-mono text-zinc-400">
          <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" /> COMPLETED</span>
          <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8]" /> ACTIVE VIEW</span>
          <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#27272A]" /> PENDING</span>
        </div>
      </div>

      {/* Chevron Stepper Grid */}
      <div className="flex items-center w-full overflow-x-auto scrollbar-none pt-0.5 pb-0.5 gap-1">
        {PIPELINE_CHEVRONS.map((stage) => {
          const state = getStageState(stage.id);
          const isActiveView = activeStageId === stage.id;
          const StageIcon = stage.icon;

          let bgClasses = 'bg-gradient-to-b from-[#181820] to-[#101015] text-zinc-400 border border-white/[0.06] hover:border-white/20';
          if (state === 'COMPLETED') {
            bgClasses = 'bg-gradient-to-b from-[#059669] to-[#047857] text-white border border-[#10B981]/50 shadow-[0_2px_8px_rgba(5,150,105,0.3)]';
          } else if (state === 'ACTIVE' || isActiveView) {
            bgClasses = 'bg-gradient-to-b from-[#0284C7] to-[#0369A1] text-white font-bold border border-[#38BDF8]/60 shadow-[0_2px_10px_rgba(2,132,199,0.35)]';
          } else if (state === 'TAMPERED' || state === 'FAILED') {
            bgClasses = 'bg-gradient-to-b from-[#DC2626] to-[#B91C1C] text-white font-bold border border-[#F87171]/60 shadow-[0_2px_10px_rgba(220,38,38,0.35)]';
          }

          return (
            <button
              key={stage.id}
              onClick={() => onSelectStage(stage.id)}
              className={`group relative ${bgClasses} flex-1 min-w-[125px] py-1.5 px-2 rounded-lg flex items-center justify-center transition-all duration-200 cursor-pointer active:scale-95 active:translate-y-0.5`}
              title={`Jump to ${stage.label}`}
            >
              <span className="truncate flex items-center gap-1.5 text-xs font-mono">
                {state === 'COMPLETED' ? (
                  <Check className="w-3.5 h-3.5 shrink-0 text-white stroke-[2.5]" />
                ) : (
                  <StageIcon className={`w-3.5 h-3.5 shrink-0 transition-transform duration-200 ${stage.anim}`} />
                )}
                <span className="font-semibold">{stage.label}</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

