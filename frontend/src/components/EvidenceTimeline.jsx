import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Terminal, CheckCircle2, CircleDot } from 'lucide-react';

export default function EvidenceTimeline({ steps = [] }) {
  if (!steps || steps.length === 0) {
    return null;
  }

  // Format ISO timestamp into clean forensic [HH:MM:SS] string
  const formatTime = (timestampStr) => {
    if (!timestampStr) return '[00:00:00]';
    try {
      const d = new Date(timestampStr);
      const hours = String(d.getUTCHours()).padStart(2, '0');
      const mins = String(d.getUTCMinutes()).padStart(2, '0');
      const secs = String(d.getUTCSeconds()).padStart(2, '0');
      return `[${hours}:${mins}:${secs}]`;
    } catch {
      return '[00:00:00]';
    }
  };

  // Map step messages to Phase 15 required forensic event labels
  const getStepLabel = (stepObj) => {
    const s = stepObj.step;
    const msg = stepObj.message || '';

    if (s === 'SCANNING') return 'Face detected';
    if (s === 'ENCODING') return 'Face signature generated';
    if (s === 'SEARCHING') return 'Reverse Trace initiated';
    if (s === 'DISCOVERING') return 'Candidate discovered';
    if (s === 'VERIFYING') return 'Candidate face correlated';
    if (s === 'FINGERPRINTING') return 'Evidence fingerprint generated';
    if (s === 'ANCHORING') return 'Blockchain transaction submitted';
    if (s === 'CONFIRMING' || s === 'VERIFIED') return 'Blockchain confirmation received';
    return msg;
  };

  return (
    <div className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-6 mb-8 backdrop-blur-md font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <h3 className="text-sm font-bold text-cyan-400 tracking-wider flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          FORENSIC EVIDENCE EXECUTION TIMELINE
        </h3>
        <span className="px-2 py-0.5 rounded text-[10px] bg-slate-950 text-slate-400 border border-slate-800 font-bold">
          UTC TIMESTAMPS
        </span>
      </div>

      {/* Terminal Timeline Logs */}
      <div className="bg-slate-950/90 border border-slate-800 rounded-lg p-4 font-mono space-y-2 max-h-[220px] overflow-y-auto">
        {steps.map((item, idx) => {
          const timeBadge = formatTime(item.timestamp);
          const label = getStepLabel(item);

          return (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04 }}
              className="flex items-center justify-between py-1 border-b border-slate-900/80 last:border-0"
            >
              <div className="flex items-center gap-3">
                <span className="text-cyan-400 font-bold text-[11px]">{timeBadge}</span>
                <span className="text-slate-200 font-semibold">{label}</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-500 hidden sm:inline">{item.step}</span>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
