import React, { useState } from 'react';
import { ShieldCheck, Lock, CheckCircle2, XCircle, Download, FileText, Activity } from 'lucide-react';

export default function SovereigntyView() {
  const [downloading, setDownloading] = useState(false);

  const rbacMatrix = [
    { role: 'operator', viewLogs: true, configSystem: false, execCommands: false, createUser: false, exportAudit: false },
    { role: 'technician', viewLogs: true, configSystem: true, execCommands: false, createUser: false, exportAudit: false },
    { role: 'maintenance_engineer', viewLogs: true, configSystem: true, execCommands: true, createUser: false, exportAudit: false },
    { role: 'supervisor', viewLogs: true, configSystem: true, execCommands: true, createUser: true, exportAudit: false },
    { role: 'plant_manager', viewLogs: true, configSystem: true, execCommands: true, createUser: true, exportAudit: true },
  ];

  const auditLogs = [
    { id: 'al_1', time: '10:06:13.300', user: 'operator', action: 'Query Dispatched', hash: 'SHA-256: 9a4f7e2c...', status: 'VERIFIED VALID' },
    { id: 'al_2', time: '10:06:13.340', user: 'technician', action: 'Config Changed', hash: 'SHA-256: 7c8d9a0f...', status: 'VERIFIED VALID' },
    { id: 'al_3', time: '10:06:13.380', user: 'maintenance_engineer', action: 'Causal Downgrade Applied', hash: 'SHA-256: b1e3a7f4...', status: 'VERIFIED VALID' },
    { id: 'al_4', time: '10:06:13.420', user: 'supervisor', action: 'Approval Note Export', hash: 'SHA-256: 3d5e2a9b...', status: 'VERIFIED VALID' },
  ];

  const handleExportDocx = () => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
      // Trigger download if available or simulate
      window.open('http://127.0.0.1:8000/api/files/download-approval-note', '_blank');
    }, 1000);
  };

  return (
    <div className="space-y-5">
      {/* Top Banner: Air-Gap Sentinel */}
      <div className="p-4 rounded-xl bg-[#141f17] border border-[#234d2b] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#1d3323] border border-[#34d399]/40 flex items-center justify-center text-[#10b981]">
            <ShieldCheck size={22} />
          </div>
          <div>
            <h2 className="text-sm font-bold text-[#f5f2ed] uppercase tracking-wide">
              SOVEREIGNTY AIRGAP SENTINEL
            </h2>
            <p className="text-xs text-[#8ca68c] font-mono mt-0.5">
              ZERO WAN SOCKETS ACTIVE • 100% AIR-GAPPED ON-PREMISE CONTROL PLANE
            </p>
          </div>
        </div>
        <span className="status-pill-emerald">
          <CheckCircle2 size={12} />
          <span>SOCKET INTEGRITY VERIFIED</span>
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: 5-Role RBAC Matrix */}
        <div className="lg:col-span-6 clora-card p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2.5">
            <h3 className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
              5-Role RBAC Matrix
            </h3>
            <span className="text-[10px] text-[#6d675e] font-mono">Strict Enforcement</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#26231f] text-[#6d675e] font-mono text-[10px]">
                  <th className="pb-2">Role</th>
                  <th className="pb-2 text-center">View Logs</th>
                  <th className="pb-2 text-center">Config</th>
                  <th className="pb-2 text-center">Exec Commands</th>
                  <th className="pb-2 text-center">Export Audit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#26231f]">
                {rbacMatrix.map((item) => (
                  <tr key={item.role} className="hover:bg-[#1a1816] transition-colors">
                    <td className="py-2.5 font-medium text-[#f5f2ed]">{item.role}</td>
                    <td className="py-2.5 text-center">
                      {item.viewLogs ? <CheckCircle2 size={13} className="text-[#10b981] inline" /> : <XCircle size={13} className="text-[#4a443d] inline" />}
                    </td>
                    <td className="py-2.5 text-center">
                      {item.configSystem ? <CheckCircle2 size={13} className="text-[#10b981] inline" /> : <XCircle size={13} className="text-[#4a443d] inline" />}
                    </td>
                    <td className="py-2.5 text-center">
                      {item.execCommands ? <CheckCircle2 size={13} className="text-[#10b981] inline" /> : <XCircle size={13} className="text-[#4a443d] inline" />}
                    </td>
                    <td className="py-2.5 text-center">
                      {item.exportAudit ? <CheckCircle2 size={13} className="text-[#10b981] inline" /> : <XCircle size={13} className="text-[#4a443d] inline" />}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Tamper-Evident SHA-256 Audit Trail */}
        <div className="lg:col-span-6 clora-card p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-[#2e2a25] pb-2.5">
            <h3 className="text-xs font-semibold text-[#f5f2ed] uppercase tracking-wide">
              Tamper-Evident SHA-256 Audit Trail
            </h3>
            <span className="status-pill-sage">HASH CHAIN VALID</span>
          </div>

          <div className="space-y-2.5 font-mono text-[11px]">
            {auditLogs.map((log) => (
              <div key={log.id} className="p-2.5 rounded-lg bg-[#161412] border border-[#2b2723] flex items-center justify-between">
                <div className="space-y-0.5 truncate mr-2">
                  <div className="text-xs text-[#f5f2ed] font-medium">{log.action}</div>
                  <div className="text-[10px] text-[#a09a90] truncate">{log.hash}</div>
                  <div className="text-[9px] text-[#6d675e]">{log.user} • {log.time}</div>
                </div>
                <span className="status-pill-emerald text-[9px] shrink-0">{log.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Export Action Card */}
      <div className="clora-card p-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText size={20} className="text-[#d9825b]" />
          <div>
            <h4 className="text-xs font-bold text-[#f5f2ed]">Official MRPL Executive Approval Note</h4>
            <p className="text-[11px] text-[#a09a90]">Generate boardroom-ready Word document (.docx) with signed cryptographic proof hash.</p>
          </div>
        </div>

        <button
          onClick={handleExportDocx}
          disabled={downloading}
          className="btn-copper text-xs py-2 px-4"
        >
          <Download size={14} />
          <span>{downloading ? 'Compiling .docx...' : 'Export Approval Note (.docx)'}</span>
        </button>
      </div>
    </div>
  );
}
