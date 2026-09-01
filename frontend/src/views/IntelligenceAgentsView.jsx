import React from 'react';
import { Bot, Layers, Database, ShieldCheck, Cpu, ArrowRight, CheckCircle2, Sliders } from 'lucide-react';

export default function IntelligenceAgentsView() {
  const agents = [
    {
      id: 'ag_planner',
      name: 'Planner & Query Router',
      framework: 'LangGraph StateGraph',
      status: 'ACTIVE',
      latency: '42 ms',
      description: 'Decomposes complex refinery inquiries into specialized retrieval and SQL sub-tasks.',
      tools: ['Query Classifier', 'Intent Mapper']
    },
    {
      id: 'ag_rag',
      name: 'Permission-Aware RAG Agent',
      framework: 'ChromaDB + SentenceTransformers',
      status: 'ACTIVE',
      latency: '85 ms',
      description: 'Executes RBAC-filtered semantic search with 1-hop self-healing query expansion.',
      tools: ['ChromaDB Vector Store', 'PermissionFilter']
    },
    {
      id: 'ag_telemetry',
      name: 'DuckDB Telemetry Agent',
      framework: 'DuckDB In-Memory Engine',
      status: 'ACTIVE',
      latency: '18 ms',
      description: 'Queries high-frequency sensor time-series tables under AST-level SQL injection guards.',
      tools: ['DuckDB SQL AST Guard', 'Telemetry Aggregator']
    },
    {
      id: 'ag_vision',
      name: 'P&ID Vision & Diagram Agent',
      framework: 'PyMuPDF + OCR Fallback',
      status: 'READY',
      latency: '210 ms',
      description: 'Parses engineering flow diagrams, valve tags, and equipment labels from P&ID sheets.',
      tools: ['P&ID Tag Extractor', 'Table Reconstructor']
    },
    {
      id: 'ag_verifier',
      name: 'Hallucination Firewall & Causal Verifier',
      framework: 'Claim NLI + Causal Leap Guard',
      status: 'ACTIVE',
      latency: '64 ms',
      description: 'Enforces strict evidence grounding and downgrades unproven causal assertions.',
      tools: ['Claim Extractor', 'Causal Leap Downgrader']
    }
  ];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono font-bold tracking-widest text-[#6d675e] uppercase">
            INTELLIGENCE • AGENTS
          </span>
          <h1 className="text-xl font-display font-bold text-[#f5f2ed]">
            Specialized Industrial Agents Hub
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <span className="status-pill-sage">
            <Bot size={12} />
            <span>05 Agents Orchestrated</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Agent Cards Grid */}
        <div className="lg:col-span-8 space-y-3">
          {agents.map((ag) => (
            <div key={ag.id} className="clora-card p-4 space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-[#201d1a] border border-[#3b3630] flex items-center justify-center text-[#d9825b]">
                    <Bot size={16} />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-[#f5f2ed]">{ag.name}</h3>
                    <span className="text-[10px] text-[#6d675e] font-mono">{ag.framework}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="status-pill-sage">{ag.status}</span>
                  <span className="text-[10px] font-mono text-[#a09a90]">{ag.latency}</span>
                </div>
              </div>

              <p className="text-xs text-[#a09a90] leading-relaxed">
                {ag.description}
              </p>

              <div className="flex items-center gap-2 pt-1 border-t border-[#26231f]">
                <span className="text-[10px] text-[#6d675e] font-mono">Bound Tools:</span>
                {ag.tools.map((t, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-[#181614] border border-[#2b2723] text-[10px] text-[#c8c2b8]">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Right: Active Tool Connections & Pipeline Summary */}
        <div className="lg:col-span-4 space-y-4">
          <div className="clora-card p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2">
              <span className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
                Active Tool Connections
              </span>
              <Sliders size={13} className="text-[#d9825b]" />
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-lg bg-[#161412] border border-[#2b2723] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database size={14} className="text-[#10b981]" />
                  <span className="font-medium text-[#f5f2ed]">DuckDB Read-Only</span>
                </div>
                <span className="status-pill-emerald text-[9px]">ACTIVE</span>
              </div>

              <div className="p-2.5 rounded-lg bg-[#161412] border border-[#2b2723] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers size={14} className="text-[#38bdf8]" />
                  <span className="font-medium text-[#f5f2ed]">ChromaDB Vector Store</span>
                </div>
                <span className="status-pill-sage text-[9px]">1,420 Chunks</span>
              </div>

              <div className="p-2.5 rounded-lg bg-[#161412] border border-[#2b2723] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck size={14} className="text-[#d9825b]" />
                  <span className="font-medium text-[#f5f2ed]">SHA-256 Audit Logger</span>
                </div>
                <span className="status-pill-copper text-[9px]">TAMPER-PROOF</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
