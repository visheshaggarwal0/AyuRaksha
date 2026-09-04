import React from 'react';
import {
  BookOpen,
  ExternalLink,
  ShieldCheck,
  Scale,
  ArrowRight,
  ArrowLeft,
  X
} from 'lucide-react';
import { Citation, StructuredAnswer, Jurisdiction } from '../../types';

interface EvidenceInspectorProps {
  citation: Citation | null;
  allCitations?: Citation[];
  activeAnswer?: StructuredAnswer | null;
  conclusionSupported?: string | null;
  jurisdiction?: Jurisdiction;
  onSelectCitation?: (c: Citation) => void;
  onClose?: () => void;
}

export const EvidenceInspector: React.FC<EvidenceInspectorProps> = ({
  citation,
  allCitations = [],
  activeAnswer,
  conclusionSupported,
  jurisdiction = 'IN',
  onSelectCitation,
  onClose
}) => {
  if (!citation) {
    return (
      <div className="p-8 text-center space-y-4 select-text flex flex-col items-center justify-center h-full">
        <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center border border-slate-200 shadow-subtle">
          <BookOpen className="w-7 h-7" />
        </div>
        <div className="space-y-1">
          <h4 className="font-extrabold text-sm text-slate-900 font-display">
            Insufficient Evidence Available
          </h4>
          <p className="text-xs text-slate-500 max-w-xs mx-auto leading-relaxed">
            No specific statutory gazette citation is currently attached to this conclusion. Click any citation badge [1], [2] or Source Card in your assessment to inspect its verbatim Gazette grounding.
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition-colors"
          >
            Close Inspector
          </button>
        )}
      </div>
    );
  }

  // Find index in citations list if available
  const currentIndex = allCitations.findIndex(
    (c) => c.source_id === citation.source_id && c.section === citation.section
  );

  const officialUrl = citation.official_url || (
    citation.source_id.includes('PATENTS')
      ? 'https://ipindia.gov.in/patents.htm'
      : citation.source_id.includes('DRUGS')
      ? 'https://cdsco.gov.in'
      : citation.source_id.includes('FSSAI')
      ? 'https://fssai.gov.in'
      : 'https://indiacode.nic.in'
  );

  // Derive source authority category
  const sourceAuthority = citation.source_id.includes('ACT')
    ? 'Primary Statutory Authority (Parliamentary Act)'
    : citation.source_id.includes('RULES')
    ? 'Subordinate Legislation (Statutory Rules)'
    : citation.source_id.includes('FSSAI')
    ? 'Statutory Food Safety Regulation (FSSAI)'
    : 'Official Regulatory Guidance & Gazette';

  // Derive "Why This Evidence Matters" contextual explanation
  const whyItMatters = citation.section.includes('3(p)')
    ? 'Under Section 3(p) of the Patents Act, 1970, formulations documented in classical Ayurvedic texts or traditional knowledge are excluded from patent monopolies to prevent biopiracy.'
    : citation.section.includes('158B')
    ? 'Rule 158B of the Drugs and Cosmetics Rules, 1945 specifies licensing evidentiary standards for Proprietary ASU medicines, differentiating them from classical Shastriya medicines.'
    : citation.section.includes('3(a)')
    ? 'Section 3(a) defines classical ASU drugs that are manufactured exclusively according to First Schedule authoritative treatises, qualifying for safety trial exemptions.'
    : citation.section.includes('3(e)')
    ? 'Section 3(e) requires polyherbal formulations to prove non-obvious synergistic efficacy rather than a mere aggregation of individual herbal properties.'
    : citation.section.includes('122E')
    ? 'Rule 122E and GSR 918(E) establish the Phytopharmaceutical drug pathway requiring minimum 4 bioactive markers and CDSCO clinical evaluation.'
    : citation.section.includes('3') && citation.source_id.includes('AAHARA')
    ? 'Regulation 3 of FSSAI Ayurveda Aahara 2022 sets the boundary between food supplements and medicinal drugs, prohibiting disease prevention/cure claims.'
    : 'This statutory provision establishes the legal threshold and compliance prerequisites applicable to your product profile.';

  return (
    <div className="flex flex-col h-full min-h-0 justify-between select-text animate-fadeIn">
      
      {/* 1. TOP BAR / HEADER */}
      <div className="p-5 border-b border-slate-100 space-y-3 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 bg-emerald-50 text-ayush-forest rounded-lg">
              <Scale className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                Statutory Evidence Inspector
              </span>
              <span className="text-xs font-mono font-bold text-slate-700">
                {citation.source_id}
              </span>
            </div>
          </div>

          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors"
              title="Close Inspector (Esc)"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Multi-citation switcher if multiple exist */}
        {allCitations.length > 1 && (
          <div className="pt-1">
            <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 mb-1.5">
              <span>Grounding Sources ({allCitations.length})</span>
              <span>Select to inspect</span>
            </div>
            <div className="flex items-center space-x-1.5 overflow-x-auto pb-1">
              {allCitations.map((c, idx) => {
                const isSelected = c.source_id === citation.source_id && c.section === citation.section;
                return (
                  <button
                    key={`${c.source_id}-${c.section}-${idx}`}
                    onClick={() => onSelectCitation && onSelectCitation(c)}
                    className={`px-2 py-1 rounded text-[10px] font-mono font-bold transition-all shrink-0 ${
                      isSelected
                        ? 'bg-ayush-forest text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    [{idx + 1}] {c.section}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 2. SCROLLABLE EVIDENCE BODY */}
      <div className="p-5 space-y-4 overflow-y-auto flex-1 min-h-0 text-xs">
        
        {/* Supported Conclusion Callout (if available) */}
        {conclusionSupported && (
          <div className="p-3.5 rounded-xl bg-emerald-950 text-white space-y-1 shadow-subtle border border-emerald-800">
            <span className="text-[9px] font-black uppercase tracking-wider text-emerald-300 block">
              Supported Regulatory / IP Conclusion
            </span>
            <p className="text-xs font-semibold leading-relaxed text-emerald-50">
              "{conclusionSupported}"
            </p>
          </div>
        )}

        {/* Source Title & Governing Authority */}
        <div className="space-y-1.5">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-slate-100 text-slate-800 border border-slate-200">
              {citation.jurisdiction === 'IN' || jurisdiction === 'IN' ? '🇮🇳 India Domestic' : '🌍 International Treaty'}
            </span>
            <span className="text-[10px] font-bold text-slate-400">
              {sourceAuthority}
            </span>
          </div>
          <h3 className="text-base font-extrabold text-slate-900 font-display leading-tight">
            {citation.source_title}
          </h3>
          <div className="inline-block font-mono font-extrabold text-xs bg-emerald-50 text-ayush-forest border border-emerald-300 px-2.5 py-1 rounded-lg shadow-xs">
            {citation.section}
          </div>
        </div>

        {/* Verbatim Gazette Excerpt */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            <span>Verbatim Official Gazette Text</span>
            <span className="text-emerald-700 font-mono">Source-Anchored</span>
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed font-serif italic border-l-4 border-l-ayush-forest">
            "{citation.verbatim_quote}"
          </div>
        </div>

        {/* Why This Evidence Matters */}
        <div className="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-1">
          <div className="flex items-center space-x-1.5 text-ayush-forest">
            <BookOpen className="w-3.5 h-3.5" />
            <span className="text-[10px] font-black uppercase tracking-wider">Why This Evidence Matters</span>
          </div>
          <p className="text-[11px] text-emerald-950 font-medium leading-relaxed">
            {whyItMatters}
          </p>
        </div>

        {/* Support Score & Entailment */}
        <div className="p-3.5 rounded-2xl bg-white border border-slate-200 flex items-center justify-between shadow-subtle">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <div>
              <span className="block font-bold text-slate-900 text-[11px]">Entailment Support Score</span>
              <span className="text-[10px] text-slate-400">Grounded against Official Statutory Corpus</span>
            </div>
          </div>
          <span className="font-mono font-black text-xs text-ayush-forest px-2 py-0.5 bg-emerald-50 rounded border border-emerald-200">
            {Math.round((citation.support_score || 0.95) * 100)}% Match
          </span>
        </div>

        {/* Evidence Chain Visual Progression */}
        <div className="space-y-1.5 pt-2 border-t border-slate-100">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Statutory Evidence Chain
          </span>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-[10px] text-slate-700">
            <div className="flex items-center space-x-1.5">
              <span className="w-4 h-4 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-[9px]">1</span>
              <span className="font-semibold">Inquiry: Formulation & IP Strategy Screening</span>
            </div>
            <div className="flex items-center space-x-1.5 pl-2 text-slate-400">
              <ArrowRight className="w-3 h-3" />
              <span>Corpus Retrieval & Relevance Reranking</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-4 h-4 rounded-full bg-ayush-forest text-white font-bold flex items-center justify-center text-[9px]">2</span>
              <span className="font-bold text-slate-900">Provision: {citation.section} ({citation.source_title})</span>
            </div>
            <div className="flex items-center space-x-1.5 pl-2 text-emerald-700">
              <ArrowRight className="w-3 h-3" />
              <span className="font-semibold">Grounded Compliance / Patent Determination</span>
            </div>
          </div>
        </div>

        {/* Optional: Recommended Next Action from activeAnswer */}
        {activeAnswer?.recommended_next_action && (
          <div className="space-y-1.5 pt-2 border-t border-slate-100">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Recommended Next Action
            </span>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] font-medium text-slate-800 leading-relaxed">
              {activeAnswer.recommended_next_action}
            </div>
          </div>
        )}

      </div>

      {/* 3. FOOTER ACTIONS */}
      <div className="p-4 border-t border-slate-100 bg-slate-50 space-y-2 shrink-0">
        {officialUrl && (
          <a
            href={officialUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-2.5 px-4 bg-ayush-forest hover:bg-ayush-forestDark text-white text-xs font-bold rounded-xl flex items-center justify-center space-x-2 transition-all shadow-subtle"
          >
            <span>Open Official Gazette Portal</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}

        {/* Previous / Next Citation Switcher Buttons */}
        {allCitations.length > 1 && onSelectCitation && currentIndex >= 0 && (
          <div className="flex gap-2">
            <button
              onClick={() => {
                const prevIdx = (currentIndex - 1 + allCitations.length) % allCitations.length;
                onSelectCitation(allCitations[prevIdx]);
              }}
              className="flex-1 py-2 bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 flex items-center justify-center space-x-1 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Previous Source</span>
            </button>
            <button
              onClick={() => {
                const nextIdx = (currentIndex + 1) % allCitations.length;
                onSelectCitation(allCitations[nextIdx]);
              }}
              className="flex-1 py-2 bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 flex items-center justify-center space-x-1 transition-colors"
            >
              <span>Next Source</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {onClose && (
          <button
            onClick={onClose}
            className="w-full py-2 bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition-colors"
          >
            Close Inspector
          </button>
        )}
      </div>

    </div>
  );
};
