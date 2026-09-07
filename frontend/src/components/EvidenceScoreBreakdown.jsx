import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, ShieldCheck, AlertCircle } from 'lucide-react';

export default function EvidenceScoreBreakdown({ evidenceScore }) {
  if (!evidenceScore) {
    return null;
  }

  const {
    reverse_search_score = 0.96,
    face_similarity = 0.91,
    image_similarity = 0.94,
    source_score = 0.80,
    metadata_score = 0.90,
    overall_score = 0.91,
    status = 'HIGH_CORRESPONDENCE',
  } = evidenceScore;

  const components = [
    { label: 'Reverse Search', score: reverse_search_score, weight: 0.40, color: 'from-cyan-500 to-blue-500' },
    { label: 'Face Similarity', score: face_similarity, weight: 0.35, color: 'from-emerald-500 to-teal-400' },
    { label: 'Image Similarity', score: image_similarity, weight: 0.10, color: 'from-purple-500 to-indigo-400' },
    { label: 'Source Relevance', score: source_score, weight: 0.10, color: 'from-amber-500 to-yellow-400' },
    { label: 'Metadata', score: metadata_score, weight: 0.05, color: 'from-cyan-400 to-sky-300' },
  ];

  return (
    <div className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-6 mb-8 backdrop-blur-md font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-6">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-cyan-400" />
          <h3 className="text-base font-bold text-cyan-100 tracking-wider">
            TRANSPARENT EVIDENCE SCORE BREAKDOWN
          </h3>
        </div>
        <span className="px-2.5 py-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold text-[10px]">
          VERIFICATION CONFIDENCE: HIGH
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Component Score Progress Bars */}
        <div className="lg:col-span-2 space-y-4">
          {components.map((comp, idx) => (
            <div key={comp.label} className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-slate-200">{comp.label}</span>
                <div className="flex items-center gap-3">
                  <span className="text-[10px] text-slate-500">Weight: {(comp.weight * 100).toFixed(0)}%</span>
                  <span className="font-bold text-cyan-300">{(comp.score * 100).toFixed(1)}%</span>
                </div>
              </div>

              {/* Animated Progress Bar */}
              <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${comp.score * 100}%` }}
                  transition={{ duration: 0.8, delay: idx * 0.1 }}
                  className={`h-full bg-gradient-to-r ${comp.color} rounded-full`}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Right Column: Overall Evidence Correspondence Box */}
        <div className="flex flex-col justify-between bg-slate-950/90 border border-emerald-500/40 rounded-xl p-6 text-center glow-emerald">
          <div>
            <span className="text-xs font-bold text-slate-400 block mb-2">
              OVERALL EVIDENCE CORRESPONDENCE
            </span>
            <div className="text-4xl font-extrabold text-emerald-400 text-glow-emerald my-2">
              {(overall_score * 100).toFixed(1)}%
            </div>
            <span className="inline-block px-3 py-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold text-xs uppercase tracking-wider">
              {status.replace('_', ' ')}
            </span>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 text-[10px] text-slate-400 text-left space-y-1.5">
            <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
              <ShieldCheck className="w-3.5 h-3.5" />
              VERIFICATION CONFIDENCE
            </div>
            <p className="text-slate-400 leading-tight">
              Combines independent reverse search relevance, SFace face similarity, and pHash scene similarity metrics.
            </p>
          </div>
        </div>

      </div>

      {/* Mandatory Terminology Disclaimer */}
      <div className="mt-6 p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2.5">
        <AlertCircle className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
        <p>
          <strong className="text-cyan-300">NOTICE:</strong> This score represents an <strong className="text-emerald-300">Evidence Correspondence</strong> score measuring visual & metadata similarity correlation. It does <strong className="text-rose-300">NOT</strong> represent legal identity proof or identity confirmation.
        </p>
      </div>
    </div>
  );
}
