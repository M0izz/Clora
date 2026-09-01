import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  FileSpreadsheet,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Plus,
  RefreshCw
} from 'lucide-react';

export default function DataSourcesView() {
  const [isUploading, setIsUploading] = useState(false);

  const [files, setFiles] = useState([
    {
      id: 'f1',
      name: 'Pump_P101_Maintenance.pdf',
      type: 'pdf',
      status: 'INDEXED',
      statusType: 'indexed',
      chunks: 342,
      rbac: ['maintenance_engineer', 'supervisor'],
      sha: 'SHA-256: af04a573...',
      size: '3.4 MB'
    },
    {
      id: 'f2',
      name: 'CDU_Vibration_Telemetry.csv',
      type: 'csv',
      status: 'DUCKDB READY',
      statusType: 'duckdb',
      chunks: 173,
      rbac: ['supervisor', 'plant_manager'],
      sha: 'SHA-256: 7706c372...',
      size: '14,200 rows'
    },
    {
      id: 'f3',
      name: 'PID_Drawing_Unit2.pdf',
      type: 'vision',
      status: 'VISION PARSED',
      statusType: 'vision',
      chunks: 117,
      rbac: ['maintenance_engineer', 'supervisor'],
      sha: 'SHA-256: 2ea4c376...',
      size: '8.1 MB'
    },
    {
      id: 'f4',
      name: 'Safety_Protocols_CDU.docx',
      type: 'docx',
      status: 'INDEXED',
      statusType: 'indexed',
      chunks: 89,
      rbac: ['operator', 'maintenance_engineer', 'supervisor'],
      sha: 'SHA-256: d8e1a904...',
      size: '1.2 MB'
    }
  ]);

  const handleSimulatedUpload = () => {
    setIsUploading(true);
    setTimeout(() => {
      setFiles(prev => [
        {
          id: `f_${Date.now()}`,
          name: 'HEX301_Inspection_Log.pdf',
          type: 'pdf',
          status: 'INDEXED',
          statusType: 'indexed',
          chunks: 48,
          rbac: ['maintenance_engineer'],
          sha: 'SHA-256: c3b91a02...',
          size: '1.8 MB'
        },
        ...prev
      ]);
      setIsUploading(false);
    }, 1200);
  };

  return (
    <div className="space-y-5">
      {/* View Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono font-bold tracking-widest text-[#6d675e] uppercase">
            KNOWLEDGE • DATA INGESTION
          </span>
          <h1 className="text-xl font-display font-bold text-[#f5f2ed]">
            Data Sources & Ingestion Hub
          </h1>
        </div>
        <button
          onClick={handleSimulatedUpload}
          className="btn-copper text-xs py-1.5 px-3.5"
        >
          <Plus size={14} />
          <span>Ingest New File</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Drag-and-Drop Ingestion Zone */}
        <div className="lg:col-span-5 clora-card p-5 space-y-4 flex flex-col justify-between">
          <div className="space-y-1">
            <h3 className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
              Local Document Ingestion
            </h3>
            <p className="text-[11px] text-[#a09a90]">
              Files are processed 100% on-premise with zero external network egress.
            </p>
          </div>

          {/* Upload Drop Target */}
          <div
            onClick={handleSimulatedUpload}
            className="border-2 border-dashed border-[#3b3630] hover:border-[#d9825b] rounded-xl p-8 flex flex-col items-center justify-center text-center space-y-3 bg-[#151312] cursor-pointer transition-all group"
          >
            <div className="w-12 h-12 rounded-full bg-[#201d1a] border border-[#3b3630] flex items-center justify-center text-[#d9825b] group-hover:scale-110 transition-transform">
              <UploadCloud size={24} />
            </div>
            <div className="space-y-1">
              <div className="text-xs font-semibold text-[#f5f2ed]">
                {isUploading ? 'Securing & Vector Indexing...' : 'Drag and drop files here'}
              </div>
              <div className="text-[10px] text-[#6d675e]">
                PDF manuals, P&ID schematics, CSV sensor telemetry, DOCX
              </div>
            </div>
          </div>

          {/* Security Badge */}
          <div className="p-3 rounded-xl bg-[#161f18] border border-[#234529] flex items-center gap-3">
            <ShieldCheck size={18} className="text-[#10b981] shrink-0" />
            <div className="space-y-0.5">
              <div className="text-[11px] font-semibold text-[#10b981]">
                0 B DATA EGRESS • MAGIC-BYTE VERIFIED
              </div>
              <div className="text-[10px] text-[#8ca68c]">
                Magic-byte inspection validates file headers to prevent malicious payloads.
              </div>
            </div>
          </div>
        </div>

        {/* Right: Data Table */}
        <div className="lg:col-span-7 clora-card p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2.5">
            <h3 className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
              Indexed Knowledge & Telemetry ({files.length})
            </h3>
            <span className="text-[10px] text-[#6d675e] font-mono">ChromaDB & DuckDB Active</span>
          </div>

          <div className="divide-y divide-[#26231f]">
            {files.map((file) => (
              <div key={file.id} className="py-3 px-1.5 flex items-center justify-between hover:bg-[#1b1917] rounded-lg transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#201d1a] border border-[#3b3630] flex items-center justify-center text-[#d9825b]">
                    {file.type === 'csv' ? (
                      <FileSpreadsheet size={15} className="text-[#10b981]" />
                    ) : file.type === 'vision' ? (
                      <Cpu size={15} className="text-[#38bdf8]" />
                    ) : (
                      <FileText size={15} className="text-[#d9825b]" />
                    )}
                  </div>
                  <div>
                    <div className="text-xs font-medium text-[#f5f2ed]">{file.name}</div>
                    <div className="text-[10px] text-[#6d675e] flex items-center gap-2 mt-0.5">
                      <span>{file.size}</span>
                      <span>•</span>
                      <span className="font-mono text-[#a09a90]">{file.sha}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2.5">
                  <div className="flex flex-col items-end gap-1">
                    {file.statusType === 'indexed' && (
                      <span className="status-pill-sage">{file.status}</span>
                    )}
                    {file.statusType === 'duckdb' && (
                      <span className="status-pill-emerald">{file.status}</span>
                    )}
                    {file.statusType === 'vision' && (
                      <span className="status-pill-copper">{file.status}</span>
                    )}
                    <span className="text-[9px] text-[#6d675e] font-mono">{file.chunks} chunks</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
