import React from 'react';
import { Layers, FileText, Settings } from 'lucide-react';
import VeriDexLogo from './VeriDexLogo';

export default function FarLeftNavStrip({ activeTab = 'timeline', onSelectTab }) {
  const items = [
    { id: 'timeline', icon: Layers, label: 'Investigation Pipeline', anim: 'group-hover:-translate-y-0.5 group-hover:scale-110' },
    { id: 'dossier', icon: FileText, label: 'Evidence Dossier', anim: 'group-hover:scale-110 group-hover:rotate-3' },
    { id: 'settings', icon: Settings, label: 'System Settings', anim: 'group-hover:rotate-90 duration-500' },
  ];

  return (
    <aside className="w-13 bg-[#08080B] border-r border-[#1C1C22] flex flex-col items-center py-3.5 gap-3 shrink-0 z-30 select-none shadow-xl">
      {/* Top Brand Mark Button -> Tactile Optic Lens */}
      <button
        onClick={() => onSelectTab && onSelectTab('home')}
        title="Return to Home / Evidence Ingestion"
        className="w-8 h-8 rounded-xl bg-gradient-to-b from-[#1A1A22] to-[#0E0E14] hover:from-[#242430] hover:to-[#161620] border border-white/10 hover:border-[#38BDF8]/50 flex items-center justify-center text-[#38BDF8] mb-1.5 transition-all duration-200 cursor-pointer shadow-md hover:shadow-[0_0_14px_rgba(56,189,248,0.25)] active:scale-95 group"
      >
        <VeriDexLogo size={20} />
      </button>

      {/* Realistic Tactile Nav Buttons */}
      <div className="flex flex-col items-center gap-2.5 flex-1 w-full px-1.5">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab && onSelectTab(item.id)}
              title={item.label}
              className={`group relative w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 cursor-pointer active:scale-90 active:translate-y-0.5 ${
                isActive
                  ? 'bg-gradient-to-b from-[#1F1F2A] to-[#12121A] text-[#38BDF8] border border-[#38BDF8]/50 shadow-[0_2px_10px_rgba(0,0,0,0.6),inset_0_1px_0_rgba(255,255,255,0.1)]'
                  : 'bg-gradient-to-b from-[#14141A] to-[#0C0C10] text-zinc-400 hover:text-white border border-white/[0.06] hover:border-white/20 hover:-translate-y-0.5 hover:shadow-[0_4px_12px_rgba(0,0,0,0.5)]'
              }`}
            >
              {isActive && (
                <span className="absolute left-0 w-1 h-4 rounded-r-full bg-[#38BDF8] shadow-[0_0_8px_#38BDF8]" />
              )}
              <Icon className={`w-4 h-4 transition-all duration-300 ease-out ${item.anim} ${isActive ? 'text-[#38BDF8]' : 'text-zinc-400 group-hover:text-zinc-100'}`} />
              
              {/* Tooltip */}
              <span className="absolute left-13 px-2.5 py-1 rounded-md bg-[#16161D] text-white text-[10px] font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 transition-all duration-150 pointer-events-none border border-white/10 z-50 shadow-xl font-mono">
                {item.label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Minimal Footer Badge Button -> Redirects to GitHub Repository */}
      <button
        onClick={() => window.open('https://github.com/DropOutsCore/VeriDex_hhgt3', '_blank')}
        title="Open GitHub Repository (DropOutsCore/VeriDex_hhgt3)"
        className="w-7 h-7 rounded-lg bg-gradient-to-b from-[#16161F] to-[#0D0D12] hover:from-[#20202C] hover:to-[#12121A] border border-white/10 hover:border-white/25 flex items-center justify-center text-zinc-400 hover:text-white text-[9px] font-mono font-bold transition-all duration-200 cursor-pointer active:scale-95 shadow-inner"
      >
        VX
      </button>
    </aside>
  );
}


