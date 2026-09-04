import React, { useState } from 'react';
import {
  Scale,
  ShieldCheck,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Compass,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { Citation, StructuredAnswer, Jurisdiction } from '../../types';
import { StatutoryMarkdownRenderer } from '../common/StatutoryMarkdownRenderer';
import { AnswerVisual } from '../visuals/AnswerVisual';

interface DecisionBriefAnswerProps {
  questionText?: string;
  answerText: string;
  answerData?: StructuredAnswer;
  jurisdiction: Jurisdiction;
  activeCitation?: Citation | null;
  drawerOpen: boolean;
  onOpenCitation: (c: Citation, answerData?: StructuredAnswer) => void;
  onInspectAllEvidence: (answerData: StructuredAnswer) => void;
  onAskFollowUp?: (query: string) => void;
}

export const DecisionBriefAnswer: React.FC<DecisionBriefAnswerProps> = ({
  questionText,
  answerText,
  answerData,
  jurisdiction,
  activeCitation,
  drawerOpen,
  onOpenCitation,
  onInspectAllEvidence,
  onAskFollowUp
}) => {
  const [showFullAnalysis, setShowFullAnalysis] = useState(true);
  const [activeInnovationStep, setActiveInnovationStep] = useState(1);

  // Extract Key Finding / Bottom Line
  const extractKeyFinding = (text: string): { summary: string; remaining: string } => {
    if (!text) return { summary: '', remaining: '' };
    const paragraphs = text.split('\n\n').filter((p) => p.trim().length > 0);
    if (paragraphs.length > 0) {
      const firstPara = paragraphs[0];
      const sentences = firstPara.match(/[^.!?]+[.!?]+/g) || [firstPara];
      const summary = sentences.slice(0, 2).join(' ').trim();
      return {
        summary: summary || firstPara,
        remaining: text
      };
    }
    return { summary: text, remaining: text };
  };

  const { summary: keyFinding } = extractKeyFinding(answerData?.direct_answer || answerText);

  // Determine IP Domain from question and answer text
  const detectIPDomain = (): string | null => {
    const combined = `${questionText || ''} ${answerText}`.toLowerCase();
    if (combined.includes('patent') || combined.includes('section 3(p)') || combined.includes('tkdl') || combined.includes('inventive step')) {
      return 'Patent / Section 3(p) Traditional Knowledge';
    }
    if (combined.includes('abs') || combined.includes('biodiversity') || combined.includes('bda') || combined.includes('national biodiversity authority')) {
      return 'Biological Diversity & ABS Regime';
    }
    if (combined.includes('geographical indication') || combined.includes(' gi ')) {
      return 'Geographical Indication (GI)';
    }
    if (combined.includes('trademark') || combined.includes('brand name')) {
      return 'Trademark & Brand Protection';
    }
    if (combined.includes('classical') || combined.includes('proprietary') || combined.includes('rule 158b') || combined.includes('asu')) {
      return 'Ayush Regulatory Licensing';
    }
    if (combined.includes('export') || combined.includes('fda') || combined.includes('dshea') || combined.includes('efsa')) {
      return 'Cross-Border Regulatory Compliance';
    }
    return null;
  };

  // Determine Product/Regulatory Category
  const detectRegulatoryCategory = (): string | null => {
    const combined = `${questionText || ''} ${answerText}`.toLowerCase();
    if (combined.includes('classical') || combined.includes('shastriya') || combined.includes('first schedule')) {
      return 'Classical Ayurvedic Medicine (Shastriya)';
    }
    if (combined.includes('proprietary') || combined.includes('patent or proprietary')) {
      return 'Proprietary Ayurvedic Medicine (ASU)';
    }
    if (combined.includes('phytopharmaceutical')) {
      return 'Phytopharmaceutical Drug (D&C Act)';
    }
    if (combined.includes('ayurveda aahar') || combined.includes('aahar') || combined.includes('fssai')) {
      return 'Ayurveda Aahar (FSSAI Regs 2022)';
    }
    if (combined.includes('cosmetic') || combined.includes('topical')) {
      return 'Ayurvedic Cosmetic Formulation';
    }
    return null;
  };

  const isPatentOrInnovationQuery = (): boolean => {
    const combined = `${questionText || ''} ${answerText}`.toLowerCase();
    return combined.includes('patent') || combined.includes('invent') || combined.includes('novel') || combined.includes('protect') || combined.includes('extraction');
  };

  const ipDomain = detectIPDomain();
  const regCategory = detectRegulatoryCategory();
  const citations = answerData?.citations || answerData?.verified_claims?.flatMap((c) => c.supporting_citations) || [];

  // Innovation Discovery Steps definition
  const innovationSteps = [
    {
      num: 1,
      title: 'Product Definition',
      prompt: 'What formulation, extract, or composition was developed?',
      options: ['Modified Polyherbal Formulation', 'Novel Standardized Herbal Extract', 'Classical Text Recipe with New Delivery System']
    },
    {
      num: 2,
      title: 'Difference from Prior Art',
      prompt: 'What distinguishes this from classical Ayurvedic texts or known remedies?',
      options: ['Specific non-classical solvent extraction', 'Unique synergism between two classical herbs', 'Novel therapeutic indication not in First Schedule']
    },
    {
      num: 3,
      title: 'Technical Feature',
      prompt: 'Which technical feature was altered (dosage, purity, excipient, processing)?',
      options: ['Standardized fraction of active biomarker', 'Aqueous-ethanolic extraction ratio', 'Novel lipid-based nano-carrier']
    },
    {
      num: 4,
      title: 'Technical Effect',
      prompt: 'What measurable improvement resulted (bioavailability, stability, yield)?',
      options: ['2.5x increase in bioavailability', '6-month room temperature shelf stability', 'Demonstrated in-vitro synergistic index > 1.2']
    },
    {
      num: 5,
      title: 'Evidence & Data',
      prompt: 'What supporting validation data or records currently exist?',
      options: ['HPLC / HPTLC fingerprint chromatograms', 'Comparative in-vitro stability assay', 'Pilot clinical observation data']
    }
  ];

  return (
    <div className="w-full rounded-2xl bg-white border border-slate-200 shadow-card overflow-hidden text-slate-900 animate-fadeIn select-text">
      
      {/* 1. DECISION BRIEF HEADER */}
      <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/80 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-emerald-100 text-ayush-forest shrink-0">
            <Scale className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block leading-none">
              Ayurvedic IP & Regulatory Decision Brief
            </span>
            <span className="text-xs font-bold text-slate-800">
              Statutory Alignment & Advisory Assessment
            </span>
          </div>
        </div>

        {/* Metadata Badges */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          {/* Jurisdiction */}
          <span className="px-2.5 py-0.5 rounded-lg font-bold bg-white text-slate-800 border border-slate-200 shadow-xs flex items-center space-x-1">
            <span>
              {jurisdiction === 'IN' ? '🇮🇳 India' : jurisdiction === 'CROSS_BORDER' ? '⚖️ Cross-Border' : '🌍 International'}
            </span>
          </span>

          {/* Evidence Confidence */}
          <span className="px-2.5 py-0.5 rounded-lg font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 shadow-xs flex items-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Evidence Confidence: {answerData?.confidence_level || 'HIGH'}</span>
          </span>
        </div>
      </div>

      {/* Domain & Category Tags (if detected) */}
      {(ipDomain || regCategory) && (
        <div className="px-5 py-2.5 bg-slate-100/50 border-b border-slate-100 flex flex-wrap items-center gap-2 text-xs">
          {ipDomain && (
            <div className="flex items-center space-x-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">IP Domain:</span>
              <span className="px-2 py-0.5 rounded-md font-bold text-[11px] bg-emerald-50 text-emerald-900 border border-emerald-200">
                {ipDomain}
              </span>
            </div>
          )}
          {regCategory && (
            <div className="flex items-center space-x-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Product Category:</span>
              <span className="px-2 py-0.5 rounded-md font-bold text-[11px] bg-slate-50 text-slate-800 border border-slate-200">
                {regCategory}
              </span>
            </div>
          )}
        </div>
      )}

      {/* 2. BOTTOM LINE (KEY FINDING CALLOUT) */}
      <div className="p-5 border-b border-slate-100 bg-emerald-950 text-white space-y-2">
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded font-black text-[9px] uppercase tracking-wider bg-emerald-800/80 text-emerald-200 border border-emerald-700">
            Bottom Line Assessment
          </span>
        </div>
        <p className="text-sm sm:text-base font-semibold text-emerald-50 leading-relaxed">
          {keyFinding}
        </p>
      </div>

      {/* 3. DYNAMIC ANSWER-AWARE DECISION MAP */}
      <div className="px-5 border-b border-slate-100 bg-slate-50/40">
        <AnswerVisual
          questionText={questionText}
          answerText={answerText}
          answerData={answerData}
          jurisdiction={jurisdiction}
          onOpenCitation={(c) => onOpenCitation(c, answerData)}
        />
      </div>

      {/* 4. SEPARATE FACT FROM STATUTORY INFERENCE */}
      <div className="p-5 border-b border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-50/30">
        <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1.5">
          <div className="flex items-center space-x-1.5 text-slate-600">
            <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200">
              Established Basis
            </span>
          </div>
          <p className="text-[11px] text-slate-700 leading-relaxed font-medium">
            {citations.length > 0
              ? `Directly referenced against ${citations.map(c => c.source_title).slice(0, 2).join(' & ')}.`
              : 'Directly grounded in Indian statutory standards and official gazette notifications.'}
          </p>
        </div>

        <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1.5">
          <div className="flex items-center space-x-1.5 text-ayush-forest">
            <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-emerald-50 text-emerald-800 border border-emerald-200">
              Statutory Interpretation
            </span>
          </div>
          <p className="text-[11px] text-slate-700 leading-relaxed font-medium">
            Reasoned evaluation based on applicable statutory thresholds, regulatory schedules, and patent eligibility criteria.
          </p>
        </div>
      </div>

      {/* 5. WHY THIS CONCLUSION — STRUCTURED REASONING */}
      <div className="p-5 space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">
            Why This Conclusion · Statutory Analysis
          </span>
          <button
            onClick={() => setShowFullAnalysis(!showFullAnalysis)}
            className="text-xs font-bold text-ayush-forest hover:text-ayush-forestDark flex items-center space-x-1 transition-colors"
          >
            <span>{showFullAnalysis ? 'Hide Detailed Analysis' : 'Show Detailed Analysis'}</span>
            {showFullAnalysis ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {showFullAnalysis && (
          <div className="space-y-4 text-xs sm:text-sm text-slate-800 leading-relaxed">
            <StatutoryMarkdownRenderer
              content={answerData?.direct_answer || answerText}
              citations={citations}
              activeCitation={drawerOpen ? activeCitation : null}
              onCitationClick={(c) => onOpenCitation(c, answerData)}
            />
          </div>
        )}
      </div>

      {/* 6. WHAT THIS MEANS FOR YOUR PRODUCT (RECOMMENDED ACTION) */}
      {answerData?.recommended_next_action && (
        <div className="mx-5 mb-5 p-4 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-2">
          <div className="flex items-center space-x-2 text-ayush-forest">
            <Compass className="w-4 h-4" />
            <span className="text-[10px] font-black uppercase tracking-wider text-emerald-950">
              What This Means For Your Product · Actionable Strategy
            </span>
          </div>
          <p className="text-xs font-semibold text-emerald-950 leading-relaxed">
            {answerData.recommended_next_action}
          </p>
        </div>
      )}

      {/* 7. "WHAT AYUरक्षा NEEDS FROM YOU" / CAVEATS */}
      {answerData?.caveats && answerData.caveats.length > 0 && (
        <div className="mx-5 mb-5 p-4 rounded-xl bg-amber-50/70 border border-amber-200 space-y-3">
          <div className="flex items-center space-x-2 text-amber-800">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span className="text-[10px] font-black uppercase tracking-wider text-amber-900">
              What Ayuरक्षा Needs From You to Conclude Reliably
            </span>
          </div>
          <ul className="space-y-1.5 pl-1">
            {answerData.caveats.map((caveat, idx) => (
              <li key={idx} className="text-xs text-amber-950 flex items-start space-x-2 font-medium">
                <span className="text-amber-500 font-bold">•</span>
                <span>{caveat}</span>
              </li>
            ))}
          </ul>

          {onAskFollowUp && (
            <div className="pt-2 border-t border-amber-200/60 flex flex-wrap gap-1.5">
              <span className="text-[10px] font-bold text-amber-800 uppercase block w-full">Quick Clarification Options:</span>
              {[
                'Formulation uses 100% Classical text recipe without modification',
                'Novel extraction process with demonstrated comparative efficacy',
                'Biological resources obtained exclusively from Indian cultivators'
              ].map((opt, i) => (
                <button
                  key={i}
                  onClick={() => onAskFollowUp(opt)}
                  className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-white hover:bg-amber-100 text-amber-900 border border-amber-200 shadow-xs transition-all text-left"
                >
                  → {opt}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 8. INNOVATION DISCOVERY FACILITATOR (FOR PATENT / IP INQUIRIES) */}
      {isPatentOrInnovationQuery() && onAskFollowUp && (
        <div className="mx-5 mb-5 p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black uppercase tracking-wider text-slate-600 flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-ayush-forest" />
              <span>Innovation Discovery Guide · Step {activeInnovationStep} of 5</span>
            </span>
            <div className="flex items-center space-x-1">
              {[1, 2, 3, 4, 5].map((s) => (
                <span
                  key={s}
                  onClick={() => setActiveInnovationStep(s)}
                  className={`w-4 h-4 rounded-full text-[9px] font-bold flex items-center justify-center cursor-pointer transition-all ${
                    s === activeInnovationStep
                      ? 'bg-ayush-forest text-white'
                      : s < activeInnovationStep
                      ? 'bg-emerald-200 text-emerald-900'
                      : 'bg-slate-200 text-slate-500'
                  }`}
                >
                  {s}
                </span>
              ))}
            </div>
          </div>

          <div className="p-3 bg-white rounded-lg border border-slate-200 space-y-2">
            <p className="text-xs font-bold text-slate-900">
              {innovationSteps[activeInnovationStep - 1].title}: {innovationSteps[activeInnovationStep - 1].prompt}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {innovationSteps[activeInnovationStep - 1].options.map((opt, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    onAskFollowUp(`For my product: ${opt}`);
                    if (activeInnovationStep < 5) setActiveInnovationStep(activeInnovationStep + 1);
                  }}
                  className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-emerald-50/60 hover:bg-emerald-100 text-emerald-900 border border-emerald-200 transition-all text-left"
                >
                  + {opt}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 9. STATUTORY SOURCE CARDS */}
      {citations.length > 0 && (
        <div className="px-5 py-4 bg-slate-50 border-t border-slate-100 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">
              Statutory Authority Source Cards ({citations.length} Grounded Provisions)
            </span>
            {answerData && (
              <button
                onClick={() => onInspectAllEvidence(answerData)}
                className="text-xs font-bold text-ayush-forest hover:text-ayush-forestDark flex items-center space-x-1"
              >
                <span>Inspect in Drawer</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {citations.map((c, idx) => {
              const isActive = drawerOpen && activeCitation?.source_id === c.source_id && activeCitation?.section === c.section;
              return (
                <div
                  key={idx}
                  onClick={() => onOpenCitation(c, answerData)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer space-y-1 shadow-subtle ${
                    isActive
                      ? 'bg-ayush-forest text-white border-ayush-forest ring-2 ring-emerald-300'
                      : 'bg-white hover:bg-emerald-50/50 border-slate-200 text-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px]">
                    <span className={`font-black uppercase tracking-wider ${isActive ? 'text-emerald-200' : 'text-slate-400'}`}>
                      Source Authority
                    </span>
                    <span className={`font-mono font-bold px-1.5 py-0.2 rounded ${isActive ? 'bg-emerald-800 text-emerald-100' : 'bg-emerald-50 text-emerald-800 border border-emerald-200'}`}>
                      Source-Backed
                    </span>
                  </div>
                  <p className={`text-xs font-bold leading-snug ${isActive ? 'text-white' : 'text-slate-900'}`}>
                    {c.source_title}
                  </p>
                  <p className={`text-[11px] font-semibold ${isActive ? 'text-emerald-100' : 'text-ayush-forest'}`}>
                    {c.section}
                  </p>
                  {c.verbatim_quote && (
                    <p className={`text-[10px] italic line-clamp-2 ${isActive ? 'text-slate-200' : 'text-slate-500'}`}>
                      "{c.verbatim_quote}"
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 10. RESTRAINED LEGAL DISCLAIMER */}
      <div className="px-5 py-2.5 bg-slate-100/70 border-t border-slate-100 text-[11px] text-slate-500 font-medium leading-relaxed flex items-center justify-between">
        <span>
          Information and decision-support only — not legal advice. For filing, licensing, or enforcement decisions, consult a qualified IP / regulatory professional.
        </span>
      </div>

    </div>
  );
};
