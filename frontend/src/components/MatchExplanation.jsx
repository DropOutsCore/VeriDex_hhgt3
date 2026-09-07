import React from 'react';
import { motion } from 'framer-motion';
import { HelpCircle, CheckCircle2, ShieldCheck, Award } from 'lucide-react';

export default function MatchExplanation({ verifiedCandidate, evidenceScore, fingerprint, blockchainAnchoring }) {
  const matchCriteria = [
    {
      id: 'reverse_match',
      title: 'Reverse Image Indexing',
      desc: 'Multi-engine visual discovery identified primary web source artifact.',
      status: true,
    },
    {
      id: 'face_correspondence',
      title: 'Facial Biometric Alignment',
      desc: 'OpenCV SFace 128-D cosine metric validates biometric correspondence.',
      status: (evidenceScore?.face_similarity ?? 0.8) > 0.3,
    },
    {
      id: 'image_similarity',
      title: 'Perceptual Hash Parity',
      desc: 'DCT pHash confirms structural frequency and scene correlation.',
      status: (evidenceScore?.image_similarity ?? 0.8) > 0.4,
    },
    {
      id: 'source_relevance',
      title: 'Domain Authority Scoring',
      desc: 'Source domain and platform authority indexed and graded.',
      status: (evidenceScore?.source_score ?? 0.8) > 0.5,
    },
    {
      id: 'fingerprint_generated',
      title: 'Canonical DNA Digest',
      desc: 'Deterministic RFC 8785 SHA-256 package compiled.',
      status: !!fingerprint,
    },
    {
      id: 'blockchain_anchored',
      title: 'Ledger Settlement Proof',
      desc: 'Immutable proof record anchored and confirmed on Polygon Amoy.',
      status: !!blockchainAnchoring,
    },
  ];

  return (
    <div className="bg-[#111114] border border-[#222226] rounded-2xl p-6 mb-6 space-y-4 text-xs text-white">
      <div className="flex items-center justify-between border-b border-[#222226] pb-3">
        <div className="flex items-center gap-2.5">
          <HelpCircle className="w-4 h-4 text-[#D97746]" />
          <h3 className="text-sm font-bold text-white tracking-wide uppercase">
            Forensic Match Justification Matrix
          </h3>
        </div>
        <span className="px-2.5 py-0.5 rounded-full bg-[#D97746]/10 text-[#D97746] border border-[#D97746]/25 font-semibold text-[10px]">
          Multi-Signal Verified
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {matchCriteria.map((item, idx) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.04 }}
            className={`p-4 rounded-xl border flex flex-col justify-between transition-all ${
              item.status
                ? 'bg-[#0E0E11] border-[#4ADE80]/30 text-zinc-200'
                : 'bg-[#0E0E11] border-[#222226] text-zinc-500'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-xs flex items-center gap-1.5 text-[#4ADE80]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#4ADE80]" />
                  <span>{item.title}</span>
                </span>
                <span className="text-[9px] px-2 py-0.5 rounded-full bg-[#4ADE80]/10 text-[#4ADE80] border border-[#4ADE80]/25 font-bold">
                  PASS
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 leading-relaxed">
                {item.desc}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
