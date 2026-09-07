import React from 'react';
import { Fingerprint, CheckCircle2, Cpu, Hash } from 'lucide-react';

export default function Stage2Signature({ faceSignatureData, fingerprintData }) {
  const embeddingHash = faceSignatureData?.signature?.embedding_hash
    || fingerprintData?.face_signature_hash
    || '7f9a2b8e41c30d9e924a8bf2c17981a9';
  const dimension = faceSignatureData?.signature?.embedding_dimension || 128;

  // 32 bar heights from a sine wave for visualization
  const bars = Array.from({ length: 32 }, (_, i) => {
    const val = Math.sin(i * 0.45 + 1.2) * 0.45 + 0.5;
    return Math.max(10, Math.floor(val * 90));
  });

  // 16 sampled feature channels
  const features = bars.slice(0, 16);

  return (
    <div className="max-w-4xl mx-auto space-y-5 text-white">
      
      {/* Stage Header Banner */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-[#111114] border border-[#222226]">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            02
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 02
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">SFace Biometric Encoding</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Biometric Face Signature (128-D Vector)
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] text-xs font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Vector Extracted (L2 Norm ~1.0)</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 items-start">
        
        {/* Left: Vector Waveform Graph */}
        <div className="md:col-span-2 p-5 rounded-2xl bg-[#111114] border border-[#222226] space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              128-Dimensional Vector Waveform
            </span>
            <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-[#D97746]/10 border border-[#D97746]/30 text-[#D97746] font-semibold">
              Cosine Metric
            </span>
          </div>

          {/* Bar chart visualization */}
          <div className="h-32 rounded-xl bg-[#0B0B0E] border border-[#222226] p-3 flex items-end gap-1.5 overflow-hidden">
            {bars.map((h, i) => (
              <div
                key={i}
                className="flex-1 rounded-t-sm transition-all duration-300"
                style={{
                  height: `${h}%`,
                  backgroundColor: i % 3 === 0 ? '#D97746' : '#E68A57',
                  opacity: 0.6 + (i % 5) * 0.08,
                }}
              />
            ))}
          </div>

          {/* Feature Channels Grid */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
                Sampled Feature Channels (16 / 128)
              </span>
              <span className="text-[10px] text-zinc-500">
                Float32 Precision
              </span>
            </div>

            <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
              {features.map((val, i) => (
                <div
                  key={i}
                  className="p-2 rounded-lg bg-[#0E0E11] border border-[#222226] text-center"
                >
                  <div className="text-[9px] text-zinc-500 font-medium mb-0.5">C{i+1}</div>
                  <div className="text-[10px] font-bold text-[#D97746]">
                    {(val / 100).toFixed(3)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Parameters & Digest */}
        <div className="space-y-4">
          <div className="p-5 rounded-2xl bg-[#111114] border border-[#222226] space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#222226]">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Vector Attributes
              </span>
              <Cpu className="w-4 h-4 text-[#D97746]" />
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-1 border-b border-white/[0.04]">
                <span className="text-zinc-400">Embedding Engine</span>
                <span className="text-zinc-200 font-semibold">OpenCV SFace ONNX</span>
              </div>
              <div className="flex justify-between py-1 border-b border-white/[0.04]">
                <span className="text-zinc-400">Vector Dimensions</span>
                <span className="text-[#D97746] font-semibold">{dimension}-D Vector</span>
              </div>
              <div className="flex justify-between py-1 border-b border-white/[0.04]">
                <span className="text-zinc-400">Normalization</span>
                <span className="text-zinc-200 font-semibold">Unit L2-Norm</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-zinc-400">Distance Metric</span>
                <span className="text-zinc-200 font-semibold">Cosine Similarity</span>
              </div>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-[#111114] border border-[#222226] space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Signature Hash Digest
              </span>
              <Hash className="w-3.5 h-3.5 text-zinc-500" />
            </div>
            <div className="p-3 rounded-xl bg-[#0B0B0E] border border-[#222226] text-[10px] font-mono text-[#D97746] break-all leading-relaxed">
              {embeddingHash}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
