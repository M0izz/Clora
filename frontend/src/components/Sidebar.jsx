import React from 'react';
import {
  Home,
  Layers,
  Clock,
  CheckSquare,
  BookOpen,
  Database,
  Network,
  Bot,
  Cpu,
  Wrench,
  ShieldCheck,
  FileText,
  Settings
} from 'lucide-react';

export default function Sidebar({ activeView = 'workbench', onViewChange }) {
  const navSections = [
    {
      title: 'WORK',
      items: [
        { id: 'home', label: 'Home', icon: Home },
        { id: 'workbench', label: 'Workbench', icon: Layers },
        { id: 'sessions', label: 'Sessions', icon: Clock },
        { id: 'tasks', label: 'Tasks', icon: CheckSquare },
      ]
    },
    {
      title: 'KNOWLEDGE',
      items: [
        { id: 'knowledge', label: 'Knowledge', icon: BookOpen },
        { id: 'data-sources', label: 'Data Sources', icon: Database },
        { id: 'graph', label: 'Graph', icon: Network },
      ]
    },
    {
      title: 'INTELLIGENCE',
      items: [
        { id: 'intelligence-agents', label: 'Agents', icon: Bot },
        { id: 'intelligence-models', label: 'Models', icon: Cpu },
        { id: 'intelligence-tools', label: 'Tools', icon: Wrench },
      ]
    },
    {
      title: 'TRUST',
      items: [
        { id: 'sovereignty', label: 'Sovereignty', icon: ShieldCheck },
        { id: 'audit-trail', label: 'Audit Trail', icon: FileText },
      ]
    },
    {
      title: 'SYSTEM',
      items: [
        { id: 'settings', label: 'Settings', icon: Settings },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-[#161412] border-r border-[#2a2622] flex flex-col justify-between p-3 select-none shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-5">
        {navSections.map((section) => (
          <div key={section.title} className="space-y-1">
            <span className="px-3 text-[10px] font-bold tracking-widest text-[#6d675e] uppercase font-mono">
              {section.title}
            </span>
            <div className="space-y-0.5 mt-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeView === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onViewChange && onViewChange(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-[#d9825b] text-white shadow-sm font-semibold'
                        : 'text-[#a09a90] hover:text-[#f5f2ed] hover:bg-[#201d1a]'
                    }`}
                  >
                    <Icon size={16} className={isActive ? 'text-white' : 'text-[#8a8377]'} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Bottom Status Footer */}
      <div className="p-3 rounded-xl bg-[#1d1a18] border border-[#2e2a25] flex items-center justify-between text-[11px] text-[#8a8377]">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#10b981]" />
          <span>v1.0 Sovereign</span>
        </div>
        <span className="font-mono text-[#6d675e]">MRPL SIH</span>
      </div>
    </aside>
  );
}
