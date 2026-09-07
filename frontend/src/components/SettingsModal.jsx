import React from 'react';
import { X, Server, Shield, Database, Sliders, CheckCircle2 } from 'lucide-react';
import VeriDexLogo from './VeriDexLogo';

export default function SettingsModal({ isOpen, onClose, isHealthy }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50 select-none">
      <div className="p-8 rounded-3xl bg-[#111114] border border-[#222226] max-w-lg w-full space-y-6 relative overflow-hidden shadow-2xl">
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full hover:bg-white/10 text-zinc-400 hover:text-white transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header Icon */}
        <div className="flex items-center gap-3 border-b border-[#222226] pb-4">
          <div className="w-10 h-10 rounded-xl bg-[#38BDF8]/10 border border-[#38BDF8]/30 flex items-center justify-center text-[#38BDF8]">
            <VeriDexLogo size={24} />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight font-mono">
              SYSTEM CONFIGURATION & DIAGNOSTICS
            </h2>
            <span className="text-xs text-zinc-400 font-mono">
              VeriDex Engine v2.6.0-ALPHA • Zero-Trust Forensic Core
            </span>
          </div>
        </div>

        {/* Settings Content Grid */}
        <div className="space-y-4 text-xs font-mono">
          
          {/* Backend API Service */}
          <div className="p-3.5 rounded-xl bg-[#0B0B0E] border border-[#222226] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Server className="w-4 h-4 text-[#38BDF8]" />
              <div>
                <div className="text-white font-bold">FastAPI Forensic Service</div>
                <div className="text-zinc-500 text-[10px]">http://127.0.0.1:8000/api/v1</div>
              </div>
            </div>
            <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold flex items-center gap-1 border ${
              isHealthy 
                ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30' 
                : 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30'
            }`}>
              <CheckCircle2 className="w-3 h-3" />
              {isHealthy ? 'ONLINE (0ms)' : 'OFFLINE'}
            </span>
          </div>

          {/* Blockchain Ledger Config */}
          <div className="p-3.5 rounded-xl bg-[#0B0B0E] border border-[#222226] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Database className="w-4 h-4 text-[#D97746]" />
              <div>
                <div className="text-white font-bold">Polygon Amoy Anchor Ledger</div>
                <div className="text-zinc-500 text-[10px]">Chain ID: 80002 • RFC 8785 Canonical</div>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-[#D97746]/10 text-[#D97746] border border-[#D97746]/30 text-[10px] font-bold">
              0xA7F5...F101
            </span>
          </div>

          {/* Biometrics Thresholds */}
          <div className="p-3.5 rounded-xl bg-[#0B0B0E] border border-[#222226] space-y-2">
            <div className="flex items-center gap-2 text-zinc-300 font-bold">
              <Sliders className="w-4 h-4 text-[#38BDF8]" />
              <span>Biometric Match Thresholds</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded bg-[#141419] border border-[#222226]">
                <span className="text-zinc-500 block text-[9px]">SFace Cosine Sim</span>
                <span className="text-white font-bold">0.650 (Match)</span>
              </div>
              <div className="p-2 rounded bg-[#141419] border border-[#222226]">
                <span className="text-zinc-500 block text-[9px]">pHash Max Distance</span>
                <span className="text-white font-bold">12 bits</span>
              </div>
            </div>
          </div>

          {/* Security Policy */}
          <div className="p-3.5 rounded-xl bg-[#0B0B0E] border border-[#222226] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-[#10B981]" />
              <div>
                <div className="text-white font-bold font-mono">Zero-Trust Isolation</div>
                <div className="text-zinc-500 text-[10px]">No Mock Fallbacks • Cryptographic Integrity Enforced</div>
              </div>
            </div>
            <span className="text-[#10B981] font-bold text-[10px]">ACTIVE</span>
          </div>

        </div>

        {/* Footer Close */}
        <div className="pt-2">
          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl bg-[#181820] hover:bg-[#22222E] text-white font-mono font-bold text-xs border border-[#27272A] transition-all duration-200 cursor-pointer"
          >
            CLOSE DIAGNOSTICS
          </button>
        </div>

      </div>
    </div>
  );
}
