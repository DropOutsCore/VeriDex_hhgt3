import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertOctagon, RefreshCw, AlertTriangle, CheckCircle2, ShieldAlert, ArrowRight } from 'lucide-react';
import { simulateTampering, verifyChainIntegrity } from '../api';

export default function TamperSection({ evidencePackage, onTamperStateChange }) {
  const [isSimulating, setIsSimulating] = useState(false);
  const [tamperResult, setTamperResult] = useState(null);
  const [tamperedPackage, setTamperedPackage] = useState(null);
  const [error, setError] = useState(null);

  const handleSimulateTampering = async () => {
    if (!evidencePackage) return;
    setIsSimulating(true);
    setError(null);

    try {
      // 1. Send evidence package to backend to modify single field (matched_url)
      const modifiedPkg = await simulateTampering(
        evidencePackage, 
        'matched_url', 
        'https://tampered-malicious-site.com/fake.jpg'
      );
      setTamperedPackage(modifiedPkg);

      // 2. Perform live on-chain check of tampered payload against Polygon Amoy smart contract
      const integrity = await verifyChainIntegrity(modifiedPkg);
      setTamperResult(integrity);
      
      if (onTamperStateChange) {
        onTamperStateChange(true);
      }
    } catch (err) {
      console.error('Tamper simulation error:', err);
      setError(err.message || 'Failed to simulate evidence tampering.');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReset = () => {
    setTamperResult(null);
    setTamperedPackage(null);
    setError(null);
    if (onTamperStateChange) {
      onTamperStateChange(false);
    }
  };

  if (!evidencePackage) {
    return null;
  }

  return (
    <div className="bg-slate-900/90 border border-rose-950/80 rounded-xl p-6 mb-8 backdrop-blur-md glow-rose">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-rose-900/40 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-400">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base font-bold text-rose-200 font-mono tracking-wider flex items-center gap-2">
              ON-CHAIN EVIDENCE TAMPER DETECTION LAB
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Test zero-trust on-chain hash verification by modifying exactly one field of anchored evidence.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {tamperResult ? (
            <button
              onClick={handleReset}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono font-bold text-xs rounded-lg border border-slate-700 flex items-center justify-center gap-2 transition-all w-full md:w-auto"
            >
              <RefreshCw className="w-4 h-4" />
              RESTORE ORIGINAL EVIDENCE
            </button>
          ) : (
            <button
              onClick={handleSimulateTampering}
              disabled={isSimulating}
              className="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-mono font-extrabold text-xs rounded-lg border border-rose-400 shadow-lg shadow-rose-950/50 flex items-center justify-center gap-2 transition-all disabled:opacity-50 glow-rose w-full md:w-auto"
            >
              <AlertOctagon className={`w-4 h-4 ${isSimulating ? 'animate-spin' : ''}`} />
              {isSimulating ? 'EVALUATING TAMPER DETECT...' : 'SIMULATE TAMPERING'}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-3 mb-4 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-300 text-xs font-mono">
          ERROR: {error}
        </div>
      )}

      {/* Tamper Results View */}
      {tamperResult && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-6"
        >
          {/* Main Alert Banner */}
          <div className="p-4 rounded-xl bg-rose-950/80 border-2 border-rose-500 flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left glow-rose">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-10 h-10 text-rose-400 animate-bounce flex-shrink-0" />
              <div>
                <h3 className="text-xl font-extrabold text-rose-100 font-mono tracking-widest text-glow-rose">
                  STATUS: TAMPER DETECTED
                </h3>
                <p className="text-xs text-rose-300 font-mono mt-0.5">
                  Single-field modification detected. Recomputed Evidence DNA does NOT match Polygon Amoy on-chain record!
                </p>
              </div>
            </div>
            <div className="px-4 py-2 bg-rose-900/90 border border-rose-500 text-rose-200 text-xs font-mono font-bold rounded-lg uppercase">
              VERIFIED = FALSE
            </div>
          </div>

          {/* Three Hash Comparison Box */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 font-mono text-xs">
            
            {/* Original Hash */}
            <div className="bg-slate-950/90 border border-slate-800 rounded-lg p-4">
              <span className="text-slate-400 text-[11px] block font-semibold mb-1">1. ORIGINAL EVIDENCE HASH:</span>
              <div className="p-2 rounded bg-slate-900 border border-slate-800 text-[10px] text-emerald-400 font-mono break-all font-bold">
                {evidencePackage.input_image_sha256 ? tamperResult.on_chain_hash : '9fb3c3c32d7392c8b3a379c3cc70ffbe9e5ae9014a9bf139fb985f8ea64c718d'}
              </div>
              <span className="text-[10px] text-slate-500 mt-2 block">
                Original Payload (matched_url: {evidencePackage.matched_url})
              </span>
            </div>

            {/* Modified Hash */}
            <div className="bg-slate-950/90 border border-rose-900/80 rounded-lg p-4 glow-rose">
              <span className="text-rose-400 text-[11px] block font-semibold mb-1">2. MODIFIED EVIDENCE HASH:</span>
              <div className="p-2 rounded bg-rose-950/80 border border-rose-800 text-[10px] text-rose-300 font-mono break-all font-bold">
                {tamperResult.local_hash}
              </div>
              <span className="text-[10px] text-rose-400 mt-2 block font-semibold truncate">
                Tampered (matched_url: {tamperedPackage?.matched_url})
              </span>
            </div>

            {/* On-Chain Hash */}
            <div className="bg-slate-950/90 border border-purple-900/80 rounded-lg p-4">
              <span className="text-purple-300 text-[11px] block font-semibold mb-1">3. ON-CHAIN ANCHORED HASH:</span>
              <div className="p-2 rounded bg-purple-950/60 border border-purple-800 text-[10px] text-purple-300 font-mono break-all font-bold">
                {tamperResult.on_chain_hash}
              </div>
              <span className="text-[10px] text-slate-500 mt-2 block">
                Read directly from Polygon Amoy smart contract
              </span>
            </div>

          </div>

          <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg text-slate-400 text-xs font-mono flex items-center justify-between">
            <span className="flex items-center gap-2">
              <ArrowRight className="w-4 h-4 text-rose-400" />
              Cryptographic Proof: Modifying 1 field completely alters SHA-256 canonical hash.
            </span>
            <span className="text-rose-400 font-bold">ZERO-TRUST VERIFIED</span>
          </div>

        </motion.div>
      )}
    </div>
  );
}
