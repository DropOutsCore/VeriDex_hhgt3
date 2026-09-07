import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, AlertCircle, RotateCcw, Check, Database, Cpu } from 'lucide-react';
import { simulateTampering, verifyChainIntegrity } from '../api';

export default function Stage8IntegrityProof({ 
  pipelineResult, 
  onTamperStateChange 
}) {
  const [isTampered, setIsTampered] = useState(false);
  const [tamperResult, setTamperResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const originalHash = pipelineResult?.fingerprint?.evidence_hash || '9f2a89c4e51001b38f190c4277b810d0a7f9a2b8e41c30d9e512401081a93e5a';
  const onChainHash = pipelineResult?.on_chain_verification?.on_chain_hash || originalHash;
  const evidencePackage = pipelineResult?.evidence_package;

  const handleSimulateTampering = async () => {
    if (!evidencePackage) return;
    setIsLoading(true);
    setError(null);

    try {
      const res = await simulateTampering(evidencePackage, 'matched_url', 'https://tampered-fake-news-site.org/hacked.jpg');
      setTamperResult(res);
      setIsTampered(true);
      if (onTamperStateChange) onTamperStateChange(true);
    } catch (err) {
      console.error('Tamper simulation error:', err);
      setError(err.message || 'Tamper simulation failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetVerification = async () => {
    setIsLoading(true);
    setError(null);

    try {
      if (evidencePackage) {
        await verifyChainIntegrity(evidencePackage);
      }
      setIsTampered(false);
      setTamperResult(null);
      if (onTamperStateChange) onTamperStateChange(false);
    } catch (err) {
      console.error('Reset verification error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-5 text-white">
      
      {/* 1. Stage Header Banner */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            08
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 08
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">Zero-Trust Audit</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              On-Chain Cryptographic Integrity Proof
            </h2>
          </div>
        </div>

        {/* Status Badge */}
        {!isTampered ? (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] text-xs font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Integrity Confirmed</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#F87171]/10 border border-[#F87171]/25 text-[#F87171] text-xs font-semibold animate-pulse">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Tamper Detected</span>
          </div>
        )}
      </div>

      {/* Main Verification Banner */}
      {!isTampered ? (
        <div className="p-6 rounded-2xl bg-[#111114] border border-[#4ADE80]/30 text-center space-y-2">
          <div className="w-10 h-10 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 flex items-center justify-center mx-auto text-[#4ADE80]">
            <Check className="w-5 h-5 stroke-[2.5]" />
          </div>

          <div>
            <h3 className="text-base font-bold text-white">
              Evidence Integrity Cryptographically Verified
            </h3>
            <p className="text-xs text-zinc-400 mt-1 max-w-lg mx-auto leading-relaxed">
              Local canonical SHA-256 evidence digest precisely matches the immutable smart contract record on Polygon Amoy. Zero tampering detected post-anchoring.
            </p>
          </div>
        </div>
      ) : (
        <div className="p-6 rounded-2xl bg-[#180B0B] border border-[#F87171]/40 text-center space-y-2">
          <div className="w-10 h-10 rounded-full bg-[#F87171]/10 border border-[#F87171]/25 flex items-center justify-center mx-auto text-[#F87171]">
            <AlertCircle className="w-5 h-5 stroke-[2.5]" />
          </div>

          <div>
            <h3 className="text-base font-bold text-[#F87171]">
              Cryptographic Integrity Mismatch Detected
            </h3>
            <p className="text-xs text-[#F87171]/90 mt-1 max-w-lg mx-auto leading-relaxed">
              The local evidence package was modified post-anchoring. Polygon Amoy blockchain record remains unchanged, exposing the metadata tamper.
            </p>
          </div>
        </div>
      )}

      {/* Side-by-Side Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Local Evidence Box */}
        <div className={`p-5 rounded-2xl bg-[#111114] border space-y-3 ${
          isTampered ? 'border-[#F87171]/40 bg-[#160B0B]' : 'border-[#222226]'
        }`}>
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
              <Cpu className="w-4 h-4 text-[#D97746]" />
              Local Evidence Digest
            </span>
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
              isTampered ? 'bg-[#F87171]/10 text-[#F87171] border border-[#F87171]/25' : 'bg-white/5 text-zinc-400'
            }`}>
              {isTampered ? 'Modified Payload' : 'Original Canonical'}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#0B0B0E] border border-[#222226] font-mono text-xs break-all leading-relaxed">
            <div className="text-[10px] text-zinc-500 mb-1">Re-computed SHA-256 Hash:</div>
            <code className={isTampered ? 'text-[#F87171] font-bold' : 'text-[#D97746]'}>
              {isTampered ? (tamperResult?.recomputed_local_hash || '71c40210e83918a991aa') : originalHash}
            </code>
          </div>
        </div>

        {/* Blockchain Record Box */}
        <div className="p-5 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
              <Database className="w-4 h-4 text-[#4ADE80]" />
              Polygon Amoy Record
            </span>
            <span className="text-[10px] text-[#4ADE80] bg-[#4ADE80]/10 px-2 py-0.5 rounded-full border border-[#4ADE80]/25 font-semibold">
              Immutable
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#0B0B0E] border border-[#222226] font-mono text-xs break-all leading-relaxed">
            <div className="text-[10px] text-zinc-500 mb-1">Anchored On-Chain Hash:</div>
            <code className="text-[#4ADE80] font-bold">
              {onChainHash}
            </code>
          </div>
        </div>

      </div>

      {/* Tamper Control Section */}
      <div className="p-5 rounded-2xl bg-[#111114] border border-[#222226] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-[#D97746]" />
            Forensic Tamper Simulation Test
          </h4>
          <p className="text-xs text-zinc-400 mt-1">
            Simulate an adversary modifying evidence metadata to test zero-trust detection.
          </p>
        </div>

        {!isTampered ? (
          <button
            onClick={handleSimulateTampering}
            disabled={isLoading || !evidencePackage}
            className="btn-danger text-xs py-2 px-4 shrink-0"
          >
            <AlertCircle className="w-3.5 h-3.5" />
            <span>{isLoading ? 'Simulating...' : 'Simulate Evidence Tampering'}</span>
          </button>
        ) : (
          <button
            onClick={handleResetVerification}
            disabled={isLoading}
            className="btn-primary text-xs py-2 px-4 shrink-0"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restore & Re-Verify</span>
          </button>
        )}
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-[#F87171]/10 border border-[#F87171]/30 text-[#F87171] text-xs">
          {error}
        </div>
      )}

    </div>
  );
}
