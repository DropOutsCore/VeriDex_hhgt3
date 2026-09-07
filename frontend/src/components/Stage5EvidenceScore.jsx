import React from 'react';
import { BarChart3, Award, Info, ShieldCheck } from 'lucide-react';

export default function Stage5EvidenceScore({ evidenceScoreData }) {
  const overallScore = evidenceScoreData?.evidence_score !== undefined ? evidenceScoreData.evidence_score.toFixed(1) : '91.3';
  const qual = evidenceScoreData?.quality_assessment || 'High Correspondence';
  const faceScore = evidenceScoreData?.components?.face_similarity !== undefined ? (evidenceScoreData.components.face_similarity * 100).toFixed(0) : '91';
  const phashScore = evidenceScoreData?.components?.phash_similarity !== undefined ? (evidenceScoreData.components.phash_similarity * 100).toFixed(0) : '94';
  const reverseScore = evidenceScoreData?.components?.reverse_search_rank !== undefined ? (evidenceScoreData.components.reverse_search_rank * 100).toFixed(0) : '96';
  const sourceScore = evidenceScoreData?.components?.source_authority !== undefined ? (evidenceScoreData.components.source_authority * 100).toFixed(0) : '82';

  return (
    <div className="max-w-4xl mx-auto space-y-5 text-white">
      
      {/* 1. Stage Header Banner */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            05
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 05
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">Bayesian Evidence Synthesis</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Evidence Correlation & Confidence Scoring
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] text-xs font-semibold">
          <Award className="w-3.5 h-3.5" />
          <span>Score Synthesized</span>
        </div>
      </div>

      {/* 2. Main Breakdown Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-stretch">
        
        {/* Left: Signal Progress Bars (7 Cols) */}
        <div className="md:col-span-7 p-6 rounded-2xl bg-[#111114] border border-[#222226] space-y-5 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-[#222226]">
            <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-[#D97746]" />
              Multi-Signal Weighted Signals
            </span>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-zinc-400">
              4 Signals
            </span>
          </div>

          <div className="space-y-4">
            
            {/* Signal 1: Face Biometric */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-medium">
                <span className="text-zinc-300">Face Biometric Correspondence (50% Weight)</span>
                <span className="text-[#4ADE80] font-bold">{faceScore}%</span>
              </div>
              <div className="h-2 bg-[#0C0C0E] rounded-full border border-[#222226] overflow-hidden">
                <div style={{ width: `${faceScore}%` }} className="h-full bg-[#4ADE80] rounded-full transition-all duration-500" />
              </div>
            </div>

            {/* Signal 2: pHash */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-medium">
                <span className="text-zinc-300">Perceptual Image Hash (20% Weight)</span>
                <span className="text-[#D97746] font-bold">{phashScore}%</span>
              </div>
              <div className="h-2 bg-[#0C0C0E] rounded-full border border-[#222226] overflow-hidden">
                <div style={{ width: `${phashScore}%` }} className="h-full bg-[#D97746] rounded-full transition-all duration-500" />
              </div>
            </div>

            {/* Signal 3: Reverse Trace Rank */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-medium">
                <span className="text-zinc-300">Reverse Trace Search Ranking (20% Weight)</span>
                <span className="text-[#D97746] font-bold">{reverseScore}%</span>
              </div>
              <div className="h-2 bg-[#0C0C0E] rounded-full border border-[#222226] overflow-hidden">
                <div style={{ width: `${reverseScore}%` }} className="h-full bg-[#D97746] rounded-full transition-all duration-500" />
              </div>
            </div>

            {/* Signal 4: Source Authority */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-medium">
                <span className="text-zinc-300">Source Domain Authority (10% Weight)</span>
                <span className="text-zinc-400 font-bold">{sourceScore}%</span>
              </div>
              <div className="h-2 bg-[#0C0C0E] rounded-full border border-[#222226] overflow-hidden">
                <div style={{ width: `${sourceScore}%` }} className="h-full bg-zinc-500 rounded-full transition-all duration-500" />
              </div>
            </div>

          </div>

          <div className="text-[11px] text-zinc-500 pt-2 border-t border-[#222226]">
            Weights calibrated based on zero-trust verification heuristics.
          </div>
        </div>

        {/* Right: Score Showcase (5 Cols) */}
        <div className="md:col-span-5 p-6 rounded-2xl bg-[#111114] border border-[#222226] flex flex-col items-center justify-between text-center space-y-4">
          <span className="text-xs font-bold text-zinc-400 tracking-wider uppercase">
            Composite Confidence
          </span>

          <div className="my-auto py-2">
            <div className="text-6xl font-extrabold text-[#D97746] tracking-tight">
              {overallScore}
            </div>
            <div className="text-xs font-bold text-[#4ADE80] mt-2 uppercase tracking-widest px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/20 inline-block">
              {qual}
            </div>
          </div>

          <div className="pt-3 border-t border-[#222226] text-[11px] text-zinc-400 flex items-start gap-2 text-left leading-relaxed">
            <Info className="w-4 h-4 text-[#D97746] shrink-0 mt-0.5" />
            <span>
              Evidence correspondence score reflects multi-signal mathematical alignment.
            </span>
          </div>
        </div>

      </div>

    </div>
  );
}
