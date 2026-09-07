import React, { useRef, useState } from 'react';
import { Upload, CheckCircle2, Scan, Image as ImageIcon } from 'lucide-react';

export default function Stage1Scan({ onUpload, isLoading, faceDetectionData, rawImageSrc }) {
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files?.[0]) onUpload(e.dataTransfer.files[0]);
  };

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) onUpload(e.target.files[0]);
  };

  const face        = faceDetectionData?.faces?.[0];
  const bbox        = face?.bbox;
  const confidence  = face?.confidence ? (face.confidence * 100).toFixed(1) : null;
  const imgW        = faceDetectionData?.image_width  || 600;
  const imgH        = faceDetectionData?.image_height || 600;

  const bboxStyle = bbox ? {
    left:   `${(bbox[0] / imgW) * 100}%`,
    top:    `${(bbox[1] / imgH) * 100}%`,
    width:  `${(bbox[2] / imgW) * 100}%`,
    height: `${(bbox[3] / imgH) * 100}%`,
  } : { left:'24%', top:'18%', width:'52%', height:'56%' };

  const hasResult = Boolean(faceDetectionData?.face_detected);

  return (
    <div className="max-w-4xl mx-auto space-y-5 text-white">
      
      {/* Stage Header Banner */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-[#111114] border border-[#222226]">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            01
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 01
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">YuNet Detection Model</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Target Face Scanner & Ingestion
            </h2>
          </div>
        </div>

        {hasResult && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] text-xs font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Face Detected ({confidence}%)</span>
          </div>
        )}
      </div>

      <div className={`grid gap-5 ${rawImageSrc ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'}`}>
        
        {/* Upload Zone */}
        {!rawImageSrc ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleDrop}
            className={`p-12 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center gap-4 cursor-pointer transition-all duration-200 ${
              isDragOver 
                ? 'border-[#D97746] bg-[#D97746]/5' 
                : 'border-[#2D2D35] bg-[#111114] hover:border-zinc-500 hover:bg-[#151519]'
            }`}
          >
            <div className="w-14 h-14 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
              <Upload className="w-6 h-6 text-[#D97746]" />
            </div>

            <div className="text-center space-y-1">
              <div className="text-sm font-semibold text-white">
                {isLoading ? 'Ingesting & Scanning Target Image...' : 'Click or Drag Target Image to Ingest'}
              </div>
              <div className="text-xs text-zinc-400">
                Supports JPG, PNG, WebP up to 25MB
              </div>
            </div>

            <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[11px] text-zinc-400 font-medium">
              YuNet 5-Point Landmark Analysis
            </div>
          </div>
        ) : (
          /* Scanned Image Preview with Bounding Box */
          <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Ingested Evidence Payload
              </span>
              <span className="text-[11px] text-zinc-500">
                {imgW} × {imgH} px
              </span>
            </div>

            <div className="relative rounded-xl overflow-hidden bg-[#0A0A0C] border border-[#222226] aspect-square flex items-center justify-center">
              <img
                src={rawImageSrc}
                alt="Target evidence"
                className="w-full h-full object-contain"
              />

              {/* Bounding Box Reticle */}
              {hasResult && (
                <div
                  className="absolute border-2 border-[#D97746] rounded pointer-events-none transition-all duration-300"
                  style={bboxStyle}
                >
                  <span className="absolute -top-5 left-0 px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#D97746] text-black">
                    FACE #1 ({confidence}%)
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Scan Telemetry & Metrics */}
        {rawImageSrc && (
          <div className="space-y-4">
            <div className="p-5 rounded-2xl bg-[#111114] border border-[#222226] space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#222226]">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Landmark Telemetry
                </span>
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[#D97746] font-semibold">
                  SFace 128-D
                </span>
              </div>

              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between py-1 border-b border-white/[0.04]">
                  <span className="text-zinc-400">Detection Model</span>
                  <span className="text-zinc-200 font-semibold">YuNet OnnxRuntime</span>
                </div>
                <div className="flex justify-between py-1 border-b border-white/[0.04]">
                  <span className="text-zinc-400">Detection Confidence</span>
                  <span className="text-[#4ADE80] font-semibold">{confidence ? `${confidence}%` : 'Evaluating...'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-white/[0.04]">
                  <span className="text-zinc-400">Bounding Box (x, y, w, h)</span>
                  <span className="text-zinc-300 font-mono text-[11px]">
                    {bbox ? `[${bbox.join(', ')}]` : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-white/[0.04]">
                  <span className="text-zinc-400">Landmarks Detected</span>
                  <span className="text-zinc-200 font-semibold">5 Points (Eyes, Nose, Mouth)</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-zinc-400">Embeddings Extracted</span>
                  <span className="text-[#D97746] font-semibold">128-Dimensional Float Vector</span>
                </div>
              </div>
            </div>

            {/* Re-upload Trigger */}
            <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between">
              <div className="text-xs text-zinc-400">
                Want to test a different exhibit?
              </div>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="btn-secondary text-xs"
              >
                Upload New Image
              </button>
            </div>
          </div>
        )}

      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />
    </div>
  );
}
