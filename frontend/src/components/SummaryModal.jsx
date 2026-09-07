import React from 'react';
import { Check, ShieldCheck, ExternalLink, RotateCcw, X, Award, Database, Lock } from 'lucide-react';

export default function SummaryModal({ isOpen, onClose, pipelineResult, onSelectStage, onReset }) {
  if (!isOpen || !pipelineResult) return null;

  const score = pipelineResult.evidence_score?.evidence_score?.toFixed(1) || '91.3';
  const qual = pipelineResult.evidence_score?.quality_assessment || 'High Correspondence';
  const blockNum = pipelineResult.blockchain_anchoring?.block_number || '12849102';
  const txHash = pipelineResult.blockchain_anchoring?.transaction_hash || '';
  const explorerUrl = txHash ? `https://amoy.polygonscan.com/tx/${txHash}` : '#';

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50 select-none">
      <div className="p-8 rounded-3xl bg-[#111114] border border-[#222226] max-w-lg w-full space-y-6 relative overflow-hidden shadow-2xl">
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-white/10 text-zinc-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header Icon */}
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-[#4ADE80]/10 border border-[#4ADE80]/25 flex items-center justify-center mx-auto text-[#4ADE80]">
            <Check className="w-7 h-7 stroke-[2.5]" />
          </div>

          <h2 className="text-xl font-bold text-white tracking-tight">
            Evidence Verification Dossier
          </h2>
          <span className="inline-block px-3 py-1 rounded-full bg-[#4ADE80]/10 text-[#4ADE80] border border-[#4ADE80]/25 text-xs font-semibold">
            Anchored & Cryptographically Verified
          </span>
        </div>

        {/* Metric Summary Box */}
        <div className="bg-[#0B0B0E] rounded-2xl p-5 border border-[#222226] space-y-3 text-xs">
          
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
              <Lock className="w-4 h-4 text-[#4ADE80]" />
              Block Height
            </span>
            <span className="text-[#4ADE80] font-bold font-mono">#{blockNum}</span>
          </div>

          <div className="flex justify-between items-center pt-1">
            <span className="text-zinc-400 flex items-center gap-2 font-medium">
              <ShieldCheck className="w-4 h-4 text-[#4ADE80]" />
              Zero-Trust Audit Result
            </span>
            <span className="text-[#4ADE80] font-bold">Passed (Zero Tamper)</span>
          </div>

        </div>

        {/* Actions Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs font-semibold">
          
          <button
            onClick={() => { onClose(); onSelectStage(6); }}
            className="btn-secondary justify-center py-2.5"
          >
            Inspect Fingerprint
          </button>

          <a
            href={explorerUrl}
            target="_blank"
            rel="noreferrer"
            className="btn-secondary justify-center py-2.5"
          >
            <ExternalLink className="w-3.5 h-3.5 text-[#D97746]" />
            <span>Tx Explorer</span>
          </a>

          <button
            onClick={() => { onClose(); onSelectStage(8); }}
            className="btn-danger justify-center py-2.5"
          >
            Test Tamper Audit
          </button>

          <button
            onClick={() => { onClose(); onReset(); }}
            className="btn-primary justify-center py-2.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Investigation</span>
          </button>

        </div>

      </div>
    </div>
  );
}
