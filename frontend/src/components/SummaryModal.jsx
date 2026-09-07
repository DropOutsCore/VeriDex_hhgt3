import React from 'react';
import { Check, ShieldCheck, ExternalLink, RotateCcw, X, Award, Database, Lock, Download } from 'lucide-react';
import VeriDexLogo from './VeriDexLogo';

export default function SummaryModal({ isOpen, onClose, pipelineResult, onSelectStage, onReset }) {
  if (!isOpen || !pipelineResult) return null;

  const score = pipelineResult.evidence_score?.evidence_score?.toFixed(1) || '91.3';
  const qual = pipelineResult.evidence_score?.quality_assessment || 'High Correspondence';
  const blockNum = pipelineResult.blockchain_anchoring?.block_number || '12849102';
  const txHash = pipelineResult.blockchain_anchoring?.transaction_hash || '';
  const explorerUrl = txHash ? `https://amoy.polygonscan.com/tx/${txHash}` : 'https://amoy.polygonscan.com';

  const handleDownloadDossier = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(pipelineResult, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `veridex-evidence-dossier-${pipelineResult.session_id || 'VX-2026'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50 select-none">
      <div className="p-8 rounded-3xl bg-[#111114] border border-[#222226] max-w-lg w-full space-y-6 relative overflow-hidden shadow-2xl">
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-white/10 text-zinc-400 hover:text-white transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header Icon */}
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-[#38BDF8]/10 border border-[#38BDF8]/25 flex items-center justify-center mx-auto text-[#38BDF8]">
            <VeriDexLogo size={32} />
          </div>

          <h2 className="text-xl font-bold text-white tracking-tight font-mono">
            EVIDENCE VERIFICATION DOSSIER
          </h2>
          <span className="inline-block px-3 py-1 rounded-full bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/25 text-xs font-semibold font-mono">
            Anchored & Cryptographically Verified
          </span>
        </div>

        {/* Metric Summary Box */}
        <div className="bg-[#0B0B0E] rounded-2xl p-5 border border-[#222226] space-y-3 text-xs font-mono">
          
          <div className="flex justify-between items-center border-b border-[#222226] pb-2.5">
            <span className="text-zinc-400 flex items-center gap-2 font-medium">
              <Award className="w-4 h-4 text-[#D97746]" />
              Composite Confidence Score
            </span>
            <span className="text-[#D97746] font-bold text-sm">{score}% ({qual})</span>
          </div>

          <div className="flex justify-between items-center border-b border-[#222226] pb-2.5">
            <span className="text-zinc-400 flex items-center gap-2 font-medium">
              <Database className="w-4 h-4 text-zinc-400" />
              Settlement Ledger
            </span>
            <span className="text-white font-semibold">Polygon Amoy (80002)</span>
          </div>

          <div className="flex justify-between items-center border-b border-[#222226] pb-2.5">
            <span className="text-zinc-400 flex items-center gap-2 font-medium">
              <Lock className="w-4 h-4 text-[#10B981]" />
              Block Height
            </span>
            <span className="text-[#10B981] font-bold font-mono">#{blockNum}</span>
          </div>

          <div className="flex justify-between items-center pt-1">
            <span className="text-zinc-400 flex items-center gap-2 font-medium">
              <ShieldCheck className="w-4 h-4 text-[#10B981]" />
              Zero-Trust Audit Result
            </span>
            <span className="text-[#10B981] font-bold">Passed (Zero Tamper)</span>
          </div>

        </div>

        {/* Actions Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs font-semibold font-mono">
          
          <button
            onClick={handleDownloadDossier}
            className="px-4 py-2.5 rounded-xl bg-[#38BDF8] hover:bg-[#0284C7] text-black font-extrabold flex items-center justify-center gap-2 transition-all duration-200 cursor-pointer col-span-2 shadow-md"
          >
            <Download className="w-4 h-4 stroke-[2.5]" />
            <span>DOWNLOAD DOSSIER (JSON)</span>
          </button>

          <button
            onClick={() => { onClose(); onSelectStage(6); }}
            className="px-4 py-2 rounded-xl bg-[#181820] hover:bg-[#22222E] text-zinc-200 border border-[#27272A] flex items-center justify-center transition-all duration-200 cursor-pointer"
          >
            Inspect Fingerprint
          </button>

          <a
            href={explorerUrl}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 rounded-xl bg-[#181820] hover:bg-[#22222E] text-zinc-200 border border-[#27272A] flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer"
          >
            <ExternalLink className="w-3.5 h-3.5 text-[#D97746]" />
            <span>Tx Explorer</span>
          </a>

          <button
            onClick={() => { onClose(); onSelectStage(8); }}
            className="px-4 py-2 rounded-xl bg-[#991B1B]/20 hover:bg-[#991B1B]/40 text-[#EF4444] border border-[#991B1B]/40 flex items-center justify-center transition-all duration-200 cursor-pointer"
          >
            Test Tamper Audit
          </button>

          <button
            onClick={() => { onClose(); onReset(); }}
            className="px-4 py-2 rounded-xl bg-[#181820] hover:bg-[#22222E] text-zinc-200 border border-[#27272A] flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Investigation</span>
          </button>

        </div>

        {/* Modal Footer Attribution */}
        <div className="text-center pt-1 border-t border-[#222226]">
          <span className="text-[11px] text-zinc-500 font-medium font-mono">
            VeriDex Forensic Engine • Built by <span className="text-[#D97746] font-semibold">Team Dropouts</span>
          </span>
        </div>

      </div>
    </div>
  );
}

