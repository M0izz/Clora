import React from 'react';
import { CheckCircle2, Circle, Clock, FileText, ArrowRight } from 'lucide-react';

export default function LiveExecutionDrawer({
  title = 'Refinery Maintenance Analysis',
  filename = 'Q2_Inspection_Reports.pdf',
  steps = [],
  currentStepIndex = 5,
  progressPct = 68,
  onViewTrace
}) {
  const defaultSteps = [
    { label: 'Task received & query classified', status: 'completed' },
    { label: 'Files secured locally (0 B egress)', status: 'completed' },
    { label: 'Content extracted & vector indexed', status: 'completed' },
    { label: 'Local model selected (Llama 3.2 3B)', status: 'completed' },
    { label: 'ChromaDB knowledge retrieved', status: 'completed' },
    { label: 'Evidence verification & Causal Leap Guard', status: 'active', subtext: `${progressPct}% Processing locally` },
    { label: 'Report generation & formatting', status: 'pending' },
  ];

  const activeSteps = steps.length > 0 ? steps : defaultSteps;

  return (
    <div className="clora-card p-4 space-y-4">
      <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2.5">
        <span className="text-[11px] font-mono uppercase tracking-widest text-[#6d675e] font-bold">
          LIVE EXECUTION
        </span>
        <span className="status-pill-sage">SOVEREIGN</span>
      </div>

      <div className="space-y-1">
        <h4 className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
          {title}
        </h4>
        <div className="flex items-center gap-1.5 text-[11px] text-[#a09a90]">
          <FileText size={12} className="text-[#d9825b]" />
          <span className="font-mono">{filename}</span>
        </div>
      </div>

      {/* Stepper Timeline */}
      <div className="space-y-3 pt-1">
        {activeSteps.map((step, idx) => {
          const isCompleted = step.status === 'completed';
          const isActive = step.status === 'active';
          return (
            <div key={idx} className="flex items-start gap-2.5 text-xs">
              <div className="pt-0.5 shrink-0">
                {isCompleted ? (
                  <CheckCircle2 size={14} className="text-[#10b981]" />
                ) : isActive ? (
                  <span className="w-3.5 h-3.5 rounded-full border-2 border-[#d9825b] flex items-center justify-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#d9825b] animate-ping" />
                  </span>
                ) : (
                  <Circle size={14} className="text-[#423d37]" />
                )}
              </div>
              <div className="space-y-0.5 flex-1">
                <div className={`font-medium ${isActive ? 'text-[#d9825b]' : isCompleted ? 'text-[#c8c2b8]' : 'text-[#6d675e]'}`}>
                  {step.label || step.name}
                </div>
                {step.subtext && (
                  <div className="text-[10px] text-[#8ca68c] font-mono">
                    {step.subtext}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <button
        onClick={onViewTrace}
        className="w-full pt-2 text-[11px] font-semibold text-[#a09a90] hover:text-[#d9825b] flex items-center justify-center gap-1.5 transition-colors border-t border-[#2a2622]"
      >
        <span>VIEW EXECUTION TRACE</span>
        <ArrowRight size={13} />
      </button>
    </div>
  );
}
