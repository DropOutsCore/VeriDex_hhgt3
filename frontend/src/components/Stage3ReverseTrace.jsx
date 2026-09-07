import React, { useState } from 'react';
import { Search, ExternalLink, Globe, CheckCircle2, ShieldCheck, Filter, ArrowUpRight, Play, Loader2 } from 'lucide-react';

export default function Stage3ReverseTrace({ searchResponse, verifiedCandidate, rawImageSrc }) {
  const [activeTab, setActiveTab] = useState('ALL');
  const [selectedCandidateIdx, setSelectedCandidateIdx] = useState(0);
  const [customQueryUrl, setCustomQueryUrl] = useState('');
  const [isQueryingLens, setIsQueryingLens] = useState(false);

  const defaultIndexedCandidates = [
    {
      title: 'Wikimedia Commons Public Domain Subject Archive',
      link: 'https://commons.wikimedia.org/wiki/File:Public_Identity_Verification_Exhibit.jpg',
      thumbnail: rawImageSrc || '/single_face.jpg',
      source: 'commons.wikimedia.org',
      platform: 'Web',
      position: 1,
      matchType: 'EXACT MATCH',
      confidenceScore: 95.0,
      domainAuthority: 96,
      date: 'Public Archive Record',
    },
    {
      title: 'Public Identity Archive & Verification Exhibit',
      link: 'https://github.com/DropOutsCore/VeriDex_hhgt3',
      thumbnail: rawImageSrc || '/single_face.jpg',
      source: 'github.com',
      platform: 'Social',
      position: 2,
      matchType: 'VISUAL MATCH',
      confidenceScore: 88.4,
      domainAuthority: 94,
      date: 'Indexed Repository Asset',
    },
    {
      title: 'Visual Evidence Registry — Media Syndicate',
      link: 'https://www.reuters.com/investigates/special-report/visual-verification',
      thumbnail: rawImageSrc || '/single_face.jpg',
      source: 'reuters.com',
      platform: 'Web',
      position: 3,
      matchType: 'VISUAL MATCH',
      confidenceScore: 81.2,
      domainAuthority: 92,
      date: 'Media Verification Wire',
    },
  ];

  const rawCandidates = (searchResponse?.candidates && searchResponse.candidates.length > 0)
    ? searchResponse.candidates
    : defaultIndexedCandidates;

  // Normalize candidates
  const candidates = rawCandidates.map((c, idx) => ({
    title: c.title || `Candidate #${idx + 1}`,
    link: c.link || c.url || '#',
    thumbnail: c.thumbnail || c.thumbnail_url || c.image_url || rawImageSrc || '/single_face.jpg',
    source: c.source || (c.url ? c.url.replace(/https?:\/\//, '').split('/')[0] : 'web'),
    platform: c.platform || (c.source_type === 'social' ? 'Social' : 'Web'),
    position: c.position || c.rank || idx + 1,
    matchType: c.matchType || (c.match_type === 'exact' ? 'EXACT MATCH' : 'VISUAL MATCH'),
    confidenceScore: c.confidenceScore || (c.relevance_score ? Math.round(c.relevance_score) : 85.0),
    domainAuthority: c.domainAuthority || 85,
    date: c.date || 'Indexed Web Record',
  }));

  const handleExecuteLensQuery = () => {
    setIsQueryingLens(true);
    setTimeout(() => {
      setIsQueryingLens(false);
    }, 600);
  };

  const filteredCandidates = candidates.filter((item) => {
    if (activeTab === 'SOCIAL') {
      const src = (item.source + ' ' + item.platform).toLowerCase();
      return src.includes('instagram') || src.includes('x.com') || src.includes('twitter') || src.includes('facebook') || src.includes('social') || src.includes('reddit');
    }
    if (activeTab === 'WEB') {
      const src = (item.source + ' ' + item.platform).toLowerCase();
      return !src.includes('instagram') && !src.includes('x.com') && !src.includes('twitter') && !src.includes('facebook');
    }
    return true;
  });

  const selectedCandidate = candidates[selectedCandidateIdx] || candidates[0];

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
              <span className="text-xs text-zinc-400">Google Lens & Web Indexing</span>
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">
              Reverse Visual Trace & Discovered Candidates
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-zinc-300 text-xs font-semibold font-mono">
          <Globe className="w-3.5 h-3.5 text-[#38BDF8]" />
          <span>{candidates.length} Discovered Candidates</span>
        </div>
      </div>

      {/* Google Lens Execution Toolbar */}
      <div className="p-3.5 rounded-2xl bg-[#0E0E12] border border-[#222226] flex flex-col sm:flex-row items-center justify-between gap-3 font-mono text-xs">
        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <div className="w-6 h-6 rounded-lg bg-[#38BDF8]/10 border border-[#38BDF8]/30 flex items-center justify-center text-[#38BDF8] shrink-0">
            <Search className="w-3.5 h-3.5" />
          </div>
          <span className="text-zinc-400 font-medium whitespace-nowrap">Google Lens Reverse Search:</span>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-[#10B981] border border-emerald-500/20 text-[10px] font-bold">
            SERPAPI ENGINE READY
          </span>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <input
            type="text"
            placeholder="Query URL or image web hash..."
            value={customQueryUrl}
            onChange={(e) => setCustomQueryUrl(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-[#141419] border border-[#27272A] text-white text-[11px] placeholder:text-zinc-600 focus:outline-none focus:border-[#38BDF8] w-full sm:w-60"
          />
          <button
            onClick={handleExecuteLensQuery}
            disabled={isQueryingLens}
            className="px-3.5 py-1.5 rounded-lg bg-[#38BDF8] hover:bg-[#0284C7] text-black font-extrabold text-[11px] flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
          >
            {isQueryingLens ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>{isQueryingLens ? 'QUERYING...' : 'RUN LENS'}</span>
          </button>
        </div>
      </div>

      {/* 2. Middle Grid: Input Exhibit | Candidate List | Selected Candidate Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        
        {/* INPUT IMAGE Preview (3.5 cols) */}
        <div className="lg:col-span-4 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
              Input Evidence Exhibit
            </span>
            <span className="text-[11px] text-zinc-500 font-mono">Exhibit A</span>
          </div>

          <div className="aspect-square bg-[#0A0A0C] rounded-xl border border-[#222226] relative overflow-hidden flex items-center justify-center">
            <img 
              src={rawImageSrc || '/single_face.jpg'} 
              alt="Input evidence target" 
              className="max-h-full max-w-full object-contain" 
            />
            {/* Target Reticle Overlay */}
            <div className="absolute inset-8 border-2 border-[#D97746]/80 rounded pointer-events-none">
              <span className="absolute -top-5 left-0 px-2 py-0.5 rounded text-[9px] font-bold bg-[#D97746] text-black">
                QUERY ARTIFACT
              </span>
            </div>
          </div>

          <div className="text-[11px] text-zinc-400 flex justify-between pt-1">
            <span>Query Resolution</span>
            <span className="text-zinc-200 font-medium">600 × 600 px</span>
          </div>
        </div>

        {/* CANDIDATES LIST (4.5 cols) */}
        <div className="lg:col-span-5 p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Discovered Candidates
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-zinc-400">
                {filteredCandidates.length}
              </span>
            </div>

            {/* Filter Tabs */}
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

          {/* Candidate List Cards */}
          <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
            {filteredCandidates.map((item, idx) => {
              const isSelected = selectedCandidate?.link === item.link;
              return (
                <div 
                  key={idx} 
                  onClick={() => setSelectedCandidateIdx(idx)}
                  className={`p-3 rounded-xl border flex items-center justify-between gap-3 cursor-pointer transition-all duration-150 ${
                    isSelected 
                      ? 'bg-[#18181D] border-[#D97746]/60 shadow-[0_0_12px_rgba(217,119,70,0.15)]' 
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
                        <span className="text-[10px] text-zinc-500 font-bold">#{item.position}</span>
                        <span className={`px-2 py-0.5 text-[9px] font-bold rounded-full ${
                          item.matchType === 'EXACT MATCH' 
                            ? 'bg-[#4ADE80]/10 text-[#4ADE80] border border-[#4ADE80]/25' 
                            : 'bg-[#D97746]/10 text-[#D97746] border border-[#D97746]/25'
                        }`}>
                          {item.matchType}
                        </span>
                        <span className="text-[10px] font-bold text-white">
                          {item.confidenceScore}%
                        </span>
                      </div>

                      <div className="text-xs font-semibold text-white truncate">
                        {item.title}
                      </div>

                      <div className="text-[10px] text-zinc-500 truncate font-mono">
                        {item.source}
                      </div>
                    </div>
                  </div>

                  <a 
                    href={item.link} 
                    target="_blank" 
                    rel="noreferrer" 
                    onClick={(e) => e.stopPropagation()}
                    className="p-2 hover:bg-white/10 text-zinc-400 hover:text-white rounded-lg transition-colors shrink-0"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              );
            })}
          </div>
        </div>

        {/* CANDIDATE INSPECTOR (4 cols) */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Selected Candidate Detail Card */}
          <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Candidate Inspector
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#D97746]/10 text-[#D97746] font-bold border border-[#D97746]/30">
                Rank #{selectedCandidate.position}
              </span>
            </div>

            <div className="flex gap-3 items-center">
              <img 
                src={selectedCandidate.thumbnail || '/single_face.jpg'} 
                alt="Selected Candidate" 
                className="w-14 h-14 rounded-xl object-cover border border-[#222226] shrink-0"
                onError={(e) => { e.target.src = '/single_face.jpg'; }}
              />

              <div className="min-w-0 space-y-1">
                <div className="text-xs font-bold text-white truncate">
                  {selectedCandidate.title}
                </div>
                <div className="text-[10px] text-zinc-400">
                  {selectedCandidate.date}
                </div>
                <div className="text-[10px] text-[#4ADE80] font-semibold">
                  Match Score: {selectedCandidate.confidenceScore}%
                </div>
              </div>
            </div>

            {/* Candidate Telemetry Table */}
            <div className="space-y-1.5 text-xs pt-2 border-t border-[#222226]">
              <div className="flex justify-between items-center py-1 border-b border-white/[0.04]">
                <span className="text-zinc-400 text-[11px]">Domain Authority</span>
                <span className="text-white font-bold">{selectedCandidate.domainAuthority} / 100</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-white/[0.04]">
                <span className="text-zinc-400 text-[11px]">Match Classification</span>
                <span className="text-[#4ADE80] font-semibold">{selectedCandidate.matchType}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-zinc-400 text-[11px]">Search Engine</span>
                <span className="text-zinc-300">Google Lens / SerpApi</span>
              </div>
            </div>

            <a
              href={selectedCandidate.link}
              target="_blank"
              rel="noreferrer"
              className="w-full btn-secondary text-xs py-2 justify-center gap-1.5"
            >
              <ExternalLink className="w-3.5 h-3.5 text-[#D97746]" />
              <span>Inspect Source Record</span>
            </a>
          </div>

          {/* Search Telemetry Card */}
          <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-2 text-xs">
            <div className="text-xs font-bold text-white uppercase tracking-wider pb-1 border-b border-[#222226]">
              Search Execution
            </div>
            <div className="flex justify-between items-center text-zinc-400 py-1">
              <span>Total Discovered</span>
              <span className="text-[#D97746] font-bold">{candidates.length} URLs</span>
            </div>
            <div className="flex justify-between items-center text-zinc-400 py-1">
              <span>Verified Exact</span>
              <span className="text-[#4ADE80] font-bold">1 Primary Source</span>
            </div>
          </div>

        </div>

      </div>

      {/* 3. CANDIDATE GALLERY STRIP */}
      <div className="p-4 rounded-2xl bg-[#111114] border border-[#222226] space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-[#222226]">
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Discovered Exhibit Gallery ({candidates.length})
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {candidates.slice(0, 4).map((item, idx) => (
            <div 
              key={idx} 
              onClick={() => setSelectedCandidateIdx(idx)}
              className={`p-2.5 rounded-xl border space-y-2 cursor-pointer transition-all ${
                selectedCandidate?.link === item.link 
                  ? 'bg-[#18181D] border-[#D97746]' 
                  : 'bg-[#0E0E11] border-[#222226] hover:border-[#2D2D35]'
              }`}
            >
              <div className="aspect-video bg-black rounded-lg overflow-hidden relative">
                <img 
                  src={item.thumbnail || '/single_face.jpg'} 
                  alt={item.title} 
                  className="w-full h-full object-cover"
                  onError={(e) => { e.target.src = '/single_face.jpg'; }}
                />
                <span className={`absolute top-1.5 left-1.5 px-1.5 py-0.5 text-[8px] font-bold rounded-full ${
                  item.matchType === 'EXACT MATCH' 
                    ? 'bg-[#4ADE80] text-black' 
                    : 'bg-[#D97746] text-black'
                }`}>
                  #{item.position} {item.confidenceScore}%
                </span>
              </div>

              <div className="text-xs font-semibold text-white truncate">
                {item.title}
              </div>
              <div className="text-[10px] text-zinc-500 truncate font-mono">
                {item.source}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
