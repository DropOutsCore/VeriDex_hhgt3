import React from 'react';
import { ShieldCheck, Activity, Cpu, Database, ExternalLink } from 'lucide-react';

export default function Header({ isHealthy, activeStatus }) {
  const contractAddress = "0xA7F56AE142C114fCA9bC0386CdD693e665ADF101";

  return (
    <header className="border-b border-cyan-900/40 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & System Title */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-cyan-950 border border-cyan-500/50 glow-cyan">
            <ShieldCheck className="w-6 h-6 text-cyan-400" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-wider text-cyan-100 font-mono">
                VERIDEX<span className="text-cyan-400">.ENGINE</span>
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800">
                v0.1.0-CORE
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono tracking-tight">
              Visual Evidence Verification & Forensic Blockchain Anchoring Engine
            </p>
          </div>
        </div>

        {/* Network & Node Status Controls */}
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
          {/* Smart Contract Indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900/90 border border-slate-800 text-slate-300">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>CONTRACT:</span>
            <a 
              href={`https://amoy.polygonscan.com/address/${contractAddress}`}
              target="_blank"
              rel="noreferrer"
              className="text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
            >
              {contractAddress.substring(0, 6)}...{contractAddress.substring(38)}
              <ExternalLink className="w-3 h-3 inline" />
            </a>
          </div>

          {/* Polygon Amoy Chain Badge */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-purple-950/40 border border-purple-800/60 text-purple-300">
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            <span>POLYGON AMOY (80002)</span>
          </div>

          {/* Backend Connection Status */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-md border font-semibold ${
            isHealthy 
              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400 glow-emerald' 
              : 'bg-rose-950/40 border-rose-800 text-rose-400 glow-rose'
          }`}>
            <Activity className={`w-3.5 h-3.5 ${isHealthy ? 'animate-pulse' : ''}`} />
            <span>{isHealthy ? 'BACKEND ONLINE' : 'DISCONNECTED'}</span>
          </div>
        </div>

      </div>
    </header>
  );
}
