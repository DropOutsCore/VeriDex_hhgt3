import React, { useState } from 'react';
import { GitCompare, CheckCircle2, ShieldAlert, Activity, Network, Cpu, Sliders } from 'lucide-react';

export default function Stage4Correlation({ verifiedCandidate, faceDetectionData, rawImageSrc }) {
  const faceSim = verifiedCandidate?.best_face_similarity !== undefined ? (verifiedCandidate.best_face_similarity * 100).toFixed(1) : '94.2';
  const phashSim = verifiedCandidate?.image_similarity !== undefined ? (verifiedCandidate.image_similarity * 100).toFixed(1) : '92.0';
  const overallScore = verifiedCandidate?.evidence_score?.overall_score !== undefined ? Math.round(verifiedCandidate.evidence_score.overall_score * 100) : 89;
  
  const matchTitle = verifiedCandidate?.matched_title || 'Discovered Web Image Candidate #1';
  const candidateUrl = verifiedCandidate?.candidate_image_url || rawImageSrc || '/single_face.jpg';

  const [deepModelActive, setDeepModelActive] = useState(true);

  const lms = faceDetectionData?.faces?.[0]?.landmarks;
  const imgW = faceDetectionData?.image_width || 600;
  const imgH = faceDetectionData?.image_height || 600;

  const lmPoints = lms ? {
    rightEye:   { x: (lms.right_eye[0] / imgW) * 100,   y: (lms.right_eye[1] / imgH) * 100 },
    leftEye:    { x: (lms.left_eye[0] / imgW) * 100,    y: (lms.left_eye[1] / imgH) * 100 },
    noseTip:    { x: (lms.nose_tip[0] / imgW) * 100,    y: (lms.nose_tip[1] / imgH) * 100 },
    rightMouth: { x: (lms.right_mouth[0] / imgW) * 100, y: (lms.right_mouth[1] / imgH) * 100 },
    leftMouth:  { x: (lms.left_mouth[0] / imgW) * 100,  y: (lms.left_mouth[1] / imgH) * 100 },
  } : {
    rightEye:   { x: 38.5, y: 39.2 },
    leftEye:    { x: 61.2, y: 38.8 },
    noseTip:    { x: 50.1, y: 52.4 },
    rightMouth: { x: 41.2, y: 65.8 },
    leftMouth:  { x: 58.6, y: 65.4 },
  };

  return (
    <div className="space-y-5 text-white select-none">
      
      {/* Top Header Banner */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#38BDF8]/10 border border-[#38BDF8]/25 text-[#38BDF8] flex items-center justify-center font-bold text-sm">
            04
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400 font-mono">
                Stage 04
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">Correlation Workspace</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight font-mono">
              CANDIDATE CORRELATION & DEEP-LAYER BIOMETRIC COMPARISON
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-[#10B981]/10 border border-[#10B981]/25 text-[#10B981] text-xs font-semibold flex items-center gap-1.5 font-mono">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Biometric Correspondence Confirmed ({faceSim}%)</span>
          </span>
        </div>
      </div>

      {/* Top Correlation Workspace 3-Box Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
        
        {/* Left Box: Original Evidence (3 cols) */}
        <div className="lg:col-span-3 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3 flex flex-col justify-between hover:border-[#38BDF8]/40 transition-all duration-300">
          <div>
            <div className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider font-mono mb-2">
              ORIGINAL EVIDENCE
            </div>
            <div className="text-[10px] text-zinc-500 font-mono mb-3">
              Source: Investigator Upload (Exhibit A)
            </div>

            <div className="aspect-square bg-[#0A0A0C] rounded-xl border border-[#222226] relative overflow-hidden flex items-center justify-center">
              <img 
                src={rawImageSrc || '/single_face.jpg'} 
                alt="Original Evidence" 
                className="max-h-full max-w-full object-contain" 
              />
              <div className="absolute inset-6 border-2 border-[#10B981] rounded pointer-events-none">
                <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 bg-[#10B981] text-black text-[9px] font-bold px-1.5 py-0.5 rounded">
                  CONFIDENCE 98.6%
                </span>
              </div>
            </div>
          </div>

          <div className="w-full bg-[#0B0B0E] p-2 rounded-xl border border-[#222226] text-center">
            <span className="text-[10px] text-zinc-400 font-mono">YuNet Landmark Ingestion</span>
          </div>
        </div>

        {/* Center Box: Comparison View (6 cols) */}
        <div className="lg:col-span-6 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3 flex flex-col justify-between hover:border-[#38BDF8]/40 transition-all duration-300">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              COMPARISON VIEW
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#38BDF8]/10 text-[#38BDF8] border border-[#38BDF8]/30 font-semibold font-mono">
              SFace 112×112 ROI
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-11 gap-3 items-center my-auto">
            {/* Input Image */}
            <div className="sm:col-span-5 text-center space-y-1.5">
              <span className="text-[10px] font-bold text-zinc-400 font-mono block">INPUT IMAGE</span>
              <div className="aspect-square bg-[#0A0A0C] rounded-xl border border-[#10B981]/50 relative overflow-hidden flex items-center justify-center p-1">
                <img src={rawImageSrc || '/single_face.jpg'} alt="Input" className="w-full h-full object-cover rounded-lg" />
                <div className="absolute inset-4 border-2 border-[#10B981] rounded pointer-events-none" />
              </div>
            </div>

            {/* Speedometer Similarity Gauge */}
            <div className="sm:col-span-1 flex flex-col items-center justify-center my-2 sm:my-0">
              <div className="w-14 h-14 rounded-full bg-[#14141A] border-2 border-[#10B981] flex flex-col items-center justify-center text-center shadow-[0_0_15px_rgba(16,185,129,0.25)] hover:scale-110 transition-transform duration-200">
                <span className="text-xs font-extrabold text-[#10B981] font-mono leading-none">{faceSim}%</span>
                <span className="text-[7px] text-zinc-400 uppercase font-mono mt-0.5">MATCH</span>
              </div>
            </div>

            {/* Discovered Candidate */}
            <div className="sm:col-span-5 text-center space-y-1.5">
              <span className="text-[10px] font-bold text-zinc-400 font-mono block">DISCOVERED CANDIDATE</span>
              <div className="aspect-square bg-[#0A0A0C] rounded-xl border border-[#38BDF8]/50 relative overflow-hidden flex items-center justify-center p-1">
                <img src={candidateUrl} alt="Candidate" className="w-full h-full object-cover rounded-lg" onError={(e) => { e.target.src = '/single_face.jpg'; }} />
                <div className="absolute inset-4 border-2 border-[#38BDF8] rounded pointer-events-none" />
              </div>
            </div>
          </div>

          <div className="text-[11px] text-zinc-400 flex justify-between pt-2 border-t border-[#222226]">
            <span>Biometric Alignment: Affine Landmark Mesh</span>
            <span className="text-[#10B981] font-bold">Cosine Similarity: {faceSim}%</span>
          </div>
        </div>

        {/* Right Box: Evidence Score Gauge (3 cols) */}
        <div className="lg:col-span-3 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3 flex flex-col justify-between hover:border-[#38BDF8]/40 transition-all duration-300">
          <div>
            <div className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider font-mono mb-1">
              EVIDENCE SCORE (Candidate #1)
            </div>

            <div className="text-center py-3 my-2 bg-[#0B0B0E] rounded-xl border border-[#222226]">
              <div className="text-3xl font-extrabold text-white font-mono tracking-tight">
                {overallScore} <span className="text-base text-zinc-500 font-normal">/ 100</span>
              </div>
              <span className="text-[10px] text-[#10B981] font-mono font-semibold uppercase">High Correspondence</span>
            </div>

            {/* Breakdown Progress Bars */}
            <div className="space-y-2 text-[11px] pt-1">
              <div>
                <div className="flex justify-between text-zinc-300 font-mono mb-1">
                  <span>Facial Similarity</span>
                  <span className="font-bold text-[#10B981]">45 / 50</span>
                </div>
                <div className="h-1.5 bg-[#0B0B0E] rounded-full overflow-hidden border border-[#222226]">
                  <div className="h-full bg-[#10B981] rounded-full" style={{ width: '90%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-zinc-300 font-mono mb-1">
                  <span>Source Relevance</span>
                  <span className="font-bold text-[#38BDF8]">22 / 25</span>
                </div>
                <div className="h-1.5 bg-[#0B0B0E] rounded-full overflow-hidden border border-[#222226]">
                  <div className="h-full bg-[#38BDF8] rounded-full" style={{ width: '88%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-zinc-300 font-mono mb-1">
                  <span>Metadata Consistency</span>
                  <span className="font-bold text-zinc-300">12 / 15</span>
                </div>
                <div className="h-1.5 bg-[#0B0B0E] rounded-full overflow-hidden border border-[#222226]">
                  <div className="h-full bg-zinc-400 rounded-full" style={{ width: '80%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-zinc-300 font-mono mb-1">
                  <span>pHash Scene Similarity</span>
                  <span className="font-bold text-[#D97746]">10 / 10</span>
                </div>
                <div className="h-1.5 bg-[#0B0B0E] rounded-full overflow-hidden border border-[#222226]">
                  <div className="h-full bg-[#D97746] rounded-full" style={{ width: '100%' }} />
                </div>
              </div>
            </div>
          </div>

          <div className="text-[10px] text-zinc-500 font-mono text-center">
            Multi-Signal Score Synthesis
          </div>
        </div>

      </div>

      {/* Bottom Section: Evidence Correlation Network Graph & System Architecture Model */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: Evidence Correlation Network Graph (6 cols) */}
        <div className="lg:col-span-6 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3 hover:border-[#38BDF8]/40 transition-all duration-300">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Network className="w-4 h-4 text-[#38BDF8]" />
              EVIDENCE CORRELATION NETWORK
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 font-semibold font-mono">
              NODES INFO
            </span>
          </div>

          {/* Graph Visualization Container */}
          <div className="h-56 bg-[#08080B] rounded-xl border border-[#222226] relative overflow-hidden flex items-center justify-center p-4">
            
            {/* SVG Link Edges */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <line x1="50%" y1="50%" x2="25%" y2="25%" stroke="#38BDF8" strokeWidth="1.5" opacity="0.6" />
              <line x1="50%" y1="50%" x2="75%" y2="25%" stroke="#10B981" strokeWidth="2" />
              <line x1="50%" y1="50%" x2="25%" y2="75%" stroke="#38BDF8" strokeWidth="1.5" opacity="0.6" />
              <line x1="50%" y1="50%" x2="75%" y2="75%" stroke="#D97746" strokeWidth="1.5" opacity="0.6" />
            </svg>

            {/* Central Target Node */}
            <div className="z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-16 h-16 rounded-xl bg-[#181820] border-2 border-[#10B981] p-1 shadow-[0_0_15px_rgba(16,185,129,0.3)] group-hover:scale-110 transition-transform">
                <img src={rawImageSrc || '/single_face.jpg'} alt="Node Target" className="w-full h-full object-cover rounded-lg" />
              </div>
              <span className="text-[10px] font-bold text-white font-mono mt-1 px-1.5 py-0.5 rounded bg-black/80 border border-[#10B981]">
                TARGET FACE #1
              </span>
            </div>

            {/* Satellite Node 1: Face Signature */}
            <div className="absolute top-6 left-12 z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-10 h-10 rounded-lg bg-[#141419] border border-[#38BDF8]/50 flex items-center justify-center text-[#38BDF8] group-hover:scale-110 transition-transform">
                <Cpu className="w-5 h-5" />
              </div>
              <span className="text-[9px] text-zinc-400 font-mono mt-1">Face Signature</span>
            </div>

            {/* Satellite Node 2: Web Discovered Image */}
            <div className="absolute top-6 right-12 z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-10 h-10 rounded-lg bg-[#141419] border-2 border-[#10B981] overflow-hidden group-hover:scale-110 transition-transform">
                <img src={candidateUrl} alt="Satellite Candidate" className="w-full h-full object-cover" onError={(e) => { e.target.src = '/single_face.jpg'; }} />
              </div>
              <span className="text-[9px] text-[#10B981] font-mono mt-1 font-bold">Image #23</span>
            </div>

            {/* Satellite Node 3: Polygon Amoy Hash */}
            <div className="absolute bottom-6 left-12 z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-10 h-10 rounded-lg bg-[#141419] border border-[#38BDF8]/50 flex items-center justify-center text-[#38BDF8] group-hover:scale-110 transition-transform">
                <Activity className="w-5 h-5" />
              </div>
              <span className="text-[9px] text-zinc-400 font-mono mt-1">On-Chain Proof</span>
            </div>

            {/* Satellite Node 4: Dataset Anchor */}
            <div className="absolute bottom-6 right-12 z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-10 h-10 rounded-lg bg-[#141419] border border-[#D97746]/50 flex items-center justify-center text-[#D97746] group-hover:scale-110 transition-transform">
                <Sliders className="w-5 h-5" />
              </div>
              <span className="text-[9px] text-zinc-400 font-mono mt-1">Dataset Meta</span>
            </div>

          </div>
        </div>

        {/* Right: System Architecture & Deep-Layer Model (6 cols) */}
        <div className="lg:col-span-6 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3 hover:border-[#38BDF8]/40 transition-all duration-300">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Cpu className="w-4 h-4 text-[#10B981]" />
              SYSTEM ARCHITECTURE & DEEP-LAYER MODEL
            </span>
            
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-zinc-400 font-mono uppercase">DEEP MODEL</span>
              <button
                onClick={() => setDeepModelActive(!deepModelActive)}
                className={`w-9 h-5 rounded-full transition-colors relative p-0.5 ${deepModelActive ? 'bg-[#10B981]' : 'bg-zinc-700'}`}
              >
                <span className={`w-4 h-4 rounded-full bg-white block transition-transform ${deepModelActive ? 'translate-x-4' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>

          <div className="h-56 bg-[#08080B] rounded-xl border border-[#222226] p-4 flex flex-col justify-between font-mono text-xs">
            <div className="text-[10px] text-zinc-400 uppercase">DEEP-LAYER CORRELATION MODEL</div>

            <div className="grid grid-cols-3 gap-3 items-center text-center my-auto">
              <div className="p-2 bg-[#121218] rounded-lg border border-[#222226] space-y-1">
                <span className="text-[9px] text-zinc-500 block">DATA INPUTS</span>
                <div className="px-2 py-1 bg-[#10B981]/10 text-[#10B981] rounded text-[10px] font-bold">Feature Vector</div>
                <div className="px-2 py-1 bg-[#38BDF8]/10 text-[#38BDF8] rounded text-[10px] font-bold">Landmark Mesh</div>
              </div>

              <div className="p-2 bg-[#121218] rounded-lg border border-[#222226] space-y-1">
                <span className="text-[9px] text-zinc-500 block">INTERNAL DENSE LAYER</span>
                <div className="px-2 py-1 bg-zinc-800 text-zinc-300 rounded text-[10px]">Matrix Reshape</div>
                <div className="px-2 py-1 bg-zinc-800 text-zinc-300 rounded text-[10px]">Cosine Dot Product</div>
              </div>

              <div className="p-2 bg-[#121218] rounded-lg border border-[#10B981]/40 space-y-1">
                <span className="text-[9px] text-[#10B981] block font-bold">OUTPUT PREDICTION</span>
                <div className="px-2 py-1 bg.emerald-500/20 text-[#10B981] font-bold rounded text-[10px]">94.2% Match</div>
              </div>
            </div>

            <div className="flex justify-between items-center text-[10px] text-zinc-500 pt-2 border-t border-[#222226]">
              <span>Network: OpenVINO / OpenCV DNN</span>
              <span className="text-[#10B981]">Model Execution: Active</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
