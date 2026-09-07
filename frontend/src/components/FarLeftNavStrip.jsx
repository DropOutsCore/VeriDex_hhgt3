import React from 'react';
import { Layers, FileText, Settings } from 'lucide-react';
import VeriDexLogo from './VeriDexLogo';

export default function FarLeftNavStrip({ activeTab = 'timeline', onSelectTab }) {
  const items = [
    { id: 'timeline', icon: Layers, label: 'Investigation Pipeline' },
    { id: 'dossier', icon: FileText, label: 'Evidence Dossier' },
    { id: 'settings', icon: Settings, label: 'System Settings' },
  ];

  return (
    <aside className="w-12 bg-[#08080B] border-r border-[#1E1E24] flex flex-col items-center py-3 gap-3 shrink-0 z-30 select-none">
      {/* Top Brand Mark Button -> Redirects to Home / Stage 1 */}
      <button
        onClick={() => onSelectTab && onSelectTab('home')}
        title="Return to Home / Evidence Ingestion"
        className="w-7 h-7 rounded-lg bg-[#38BDF8]/10 hover:bg-[#38BDF8]/20 border border-[#38BDF8]/30 flex items-center justify-center text-[#38BDF8] mb-1 transition-all duration-200 cursor-pointer hover:scale-105"
      >
        <VeriDexLogo size={18} />
      </button>

      {/* Minimalist Nav Items */}
      <div className="flex flex-col items-center gap-2 flex-1 w-full px-1">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab && onSelectTab(item.id)}
              title={item.label}
              className={`group relative w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'bg-[#181820] text-[#38BDF8] border border-[#38BDF8]/40 shadow-[0_0_8px_rgba(56,189,248,0.2)]'
                  : 'text-zinc-500 hover:text-zinc-200 hover:bg-white/5'
              }`}
            >
              {isActive && (
                <span className="absolute left-0 w-0.5 h-4 rounded-r bg-[#38BDF8]" />
              )}
              <Icon className={`w-4 h-4 transition-transform duration-200 group-hover:scale-105 ${isActive ? 'text-[#38BDF8]' : ''}`} />
              
              {/* Tooltip */}
              <span className="absolute left-12 px-2.5 py-1 rounded bg-[#18181D] text-white text-[10px] font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none border border-[#2D2D35] z-50 shadow-md">
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
        className="w-6 h-6 rounded-md bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center text-zinc-400 hover:text-white text-[9px] font-mono font-bold transition-all duration-200 cursor-pointer"
      >
        VX
      </button>
    </aside>
  );
}


