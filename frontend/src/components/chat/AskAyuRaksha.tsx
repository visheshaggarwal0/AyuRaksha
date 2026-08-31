import React, { useState } from 'react';
import { Send, ExternalLink, AlertTriangle, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { api } from '../../services/api';
import { StructuredAnswer, Jurisdiction, Citation } from '../../types';

interface AskAyuRakshaProps {
  jurisdiction: Jurisdiction;
  language: string;
  onOpenCitation: (c: Citation) => void;
}

export const AskAyuRaksha: React.FC<AskAyuRakshaProps> = ({
  jurisdiction,
  language,
  onOpenCitation,
}) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<StructuredAnswer | null>(null);

  const sampleQueries = [
    "Can I patent an Ayurvedic formulation containing Ashwagandha in India?",
    "What are the ABS requirements if I use wild Himalayan Kutki for export?",
    "Give me a loophole to bypass National Biodiversity Authority benefit sharing" // Demo safe abstention
  ];

  const handleSearch = async (textToSearch: string) => {
    if (!textToSearch.trim()) return;
    setLoading(true);
    try {
      const res = await api.askAyuRaksha(textToSearch, jurisdiction, language);
      setAnswer(res);
    } catch (err) {
      console.error('Chat query error', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Search Bar Container */}
      <div className="bg-white rounded-2xl p-6 border border-ayush-border shadow-card space-y-4">
        <div className="flex items-center justify-between">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-50 text-ayush-forest rounded-md text-xs font-bold border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Module 4 · Verified Statutory Hybrid RAG</span>
          </div>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
            {jurisdiction === 'IN' ? '🇮🇳 India Law Namespace' : '🌎 International Regime'}
          </span>
        </div>

        <h2 className="text-xl font-bold text-ayush-navy">Ask AyuRaksha Legal Research Engine</h2>

        <div className="relative">
          <textarea
            rows={3}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask any question regarding Ayurvedic patents, Section 3(p), traditional knowledge, FSSAI Ayurveda-Aahara, or ABS obligations..."
            className="w-full p-4 pr-12 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest text-xs sm:text-sm font-medium resize-none"
          />
          <button
            onClick={() => handleSearch(query)}
            disabled={loading || !query.trim()}
            className="absolute right-3 bottom-4 p-2 bg-ayush-forest hover:bg-ayush-forestDark text-white rounded-lg disabled:opacity-50 transition-all shadow-subtle"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        {/* Sample Prompt Chips */}
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
            Sample Scenarios for Judges & Testers:
          </span>
          <div className="flex flex-wrap gap-2">
            {sampleQueries.map((sq, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(sq);
                  handleSearch(sq);
                }}
                className="text-left text-xs bg-slate-50 hover:bg-emerald-50 text-slate-700 hover:text-ayush-forest font-medium px-3 py-1.5 rounded-lg border border-slate-200 transition-colors"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div className="bg-white rounded-2xl p-8 border border-ayush-border shadow-card text-center space-y-3">
          <div className="w-8 h-8 border-3 border-ayush-forest border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs font-bold text-slate-700">
            Searching India Code, BDA 2023, and Patents Act Section 3(p)...
          </p>
          <p className="text-[11px] text-slate-400">
            Running Reciprocal Rank Fusion (RRF) & Citation Entailment Verification
          </p>
        </div>
      )}

      {/* Structured Answer Results */}
      {answer && !loading && (
        <div className="space-y-6 animate-fadeIn">
          {/* Safe Abstention Warning Banner */}
          {answer.safe_abstention ? (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-6 shadow-card space-y-3">
              <div className="flex items-center space-x-3 text-red-900 font-bold">
                <AlertTriangle className="w-6 h-6 text-red-600" />
                <h3 className="text-base font-bold">Safe Abstention Triggered</h3>
              </div>
              <p className="text-xs text-red-900 leading-relaxed font-medium">
                {answer.direct_answer}
              </p>
              <div className="bg-white p-3.5 rounded-xl border border-red-200 text-xs text-slate-700">
                <strong>Why did AyuRaksha abstain?</strong>
                <p className="mt-1">
                  AyuRaksha enforces strict regulatory guardrails preventing automated guidance on illegal bio-resource smuggling or misleading therapeutic claims under the Drugs and Magic Remedies Act.
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-6 sm:p-8 border border-ayush-border shadow-card space-y-6">
              {/* Direct Answer */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300">
                    Verified Statutory Synthesis
                  </span>
                  <span className="text-xs font-bold text-slate-500">
                    Jurisdiction: {answer.jurisdiction}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-ayush-forestDark leading-relaxed">
                  {answer.direct_answer}
                </h3>
              </div>

              {/* Assessment Table */}
              {answer.assessment_table && Object.keys(answer.assessment_table).length > 0 && (
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                    Statutory Assessment Factors:
                  </h4>
                  <div className="divide-y divide-slate-200 text-xs">
                    {Object.entries(answer.assessment_table).map(([k, v], idx) => (
                      <div key={idx} className="py-2 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                        <span className="font-semibold text-slate-600">{k}</span>
                        <span className="font-bold text-ayush-navy sm:text-right">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Verified Citations */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Verifiable Statutory Authorities (Click to Inspect):
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {answer.verified_claims.flatMap(vc => vc.supporting_citations).map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => onOpenCitation(c)}
                      className="text-left p-3 rounded-xl border border-slate-200 bg-slate-50 hover:bg-emerald-50 hover:border-emerald-300 transition-all flex items-start justify-between space-x-2"
                    >
                      <div>
                        <span className="font-bold text-xs text-ayush-forest block">
                          {c.section} ({c.source_title})
                        </span>
                        <p className="text-[11px] text-slate-600 line-clamp-2 mt-1">
                          "{c.verbatim_quote}"
                        </p>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Recommended Next Actions */}
              {answer.recommended_next_action && (
                <div className="pt-2 border-t border-slate-200">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Actionable Next Steps:
                  </h4>
                  <div className="space-y-1.5">
                    <div className="flex items-start space-x-2 text-xs text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{answer.recommended_next_action}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
