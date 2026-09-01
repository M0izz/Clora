import React from 'react';
import { Cpu, Bot, BookOpen, Wrench } from 'lucide-react';

export default function LocalIntelligenceCard() {
  return (
    <div className="clora-card p-4 space-y-3.5">
      <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2">
        <span className="text-[11px] font-mono uppercase tracking-widest text-[#6d675e] font-bold">
          LOCAL INTELLIGENCE
        </span>
        <span className="text-[10px] text-[#8ca68c] font-mono">100% On-Premise</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="clora-surface p-2.5 space-y-1">
          <div className="flex items-center gap-1.5 text-[11px] text-[#a09a90]">
            <Cpu size={13} className="text-[#d9825b]" />
            <span>Local Models</span>
          </div>
          <div className="text-xl font-display font-bold text-[#f5f2ed]">03</div>
          <div className="text-[10px] text-[#6d675e]">Llama, Qwen, Phi</div>
        </div>

        <div className="clora-surface p-2.5 space-y-1">
          <div className="flex items-center gap-1.5 text-[11px] text-[#a09a90]">
            <Bot size={13} className="text-[#6e8c6e]" />
            <span>Specialized Agents</span>
          </div>
          <div className="text-xl font-display font-bold text-[#f5f2ed]">05</div>
          <div className="text-[10px] text-[#6d675e]">LangGraph Active</div>
        </div>

        <div className="clora-surface p-2.5 space-y-1">
          <div className="flex items-center gap-1.5 text-[11px] text-[#a09a90]">
            <BookOpen size={13} className="text-[#38bdf8]" />
            <span>Knowledge Base</span>
          </div>
          <div className="text-xl font-display font-bold text-[#f5f2ed]">14</div>
          <div className="text-[10px] text-[#6d675e]">Collections Indexed</div>
        </div>

        <div className="clora-surface p-2.5 space-y-1">
          <div className="flex items-center gap-1.5 text-[11px] text-[#a09a90]">
            <Wrench size={13} className="text-[#fbbf24]" />
            <span>Approved Tools</span>
          </div>
          <div className="text-xl font-display font-bold text-[#f5f2ed]">12</div>
          <div className="text-[10px] text-[#6d675e]">DuckDB, Chroma, AST</div>
        </div>
      </div>

      <div className="p-2.5 rounded-lg bg-[#181614] border border-[#2b2723] text-[10px] text-[#a09a90] space-y-1">
        <span className="text-[#d9825b] font-semibold uppercase tracking-wider block text-[9px]">
          RECOMMENDED CONFIGURATION
        </span>
        <p className="leading-relaxed text-[#8a8377]">
          Document Analysis Agent → Small Local Reasoning Model → Local Knowledge Retrieval → Evidence Verification
        </p>
      </div>
    </div>
  );
}
