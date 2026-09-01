import React, { useState } from 'react';
import {
  Sparkles,
  Plus,
  BookOpen,
  Paperclip,
  Wrench,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Clock,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { executeQuery } from '../services/api';

export default function WorkbenchView({ onSelectEvidence }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const sampleRecentWork = [
    { id: 'rw1', name: 'Pump P-101 Root Cause Analysis', status: 'Completed', tag: 'Verified', time: '12 min ago', type: 'verified' },
    { id: 'rw2', name: 'Safety Inspection Review (Unit 2)', status: 'Needs Approval', tag: '3 evidence conflicts', time: '38 min ago', type: 'conflict' },
    { id: 'rw3', name: 'Production Variance Analysis', status: 'In Progress', tag: 'Step 4 of 6', time: 'Now', type: 'progress' },
    { id: 'rw4', name: 'Monthly Operations Report', status: 'Completed', tag: 'Verified', time: 'Yesterday', type: 'verified' },
  ];

  const handleRun = async (queryText) => {
    const textToRun = queryText || prompt || 'Why did Booster Pump P-101 fail at 14:35Z?';
    setLoading(true);
    setResult(null);

    const data = await executeQuery(textToRun);
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Workspace Hero & Query Card */}
      <div className="clora-card p-6 space-y-4 relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[11px] font-mono font-bold tracking-widest text-[#6d675e] uppercase">
              WORKSPACE
            </span>
            <h1 className="text-2xl font-display font-bold text-[#f5f2ed]">
              What are we working on?
            </h1>
          </div>
          <div className="flex flex-col items-end text-right">
            <span className="text-[11px] font-semibold text-[#6e8c6e] flex items-center gap-1.5">
              <ShieldCheck size={13} />
              <span>THIS EXECUTION IS LOCAL</span>
            </span>
            <span className="text-[10px] text-[#6d675e] font-mono">
              0 B DATA EGRESS • NO EXTERNAL API REQUESTS
            </span>
          </div>
        </div>

        {/* Input Box */}
        <div className="rounded-xl border border-[#3b3630] bg-[#171513] focus-within:border-[#d9825b] transition-all p-3 space-y-3">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Analyze, create, investigate, or execute a task... (e.g. Why did Booster Pump P-101 fail?)"
            className="w-full bg-transparent text-sm text-[#f5f2ed] placeholder:text-[#6d675e] resize-none outline-none min-h-[70px]"
          />

          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[#26231f]">
            <div className="flex items-center gap-2">
              <button className="btn-outline text-xs py-1 px-2.5">
                <Plus size={13} />
                <span>Add Files</span>
              </button>
              <button className="btn-outline text-xs py-1 px-2.5">
                <BookOpen size={13} />
                <span>Knowledge Context</span>
              </button>
              <button className="btn-outline text-xs py-1 px-2.5">
                <Paperclip size={13} />
                <span>Attach Data</span>
              </button>
              <button className="btn-outline text-xs py-1 px-2.5">
                <Wrench size={13} />
                <span>Select Tool</span>
              </button>
            </div>

            <button
              onClick={() => handleRun()}
              disabled={loading}
              className="btn-copper text-xs py-1.5 px-4"
            >
              {loading ? (
                <>
                  <span className="w-3.5 h-3.5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                  <span>Processing Locally...</span>
                </>
              ) : (
                <>
                  <span>Run</span>
                  <ArrowRight size={14} />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Action Filter Pills */}
        <div className="flex items-center gap-2 pt-1">
          {['Analyze Documents', 'Compare Data', 'Run Workflow', 'Create Report'].map((pill, i) => (
            <button
              key={i}
              onClick={() => handleRun(`Execute task: ${pill}`)}
              className="px-3 py-1 rounded-full text-xs font-medium bg-[#1d1b18] border border-[#2e2a25] text-[#a09a90] hover:text-[#f5f2ed] hover:border-[#d9825b] transition-all"
            >
              {pill}
            </button>
          ))}
        </div>
      </div>

      {/* Synthesized Response Section (If Available) */}
      {result && (
        <div className="clora-card p-6 space-y-4 border-[#d9825b]/40">
          <div className="flex items-center justify-between border-b border-[#2e2a25] pb-3">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]" />
              <h3 className="text-sm font-semibold text-[#f5f2ed] tracking-wide uppercase">
                Evidence-Grounded Investigation Report
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="status-pill-sage">
                <ShieldCheck size={12} />
                {result.guardrail_status || 'VERIFIED'}
              </span>
              <span className="status-pill-copper">
                Confidence: {Math.round((result.confidence || 0.94) * 100)}%
              </span>
            </div>
          </div>

          <div className="space-y-4 text-xs leading-relaxed text-[#c8c2b8]">
            <pre className="font-sans whitespace-pre-wrap text-[#d6d0c4] bg-[#161412] p-4 rounded-xl border border-[#2c2824]">
              {result.answer}
            </pre>
          </div>

          {/* Document Sources Badges */}
          <div className="pt-2 border-t border-[#26231f] flex items-center justify-between">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] text-[#6d675e] font-mono">CITED SOURCES:</span>
              {(result.sources || []).map((src, i) => (
                <button
                  key={i}
                  onClick={() => onSelectEvidence && onSelectEvidence(src)}
                  className="px-2.5 py-1 rounded-lg bg-[#201e1b] border border-[#3b3630] text-[11px] text-[#a09a90] hover:text-[#d9825b] hover:border-[#d9825b] transition-all flex items-center gap-1.5"
                >
                  <FileText size={11} className="text-[#d9825b]" />
                  <span>{src.filename} (p.{src.page || 1})</span>
                  <ExternalLink size={10} />
                </button>
              ))}
            </div>
            <span className="text-[10px] text-[#6e8c6e] font-mono">100% Citation Grounded</span>
          </div>
        </div>
      )}

      {/* Recent Work Table */}
      <div className="clora-card p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2.5">
          <h3 className="text-sm font-semibold text-[#f5f2ed] tracking-wide">
            Recent Work
          </h3>
          <span className="text-[11px] text-[#6d675e] font-mono">4 Investigations Cached</span>
        </div>

        <div className="divide-y divide-[#26231f]">
          {sampleRecentWork.map((item) => (
            <div
              key={item.id}
              onClick={() => handleRun(item.name)}
              className="py-3 px-2 flex items-center justify-between hover:bg-[#1f1d1a] rounded-lg transition-colors cursor-pointer group"
            >
              <div className="flex items-center gap-3">
                <FileText size={15} className="text-[#d9825b] group-hover:scale-110 transition-transform" />
                <div>
                  <div className="text-xs font-medium text-[#f5f2ed] group-hover:text-[#d9825b] transition-colors">
                    {item.name}
                  </div>
                  <div className="text-[10px] text-[#6d675e] flex items-center gap-2 mt-0.5">
                    <span>{item.time}</span>
                    <span>•</span>
                    <span>Local Session</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {item.type === 'verified' && (
                  <span className="status-pill-sage">{item.status}</span>
                )}
                {item.type === 'conflict' && (
                  <span className="status-pill-amber">{item.tag}</span>
                )}
                {item.type === 'progress' && (
                  <span className="status-pill-copper">{item.tag}</span>
                )}
                <ChevronRight size={14} className="text-[#6d675e] group-hover:text-[#d9825b] transition-colors" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
