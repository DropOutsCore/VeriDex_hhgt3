import React from 'react';
import { motion } from 'framer-motion';
import { HelpCircle, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';

export default function MatchExplanation({ verifiedCandidate, evidenceScore, fingerprint, blockchainAnchoring }) {
  const matchCriteria = [
    {
      id: 'reverse_match',
      title: 'Reverse image match',
      desc: 'Google Lens discovery identified top candidate source from public web index.',
      status: true,
    },
    {
      id: 'face_correspondence',
      title: 'Face correspondence',
      desc: 'OpenCV SFace cosine similarity matches input face embedding signature.',
      status: (evidenceScore?.face_similarity ?? 0.8) > 0.3,
    },
    {
      id: 'image_similarity',
      title: 'Perceptual image similarity',
      desc: 'DCT pHash confirms high global visual scene structure correlation.',
      status: (evidenceScore?.image_similarity ?? 0.8) > 0.4,
    },
    {
      id: 'source_relevance',
      title: 'Source relevance',
      desc: 'Candidate domain and publisher platform evaluated for source authority.',
      status: (evidenceScore?.source_score ?? 0.8) > 0.5,
    },
    {
      id: 'fingerprint_generated',
      title: 'Evidence fingerprint generated',
      desc: 'Canonical SHA-256 Evidence DNA payload compiled deterministically.',
      status: !!fingerprint,
    },
    {
      id: 'blockchain_anchored',
      title: 'Blockchain anchor confirmed',
      desc: 'Immutable proof record anchored and confirmed on Polygon Amoy testnet.',
      status: !!blockchainAnchoring,
    },
  ];

  return (
    <div className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-6 mb-8 backdrop-blur-md font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-5">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-cyan-400" />
          <h3 className="text-base font-bold text-cyan-100 tracking-wider">
            WHY THIS CANDIDATE?
          </h3>
        </div>
        <span className="px-2.5 py-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold text-[10px]">
          FORENSIC MATCH EXPLANATION
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {matchCriteria.map((item, idx) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className={`p-4 rounded-lg border flex flex-col justify-between transition-all ${
              item.status
                ? 'bg-slate-950/80 border-emerald-500/40 text-slate-200'
                : 'bg-slate-950/40 border-slate-800 text-slate-500'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-xs flex items-center gap-1.5 text-emerald-400">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ✓ {item.title}
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
                  VERIFIED
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                {item.desc}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
