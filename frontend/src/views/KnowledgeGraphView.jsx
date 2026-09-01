import React, { useState } from 'react';
import {
  Network,
  FileText,
  ShieldCheck,
  Search,
  ZoomIn,
  ZoomOut,
  Maximize2,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Layers
} from 'lucide-react';

export default function KnowledgeGraphView() {
  const [selectedNode, setSelectedNode] = useState('P-101');

  const nodes = [
    { id: 'P-101', name: 'Pump P-101', type: 'Charge Pump', status: 'CRITICAL', temp: '104.2°C', vibration: '9.82 mm/s', x: 120, y: 150, radius: 40 },
    { id: 'HEX-301', name: 'Heat Exchanger HEX-301', type: 'Pre-Heat', status: 'WARNING', temp: '88.5°C', vibration: '3.1 mm/s', x: 260, y: 90, radius: 32 },
    { id: 'TK-502', name: 'Storage Tank TK-502', type: 'Naphtha Tank', status: 'NORMAL', temp: '32.0°C', vibration: '0.8 mm/s', x: 380, y: 170, radius: 35 },
    { id: 'CV-104B', name: 'Valve CV-104B', type: 'Return Valve', status: 'THROTTLED', temp: '65.0°C', vibration: '1.2 mm/s', x: 250, y: 250, radius: 28 },
  ];

  const auditEvents = [
    { id: 'ev1', hash: '0a4b36d31b3b3359672a8235d7a4b5d7333090798e23...', user: 'maintenance_engineer', status: 'VERIFIED VALID', time: '09:42 AM' },
    { id: 'ev2', hash: 'b24b97838c2058795329d489a96ddbc66a0243a5cd98...', user: 'maintenance_engineer', status: 'VERIFIED VALID', time: '09:42 AM' },
    { id: 'ev3', hash: '0a4b87881b7a8272833d2c35e99d71d37053bb273348...', user: 'supervisor', status: 'VERIFIED VALID', time: '09:43 AM' },
    { id: 'ev4', hash: '0a4be7a82b3cd2480163a5895a5b2528dab2a2d6e739...', user: 'operator', status: 'VERIFIED VALID', time: '09:45 AM' },
  ];

  const activeNodeData = nodes.find(n => n.id === selectedNode) || nodes[0];

  return (
    <div className="space-y-5">
      {/* Header Info */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono font-bold tracking-widest text-[#6d675e] uppercase">
            KNOWLEDGE • TOPOLOGY REASONING
          </span>
          <h1 className="text-xl font-display font-bold text-[#f5f2ed]">
            Refinery Asset Topology & Evidence Inspector
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <span className="status-pill-sage">
            <Activity size={12} />
            <span>Topology Live</span>
          </span>
          <span className="status-pill-copper">
            <span>Blast Radius: Calculated</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Interactive Topology Canvas */}
        <div className="lg:col-span-7 clora-card p-5 space-y-3 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2.5">
            <span className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
              Refinery Asset Topology & Blast Radius
            </span>
            <div className="flex items-center gap-1.5 text-[#6d675e]">
              <button className="p-1 rounded hover:bg-[#26231f] text-[#a09a90]"><ZoomIn size={14} /></button>
              <button className="p-1 rounded hover:bg-[#26231f] text-[#a09a90]"><ZoomOut size={14} /></button>
              <button className="p-1 rounded hover:bg-[#26231f] text-[#a09a90]"><Maximize2 size={14} /></button>
            </div>
          </div>

          {/* SVG Canvas */}
          <div className="w-full h-[320px] bg-[#141211] rounded-xl border border-[#2c2823] relative flex items-center justify-center overflow-hidden">
            {/* Blast Radius Glowing Halo */}
            <div className="absolute top-[80px] left-[50px] w-[140px] h-[140px] rounded-full bg-[#d9825b]/10 border border-[#d9825b]/30 animate-pulse-glow" />
            <div className="absolute top-[50px] left-[20px] w-[200px] h-[200px] rounded-full border border-dashed border-[#d9825b]/20" />

            <svg className="w-full h-full" viewBox="0 0 460 300">
              {/* Connection Lines */}
              <line x1="120" y1="150" x2="260" y2="90" stroke="#4a443d" strokeWidth="2" strokeDasharray="4 4" />
              <line x1="260" y1="90" x2="380" y2="170" stroke="#4a443d" strokeWidth="2" />
              <line x1="120" y1="150" x2="250" y2="250" stroke="#d9825b" strokeWidth="2" />
              <line x1="250" y1="250" x2="380" y2="170" stroke="#4a443d" strokeWidth="2" />

              {/* Asset Nodes */}
              {nodes.map((node) => {
                const isSelected = selectedNode === node.id;
                const isCritical = node.status === 'CRITICAL';
                return (
                  <g
                    key={node.id}
                    onClick={() => setSelectedNode(node.id)}
                    className="cursor-pointer transition-all hover:scale-105"
                  >
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={node.radius}
                      fill="#1e1b19"
                      stroke={isCritical ? '#f43f5e' : isSelected ? '#d9825b' : '#6e8c6e'}
                      strokeWidth={isSelected ? '3' : '2'}
                      filter="drop-shadow(0 4px 10px rgba(0,0,0,0.5))"
                    />
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={node.radius - 8}
                      fill={isCritical ? 'rgba(244, 63, 94, 0.15)' : 'rgba(217, 130, 91, 0.1)'}
                    />
                    <text
                      x={node.x}
                      y={node.y - 2}
                      textAnchor="middle"
                      fill="#f5f2ed"
                      fontSize="11"
                      fontWeight="bold"
                    >
                      {node.id}
                    </text>
                    <text
                      x={node.x}
                      y={node.y + 12}
                      textAnchor="middle"
                      fill={isCritical ? '#f87171' : '#a09a90'}
                      fontSize="9"
                    >
                      {node.temp}
                    </text>
                  </g>
                );
              })}
            </svg>

            {/* Blast Radius Label */}
            <div className="absolute top-4 left-4 bg-[#1e1c19]/90 border border-[#3d3832] rounded-lg px-2.5 py-1 text-[10px] text-[#f0a380] flex items-center gap-1.5 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-[#d9825b] animate-ping" />
              <span>Blast-Radius: Unit 2 Isolation Sector Active</span>
            </div>
          </div>

          {/* Selected Node Details Bar */}
          <div className="clora-surface p-3 flex items-center justify-between text-xs">
            <div className="flex items-center gap-3">
              <span className="font-bold text-[#f5f2ed]">{activeNodeData.name}</span>
              <span className="text-[#6d675e]">•</span>
              <span className="text-[#a09a90]">{activeNodeData.type}</span>
            </div>
            <div className="flex items-center gap-3 font-mono">
              <span className="text-[#f87171]">Temp: {activeNodeData.temp}</span>
              <span className="text-[#fbbf24]">Vib: {activeNodeData.vibration}</span>
            </div>
          </div>
        </div>

        {/* Right Column: Multi-Modal Document Split Viewer & Audit Stream */}
        <div className="lg:col-span-5 space-y-4">
          {/* Document Verification Box */}
          <div className="clora-card p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-[#f5f2ed]">
                <FileText size={14} className="text-[#d9825b]" />
                <span>Document Evidence Split View</span>
              </div>
              <span className="text-[10px] text-[#6e8c6e] font-mono">Page 42 of 52</span>
            </div>

            <div className="p-3.5 rounded-xl bg-[#151312] border border-[#2e2a25] space-y-2 text-xs leading-relaxed text-[#c8c2b8]">
              <div className="text-[10px] text-[#6d675e] font-mono uppercase">
                Pump_P101_Maintenance_Manual.pdf
              </div>
              <p className="text-[#a09a90]">
                ...operating guidelines for continuous service in crude distillation units.
              </p>
              {/* Highlighted Evidence Box */}
              <div className="p-2 rounded bg-[#fbbf24]/15 border-l-2 border-[#fbbf24] text-[#fef3c7] font-medium">
                Section 4.3: Bearing Operating Limits: 80°C Max. Prolonged operation above 95°C indicates coolant flow restriction or lubricant starvation, leading to rapid micro-spalling.
              </div>
              <p className="text-[#a09a90]">
                Inspect cooling valve CV-104B and verify differential lube header pressure.
              </p>
            </div>
          </div>

          {/* Tamper-Evident SHA-256 Audit Stream */}
          <div className="clora-card p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2">
              <span className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
                Tamper-Evident SHA-256 Audit Stream
              </span>
              <span className="status-pill-sage">CRYPTOGRAPHIC PROOF</span>
            </div>

            <div className="space-y-2 font-mono text-[10px]">
              {auditEvents.map((ev) => (
                <div key={ev.id} className="p-2 rounded-lg bg-[#161412] border border-[#2b2723] flex items-center justify-between">
                  <div className="space-y-0.5 truncate mr-2">
                    <div className="text-[#a09a90] truncate">{ev.hash}</div>
                    <div className="text-[#6d675e]">{ev.user} • {ev.time}</div>
                  </div>
                  <span className="text-[#34d399] font-bold shrink-0">{ev.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
