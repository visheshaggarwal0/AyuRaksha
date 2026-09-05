import React, { useState } from 'react';
import { BookOpen, Network, ShieldCheck } from 'lucide-react';
import { CorpusExplorer } from './CorpusExplorer';
import { KnowledgeGraphExplorer } from '../graph/KnowledgeGraphExplorer';

interface EvaluatorCorpusSuiteProps {
  onSelectCitation?: (c: any) => void;
  onAskCopilot?: (q: string) => void;
}

export const EvaluatorCorpusSuite: React.FC<EvaluatorCorpusSuiteProps> = ({
  onSelectCitation,
  onAskCopilot
}) => {
  const [activeTab, setActiveTab] = useState<'corpus' | 'graph'>('corpus');

  return (
    <div className="h-full flex flex-col space-y-4 animate-fadeIn">
      {/* Top Switcher Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 shrink-0">
        <div className="flex items-center space-x-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200/80 text-xs font-bold">
          <button
            onClick={() => setActiveTab('corpus')}
            className={`px-3.5 py-1.5 rounded-lg transition-all flex items-center space-x-1.5 cursor-pointer ${
              activeTab === 'corpus'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-ayush-forest" />
            <span>Statutory Corpus & Gazette Provenance</span>
          </button>
          <button
            onClick={() => setActiveTab('graph')}
            className={`px-3.5 py-1.5 rounded-lg transition-all flex items-center space-x-1.5 cursor-pointer ${
              activeTab === 'graph'
                ? 'bg-ayush-forest text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Network className="w-3.5 h-3.5 text-emerald-200" />
            <span>Relational Knowledge Graph</span>
          </button>
        </div>

        <div className="hidden sm:flex items-center space-x-2 text-[11px] font-semibold text-slate-500 bg-slate-50 px-3 py-1 rounded-lg border border-slate-200">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>SIH 26045 Ground Truth Evaluator Suite</span>
        </div>
      </div>

      {/* Main Content Pane */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        {activeTab === 'corpus' ? (
          <CorpusExplorer />
        ) : (
          <KnowledgeGraphExplorer
            onSelectCitation={onSelectCitation}
            onAskCopilot={onAskCopilot}
          />
        )}
      </div>
    </div>
  );
};
