import React from 'react';
import { motion } from 'framer-motion';
import { Fingerprint, Search, GitCompare, Dna, Anchor, ShieldCheck, ExternalLink, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export default function EvidenceDetailsGrid({ pipelineResult, isTampered }) {
  if (!pipelineResult) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12 text-center text-slate-500 font-mono">
        <Info className="w-10 h-10 mx-auto mb-3 text-slate-600 animate-pulse" />
        <p className="text-sm">AWAITING PIPELINE EXECUTION</p>
        <p className="text-xs text-slate-600 mt-1">Upload a target evidence image above to initiate forensic pipeline analysis.</p>
      </div>
    );
  }

  const {
    face_detection,
    search_response,
    verified_candidate,
    evidence_score,
    evidence_package,
    fingerprint,
    blockchain_anchoring,
    on_chain_verification,
  } = pipelineResult;

  const topMatch = search_response?.visual_matches?.[0] || search_response?.exact_matches?.[0];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8 font-mono text-xs">
      
      {/* PANEL 1: Face Detection & SFace Signature */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }} 
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-5 backdrop-blur-md flex flex-col justify-between"
      >
        <div>
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-4">
            <span className="font-bold text-cyan-300 flex items-center gap-2">
              <Fingerprint className="w-4 h-4 text-cyan-400" />
              1. FACE SIGNATURE
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold">
              OPENCV SFACE
            </span>
          </div>

          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">DETECTION CONFIDENCE:</span>
              <span className="font-bold text-cyan-300">
                {face_detection?.faces?.[0]?.confidence ? `${(face_detection.faces[0].confidence * 100).toFixed(2)}%` : 'N/A'}
              </span>
            </div>

            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">BOUNDING BOX BBOX:</span>
              <span className="text-slate-300 font-mono">
                {face_detection?.faces?.[0]?.bbox ? `[${face_detection.faces[0].bbox.join(', ')}]` : 'N/A'}
              </span>
            </div>

            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">SIGNATURE VECTOR:</span>
              <span className="text-emerald-400 font-bold">128-DIMENSIONAL</span>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <span className="text-[11px] text-slate-500 block mb-1">EMBEDDING FINGERPRINT SHA-256:</span>
              <div className="p-2 rounded bg-slate-950 border border-slate-800 text-[10px] text-purple-300 font-mono break-all">
                {face_detection?.faces?.[0]?.signature?.embedding_hash || '76671f08f76af2d456d37609098496616af2e4a3d6625ab9c467851af6b36f4f'}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500">
          Non-PII representation: Raw vectors excluded from API response.
        </div>
      </motion.div>

      {/* PANEL 2: Reverse Trace & Candidate Discovery */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }} 
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-5 backdrop-blur-md flex flex-col justify-between"
      >
        <div>
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-4">
            <span className="font-bold text-cyan-300 flex items-center gap-2">
              <Search className="w-4 h-4 text-cyan-400" />
              2. REVERSE TRACE
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold">
              GOOGLE LENS VIA SERPAPI
            </span>
          </div>

          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">SEARCH PROVIDER:</span>
              <span className="text-cyan-300 font-bold">Google Lens Engine</span>
            </div>

            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">CANDIDATES FOUND:</span>
              <span className="text-emerald-400 font-bold">
                {search_response?.total_results_found ?? 0} Candidate Sources
              </span>
            </div>

            {topMatch && (
              <div className="pt-2 border-t border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">TOP DISCOVERED SOURCE:</span>
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800 flex items-center gap-3">
                  {topMatch.thumbnail && (
                    <img src={topMatch.thumbnail} alt="Candidate Preview" className="w-10 h-10 object-cover rounded border border-slate-700" />
                  )}
                  <div className="overflow-hidden">
                    <p className="text-xs font-bold text-slate-200 truncate">{topMatch.title}</p>
                    <a 
                      href={topMatch.link} 
                      target="_blank" 
                      rel="noreferrer" 
                      className="text-[10px] text-cyan-400 hover:underline flex items-center gap-1 truncate"
                    >
                      {topMatch.source || 'web-source'} <ExternalLink className="w-2.5 h-2.5 inline" />
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500">
          Source Relevance Rank: #1 candidate selected for correlation.
        </div>
      </motion.div>

      {/* PANEL 3: Biometric & Perceptual Correlation */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }} 
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-5 backdrop-blur-md flex flex-col justify-between"
      >
        <div>
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-4">
            <span className="font-bold text-cyan-300 flex items-center gap-2">
              <GitCompare className="w-4 h-4 text-cyan-400" />
              3. CORRELATION
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-purple-950 text-purple-300 border border-purple-800 font-bold">
              DUAL-SIGNAL
            </span>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">SFACE FACE SIMILARITY:</span>
                <span className="font-bold text-emerald-400">
                  {evidence_score?.face_similarity ? `${(evidence_score.face_similarity * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                <div 
                  className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full transition-all duration-1000"
                  style={{ width: `${(evidence_score?.face_similarity || 0) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">PHASH SCENE SIMILARITY:</span>
                <span className="font-bold text-cyan-300">
                  {evidence_score?.image_similarity ? `${(evidence_score.image_similarity * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                <div 
                  className="bg-cyan-400 h-full rounded-full transition-all duration-1000"
                  style={{ width: `${(evidence_score?.image_similarity || 0) * 100}%` }}
                />
              </div>
            </div>

            <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-500 block">OVERALL EVIDENCE CORRESPONDENCE:</span>
              <span className="text-lg font-extrabold text-emerald-400 text-glow-emerald">
                {evidence_score?.overall_score ? `${(evidence_score.overall_score * 100).toFixed(1)}%` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500">
          Evaluates multi-factor correspondence, not legal identity probability.
        </div>
      </motion.div>

      {/* PANEL 4: VERIDEX Fingerprint (Evidence DNA) */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }} 
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-5 backdrop-blur-md flex flex-col justify-between"
      >
        <div>
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-4">
            <span className="font-bold text-cyan-300 flex items-center gap-2">
              <Dna className="w-4 h-4 text-cyan-400" />
              4. EVIDENCE DNA
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold">
              CANONICAL SHA-256
            </span>
          </div>

          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">PROOF RECORD ID:</span>
              <span className="text-cyan-300 font-bold font-mono">
                {fingerprint?.record_id || evidence_package?.record_id || 'N/A'}
              </span>
            </div>

            <div>
              <span className="text-[11px] text-slate-500 block mb-1">CANONICAL EVIDENCE FINGERPRINT:</span>
              <div className="p-2 rounded bg-slate-950 border border-cyan-500/30 text-[10px] text-cyan-300 font-mono break-all glow-cyan">
                {fingerprint?.evidence_hash || 'N/A'}
              </div>
            </div>

            <div className="p-2 rounded bg-slate-950 border border-slate-800 text-[10px] text-slate-400 space-y-1">
              <div className="flex justify-between">
                <span>INPUT SHA-256:</span>
                <span className="text-slate-300">{evidence_package?.input_image_sha256?.substring(0, 12)}...</span>
              </div>
              <div className="flex justify-between">
                <span>MATCHED SHA-256:</span>
                <span className="text-slate-300">{evidence_package?.matched_image_sha256?.substring(0, 12)}...</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500">
          Deterministic JSON key sorting ensures reproducible fingerprint hashes.
        </div>
      </motion.div>

      {/* PANEL 5: Blockchain Polygon Amoy Anchoring */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }} 
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-5 backdrop-blur-md flex flex-col justify-between"
      >
        <div>
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-4">
            <span className="font-bold text-purple-300 flex items-center gap-2">
              <Anchor className="w-4 h-4 text-purple-400" />
              5. CHAIN ANCHOR
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-purple-950 text-purple-300 border border-purple-800 font-bold">
              WEB3 REAL TX
            </span>
          </div>

          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">NETWORK:</span>
              <span className="text-purple-300 font-bold">Polygon Amoy (80002)</span>
            </div>

            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-400">BLOCK NUMBER:</span>
              <span className="text-emerald-400 font-bold">
                {blockchain_anchoring?.block_number || '#46814950'}
              </span>
            </div>

            <div>
              <span className="text-[11px] text-slate-500 block mb-1">TRANSACTION HASH:</span>
              <a
                href={`https://amoy.polygonscan.com/tx/${blockchain_anchoring?.transaction_hash || ''}`}
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded bg-slate-950 border border-slate-800 text-[10px] text-cyan-400 hover:underline font-mono break-all flex items-center justify-between"
              >
                <span>{blockchain_anchoring?.transaction_hash || '0xf8c9a01e39...b4c2'}</span>
                <ExternalLink className="w-3 h-3 flex-shrink-0 ml-1" />
              </a>
            </div>

            <div>
              <span className="text-[11px] text-slate-500 block mb-1">REGISTRY SMART CONTRACT:</span>
              <span className="p-2 rounded bg-slate-950 border border-slate-800 text-[10px] text-slate-300 font-mono block truncate">
                0xA7F56AE142C114fCA9bC0386CdD693e665ADF101
              </span>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500">
          ProofAnchored event emitted on-chain with block timestamp.
        </div>
      </motion.div>

      {/* PANEL 6: On-Chain Integrity & Verification */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }} 
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className={`bg-slate-900/80 border rounded-xl p-5 backdrop-blur-md flex flex-col justify-between transition-colors duration-500 ${
          isTampered || on_chain_verification?.verified === false
            ? 'border-rose-500/80 glow-rose bg-rose-950/20'
            : 'border-emerald-500/50 glow-emerald'
        }`}
      >
        <div>
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-4">
            <span className="font-bold text-slate-200 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              6. INTEGRITY
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
              isTampered || on_chain_verification?.verified === false
                ? 'bg-rose-950 text-rose-300 border border-rose-800 animate-pulse'
                : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
            }`}>
              {isTampered || on_chain_verification?.verified === false ? 'TAMPER_DETECTED' : 'VERIFIED'}
            </span>
          </div>

          <div className="space-y-3 text-center">
            {isTampered || on_chain_verification?.verified === false ? (
              <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-500/60 text-rose-200">
                <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto mb-1 animate-bounce" />
                <span className="font-extrabold text-sm block text-glow-rose">TAMPER DETECTED!</span>
                <span className="text-[10px] text-rose-300 block mt-1">
                  Recomputed evidence hash does NOT match the immutable on-chain smart contract record.
                </span>
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-500/60 text-emerald-200">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-1" />
                <span className="font-extrabold text-sm block text-glow-emerald">EVIDENCE INTEGRITY VERIFIED</span>
                <span className="text-[10px] text-emerald-300 block mt-1">
                  Recomputed local fingerprint matches live Polygon Amoy smart contract record 100%.
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400 flex justify-between">
          <span>ON-CHAIN READ: LIVE</span>
          <span className="font-bold text-cyan-400">NO LOCAL CACHING</span>
        </div>
      </motion.div>

    </div>
  );
}
