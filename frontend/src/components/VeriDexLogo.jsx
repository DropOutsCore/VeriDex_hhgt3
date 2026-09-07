import React from 'react';

export default function VeriDexLogo({ className = "w-6 h-6", size = 24 }) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 32 32" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="veridex-grad" x1="2" y1="2" x2="30" y2="30" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#38BDF8" />
          <stop offset="50%" stopColor="#0284C7" />
          <stop offset="100%" stopColor="#D97746" />
        </linearGradient>
      </defs>
      
      {/* Outer Hexagonal Shield Frame */}
      <path 
        d="M16 3L28 8.5V17.5C28 24.2 22.8 29.3 16 31C9.2 29.3 4 24.2 4 17.5V8.5L16 3Z" 
        stroke="url(#veridex-grad)" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        fill="rgba(56, 189, 248, 0.08)"
      />
      
      {/* Stylized V-Aperture Focal Core */}
      <path 
        d="M10 11L16 22L22 11" 
        stroke="#38BDF8" 
        strokeWidth="2.5" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
      />
      
      {/* Biometric Center Dot */}
      <circle cx="16" cy="12" r="2" fill="#D97746" />
    </svg>
  );
}
