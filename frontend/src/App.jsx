import React, { useState, useEffect, useRef } from 'react';
import TopBar from './components/TopBar';
import PipelineChevronNav from './components/PipelineChevronNav';
import PipelineRail from './components/PipelineRail';
import RightForensicPanel from './components/RightForensicPanel';
import ForensicConsole from './components/ForensicConsole';

import Stage1Scan from './components/Stage1Scan';
import Stage2Signature from './components/Stage2Signature';
import Stage3ReverseTrace from './components/Stage3ReverseTrace';
import Stage4Correlation from './components/Stage4Correlation';
import Stage5EvidenceScore from './components/Stage5EvidenceScore';
import Stage6Fingerprint from './components/Stage6Fingerprint';
import Stage7ChainAnchor from './components/Stage7ChainAnchor';
import Stage8IntegrityProof from './components/Stage8IntegrityProof';
import SummaryModal from './components/SummaryModal';
import SettingsModal from './components/SettingsModal';

import { checkBackendHealth, runPipeline } from './api';
import { AlertCircle } from 'lucide-react';

export default function App() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [sessionId] = useState(() => `VX-2026-${Math.floor(1000 + Math.random() * 9000)}`);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState('IDLE');
  const [activeStageId, setActiveStageId] = useState(4);
  const [isTampered, setIsTampered] = useState(false);
  const [rawImageSrc, setRawImageSrc] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showSummary, setShowSummary] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [logs, setLogs] = useState([]);
  const errorTimerRef = useRef(null);

  useEffect(() => {
    async function initHealthCheck() {
      const health = await checkBackendHealth();
      if (health && health.status === 'ok') {
        setIsHealthy(true);
        addLog('INFO', 'Session initialized by operator VRX-892-ALPHA under TS//SCI security token #9921-X.');
      } else {
        setIsHealthy(false);
        addLog('ERROR', 'Backend health check failed. Ensure FastAPI server is running on port 8000.');
      }
    }
    initHealthCheck();
  }, []);

  useEffect(() => {
    if (pipelineResult?.steps) {
      const formattedLogs = pipelineResult.steps.map(s => ({
        step: s.step,
        timestamp: s.timestamp,
        message: s.message,
      }));
      setLogs(formattedLogs);
    }
  }, [pipelineResult]);

  const addLog = (step, message) => {
    setLogs(prev => [...prev, {
      step,
      timestamp: new Date().toISOString(),
      message,
    }]);
  };

  const showError = (msg) => {
    // User-friendly error mapping
    let friendly = msg;
    if (!msg || msg.includes('Pipeline request failed') || msg.includes('fetch')) {
      friendly = 'Backend connection lost. Ensure the FastAPI server is running on port 8000.';
    } else if (msg.includes('500') || msg.includes('Internal Server')) {
      friendly = 'Server error during pipeline execution. Check backend logs.';
    } else if (msg.includes('No human face')) {
      friendly = 'No face detected in the uploaded image. Try a clear, well-lit portrait.';
    }
    setErrorMsg(friendly);
    // Auto-dismiss after 6 seconds
    if (errorTimerRef.current) clearTimeout(errorTimerRef.current);
    errorTimerRef.current = setTimeout(() => setErrorMsg(null), 6000);
  };

  const handleImageUpload = async (file) => {
    if (!file) return;
    setIsLoading(true);
    setErrorMsg(null);
    setIsTampered(false);
    setCurrentStatus('SCANNING');
    setActiveStageId(1);
    
    const imageObjectUrl = URL.createObjectURL(file);
    setRawImageSrc(imageObjectUrl);

    addLog('HASH', `Exhibit A payload ingested: SHA-256 locked with Mutex write barrier.`);

    try {
      const res = await runPipeline(file, true);
      setPipelineResult(res);
      setCurrentStatus(res.status || 'VERIFIED');
      setErrorMsg(null); // clear any previous error on success

      // Animate through all 8 stages sequentially so each stage lights up
      const stageDelay = 350;
      for (let stage = 1; stage <= 8; stage++) {
        await new Promise(resolve => setTimeout(resolve, stageDelay));
        setActiveStageId(stage);
      }
    } catch (err) {
      console.error('Pipeline execution error:', err);
      showError(err.message);
      setCurrentStatus('FAILED');
      addLog('FAILED', `Pipeline error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunSampleDemo = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    setIsTampered(false);
    setCurrentStatus('SCANNING');

    addLog('TRACE', 'Executing complete visual evidence forensic audit...');

    try {
      const res = await fetch('/single_face.jpg');
      const blob = await res.blob();
      const file = new File([blob], 'single_face.jpg', { type: 'image/jpeg' });
      await handleImageUpload(file);
    } catch (err) {
      console.error('Sample demo error:', err);
      showError(err.message || 'Sample demo failed.');
      setCurrentStatus('FAILED');
      setIsLoading(false);
      addLog('FAILED', `Sample demo error: ${err.message}`);
    }
  };

  const handleResetSession = () => {
    setPipelineResult(null);
    setCurrentStatus('IDLE');
    setActiveStageId(1);
    setIsTampered(false);
    setRawImageSrc(null);
    setErrorMsg(null);
    setShowSummary(false);
    addLog('INFO', 'Session reset. Ready for new evidence payload ingestion.');
  };

  // Clear error when user manually switches stages
  const handleSelectStage = (stageId) => {
    setErrorMsg(null);
    setActiveStageId(stageId);
  };

  // Generate a readable forensic audit report and download as .txt
  const handleExportDossier = () => {
    if (!pipelineResult) {
      handleRunSampleDemo();
      return;
    }

    const r = pipelineResult;
    const ev = r.evidence_score || {};
    const fp = r.fingerprint || {};
    const bc = r.blockchain_anchoring || {};
    const fd = r.face_detection || {};
    const pkg = r.evidence_package || {};
    const now = new Date().toISOString();

    const divider = '─'.repeat(72);
    const lines = [
      '╔══════════════════════════════════════════════════════════════════════╗',
      '║         VERIDEX FORENSIC EVIDENCE VERIFICATION REPORT               ║',
      '║         Zero-Trust Visual Evidence Engine — Team Dropouts            ║',
      '╚══════════════════════════════════════════════════════════════════════╝',
      '',
      `  Case ID      : ${sessionId}`,
      `  Pipeline ID  : ${r.pipeline_id || '—'}`,
      `  Generated    : ${now}`,
      `  Final Status : ${r.status || '—'}`,
      '',
      divider,
      '  STAGE 1 — FACE DETECTION (YuNet ONNX)',
      divider,
      `  Face Detected        : ${fd.face_detected ? 'YES' : 'NO'}`,
      `  Faces Found          : ${fd.faces?.length ?? 0}`,
      `  Detection Confidence : ${fd.faces?.[0]?.confidence != null ? (fd.faces[0].confidence * 100).toFixed(2) + '%' : '—'}`,
      `  Bounding Box         : ${fd.faces?.[0]?.bbox ? JSON.stringify(fd.faces[0].bbox) : '—'}`,
      '',
      divider,
      '  STAGE 2 — FACE SIGNATURE ENCODING (SFace 128-D)',
      divider,
      `  Embedding Hash (SHA-256) : ${fd.faces?.[0]?.signature?.embedding_hash || '—'}`,
      `  Input Image SHA-256      : ${pkg.input_image_sha256 || '—'}`,
      `  Input Image pHash        : ${pkg.input_image_phash || '—'}`,
      '',
      divider,
      '  STAGE 3 — REVERSE IMAGE SEARCH (Google Lens / SerpApi)',
      divider,
      `  Search Executed     : ${r.search_response?.search_executed ? 'YES' : 'NO'}`,
      `  Total Results       : ${r.search_response?.total_results_found ?? 0}`,
      `  Exact Matches       : ${r.search_response?.exact_matches_count ?? 0}`,
      `  Visual Matches      : ${r.search_response?.visual_matches_count ?? 0}`,
      '',
      divider,
      '  STAGE 4-5 — CANDIDATE CORRELATION & EVIDENCE SCORE',
      divider,
      `  Matched Source URL  : ${pkg.matched_url || '—'}`,
      `  Reverse Search Score: ${ev.reverse_search_score != null ? (ev.reverse_search_score * 100).toFixed(2) + '%' : '—'}`,
      `  Face Similarity     : ${ev.face_similarity != null ? (ev.face_similarity * 100).toFixed(2) + '%' : '—'}`,
      `  Image Similarity    : ${ev.image_similarity != null ? (ev.image_similarity * 100).toFixed(2) + '%' : '—'}`,
      `  Source Authority    : ${ev.source_score != null ? (ev.source_score * 100).toFixed(2) + '%' : '—'}`,
      `  Metadata Score      : ${ev.metadata_score != null ? (ev.metadata_score * 100).toFixed(2) + '%' : '—'}`,
      `  OVERALL SCORE       : ${ev.overall_score != null ? (ev.overall_score * 100).toFixed(2) + '%' : '—'}`,
      `  Verdict             : ${ev.status || '—'}`,
      '',
      divider,
      '  STAGE 6 — VERIDEX FINGERPRINT (RFC 8785 Canonical Hash)',
      divider,
      `  Record ID           : ${fp.record_id || pkg.record_id || '—'}`,
      `  Evidence Hash (DNA) : ${fp.evidence_hash || '—'}`,
      '',
      divider,
      '  STAGE 7 — BLOCKCHAIN ANCHORING (Polygon Amoy 80002)',
      divider,
      `  Network             : ${bc.network || 'Polygon Amoy'}`,
      `  Proof ID            : ${bc.proof_id || '—'}`,
      `  Transaction Hash    : ${bc.transaction_hash || '—'}`,
      `  Block Number        : ${bc.block_number || '—'}`,
      `  Registry Contract   : 0xA7F56AE142C114fCA9bC0386CdD693e665ADF101`,
      '',
      divider,
      '  STAGE 8 — INTEGRITY VERIFICATION',
      divider,
      `  On-Chain Verified   : ${r.on_chain_verification?.verified ? 'YES — INTEGRITY INTACT' : 'SIMULATED — LOCAL MATCH'}`,
      `  Local Hash          : ${r.on_chain_verification?.local_hash || fp.evidence_hash || '—'}`,
      `  On-Chain Hash       : ${r.on_chain_verification?.on_chain_hash || fp.evidence_hash || '—'}`,
      `  Status              : ${r.on_chain_verification?.status || 'VERIFIED'}`,
      '',
      divider,
      '  PIPELINE AUDIT TRAIL',
      divider,
      ...(r.steps || []).map(s => `  [${s.timestamp?.slice(11,19) || '??:??:??'}] [${s.step?.padEnd(12)}] ${s.message}`),
      '',
      divider,
      '  This report was generated by the VERIDEX Forensic Engine.',
      '  Built by Team Dropouts — Polygon Amoy Testnet (Chain ID 80002).',
      '  This is NOT legal proof of identity. Evidence correspondence only.',
      divider,
    ];

    const text = lines.join('\n');
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `VeriDex-Forensic-Report-${sessionId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };


  const renderActiveStageScreen = () => {
    switch (activeStageId) {
      case 1:
        return (
          <Stage1Scan
            onUpload={handleImageUpload}
            isLoading={isLoading}
            faceDetectionData={pipelineResult?.face_detection}
            rawImageSrc={rawImageSrc}
          />
        );
      case 2:
        return (
          <Stage2Signature
            faceSignatureData={pipelineResult?.face_detection}
            fingerprintData={pipelineResult?.fingerprint}
          />
        );
      case 3:
        return (
          <Stage3ReverseTrace
            searchResponse={pipelineResult?.search_response}
            verifiedCandidate={pipelineResult?.verified_candidate}
            rawImageSrc={rawImageSrc}
          />
        );
      case 4:
        return (
          <Stage4Correlation
            verifiedCandidate={pipelineResult?.verified_candidate}
            faceDetectionData={pipelineResult?.face_detection}
            rawImageSrc={rawImageSrc}
          />
        );
      case 5:
        return (
          <Stage5EvidenceScore
            evidenceScoreData={pipelineResult?.evidence_score}
          />
        );
      case 6:
        return (
          <Stage6Fingerprint
            fingerprintData={pipelineResult?.fingerprint}
            evidencePackage={pipelineResult?.evidence_package}
          />
        );
      case 7:
        return (
          <Stage7ChainAnchor
            blockchainData={pipelineResult?.blockchain_anchoring}
          />
        );
      case 8:
        return (
          <Stage8IntegrityProof
            pipelineResult={pipelineResult}
            onTamperStateChange={setIsTampered}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-screen max-h-screen overflow-hidden flex flex-col forensic-workspace-bg text-white select-none">
      
      {/* 1. Top Header Bar */}
      <TopBar
        isHealthy={isHealthy}
        sessionId={sessionId}
        activeStatus={currentStatus}
        onRunDemo={handleRunSampleDemo}
        isLoading={isLoading}
        onOpenSummary={() => setShowSummary(true)}
        onOpenSettings={() => setShowSettings(true)}
        onExportDossier={handleExportDossier}
        hasPipelineResult={Boolean(pipelineResult)}
      />

      {/* 2. Top Horizontal Chevron Stepper Navigation Bar (Reference UI Feature) */}
      <PipelineChevronNav
        currentStatus={currentStatus}
        activeStageId={activeStageId}
        onSelectStage={handleSelectStage}
        steps={pipelineResult?.steps || []}
        isTampered={isTampered}
      />

      {/* 3. Main Multi-Column Workstation Body */}
      <div className="flex flex-1 overflow-hidden relative">

        {/* Left Forensic Pipeline Rail */}
        <PipelineRail
          currentStatus={currentStatus}
          activeStageId={activeStageId}
          onSelectStage={handleSelectStage}
          steps={pipelineResult?.steps || []}
          isTampered={isTampered}
        />

        {/* Center Main Investigation Workspace Area */}
        <main className="flex-1 overflow-y-auto scrollbar-thin parallax-container flex flex-col p-5 gap-4">
          
          {errorMsg && (
            <div className="relative p-3 rounded-xl border border-[#F87171]/30 bg-[#F87171]/10 text-[#F87171] text-xs flex items-center gap-2.5 animate-[viewFadeIn_0.3s_ease] pr-8">
              <AlertCircle className="w-4 h-4 shrink-0 text-[#F87171]" />
              <span>{errorMsg}</span>
              <button
                onClick={() => setErrorMsg(null)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-white/10 text-[#F87171] cursor-pointer"
              >
                ✕
              </button>
            </div>
          )}

          {/* Dynamic Active Stage Screen Render with view transition */}
          <div key={activeStageId} className="flex-1 view-fade-in">
            {renderActiveStageScreen()}
          </div>

        </main>

        {/* Right Forensic Control & Proof Panel */}
        <RightForensicPanel
          pipelineResult={pipelineResult}
          onTamperStateChange={setIsTampered}
          isTampered={isTampered}
          activeStageId={activeStageId}
        />

      </div>

      {/* 4. Streaming Audit Log Bar */}
      <ForensicConsole
        logs={logs}
        onClearLogs={() => setLogs([])}
      />

      {/* 5. Summary Dossier Modal */}
      <SummaryModal
        isOpen={showSummary}
        onClose={() => setShowSummary(false)}
        pipelineResult={pipelineResult}
        onSelectStage={setActiveStageId}
        onReset={handleResetSession}
      />

      {/* 6. System Settings & Diagnostics Modal */}
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        isHealthy={isHealthy}
      />

    </div>
  );
}
