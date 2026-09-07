import React from 'react';

export default function VeriDexLogo({ className = "w-6 h-6", size = 24 }) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 32 32" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={`group transition-transform duration-300 ease-out hover:scale-110 ${className}`}
    >
      <defs>
        {/* Precision Metallic Copper / Titanium Gradient */}
        <linearGradient id="shield-rim" x1="4" y1="2" x2="28" y2="30" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#38BDF8" />
          <stop offset="40%" stopColor="#0284C7" />
          <stop offset="70%" stopColor="#B85D2E" />
          <stop offset="100%" stopColor="#D97746" />
        </linearGradient>

        <linearGradient id="lens-core" x1="10" y1="8" x2="22" y2="24" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#1E293B" />
          <stop offset="100%" stopColor="#0B0F17" />
        </linearGradient>

        <radialGradient id="optic-gleam" cx="16" cy="14" r="8" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#38BDF8" stopOpacity="0" />
        </radialGradient>
      </defs>
      
      {/* 1. Precision Shield Outer Shell */}
      <path 
        d="M16 2.5L27.5 7.5V17C27.5 23.5 22.4 28.6 16 30.5C9.6 28.6 4.5 23.5 4.5 17V7.5L16 2.5Z" 
        stroke="url(#shield-rim)" 
        strokeWidth="1.75" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        fill="url(#lens-core)"
      />
      
      {/* 2. Optic Glass Reflex Circle */}
      <circle cx="16" cy="16" r="8.5" fill="url(#optic-gleam)" stroke="rgba(56, 189, 248, 0.25)" strokeWidth="1" strokeDasharray="2 2" />

      {/* 3. Precision V-Aperture Wing */}
      <path 
        d="M10.5 11L16 22L21.5 11" 
        stroke="#38BDF8" 
        strokeWidth="2.2" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        className="transition-all duration-300 group-hover:stroke-[#F08B57]"
      />
      
      {/* 4. Optical Center Reticle Crosshairs */}
      <line x1="16" y1="9" x2="16" y2="12" stroke="#D97746" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="16" y1="20" x2="16" y2="23" stroke="#D97746" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="11" y1="15.5" x2="13.5" y2="15.5" stroke="#D97746" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="18.5" y1="15.5" x2="21" y2="15.5" stroke="#D97746" strokeWidth="1.5" strokeLinecap="round" />

      {/* 5. Central Laser Core Indicator */}
      <circle cx="16" cy="15.5" r="1.75" fill="#D97746" className="animate-pulse" />
    </svg>
  );
}
