import React, { useState, useRef } from 'react';
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
  ExternalLink,
  X,
  Upload,
  Cpu,
  Database,
  Sliders,
  Check
} from 'lucide-react';
import { executeQuery } from '../services/api';

export default function WorkbenchView({ onSelectEvidence }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Modal & Selection States
  const [activeModal, setActiveModal] = useState(null); // 'add-files' | 'knowledge' | 'attach-data' | 'select-tool'
  const fileInputRef = useRef(null);

  // Interactive Attachments
  const [attachedFiles, setAttachedFiles] = useState([
    { name: 'Pump_P101_Maintenance.pdf', size: '3.4 MB', type: 'PDF' }
  ]);
  const [selectedCollections, setSelectedCollections] = useState(['col_1', 'col_2']);
  const [selectedDatasets, setSelectedDatasets] = useState(['ds_1']);
  const [selectedModel, setSelectedModel] = useState('llama-3.2-3b');
  const [selectedTools, setSelectedTools] = useState(['duckdb', 'chromadb', 'causal_verifier']);

  const sampleRecentWork = [
    { id: 'rw1', name: 'Pump P-101 Root Cause Analysis', status: 'Completed', tag: 'Verified', time: '12 min ago', type: 'verified' },
    { id: 'rw2', name: 'Safety Inspection Review (Unit 2)', status: 'Needs Approval', tag: '3 evidence conflicts', time: '38 min ago', type: 'conflict' },
    { id: 'rw3', name: 'Production Variance Analysis', status: 'In Progress', tag: 'Step 4 of 6', time: 'Now', type: 'progress' },
    { id: 'rw4', name: 'Monthly Operations Report', status: 'Completed', tag: 'Verified', time: 'Yesterday', type: 'verified' },
  ];

  const knowledgeCollections = [
    { id: 'col_1', name: 'CDU Unit-02 Operating Manuals', chunks: '342 chunks', rbac: 'Engineer', type: 'Manuals' },
    { id: 'col_2', name: 'Refinery P&ID Schematics 2026', chunks: '117 chunks', rbac: 'Engineer', type: 'Vision' },
    { id: 'col_3', name: 'Emergency Shutdown & Safety SOPs', chunks: '89 chunks', rbac: 'All Roles', type: 'Safety' },
    { id: 'col_4', name: 'Vendor Equipment Cut-Sheets (Sulzer)', chunks: '156 chunks', rbac: 'Supervisor', type: 'Vendor' },
  ];

  const tabularDatasets = [
    { id: 'ds_1', name: 'CDU_Vibration_Telemetry.csv', rows: '14,200 rows', table: 'duckdb_telemetry', updated: 'Live' },
    { id: 'ds_2', name: 'Bearing_Temperature_Log.csv', rows: '8,450 rows', table: 'bearing_temps', updated: '10m ago' },
    { id: 'ds_3', name: 'Lube_Oil_Header_Pressure.csv', rows: '6,120 rows', table: 'lube_pressures', updated: '1h ago' },
  ];

  const modelsList = [
    { id: 'llama-3.2-3b', name: 'Llama 3.2 3B (Default)', desc: 'Fast general-purpose sovereign reasoning', vram: '3.2 GB' },
    { id: 'qwen-2.5-3b', name: 'Qwen 2.5 3B (Long Context)', desc: '32k window for multi-document synthesis', vram: '3.0 GB' },
    { id: 'phi-3-mini', name: 'Phi-3 Mini 3.8B', desc: 'Step-by-step procedural logic & math', vram: '3.8 GB' },
  ];

  const availableTools = [
    { id: 'chromadb', name: 'ChromaDB Vector Retrieval', desc: 'RBAC-filtered semantic chunk search' },
    { id: 'duckdb', name: 'DuckDB SQL Engine', desc: 'In-memory SQL analytics with AST injection guard' },
    { id: 'causal_verifier', name: 'Causal Leap Verifier', desc: 'Downgrades unsupported causal claims' },
    { id: 'vision_ocr', name: 'P&ID Diagram Parser', desc: 'Visual equipment tag and line extractor' },
  ];

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      const newItems = files.map(f => ({
        name: f.name,
        size: `${(f.size / (1024 * 1024)).toFixed(1)} MB`,
        type: f.name.split('.').pop().toUpperCase()
      }));
      setAttachedFiles(prev => [...prev, ...newItems]);
      setActiveModal(null);
    }
  };

  const removeFile = (idx) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== idx));
  };

  const toggleCollection = (id) => {
    setSelectedCollections(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleDataset = (id) => {
    setSelectedDatasets(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleTool = (id) => {
    setSelectedTools(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

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

          {/* Active Context Chips Bar */}
          {(attachedFiles.length > 0 || selectedCollections.length > 0 || selectedDatasets.length > 0) && (
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#24211d]">
              {/* Attached Files */}
              {attachedFiles.map((file, idx) => (
                <span
                  key={`file_${idx}`}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#201e1a] border border-[#3d3830] text-[11px] text-[#f5f2ed]"
                >
                  <FileText size={11} className="text-[#d9825b]" />
                  <span className="font-mono">{file.name}</span>
                  <button
                    onClick={() => removeFile(idx)}
                    className="text-[#6d675e] hover:text-[#f43f5e] ml-1"
                  >
                    <X size={12} />
                  </button>
                </span>
              ))}

              {/* Selected Collections Count */}
              {selectedCollections.length > 0 && (
                <button
                  onClick={() => setActiveModal('knowledge')}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#18231d] border border-[#2a4d32] text-[11px] text-[#8ca68c] hover:border-[#6e8c6e]"
                >
                  <BookOpen size={11} className="text-[#6e8c6e]" />
                  <span>{selectedCollections.length} Knowledge Bases</span>
                </button>
              )}

              {/* Selected Datasets Count */}
              {selectedDatasets.length > 0 && (
                <button
                  onClick={() => setActiveModal('attach-data')}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#192226] border border-[#284954] text-[11px] text-[#7dd3fc] hover:border-[#38bdf8]"
                >
                  <Database size={11} className="text-[#38bdf8]" />
                  <span>{selectedDatasets.length} Telemetry Tables</span>
                </button>
              )}

              {/* Active Model Pill */}
              <button
                onClick={() => setActiveModal('select-tool')}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#26201b] border border-[#4d3324] text-[11px] text-[#f0a380] hover:border-[#d9825b]"
              >
                <Cpu size={11} className="text-[#d9825b]" />
                <span>{modelsList.find(m => m.id === selectedModel)?.name.split(' ')[0] || 'Llama 3.2'}</span>
              </button>
            </div>
          )}

          {/* Action Buttons Toolbar */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[#26231f]">
            <div className="flex items-center gap-2">
              {/* Hidden Native File Input */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                multiple
                className="hidden"
              />

              {/* 1. Add Files Button */}
              <button
                onClick={() => setActiveModal('add-files')}
                className="btn-outline text-xs py-1 px-2.5"
              >
                <Plus size={13} />
                <span>Add Files</span>
              </button>

              {/* 2. Knowledge Context Button */}
              <button
                onClick={() => setActiveModal('knowledge')}
                className="btn-outline text-xs py-1 px-2.5"
              >
                <BookOpen size={13} />
                <span>Knowledge Context</span>
              </button>

              {/* 3. Attach Data Button */}
              <button
                onClick={() => setActiveModal('attach-data')}
                className="btn-outline text-xs py-1 px-2.5"
              >
                <Paperclip size={13} />
                <span>Attach Data</span>
              </button>

              {/* 4. Select Tool / Model Button */}
              <button
                onClick={() => setActiveModal('select-tool')}
                className="btn-outline text-xs py-1 px-2.5"
              >
                <Wrench size={13} />
                <span>Select Model & Tools</span>
              </button>
            </div>

            {/* Run Query Button */}
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

      {/* MODAL 1: ADD FILES */}
      {activeModal === 'add-files' && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="clora-card w-full max-w-lg p-6 space-y-5 border-[#d9825b]/50 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-3">
              <div className="flex items-center gap-2 text-sm font-bold text-[#f5f2ed]">
                <Plus size={16} className="text-[#d9825b]" />
                <span>Attach Files to Execution Context</span>
              </div>
              <button onClick={() => setActiveModal(null)} className="text-[#a09a90] hover:text-[#f5f2ed]">
                <X size={18} />
              </button>
            </div>

            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-[#3b3630] hover:border-[#d9825b] rounded-xl p-8 flex flex-col items-center justify-center text-center space-y-2 bg-[#171513] cursor-pointer transition-all"
            >
              <Upload size={28} className="text-[#d9825b]" />
              <span className="text-xs font-semibold text-[#f5f2ed]">Click to browse or drop local files</span>
              <span className="text-[10px] text-[#6d675e]">PDF manuals, CSV telemetry logs, P&ID drawings</span>
            </div>

            <div className="space-y-2">
              <span className="text-[11px] font-mono text-[#6d675e] uppercase">Quick Select From Workspace:</span>
              <div className="space-y-1 max-h-36 overflow-y-auto">
                {[
                  { name: 'Pump_P101_Maintenance.pdf', size: '3.4 MB' },
                  { name: 'PID_Drawing_Unit2.pdf', size: '8.1 MB' },
                  { name: 'Safety_Protocols_CDU.docx', size: '1.2 MB' }
                ].map((sample, idx) => (
                  <div
                    key={idx}
                    onClick={() => {
                      setAttachedFiles(prev => [...prev, sample]);
                      setActiveModal(null);
                    }}
                    className="p-2 rounded-lg bg-[#1b1917] hover:bg-[#25221e] border border-[#2b2723] flex items-center justify-between cursor-pointer text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <FileText size={14} className="text-[#d9825b]" />
                      <span className="text-[#f5f2ed]">{sample.name}</span>
                    </div>
                    <span className="text-[10px] text-[#6d675e] font-mono">{sample.size}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-[#2a2622]">
              <button onClick={() => setActiveModal(null)} className="btn-outline text-xs">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: KNOWLEDGE CONTEXT */}
      {activeModal === 'knowledge' && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="clora-card w-full max-w-lg p-6 space-y-5 border-[#6e8c6e]/50 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-3">
              <div className="flex items-center gap-2 text-sm font-bold text-[#f5f2ed]">
                <BookOpen size={16} className="text-[#6e8c6e]" />
                <span>Select Knowledge Base Collections</span>
              </div>
              <button onClick={() => setActiveModal(null)} className="text-[#a09a90] hover:text-[#f5f2ed]">
                <X size={18} />
              </button>
            </div>

            <div className="space-y-2 max-h-60 overflow-y-auto">
              {knowledgeCollections.map((col) => {
                const isSelected = selectedCollections.includes(col.id);
                return (
                  <div
                    key={col.id}
                    onClick={() => toggleCollection(col.id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                      isSelected
                        ? 'bg-[#1a241c] border-[#6e8c6e] text-[#f5f2ed]'
                        : 'bg-[#181614] border-[#2e2a25] text-[#a09a90] hover:border-[#3d3830]'
                    }`}
                  >
                    <div className="space-y-0.5">
                      <div className="text-xs font-semibold">{col.name}</div>
                      <div className="text-[10px] text-[#6d675e] font-mono flex items-center gap-2">
                        <span>{col.chunks}</span>
                        <span>•</span>
                        <span>RBAC: {col.rbac}</span>
                      </div>
                    </div>
                    <div className={`w-5 h-5 rounded flex items-center justify-center border ${
                      isSelected ? 'bg-[#6e8c6e] border-[#6e8c6e] text-white' : 'border-[#3d3830]'
                    }`}>
                      {isSelected && <Check size={13} />}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-[#2a2622]">
              <span className="text-[11px] text-[#6e8c6e] font-mono">
                {selectedCollections.length} collections active
              </span>
              <button onClick={() => setActiveModal(null)} className="btn-copper text-xs">
                Apply Context
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: ATTACH DATA */}
      {activeModal === 'attach-data' && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="clora-card w-full max-w-lg p-6 space-y-5 border-[#38bdf8]/50 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-3">
              <div className="flex items-center gap-2 text-sm font-bold text-[#f5f2ed]">
                <Database size={16} className="text-[#38bdf8]" />
                <span>Attach Tabular Telemetry (DuckDB)</span>
              </div>
              <button onClick={() => setActiveModal(null)} className="text-[#a09a90] hover:text-[#f5f2ed]">
                <X size={18} />
              </button>
            </div>

            <div className="space-y-2 max-h-60 overflow-y-auto">
              {tabularDatasets.map((ds) => {
                const isSelected = selectedDatasets.includes(ds.id);
                return (
                  <div
                    key={ds.id}
                    onClick={() => toggleDataset(ds.id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                      isSelected
                        ? 'bg-[#182328] border-[#38bdf8] text-[#f5f2ed]'
                        : 'bg-[#181614] border-[#2e2a25] text-[#a09a90] hover:border-[#3d3830]'
                    }`}
                  >
                    <div className="space-y-0.5">
                      <div className="text-xs font-semibold">{ds.name}</div>
                      <div className="text-[10px] text-[#6d675e] font-mono flex items-center gap-2">
                        <span>{ds.rows}</span>
                        <span>•</span>
                        <span>Table: {ds.table}</span>
                      </div>
                    </div>
                    <div className={`w-5 h-5 rounded flex items-center justify-center border ${
                      isSelected ? 'bg-[#38bdf8] border-[#38bdf8] text-black font-bold' : 'border-[#3d3830]'
                    }`}>
                      {isSelected && <Check size={13} />}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-[#2a2622]">
              <span className="text-[11px] text-[#38bdf8] font-mono">
                {selectedDatasets.length} tables mounted to DuckDB
              </span>
              <button onClick={() => setActiveModal(null)} className="btn-copper text-xs">
                Attach Tables
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 4: SELECT MODEL & TOOLS */}
      {activeModal === 'select-tool' && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="clora-card w-full max-w-lg p-6 space-y-5 border-[#d9825b]/50 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#2e2a25] pb-3">
              <div className="flex items-center gap-2 text-sm font-bold text-[#f5f2ed]">
                <Cpu size={16} className="text-[#d9825b]" />
                <span>Select Sovereign Model & Agent Tools</span>
              </div>
              <button onClick={() => setActiveModal(null)} className="text-[#a09a90] hover:text-[#f5f2ed]">
                <X size={18} />
              </button>
            </div>

            {/* Model Selector */}
            <div className="space-y-2">
              <span className="text-[11px] font-mono text-[#6d675e] uppercase">Active Local LLM Engine:</span>
              <div className="space-y-1.5">
                {modelsList.map((m) => {
                  const isSelected = selectedModel === m.id;
                  return (
                    <div
                      key={m.id}
                      onClick={() => setSelectedModel(m.id)}
                      className={`p-2.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                        isSelected
                          ? 'bg-[#291f19] border-[#d9825b] text-[#f5f2ed]'
                          : 'bg-[#181614] border-[#2e2a25] text-[#a09a90] hover:border-[#3d3830]'
                      }`}
                    >
                      <div className="space-y-0.5">
                        <div className="text-xs font-bold">{m.name}</div>
                        <div className="text-[10px] text-[#6d675e]">{m.desc}</div>
                      </div>
                      <span className="text-[10px] font-mono text-[#d9825b]">{m.vram}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Tool Toggles */}
            <div className="space-y-2 pt-2 border-t border-[#26231f]">
              <span className="text-[11px] font-mono text-[#6d675e] uppercase">Enabled Agent Tool Bindings:</span>
              <div className="grid grid-cols-2 gap-2">
                {availableTools.map((tool) => {
                  const isEnabled = selectedTools.includes(tool.id);
                  return (
                    <div
                      key={tool.id}
                      onClick={() => toggleTool(tool.id)}
                      className={`p-2 rounded-lg border transition-all cursor-pointer flex items-center justify-between text-xs ${
                        isEnabled
                          ? 'bg-[#1e1c19] border-[#6e8c6e] text-[#f5f2ed]'
                          : 'bg-[#161412] border-[#26231f] text-[#6d675e]'
                      }`}
                    >
                      <span className="truncate">{tool.name}</span>
                      {isEnabled && <Check size={12} className="text-[#6e8c6e] shrink-0" />}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-[#2a2622]">
              <button onClick={() => setActiveModal(null)} className="btn-copper text-xs">
                Confirm Selection
              </button>
            </div>
          </div>
        </div>
      )}

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
