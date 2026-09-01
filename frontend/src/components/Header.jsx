import React, { useState, useEffect } from 'react';
import { ShieldCheck, User, Cpu } from 'lucide-react';

export default function Header({ activeWorkspace = 'CDU Unit-02 Maintenance', userRole = 'Maintenance Engineer' }) {
  const [timeStr, setTimeStr] = useState('09:42 AM / 31 Aug 2026');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      const date = now.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
      setTimeStr(`${time} / ${date}`);
    };
    updateTime();
    const interval = setInterval(updateTime, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-[#2e2a26] bg-[#171513] px-6 flex items-center justify-between z-30 sticky top-0">
      {/* Brand Logo & Tagline */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-[#24211d] border border-[#d9825b]/40 flex items-center justify-center text-[#d9825b] font-bold text-lg shadow-sm">
          <span className="font-mono tracking-tighter">❖</span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-display font-bold text-base tracking-wider text-[#f5f2ed]">CLORA</span>
            <span className="text-[#6d675e] text-xs font-mono">—</span>
            <span className="text-[#a09a90] text-xs font-semibold uppercase tracking-widest hidden sm:inline">
              Sovereign AI Operating Environment
            </span>
          </div>
        </div>
      </div>

      {/* Center/Right: Target Air-Gapped Mode Widget */}
      <div className="flex items-center gap-4">
        <div className="flex items-center bg-[#1c1a17] border border-[#2e2b26] rounded-xl px-4 py-1.5 shadow-inner">
          {/* Status Indicator */}
          <div className="flex items-center gap-2.5 pr-4 border-r border-[#2e2a25]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] animate-pulse-glow shadow-[0_0_8px_#10b981]" />
            <div className="flex flex-col">
              <span className="text-[#10b981] font-semibold text-xs tracking-wide">AIR-GAPPED MODE</span>
              <span className="text-[#6d675e] text-[10px]">No external connectivity</span>
            </div>
          </div>

          {/* External Requests */}
          <div className="flex flex-col px-4 border-r border-[#2e2a25]">
            <span className="text-[#6d675e] text-[10px]">External Requests</span>
            <span className="text-[#f5f2ed] font-mono font-bold text-xs">0</span>
          </div>

          {/* Data Egress */}
          <div className="flex flex-col px-4 border-r border-[#2e2a25]">
            <span className="text-[#6d675e] text-[10px]">Data Egress</span>
            <span className="text-[#f5f2ed] font-mono font-bold text-xs">0 B</span>
          </div>

          {/* Live Timestamp */}
          <div className="pl-4 text-[#a09a90] font-mono text-xs font-medium">
            {timeStr}
          </div>
        </div>

        {/* User Badge */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-[#2e2a25]">
          <div className="w-8 h-8 rounded-full bg-[#26231f] border border-[#3b3630] flex items-center justify-center text-[#d9825b]">
            <User size={15} />
          </div>
          <div className="hidden md:flex flex-col text-left">
            <span className="text-xs font-semibold text-[#f5f2ed]">{userRole}</span>
            <span className="text-[10px] text-[#6e8c6e] font-medium">Unit 2 Access</span>
          </div>
        </div>
      </div>
    </header>
  );
}
