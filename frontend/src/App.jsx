import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LiveExecutionDrawer from './components/LiveExecutionDrawer';
import LocalIntelligenceCard from './components/LocalIntelligenceCard';

import WorkbenchView from './views/WorkbenchView';
import KnowledgeGraphView from './views/KnowledgeGraphView';
import DataSourcesView from './views/DataSourcesView';
import IntelligenceAgentsView from './views/IntelligenceAgentsView';
import IntelligenceModelsView from './views/IntelligenceModelsView';
import SovereigntyView from './views/SovereigntyView';

export default function App() {
  const [activeView, setActiveView] = useState('workbench');

  return (
    <div className="min-h-screen bg-[#141312] text-[#f5f2ed] flex flex-col font-sans selection:bg-[#d9825b] selection:text-white">
      {/* Top Header with Target Air-Gapped Status Widget */}
      <Header />

      {/* Main Layout Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Categorized Left Sidebar */}
        <Sidebar activeView={activeView} onViewChange={setActiveView} />

        {/* Dynamic Center Main Content Area */}
        <main className="flex-1 p-6 overflow-y-auto max-w-[1600px] mx-auto w-full">
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
            {/* Center View Area (8 cols on XL screens) */}
            <div className={`${activeView === 'workbench' ? 'xl:col-span-8' : 'xl:col-span-12'}`}>
              {activeView === 'workbench' && <WorkbenchView />}
              {activeView === 'home' && <WorkbenchView />}
              {activeView === 'graph' && <KnowledgeGraphView />}
              {activeView === 'knowledge' && <KnowledgeGraphView />}
              {activeView === 'data-sources' && <DataSourcesView />}
              {activeView === 'intelligence-agents' && <IntelligenceAgentsView />}
              {activeView === 'intelligence-models' && <IntelligenceModelsView />}
              {activeView === 'intelligence-tools' && <IntelligenceAgentsView />}
              {activeView === 'sovereignty' && <SovereigntyView />}
              {activeView === 'audit-trail' && <SovereigntyView />}
              {activeView === 'settings' && <SovereigntyView />}
              {activeView === 'sessions' && <WorkbenchView />}
              {activeView === 'tasks' && <WorkbenchView />}
            </div>

            {/* Right Execution Sidebar (4 cols on XL screens when in Workbench) */}
            {activeView === 'workbench' && (
              <div className="xl:col-span-4 space-y-5">
                <LiveExecutionDrawer />
                <LocalIntelligenceCard />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
