import React, { useState } from 'react';
import { Copy, Check, ExternalLink, AlertTriangle, RotateCcw, Shield, CheckCircle2 } from 'lucide-react';
import { simulateTampering, verifyChainIntegrity } from '../api';

const METRIC_ROW = ({ label, value, valueColor }) => (
  <div className="flex justify-between items-center py-1.5 border-b border-[#222226] text-xs">
    <span className="text-zinc-400 text-[11px] font-medium">
      {label}
    </span>
    <span className="font-semibold text-xs" style={{ color: valueColor || '#FFFFFF' }}>
      {value}
    </span>
  </div>
);

const SCORE_BAR = ({ label, pct, color = '#D97746' }) => (
  <div className="space-y-1.5 mb-2.5">
    <div className="flex justify-between items-center text-xs">
      <span className="text-zinc-400 text-[11px] font-medium">{label}</span>
      <span className="font-bold text-xs" style={{ color }}>{pct}%</span>
    </div>
    <div className="h-1.5 bg-[#0C0C0E] border border-[#222226] rounded-full overflow-hidden">
      <div 
        className="h-full rounded-full transition-all duration-500 ease-out" 
        style={{ 
          width: `${Math.min(100, Math.max(0, parseFloat(pct) || 0))}%`, 
          backgroundColor: color 
        }} 
      />
    </div>
  </div>
);

const PANEL_CARD = ({ title, badge, children }) => (
  <div className="p-4 border-b border-[#222226]">
    <div className="flex items-center justify-between mb-3">
      <span className="text-[10px] font-semibold tracking-wider text-zinc-400 uppercase">
        {title}
      </span>
      {badge && (
        <span className="text-[9px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-zinc-400 font-medium">
          {badge}
        </span>
      )}
    </div>
    {children}
  </div>
);

