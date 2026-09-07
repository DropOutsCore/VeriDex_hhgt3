import React from 'react';
import { Menu, Grid, Clock, User, FileText, Settings, Shield } from 'lucide-react';

export default function FarLeftNavStrip({ activeTab = 'timeline', onSelectTab }) {
  const items = [
    { id: 'menu', icon: Menu, label: 'Menu' },
    { id: 'grid', icon: Grid, label: 'Workspace Grid' },
    { id: 'timeline', icon: Clock, label: 'Investigation Timeline' },
    { id: 'user', icon: User, label: 'Operator Identity' },
    { id: 'dossier', icon: FileText, label: 'Evidence Dossier' },
    { id: 'settings', icon: Settings, label: 'System Settings' },
  ];

  return (
    <aside className="w-13 bg-[#070709] border-r border-[#1C1C22] flex flex-col items-center py-3.5 gap-4 shrink-0 z-30 select-none">
      {/* Top Brand Dot */}
      <div className="w-8 h-8 rounded-xl bg-[#D97746]/10 border border-[#D97746]/30 flex items-center justify-center text-[#D97746] mb-2 shadow-[0_0_12px_rgba(217,119,70,0.2)]">
        <Shield className="w-4 h-4" />
      </div>

      {/* Nav Items */}
      <div className="flex flex-col items-center gap-2 flex-1 w-full px-1.5">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab && onSelectTab(item.id)}
              title={item.label}
              className={`group relative w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 ${
                isActive
                  ? 'bg-[#18181F] text-[#38BDF8] border border-[#38BDF8]/40 shadow-[0_0_12px_rgba(56,189,248,0.25)]'
                  : 'text-zinc-500 hover:text-zinc-200 hover:bg-white/5 hover:border hover:border-white/10'
              }`}
            >
              {isActive && (
                <span className="absolute left-0 w-1 h-5 rounded-r bg-[#38BDF8] shadow-[0_0_8px_#38BDF8]" />
              )}
              <Icon className={`w-4 h-4 transition-transform duration-200 group-hover:scale-110 ${isActive ? 'text-[#38BDF8]' : ''}`} />
              
              {/* Floating Tooltip */}
              <span className="absolute left-14 px-2.5 py-1 rounded-md bg-[#18181D] text-white text-[10px] font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none border border-[#2D2D35] z-50 shadow-xl">
                {item.label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Footer User Info */}
      <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-zinc-400 text-[10px] font-bold">
        VX
      </div>
    </aside>
  );
}
