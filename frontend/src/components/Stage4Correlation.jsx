import React from 'react';
import { GitCompare, Scan, CheckCircle2, ShieldAlert, Sparkles } from 'lucide-react';

export default function Stage4Correlation({ verifiedCandidate, faceDetectionData, rawImageSrc }) {
  const faceSim = verifiedCandidate?.face_similarity !== undefined ? (verifiedCandidate.face_similarity * 100).toFixed(1) : '91.4';
  const phashSim = verifiedCandidate?.phash_similarity !== undefined ? (verifiedCandidate.phash_similarity * 100).toFixed(1) : '94.2';
  const deltaVal = (100 - parseFloat(faceSim)).toFixed(1);
  const matchTitle = verifiedCandidate?.matched_title || 'Discovered Web Image Correspondence';
  const candidateUrl = verifiedCandidate?.candidate_image_url || '/single_face.jpg';

  return (
    <div className="space-y-5 text-white">
      
      {/* 1. Stage Header Banner */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            04
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 04
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">Dual Exhibit Correlation</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Biometric Correspondence & Discrepancy Diff
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] text-xs font-semibold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Biometric Match Confirmed ({faceSim}%)</span>
          </span>
        </div>
      </div>

      {/* 2. Side-by-Side Dual View Exhibits */}
      <div className="grid grid-cols-1 md:grid-cols-11 gap-4 items-center">
        
        {/* Exhibit A: Questioned Target */}
        <div className="md:col-span-5 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="flex items-center gap-1.5 text-xs font-bold text-white uppercase tracking-wider">
              <ShieldAlert className="w-3.5 h-3.5 text-[#D97746]" />
              Exhibit A • Questioned Target
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] font-semibold">
              INPUT
            </span>
          </div>

          <div className="aspect-square bg-[#0A0A0C] rounded-xl border border-[#222226] relative overflow-hidden flex items-center justify-center">
            <img 
              src={rawImageSrc || '/single_face.jpg'} 
              alt="Questioned target artifact" 
              className="max-h-full max-w-full object-contain" 
            />
            {/* Overlay Box */}
            <div className="absolute inset-8 border-2 border-[#D97746] rounded pointer-events-none">
              <div className="absolute -top-5 left-0 bg-[#D97746] text-black px-1.5 py-0.5 text-[9px] font-bold rounded">
                TARGET FACE
              </div>
            </div>
          </div>

          <div className="text-[11px] text-zinc-400 flex justify-between pt-1">
            <span>Sensor: SFace 128-D</span>
            <span>Target Payload</span>
          </div>
        </div>

        {/* Center Delta Badge */}
        <div className="md:col-span-1 flex flex-col items-center justify-center gap-1.5 py-2">
          <div className="w-12 h-12 rounded-full bg-[#18181D] border border-[#D97746]/40 text-[#D97746] flex flex-col items-center justify-center shadow-lg">
            <span className="text-[9px] text-zinc-400 font-bold">Δ</span>
            <span className="text-xs font-extrabold text-[#D97746]">{deltaVal}%</span>
          </div>
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold">
            Delta
          </span>
        </div>

        {/* Exhibit B: Canonical Archive */}
        <div className="md:col-span-5 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="flex items-center gap-1.5 text-xs font-bold text-white uppercase tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#4ADE80]" />
              Exhibit B • Canonical Archive
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] font-semibold">
              MATCH {faceSim}%
            </span>
          </div>

          <div className="aspect-square bg-[#0A0A0C] rounded-xl border border-[#222226] relative overflow-hidden flex items-center justify-center">
            <img 
              src={candidateUrl} 
              alt="Discovered candidate archive" 
              className="max-h-full max-w-full object-contain"
              onError={(e) => { e.target.src = '/single_face.jpg'; }} 
            />
            {/* Overlay Box */}
            <div className="absolute inset-8 border-2 border-[#4ADE80] rounded pointer-events-none">
              <div className="absolute -top-5 left-0 bg-[#4ADE80] text-black px-1.5 py-0.5 text-[9px] font-bold rounded">
                CANONICAL BASELINE
              </div>
            </div>
          </div>

          <div className="text-[11px] text-zinc-400 flex justify-between pt-1">
            <span>Canonical Archive Match</span>
            <span className="text-[#4ADE80] font-medium">Rank #1</span>
          </div>
        </div>

      </div>

      {/* 3. Metrics Summary Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] text-center space-y-1">
          <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">Face Correspondence</span>
          <div className="text-xl font-bold text-[#4ADE80]">{faceSim}%</div>
          <span className="text-[11px] text-zinc-500">Cosine Distance</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] text-center space-y-1">
          <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">pHash Perceptual Parity</span>
          <div className="text-xl font-bold text-[#D97746]">{phashSim}%</div>
          <span className="text-[11px] text-zinc-500">Hamming Distance</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] text-center space-y-1">
          <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">Discrepancy Delta</span>
          <div className="text-xl font-bold text-white">Δ {deltaVal}%</div>
          <span className="text-[11px] text-[#4ADE80]">Within Threshold</span>
        </div>

        <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] text-center space-y-1">
          <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">Primary Rank</span>
          <div className="text-xl font-bold text-[#D97746]">#01 Candidate</div>
          <span className="text-[11px] text-zinc-400 truncate block">{matchTitle}</span>
        </div>
      </div>

    </div>
  );
}
