import React from 'react';
import { Cpu, Zap, Activity, HardDrive, CheckCircle2 } from 'lucide-react';

export default function IntelligenceModelsView() {
  const models = [
    {
      id: 'm_llama',
      name: 'Llama 3.2 3B',
      role: 'Default Agent Reasoning Model',
      ttft: '0.51 s',
      throughput: '10.2 tok/s',
      vram: '3.2 GB',
      precision: 'GGUF Q4_K_M',
      status: 'LOADED IN MEMORY',
      statusType: 'active'
    },
    {
      id: 'm_qwen',
      name: 'Qwen 2.5 3B',
      role: 'Long-Context Synthesis & Code Engine',
      ttft: '1.90 s',
      throughput: '8.7 tok/s',
      vram: '3.0 GB',
      precision: 'GGUF Q4_K_M',
      status: 'READY',
      statusType: 'ready'
    },
    {
      id: 'm_phi',
      name: 'Phi-3 Mini 3.8B',
      role: 'Procedural & Formula Logic Engine',
      ttft: '1.37 s',
      throughput: '7.5 tok/s',
      vram: '3.8 GB',
      precision: 'GGUF Q4_K_M',
      status: 'READY',
      statusType: 'ready'
    },
    {
      id: 'm_minilm',
      name: 'all-MiniLM-L6-v2',
      role: 'Local Dense Embedding Model',
      ttft: '< 1 ms',
      throughput: '906 chunks/s',
      vram: '0.12 MB',
      precision: 'PyTorch FP32',
      status: 'LOADED IN MEMORY',
      statusType: 'active'
    }
  ];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono font-bold tracking-widest text-[#6d675e] uppercase">
            INTELLIGENCE • LOCAL COMPUTE
          </span>
          <h1 className="text-xl font-display font-bold text-[#f5f2ed]">
            Local Models & Compute Registry
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <span className="status-pill-emerald">
            <Zap size={12} />
            <span>Ollama Daemon Active</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Model Cards Grid */}
        <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          {models.map((mod) => (
            <div key={mod.id} className="clora-card p-4 space-y-3 flex flex-col justify-between">
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-[#f5f2ed]">{mod.name}</h3>
                  {mod.statusType === 'active' ? (
                    <span className="status-pill-copper text-[9px]">{mod.status}</span>
                  ) : (
                    <span className="status-pill-sage text-[9px]">{mod.status}</span>
                  )}
                </div>
                <div className="text-[10px] text-[#a09a90]">{mod.role}</div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[#26231f] text-[11px] font-mono">
                <div className="space-y-0.5">
                  <span className="text-[9px] text-[#6d675e] block">TTFT</span>
                  <span className="text-[#f5f2ed] font-bold">{mod.ttft}</span>
                </div>
                <div className="space-y-0.5">
                  <span className="text-[9px] text-[#6d675e] block">Throughput</span>
                  <span className="text-[#d9825b] font-bold">{mod.throughput}</span>
                </div>
                <div className="space-y-0.5">
                  <span className="text-[9px] text-[#6d675e] block">VRAM Usage</span>
                  <span className="text-[#a09a90]">{mod.vram}</span>
                </div>
                <div className="space-y-0.5">
                  <span className="text-[9px] text-[#6d675e] block">Precision</span>
                  <span className="text-[#8ca68c]">{mod.precision}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Right Panel: Resource Meters */}
        <div className="lg:col-span-4 space-y-4">
          <div className="clora-card p-4 space-y-4">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2">
              <span className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
                Sovereign Compute Allocation
              </span>
              <HardDrive size={13} className="text-[#d9825b]" />
            </div>

            {/* RAM Meter */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#a09a90]">System RAM</span>
                <span className="font-mono text-[#f5f2ed] font-bold">12.4 GB / 32.0 GB</span>
              </div>
              <div className="w-full h-2 rounded-full bg-[#181614] overflow-hidden">
                <div className="h-full bg-[#d9825b] rounded-full w-[38%]" />
              </div>
            </div>

            {/* GPU VRAM Meter */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#a09a90]">GPU VRAM (Local CUDA)</span>
                <span className="font-mono text-[#f5f2ed] font-bold">3.2 GB / 8.0 GB</span>
              </div>
              <div className="w-full h-2 rounded-full bg-[#181614] overflow-hidden">
                <div className="h-full bg-[#10b981] rounded-full w-[40%]" />
              </div>
            </div>

            <div className="p-3 rounded-lg bg-[#181614] border border-[#2b2723] space-y-1 text-xs text-[#a09a90]">
              <span className="text-[#10b981] font-semibold text-[10px] uppercase tracking-wide block">
                Air-Gapped Ingestion Sentinel
              </span>
              <p className="text-[11px] text-[#8a8377] leading-relaxed">
                Zero external model endpoints are referenced. All model weights execute entirely from local NVMe cache.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
