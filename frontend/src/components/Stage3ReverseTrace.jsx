import React, { useState } from 'react';
import { Search, ExternalLink, Check, ChevronLeft, ChevronRight, Filter, Globe, Sparkles } from 'lucide-react';

export default function Stage3ReverseTrace({ searchResponse, verifiedCandidate, rawImageSrc }) {
  const [activeTab, setActiveTab] = useState('ALL');

  const candidates = searchResponse?.candidates || (verifiedCandidate ? [{
    title: verifiedCandidate.matched_title || 'Instagram - @priya.singh',
    link: verifiedCandidate.matched_url || 'https://www.instagram.com/p/sample_portrait',
    thumbnail: verifiedCandidate.candidate_image_url || '/single_face.jpg',
    source: verifiedCandidate.domain || 'instagram.com',
    position: 1,
    matchType: 'EXACT MATCH',
    likes: '2.4K likes',
    date: '6 months ago',
  }] : [
    {
      title: 'Instagram - @priya.singh',
      link: 'https://www.instagram.com/p/sample_portrait',
      thumbnail: '/single_face.jpg',
      source: 'instagram.com',
      position: 1,
      matchType: 'EXACT MATCH',
      likes: '2.4K likes',
      date: '6 months ago',
    },
    {
      title: 'X (Twitter) - @priya_s',
      link: 'https://x.com/priya_s/status/123456789',
      thumbnail: '/single_face.jpg',
      source: 'x.com',
      position: 2,
      matchType: 'VISUAL MATCH',
      likes: '1.2K likes',
      date: '6 months ago',
    },
    {
      title: 'Facebook - Priya Singh',
      link: 'https://facebook.com/photo.php?fbid=987654',
      thumbnail: '/single_face.jpg',
      source: 'facebook.com',
      position: 3,
      matchType: 'VISUAL MATCH',
      likes: '842 likes',
      date: '6 months ago',
    },
    {
      title: 'News Article - Times of India',
      link: 'https://timesofindia.indiatimes.com/news/sample',
      thumbnail: '/single_face.jpg',
      source: 'timesofindia.com',
      position: 4,
      matchType: 'WEB RESULT',
      likes: 'News Article',
      date: '6 months ago',
    }
  ]);

  const topCandidate = candidates[0];

  return (
    <div className="space-y-5 text-white">
      
      {/* 1. Stage Header Banner */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#D97746]/10 border border-[#D97746]/25 text-[#D97746] flex items-center justify-center font-bold text-sm">
            03
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-zinc-400">
                Stage 03
              </span>
              <span className="text-zinc-600">•</span>
              <span className="text-xs text-zinc-400">Multi-Engine Search</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Reverse Visual Trace & Web Index
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-zinc-300 text-xs font-semibold">
          <Globe className="w-3.5 h-3.5 text-[#D97746]" />
          <span>{candidates.length} Matches Discovered</span>
        </div>
      </div>

      {/* 2. Middle Grid: Input Exhibit | Search Results | Meta */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        
        {/* INPUT IMAGE Preview (3.5 cols) */}
        <div className="lg:col-span-4 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
              Input Evidence Exhibit
            </span>
            <span className="text-[11px] text-zinc-500">Exhibit A</span>
          </div>

          <div className="aspect-square bg-[#0A0A0C] rounded-xl border border-[#222226] relative overflow-hidden flex items-center justify-center">
            <img 
              src={rawImageSrc || '/single_face.jpg'} 
              alt="Input evidence target" 
              className="max-h-full max-w-full object-contain" 
            />
            {/* Target Reticle Overlay */}
            <div className="absolute inset-8 border-2 border-[#D97746]/80 rounded pointer-events-none" />
          </div>
        </div>

        {/* SEARCH RESULTS Candidate Cards List (5 cols) */}
        <div className="lg:col-span-5 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Candidates
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-zinc-400">
                {candidates.length}
              </span>
            </div>

            {/* Filter Pills */}
            <div className="flex items-center gap-1">
              {['ALL', 'SOCIAL', 'WEB'].map((tab) => (
                <button 
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-medium transition-all ${
                    activeTab === tab 
                      ? 'bg-[#D97746] text-black font-semibold' 
                      : 'text-zinc-400 hover:text-white bg-white/5'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          {/* Candidate List Items */}
          <div className="space-y-2 max-h-[340px] overflow-y-auto pr-1">
            {candidates.map((item, idx) => (
              <div 
                key={idx} 
                className={`p-3 rounded-xl border flex items-center justify-between gap-3 transition-all duration-150 ${
                  idx === 0 
                    ? 'bg-[#18181D] border-[#D97746]/50 shadow-sm' 
                    : 'bg-[#0E0E11] border-[#222226] hover:border-[#2D2D35] hover:bg-[#131317]'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <img 
                    src={item.thumbnail || '/single_face.jpg'} 
                    alt={item.title} 
                    className="w-12 h-12 rounded-lg object-cover border border-[#222226] shrink-0"
                    onError={(e) => { e.target.src = '/single_face.jpg'; }}
                  />

                  <div className="min-w-0 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-zinc-500 font-bold">#{item.position || idx + 1}</span>
                      <span className={`px-2 py-0.5 text-[9px] font-bold rounded-full ${
                        item.matchType === 'EXACT MATCH' 
                          ? 'bg-[#4ADE80]/10 text-[#4ADE80] border border-[#4ADE80]/25' 
                          : 'bg-[#D97746]/10 text-[#D97746] border border-[#D97746]/25'
                      }`}>
                        {item.matchType || 'VISUAL MATCH'}
                      </span>
                    </div>

                    <div className="text-xs font-semibold text-white truncate">
                      {item.title}
                    </div>

                    <div className="text-[10px] text-zinc-500 truncate">
                      {item.link}
                    </div>
                  </div>
                </div>

                <a 
                  href={item.link} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="p-2 hover:bg-white/10 text-zinc-400 hover:text-white rounded-lg transition-colors shrink-0"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* SEARCH TELEMETRY & TOP CANDIDATE (3.5 cols) */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Search Details Card */}
          <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
            <div className="text-xs font-bold text-white uppercase tracking-wider pb-2 border-b border-[#222226]">
              Search Telemetry
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center text-zinc-400 py-1 border-b border-white/[0.04]">
                <span>Search Provider</span>
                <span className="text-zinc-200 font-semibold flex items-center gap-1">
                  <Search className="w-3 h-3 text-[#D97746]" />
                  Google Lens / SerpApi
                </span>
              </div>

              <div className="flex justify-between items-center text-zinc-400 py-1 border-b border-white/[0.04]">
                <span>Matches Found</span>
                <span className="text-[#D97746] font-bold">14 Candidates</span>
              </div>

              <div className="flex justify-between items-center text-zinc-400 py-1 border-b border-white/[0.04]">
                <span>Exact Matches</span>
                <span className="text-[#4ADE80] font-bold">3 Verified</span>
              </div>

              <div className="flex justify-between items-center text-zinc-400 py-1">
                <span>Execution Time</span>
                <span className="text-zinc-300">4.7s</span>
              </div>
            </div>
          </div>

          {/* Top Candidate Preview Card */}
          <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
            <div className="text-xs font-bold text-white uppercase tracking-wider pb-2 border-b border-[#222226]">
              Top Match Candidate
            </div>

            <div className="flex gap-3 items-center">
              <img 
                src={topCandidate?.thumbnail || '/single_face.jpg'} 
                alt="Top Candidate" 
                className="w-12 h-12 rounded-xl object-cover border border-[#222226] shrink-0"
              />

              <div className="min-w-0 space-y-0.5">
                <div className="text-xs font-bold text-white truncate">
                  {topCandidate?.title || 'Instagram - @priya.singh'}
                </div>
                <div className="text-[10px] text-zinc-500">
                  2.4K likes • Public Post
                </div>
              </div>
            </div>

            <a
              href={topCandidate?.link || '#'}
              target="_blank"
              rel="noreferrer"
              className="w-full btn-secondary text-xs py-2 justify-center gap-1.5"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Inspect Source Record</span>
            </a>
          </div>

        </div>

      </div>

      {/* 3. CANDIDATE GALLERY BAR */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Discovered Exhibit Gallery
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {candidates.slice(0, 5).map((item, idx) => (
            <div key={idx} className="p-2.5 rounded-xl bg-[#0E0E11] border border-[#222226] space-y-2 hover:border-[#2D2D35] transition-all">
              <div className="aspect-video bg-black rounded-lg overflow-hidden relative">
                <img 
                  src={item.thumbnail || '/single_face.jpg'} 
                  alt={item.title} 
                  className="w-full h-full object-cover"
                />
                <span className={`absolute top-1.5 left-1.5 px-1.5 py-0.5 text-[8px] font-bold rounded-full ${
                  item.matchType === 'EXACT MATCH' 
                    ? 'bg-[#4ADE80] text-black' 
                    : 'bg-[#D97746] text-black'
                }`}>
                  #{idx+1} {item.matchType === 'EXACT MATCH' ? 'EXACT' : 'VISUAL'}
                </span>
              </div>

              <div className="text-xs font-medium text-white truncate">
                {item.title}
              </div>
              <div className="text-[10px] text-zinc-500 truncate">
                {item.source || 'web.archive'}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
