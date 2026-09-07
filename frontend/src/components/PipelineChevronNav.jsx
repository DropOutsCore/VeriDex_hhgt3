import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

export const PIPELINE_CHEVRONS = [
  { id: 1, key: 'SCAN', label: '1. SCAN' },
  { id: 2, key: 'SIGNATURE', label: '2. FACE SIGNATURE' },
  { id: 3, key: 'TRACE', label: '3. REVERSE TRACE' },
  { id: 4, key: 'CORRELATION', label: '4. CANDIDATE CORRELATION' },
  { id: 5, key: 'EVIDENCE', label: '5. EVIDENCE SCORE' },
  { id: 6, key: 'FINGERPRINT', label: '6. VERIDEX FINGERPRINT' },
  { id: 7, key: 'CHAIN', label: '7. BLOCKCHAIN ANCHOR' },
  { id: 8, key: 'PROOF', label: '8. INTEGRITY VERIFICATION' },
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
    <div className="w-full bg-[#0D0D11] border-b border-[#222228] px-4 py-2 flex flex-col gap-1.5 shrink-0 select-none shadow-md">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-extrabold tracking-widest text-zinc-400 uppercase font-mono flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#38BDF8] animate-ping" />
          INVESTIGATION PIPELINE NAVIGATION
        </span>
        <div className="flex items-center gap-3 text-[10px] font-mono text-zinc-400">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#10B981]" /> COMPLETED</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#38BDF8]" /> ACTIVE VIEW</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#27272A]" /> PENDING</span>
        </div>
      </div>

      {/* Chevron Bar Stepper Grid */}
      <div className="flex items-center w-full overflow-x-auto scrollbar-none pt-0.5 pb-1">
        {PIPELINE_CHEVRONS.map((stage) => {
          const state = getStageState(stage.id);
          const isActiveView = activeStageId === stage.id;

          let bgClasses = 'bg-[#181820] text-zinc-400';
          if (state === 'COMPLETED') {
            bgClasses = 'bg-gradient-to-r from-[#059669] to-[#10B981] text-white shadow-sm';
          } else if (state === 'ACTIVE' || isActiveView) {
            bgClasses = 'bg-gradient-to-r from-[#0284C7] to-[#38BDF8] text-white font-bold shadow-[0_0_15px_rgba(56,189,248,0.35)]';
          } else if (state === 'TAMPERED' || state === 'FAILED') {
            bgClasses = 'bg-gradient-to-r from-[#991B1B] to-[#EF4444] text-white font-bold animate-pulse';
          }

          return (
            <button
              key={stage.id}
              onClick={() => onSelectStage(stage.id)}
              className={`chevron-nav-item ${bgClasses} flex-1 min-w-[125px] justify-center transition-all duration-200 hover:scale-[1.02]`}
              title={`Jump to ${stage.label}`}
            >
              <span className="truncate flex items-center gap-1.5">
                {state === 'COMPLETED' && <CheckCircle2 className="w-3 h-3 shrink-0 text-white" />}
                {state === 'ACTIVE' && <Clock className="w-3 h-3 shrink-0 text-white animate-spin" />}
                {state === 'TAMPERED' && <AlertTriangle className="w-3 h-3 shrink-0 text-white" />}
                <span>{stage.label}</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
