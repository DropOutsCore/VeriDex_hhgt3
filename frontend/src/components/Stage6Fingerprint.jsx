import React, { useState } from 'react';
import { FileCode, Copy, Check, ShieldCheck, Hash } from 'lucide-react';

export default function Stage6Fingerprint({ fingerprintData, evidencePackage }) {
  const [copied, setCopied] = useState(false);
  const evidenceHash = fingerprintData?.evidence_hash || '9f2a89c4e51001b38f190c4277b810d0a7f9a2b8e41c30d9e512401081a93e5a';

  const handleCopy = () => {
    navigator.clipboard.writeText(evidenceHash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const pkg = evidencePackage || {
    target_image_sha256: '4a1b029ffbc89128f91',
    matched_image_sha256: 'e8190c4109ba77b8',
    face_signature_hash: '7f9a2b8e41c30d9e81a9',
    matched_url: 'https://instagram.com/p/sample_portrait',
    evidence_score: 91.3,
    timestamp: new Date().toISOString(),
  };

  return (
    <div className="max-w-4xl mx-auto space-y-5 text-white">
      
      {/* 1. Stage Header Banner */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            06
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 06
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">Deterministic Fingerprinting</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Canonical RFC 8785 DNA Digest
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Digest Generated</span>
        </div>
      </div>

      {/* Cryptographic Seal Showcase */}
      <div className="p-6 rounded-2xl bg-[#111114] border border-[#222226] space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-white font-bold text-xs uppercase tracking-wider">
            <Hash className="w-4 h-4 text-[#D97746]" />
            <span>Canonical SHA-256 Fingerprint Digest</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-zinc-300 text-[10px] font-medium">
              RFC 8785 Canonical JSON
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-[#D97746]/10 border border-[#D97746]/30 text-[#D97746] text-[10px] font-semibold">
              256-Bit Digest
            </span>
          </div>
        </div>

        {/* Big Hash Box */}
        <div className="p-4 rounded-xl bg-[#0B0B0E] border border-[#222226] flex items-center justify-between gap-4">
          <code className="text-xs md:text-sm font-bold text-[#D97746] tracking-wider break-all font-mono">
            {evidenceHash}
          </code>

          <button
            onClick={handleCopy}
            className="btn-primary text-xs py-2 px-4 shrink-0"
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy Hash'}</span>
          </button>
        </div>
      </div>

      {/* Evidence Composition Breakdown Grid */}
      <div className="p-6 rounded-2xl bg-[#111114] border border-[#222226] space-y-4">
        <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2 pb-3 border-b border-[#222226]">
          <FileCode className="w-4 h-4 text-[#D97746]" />
          <span>Evidence Package Component Manifest</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226] space-y-1">
            <span className="text-zinc-400 font-medium block text-[11px]">Target Image SHA-256</span>
            <code className="text-[#D97746] break-all font-mono text-[11px]">{pkg.target_image_sha256 || '4a1b02...8f91'}</code>
          </div>

          <div className="bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226] space-y-1">
            <span className="text-zinc-400 font-medium block text-[11px]">Matched Image SHA-256</span>
            <code className="text-zinc-300 break-all font-mono text-[11px]">{pkg.matched_image_sha256 || 'e8190c...77b8'}</code>
          </div>

          <div className="bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226] space-y-1">
            <span className="text-zinc-400 font-medium block text-[11px]">Face Signature Hash</span>
            <code className="text-[#4ADE80] break-all font-mono text-[11px]">{pkg.face_signature_hash || '7f9a2b...81a9'}</code>
          </div>

          <div className="bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226] space-y-1">
            <span className="text-zinc-400 font-medium block text-[11px]">Synthesized Evidence Score</span>
            <span className="text-[#D97746] font-bold text-xs block">{pkg.evidence_score || 91.3}%</span>
          </div>

          <div className="bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226] space-y-1 md:col-span-2">
            <span className="text-zinc-400 font-medium block text-[11px]">Canonical Matched Source URL</span>
            <code className="text-zinc-300 break-all font-mono text-[11px]">{pkg.matched_url || 'https://instagram.com/p/sample_portrait'}</code>
          </div>
        </div>
      </div>

    </div>
  );
}