export default function RightForensicPanel({ pipelineResult, onTamperStateChange, isTampered }) {
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const ev = pipelineResult?.evidence_score;
  const overallScore = ev?.evidence_score?.toFixed(1) ?? '—';
  const faceScore    = ev?.components?.face_similarity    != null ? (ev.components.face_similarity    * 100).toFixed(1) : '—';
  const phashScore   = ev?.components?.phash_similarity   != null ? (ev.components.phash_similarity   * 100).toFixed(1) : '—';
  const revScore     = ev?.components?.reverse_search_rank != null ? (ev.components.reverse_search_rank * 100).toFixed(1) : '—';
  const srcScore     = ev?.components?.source_authority   != null ? (ev.components.source_authority   * 100).toFixed(1) : '—';

  const evidenceHash = pipelineResult?.fingerprint?.evidence_hash || null;
  const bc           = pipelineResult?.blockchain_anchoring;
  const txHash       = bc?.transaction_hash || null;
  const blockNum     = bc?.block_number     || null;
  const explorerUrl  = txHash ? `https://amoy.polygonscan.com/tx/${txHash}` : null;

  const candidates   = pipelineResult?.search_response?.candidates || [];

  const handleCopy = () => {
    if (evidenceHash) {
      navigator.clipboard.writeText(evidenceHash);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSimulateTampering = async () => {
    if (!pipelineResult?.evidence_package) return;
    setIsLoading(true);
    try {
      await simulateTampering(pipelineResult.evidence_package, 'matched_url', 'https://tampered-fake-news-site.org/hacked.jpg');
      if (onTamperStateChange) onTamperStateChange(true);
    } catch (err) {
      console.error('Tamper error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetVerification = async () => {
    setIsLoading(true);
    try {
      if (pipelineResult?.evidence_package) await verifyChainIntegrity(pipelineResult.evidence_package);
      if (onTamperStateChange) onTamperStateChange(false);
    } catch (err) {
      console.error('Reset error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <aside className="w-72 bg-[#0A0A0D] border-l border-[#222226] flex flex-col h-full shrink-0 overflow-y-auto">
      
      {/* STATUS BANNER */}
      <div className={`p-4 border-b transition-all duration-300 ${
        isTampered 
          ? 'bg-[#180B0B] border-[#F87171]/40' 
          : 'bg-[#101014] border-[#222226]'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isTampered ? 'bg-[#F87171] animate-ping' : 'bg-[#4ADE80]'}`} />
            <span className={`text-xs font-bold tracking-wide uppercase ${isTampered ? 'text-[#F87171]' : 'text-[#4ADE80]'}`}>
              {isTampered ? 'Tamper Detected' : 'Evidence Verified'}
            </span>
          </div>
          {overallScore !== '—' && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-white font-bold">
              {overallScore}%
            </span>
          )}
        </div>
        <p className={`text-[11px] leading-relaxed ${isTampered ? 'text-[#F87171]/90' : 'text-zinc-400'}`}>
          {isTampered
            ? 'Canonical cryptographic digest mismatch. Ledger anchoring proof invalidated.'
            : 'Multi-signal biometric correlation anchored on Polygon Amoy ledger.'}
        </p>
      </div>

      {/* SCORE BREAKDOWN */}
      <PANEL_CARD title="Correspondence Matrix">
        <SCORE_BAR label="Face Biometrics"   pct={faceScore}  color="#4ADE80" />
        <SCORE_BAR label="Perceptual Hash"   pct={phashScore} color="#D97746" />
        <SCORE_BAR label="Reverse Index"     pct={revScore}   color="#D97746" />
        <SCORE_BAR label="Source Authority"  pct={srcScore}   color="#A1A1AA" />
        
        <div className="mt-3 pt-2.5 border-t border-[#222226] flex justify-between items-center">
          <span className="text-zinc-400 text-xs font-medium">Confidence Score</span>
          <span className="text-sm font-bold text-[#D97746]">
            {overallScore}{overallScore !== '—' ? '%' : ''}
          </span>
        </div>
      </PANEL_CARD>

      {/* EVIDENCE HASH */}
      {evidenceHash && (
        <PANEL_CARD title="Cryptographic Fingerprint" badge="RFC 8785">
          <div className="p-2.5 rounded-xl bg-[#0B0B0E] border border-[#222226] text-[10px] text-[#D97746] font-mono break-all leading-relaxed mb-2.5">
            {evidenceHash}
          </div>
          <button
            onClick={handleCopy}
            className="w-full btn-secondary text-xs py-1.5 justify-center gap-1.5"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-[#4ADE80]" /> : <Copy className="w-3.5 h-3.5 text-zinc-400" />}
            <span>{copied ? 'Hash Copied' : 'Copy Hash Digest'}</span>
          </button>
        </PANEL_CARD>
      )}

      {/* LEDGER PROOF */}
      {txHash && (
        <PANEL_CARD title="Blockchain Anchor" badge="Polygon Amoy">
          <METRIC_ROW label="Network" value="Polygon Amoy (80002)" />
          <METRIC_ROW label="Block Number" value={blockNum ? `#${blockNum}` : '—'} valueColor="#D97746" />
          
          <div className="mt-2.5">
            <div className="text-[10px] text-zinc-400 font-medium uppercase mb-1">
              Transaction Hash
            </div>
            <div className="p-2.5 rounded-xl bg-[#0B0B0E] border border-[#222226] text-[10px] text-[#D97746] font-mono break-all leading-relaxed mb-2.5">
              {txHash}
            </div>
            {explorerUrl && (
              <a
                href={explorerUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-zinc-300 hover:text-white font-medium transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5 text-[#D97746]" />
                <span>View on PolygonScan</span>
              </a>
            )}
          </div>
        </PANEL_CARD>
      )}

      {/* SOURCES */}
      {candidates.length > 0 && (
        <PANEL_CARD title={`Discovered Sources (${candidates.length})`}>
          <div className="space-y-1.5">
            {candidates.slice(0, 4).map((c, i) => (
              <div
                key={i}
                className="p-2.5 rounded-xl bg-[#111114] border border-[#222226] hover:border-[#2D2D35] transition-all"
              >
                <div className="text-xs font-medium text-white truncate mb-1">
                  {c.title || c.source}
                </div>
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-zinc-500 uppercase">{c.match_type || 'visual match'}</span>
                  <span className="text-[#4ADE80] font-semibold">Rank #{c.rank || i + 1}</span>
                </div>
              </div>
            ))}
          </div>
        </PANEL_CARD>
      )}

      {/* INTEGRITY ACTIONS */}
      <div className="p-4 mt-auto border-t border-[#222226] bg-[#0C0C0F]">
        {!isTampered ? (
          <button
            onClick={handleSimulateTampering}
            disabled={isLoading || !pipelineResult?.evidence_package}
            className="w-full btn-danger justify-center gap-2 py-2"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Simulate Evidence Tamper</span>
          </button>
        ) : (
          <button
            onClick={handleResetVerification}
            disabled={isLoading}
            className="w-full btn-primary justify-center gap-2 py-2"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restore & Re-Verify</span>
          </button>
        )}
      </div>
    </aside>
  );
}
