import React, { useRef, useState } from 'react';
import { Upload, Image as ImageIcon, Eye, Target, Sparkles, AlertCircle } from 'lucide-react';

export default function ImageUploadScanner({ onUpload, isLoading, faceDetectionData }) {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (file) => {
    if (!file) return;
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    onUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Compute face bounding box percentage overlay if YuNet detected face
  let bboxStyle = null;
  let detectedFace = null;
  if (faceDetectionData && faceDetectionData.face_detected && faceDetectionData.faces && faceDetectionData.faces[0]) {
    detectedFace = faceDetectionData.faces[0];
    const [x, y, w, h] = detectedFace.bbox;
    const imgW = faceDetectionData.image_width || 500;
    const imgH = faceDetectionData.image_height || 500;

    bboxStyle = {
      left: `${(x / imgW) * 100}%`,
      top: `${(y / imgH) * 100}%`,
      width: `${(w / imgW) * 100}%`,
      height: `${(h / imgH) * 100}%`,
    };
  }

  return (
    <div className="bg-slate-900/80 border border-cyan-900/50 rounded-xl p-6 mb-8 backdrop-blur-md">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h2 className="text-sm font-semibold tracking-wider text-cyan-400 font-mono flex items-center gap-2">
          <Target className="w-4 h-4 text-cyan-400" />
          PRIMARY EVIDENCE IMAGE SCANNER
        </h2>
        <span className="text-xs font-mono text-slate-400">
          OPENCV YUNET + SFACE ENGINE
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Upload Zone & Interactive Preview */}
        <div 
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
          className="relative min-h-[300px] border-2 border-dashed border-cyan-800/60 hover:border-cyan-400 bg-slate-950/60 rounded-xl flex flex-col items-center justify-center p-6 text-center cursor-pointer transition-all duration-300 group overflow-hidden"
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={(e) => e.target.files && handleFileChange(e.target.files[0])} 
            accept="image/*" 
            className="hidden" 
          />

          {previewUrl ? (
            <div className="relative w-full h-full flex items-center justify-center">
              <img 
                src={previewUrl} 
                alt="Primary Evidence" 
                className="max-h-[280px] w-auto object-contain rounded-lg border border-slate-800" 
              />

              {/* Bounding Box Overlay for YuNet Detection */}
              {bboxStyle && (
                <div 
                  style={bboxStyle}
                  className="absolute border-2 border-cyan-400 bg-cyan-400/10 shadow-[0_0_15px_rgba(0,240,255,0.4)] pointer-events-none rounded transition-all duration-500"
                >
                  <span className="absolute -top-6 left-0 px-1.5 py-0.5 bg-cyan-950 border border-cyan-400 text-cyan-300 text-[10px] font-mono font-bold rounded">
                    FACE CONF: {(detectedFace.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}

              {/* Cyber Scanline overlay */}
              {isLoading && (
                <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/20 via-transparent to-cyan-500/20 animate-scanline pointer-events-none" />
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-3">
              <div className="p-4 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8" />
              </div>
              <div>
                <p className="text-sm font-mono font-semibold text-cyan-200">
                  DRAG & DROP EVIDENCE IMAGE HERE
                </p>
                <p className="text-xs text-slate-500 font-mono mt-1">
                  Supports PNG, JPG, WEBP formats (Auto YuNet Face Detection)
                </p>
              </div>
              <button 
                type="button" 
                className="mt-2 px-4 py-2 bg-cyan-950 hover:bg-cyan-900 border border-cyan-500/60 text-cyan-300 text-xs font-mono font-bold rounded-lg transition-colors"
              >
                SELECT LOCAL FILE
              </button>
            </div>
          )}
        </div>

        {/* Metadata & Scan Telemetry Box */}
        <div className="flex flex-col justify-between bg-slate-950/70 border border-slate-800 rounded-xl p-5 font-mono text-xs">
          <div>
            <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-2 mb-3">
              <span className="font-semibold text-cyan-300 flex items-center gap-1.5">
                <Eye className="w-4 h-4 text-cyan-400" /> SCAN TELEMETRY
              </span>
              <span>
                {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB` : 'NO FILE SELECTED'}
              </span>
            </div>

            {detectedFace ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between bg-slate-900/80 p-2.5 rounded border border-cyan-900/40">
                  <span className="text-slate-400">FACE DETECTION STATUS:</span>
                  <span className="text-emerald-400 font-bold">HUMAN FACE DETECTED</span>
                </div>

                <div className="flex items-center justify-between bg-slate-900/80 p-2.5 rounded border border-slate-800">
                  <span className="text-slate-400">DETECTION CONFIDENCE:</span>
                  <span className="text-cyan-300 font-bold">{(detectedFace.confidence * 100).toFixed(2)}%</span>
                </div>

                <div className="flex items-center justify-between bg-slate-900/80 p-2.5 rounded border border-slate-800">
                  <span className="text-slate-400">BOUNDING BOX BBOX:</span>
                  <span className="text-slate-200">[{detectedFace.bbox.join(', ')}]</span>
                </div>

                <div className="flex items-center justify-between bg-slate-900/80 p-2.5 rounded border border-slate-800">
                  <span className="text-slate-400">SFACE VECTOR HASH:</span>
                  <span className="text-purple-300 font-mono text-[11px] truncate max-w-[200px]">
                    {detectedFace.signature?.embedding_hash || 'GENERATED'}
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-8 border border-dashed border-slate-800 rounded-lg text-slate-500">
                <AlertCircle className="w-8 h-8 text-slate-600 mb-2" />
                <p>Upload a target image file to initiate high-speed OpenCV YuNet face detection & SFace signature encoding.</p>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
            <span className="text-[11px] text-slate-500">
              ZERO-TRUST PRIVACY: Raw face vectors are never published on-chain.
            </span>
            {selectedFile && (
              <button
                type="button"
                onClick={() => onUpload(selectedFile)}
                disabled={isLoading}
                className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5" />
                {isLoading ? 'RUNNING PIPELINE...' : 'RE-RUN PIPELINE'}
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
