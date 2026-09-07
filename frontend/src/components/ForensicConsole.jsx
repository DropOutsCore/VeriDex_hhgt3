import React, { useState, useRef, useEffect } from 'react';
import { Download, Check, ChevronUp, ChevronDown, Terminal } from 'lucide-react';

const LOG_COLORS = {
  VERIFIED:  '#4ADE80',
  COMPLETE:  '#4ADE80',
  CHAIN:     '#4ADE80',
  ANCHORING: '#4ADE80',
  FAILED:    '#F87171',
  TAMPER:    '#F87171',
  ERROR:     '#F87171',
  SCANNING:  '#D97746',
  ENCODING:  '#D97746',
  SEARCHING: '#D97746',
  DISCOVERING:'#D97746',
  VERIFYING: '#D97746',
  FINGERPRINTING: '#D97746',
  HASH:      '#D97746',
  TRACE:     '#D97746',
  INFO:      '#A1A1AA',
};

function getLogColor(step) {
  if (!step) return '#A1A1AA';
  const upper = step.toUpperCase();
  for (const [key, color] of Object.entries(LOG_COLORS)) {
    if (upper.includes(key)) return color;
  }
  return '#A1A1AA';
}

export default function ForensicConsole({ logs = [], onClearLogs }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [exported, setExported] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    if (isExpanded && endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isExpanded]);

  const handleExport = () => {
    if (!logs.length) return;
    const text = logs.map(l => `[${l.timestamp}] [${l.step}] ${l.message}`).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `veridex_audit_${Date.now()}.log`;
    a.click();
    URL.revokeObjectURL(url);
    setExported(true);
    setTimeout(() => setExported(false), 2000);
  };

  const defaultLogs = [
    { timestamp: new Date().toISOString(), step: 'INFO', message: 'VERIDEX forensic engine initialized. Ready for visual evidence audit.' },
  ];

  const activeLogs = logs.length > 0 ? logs : defaultLogs;
  const latest = activeLogs[activeLogs.length - 1];

  const fmtTime = (ts) => {
    if (!ts) return '--:--:--';
    if (ts.includes('T')) return ts.split('T')[1]?.split('.')[0] || ts;
    return ts;
  };

  return (
    <div className="bg-[#0A0A0D] border-t border-[#222226] text-xs shrink-0 z-20 transition-all">
      {/* Console Bar */}
      <div className="h-9 flex items-center justify-between px-4">
        {/* Left: Terminal indicator + latest log */}
        <div 
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-3 cursor-pointer flex-1 min-w-0"
        >
          <div className="flex items-center gap-1.5 text-[10px] font-semibold tracking-wider text-zinc-400 uppercase">
            <Terminal className="w-3.5 h-3.5 text-[#D97746]" />
            <span>Audit Trail</span>
          </div>

          <span className="text-zinc-700">|</span>

          {!isExpanded && latest && (
            <div className="flex items-center gap-2 overflow-hidden text-xs text-zinc-400">
              <span className="text-zinc-600 text-[11px]">[{fmtTime(latest.timestamp)}]</span>
              <span className="font-semibold text-[11px]" style={{ color: getLogColor(latest.step) }}>
                [{latest.step}]
              </span>
              <span className="truncate text-zinc-300 text-[11px]">{latest.message}</span>
            </div>
          )}
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2.5">
          <div className="hidden md:flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] text-zinc-400 font-medium">
            <span>Made by</span>
            <span className="text-[#D97746] font-semibold">Team Dropouts</span>
          </div>

          <span className="text-[10px] text-zinc-500 font-medium hidden sm:inline">
            {activeLogs.length} events
          </span>

          <button
            onClick={handleExport}
            className="px-2.5 py-1 rounded-full text-[10px] font-medium text-zinc-400 hover:text-white bg-white/5 border border-white/10 hover:border-white/20 transition-all flex items-center gap-1"
          >
            {exported ? <Check className="w-3 h-3 text-[#4ADE80]" /> : <Download className="w-3 h-3" />}
            <span>Export</span>
          </button>

          <button
            onClick={onClearLogs}
            className="px-2.5 py-1 rounded-full text-[10px] font-medium text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            Clear
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-zinc-400 hover:text-white transition-colors"
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Expanded Logs Panel */}
      {isExpanded && (
        <div className="h-36 overflow-y-auto px-4 py-2 border-t border-[#222226] bg-[#08080B] space-y-1 font-mono text-[11px]">
          {activeLogs.map((log, i) => (
            <div key={i} className="flex items-start gap-3 py-0.5 border-b border-white/[0.03]">
              <span className="text-zinc-600 shrink-0 w-16">
                {fmtTime(log.timestamp)}
              </span>
              <span 
                className="font-bold shrink-0 w-24 uppercase"
                style={{ color: getLogColor(log.step) }}
              >
                [{log.step || 'INFO'}]
              </span>
              <span className="text-zinc-300 break-all flex-1">
                {log.message}
              </span>
            </div>
          ))}
          <div ref={endRef} />
        </div>
      )}
    </div>
  );
}
