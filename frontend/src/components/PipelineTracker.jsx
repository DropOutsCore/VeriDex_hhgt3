import React from 'react';
import { motion } from 'framer-motion';
import { Scan, Fingerprint, Search, GitCompare, Dna, Anchor, ShieldCheck, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';

const STAGES = [
  { id: 'SCAN', label: 'SCAN', desc: 'YuNet Detection', icon: Scan },
  { id: 'SIGNATURE', label: 'SIGNATURE', desc: 'SFace 128-D Vector', icon: Fingerprint },
  { id: 'REVERSE TRACE', label: 'REVERSE TRACE', desc: 'Google Lens Discovery', icon: Search },
  { id: 'CORRELATION', label: 'CORRELATION', desc: 'Candidate Match', icon: GitCompare },
  { id: 'FINGERPRINT', label: 'FINGERPRINT', desc: 'Evidence DNA Payload', icon: Dna },
  { id: 'CHAIN ANCHOR', label: 'CHAIN ANCHOR', desc: 'Polygon Amoy Web3', icon: Anchor },
  { id: 'INTEGRITY', label: 'INTEGRITY', desc: 'On-Chain Proof', icon: ShieldCheck },
];

export default function PipelineTracker({ currentStatus, steps = [], isTampered = false }) {
  
  // Maps backend status enum to active step index
  const getActiveIndex = (status) => {
    switch (status) {
      case 'SCANNING': return 0;
      case 'ENCODING': return 1;
      case 'SEARCHING': return 2;
      case 'DISCOVERING': return 2;
      case 'VERIFYING': return 3;
      case 'FINGERPRINTING': return 4;
      case 'ANCHORING': return 5;
      case 'CONFIRMING': return 5;
      case 'VERIFIED': return 6;
      case 'FAILED': return 6;
      default: return -1; // IDLE
    }
  };

  const activeIndex = getActiveIndex(currentStatus);
  const isFailed = currentStatus === 'FAILED';

  return (
    <div className="w-full bg-slate-900/60 border border-cyan-900/40 rounded-xl p-6 mb-8 backdrop-blur-md">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h2 className="text-sm font-semibold tracking-wider text-cyan-400 font-mono flex items-center gap-2">
          <Scan className="w-4 h-4 text-cyan-400" />
          FORENSIC PIPELINE EXECUTION PIPELINE
        </h2>
        <div className="text-xs font-mono text-slate-400">
          STATUS: <span className={`font-bold ${isTampered ? 'text-rose-400 text-glow-rose animate-pulse' : currentStatus === 'VERIFIED' ? 'text-emerald-400 text-glow-emerald' : 'text-cyan-400'}`}>{isTampered ? 'TAMPER_DETECTED' : currentStatus}</span>
        </div>
      </div>

      {/* Stepper Grid */}
      <div className="grid grid-cols-2 md:grid-cols-7 gap-3">
        {STAGES.map((stage, idx) => {
          const Icon = stage.icon;
          const isComplete = activeIndex > idx || (currentStatus === 'VERIFIED' && !isFailed);
          const isActive = activeIndex === idx && !isFailed;
          const isCurrentFailed = isFailed && activeIndex === idx;

          let cardBorder = 'border-slate-800 bg-slate-950/40 text-slate-500';
          let iconColor = 'text-slate-600';
          let statusBadge = null;

          if (isTampered && idx === 6) {
            cardBorder = 'border-rose-500/80 bg-rose-950/30 text-rose-300 glow-rose';
            iconColor = 'text-rose-400';
            statusBadge = <AlertTriangle className="w-4 h-4 text-rose-400 animate-bounce" />;
          } else if (isCurrentFailed) {
            cardBorder = 'border-rose-500/80 bg-rose-950/30 text-rose-300 glow-rose';
            iconColor = 'text-rose-400';
            statusBadge = <AlertTriangle className="w-4 h-4 text-rose-400" />;
          } else if (isComplete) {
            cardBorder = 'border-emerald-500/50 bg-emerald-950/20 text-emerald-300 glow-emerald';
            iconColor = 'text-emerald-400';
            statusBadge = <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
          } else if (isActive) {
            cardBorder = 'border-cyan-400 bg-cyan-950/40 text-cyan-200 glow-cyan';
            iconColor = 'text-cyan-400';
            statusBadge = <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />;
          }

          return (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className={`relative flex flex-col items-center justify-between p-3 rounded-lg border text-center transition-all duration-300 ${cardBorder}`}
            >
              {/* Connector line for desktop */}
              {idx < STAGES.length - 1 && (
                <div className="hidden md:block absolute -right-2 top-1/2 -translate-y-1/2 w-4 h-0.5 z-10 bg-slate-800" />
              )}

              <div className="flex items-center justify-between w-full mb-2">
                <span className="text-[10px] font-mono text-slate-500 font-bold">0{idx + 1}</span>
                {statusBadge}
              </div>

              <div className="p-2 rounded-lg bg-slate-900/60 mb-2">
                <Icon className={`w-5 h-5 ${iconColor}`} />
              </div>

              <div>
                <div className="text-xs font-bold font-mono tracking-tight">{stage.label}</div>
                <div className="text-[10px] text-slate-400 font-mono tracking-tighter mt-0.5">{stage.desc}</div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
