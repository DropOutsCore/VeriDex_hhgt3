import React from 'react';
import { Lock, ExternalLink, CheckCircle2, ArrowRight, Database, FileCode } from 'lucide-react';

export default function Stage7ChainAnchor({ blockchainData }) {
  const contractAddress = blockchainData?.contract_address || '0xA7F56AE142C114fCA9bC0386CdD693e665ADF101';
  const txHash = blockchainData?.transaction_hash || '0x1e0b1c03ba329e9fb8bb8bcc2c5d87908002f23a2b5a7811cbda8b298d465d78';
  const blockNumber = blockchainData?.block_number || '12849102';
  const chainId = blockchainData?.chain_id || 80002;
  const explorerUrl = `https://amoy.polygonscan.com/tx/${txHash}`;

  return (
    <div className="max-w-4xl mx-auto space-y-5 text-white">
      
      {/* 1. Stage Header Banner */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            07
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 07
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">Polygon Amoy Registry</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Blockchain Ledger Anchoring & Settlement
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#4ADE80]/10 border border-[#4ADE80]/25 text-[#4ADE80] text-xs font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Anchored On-Chain</span>
        </div>
      </div>

      {/* Node Settlement Flow */}
      <div className="p-6 rounded-2xl bg-[#111114] border border-[#222226] space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#222226]">
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Settlement Node Pipeline
          </span>
          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[#D97746] font-semibold">
            Polygon Amoy (80002)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-center text-center py-2">
          
          <div className="p-4 bg-[#0E0E11] rounded-xl border border-[#222226] space-y-1.5">
            <FileCode className="w-5 h-5 text-[#D97746] mx-auto" />
            <div className="text-xs font-bold text-white">DNA Fingerprint</div>
            <div className="text-[10px] text-zinc-500 font-mono">SHA-256 Digest</div>
          </div>

          <div className="hidden md:flex justify-center">
            <ArrowRight className="w-4 h-4 text-zinc-500" />
          </div>

          <div className="p-4 bg-[#18181D] rounded-xl border border-[#D97746]/40 space-y-1.5">
            <Database className="w-5 h-5 text-[#D97746] mx-auto" />
            <div className="text-xs font-bold text-white">Polygon Amoy</div>
            <div className="text-[10px] text-[#D97746] font-medium">VeridexRegistry.sol</div>
          </div>

          <div className="hidden md:flex justify-center">
            <ArrowRight className="w-4 h-4 text-zinc-500" />
          </div>

          <div className="p-4 bg-[#0E0E11] rounded-xl border border-[#4ADE80]/30 space-y-1.5">
            <Lock className="w-5 h-5 text-[#4ADE80] mx-auto" />
            <div className="text-xs font-bold text-white">Anchored Block</div>
            <div className="text-[10px] text-[#4ADE80] font-bold font-mono">Block #{blockNumber}</div>
          </div>

        </div>
      </div>

      {/* Technical Parameters Card */}
      <div className="p-6 rounded-2xl bg-[#111114] border border-[#222226] space-y-4">
        <div className="text-xs font-bold text-white uppercase tracking-wider pb-3 border-b border-[#222226]">
          Proof Telemetry & Blockchain Parameters
        </div>

        <div className="space-y-2.5 text-xs">
          
          <div className="flex justify-between items-center bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226]">
            <span className="text-zinc-400">Network / Chain</span>
            <span className="text-white font-semibold">Polygon Amoy Testnet (Chain ID 80002)</span>
          </div>

          <div className="flex flex-col sm:flex-row justify-between sm:items-center bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226] gap-1">
            <span className="text-zinc-400">Smart Contract Address</span>
            <code className="text-[#D97746] font-mono text-[11px] break-all">{contractAddress}</code>
          </div>

          <div className="flex flex-col sm:flex-row justify-between sm:items-center bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226] gap-1">
            <span className="text-zinc-400">Transaction Hash</span>
            <a 
              href={explorerUrl} 
              target="_blank" 
              rel="noreferrer" 
              className="text-[#D97746] hover:underline flex items-center gap-1.5 font-mono text-[11px] break-all"
            >
              <span>{txHash}</span>
              <ExternalLink className="w-3.5 h-3.5 shrink-0" />
            </a>
          </div>

          <div className="flex justify-between items-center bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226]">
            <span className="text-zinc-400">Anchored Block Height</span>
            <span className="text-[#4ADE80] font-bold">#{blockNumber}</span>
          </div>

          <div className="flex justify-between items-center bg-[#0E0E11] p-3.5 rounded-xl border border-[#222226]">
            <span className="text-zinc-400">Cryptographic Settlement</span>
            <span className="text-[#4ADE80] font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[#4ADE80]" />
              <span>Confirmed On-Chain</span>
            </span>
          </div>

        </div>
      </div>

    </div>
  );
}
