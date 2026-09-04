import React, { useState } from 'react';
import {
  Scale,
  Leaf,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  ArrowDown,
  BookOpen,
  ExternalLink,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { Citation, StructuredAnswer, Jurisdiction } from '../../types';

interface AnswerVisualProps {
  questionText?: string;
  answerText: string;
  answerData?: StructuredAnswer;
  jurisdiction?: Jurisdiction;
  onOpenCitation?: (citation: Citation) => void;
  className?: string;
  compact?: boolean;
}

export type VisualType =
  | 'classification'
  | 'ip_strategy'
  | 'abs_flow'
  | 'regulatory'
  | 'international'
  | 'evidence_chain'
  | 'abstention';

export const AnswerVisual: React.FC<AnswerVisualProps> = ({
  questionText = '',
  answerText = '',
  answerData,
  jurisdiction = 'IN',
  onOpenCitation,
  className = '',
  compact = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // If answer is conversational or trivial, do not render a visual
  const combined = `${questionText} ${answerText} ${answerData?.direct_answer || ''}`.toLowerCase();
  const isGreetingOrTrivial =
    combined.length < 50 ||
    /^(hi|hello|hey|namaste|good morning|thanks|thank you|who are you)[\s.?!]*$/i.test(
      questionText.trim()
    );

  if (isGreetingOrTrivial) {
    return null;
  }

  // Detect Visual Type dynamically from data
  const detectVisualType = (): VisualType => {
    if (answerData?.safe_abstention || combined.includes('insufficient evidence') || combined.includes('safety abstention')) {
      return 'abstention';
    }
    if (combined.includes('international') || combined.includes('export') || combined.includes('us fda') || combined.includes('wipo')) {
      return 'international';
    }
    if (combined.includes('abs') || combined.includes('biodiversity') || combined.includes('sbb') || combined.includes('nba')) {
      return 'abs_flow';
    }
    if (combined.includes('patent') || combined.includes('section 3(p)') || combined.includes('trademark') || combined.includes('section 3(e)')) {
      return 'ip_strategy';
    }
    if (combined.includes('classical') || combined.includes('proprietary') || combined.includes('phytopharmaceutical') || combined.includes('aahara')) {
      return 'classification';
    }
    if (combined.includes('sla') || combined.includes('license') || combined.includes('rule 158b') || combined.includes('gmp')) {
      return 'regulatory';
    }
    return 'evidence_chain';
  };

  const visualType = detectVisualType();
  const citations = answerData?.citations || [];

  // Find matching citation helper
  const findCitation = (sectionKeyword: string): Citation | undefined => {
    return citations.find((c) =>
      c.section.toLowerCase().includes(sectionKeyword.toLowerCase()) ||
      c.source_id.toLowerCase().includes(sectionKeyword.toLowerCase()) ||
      c.source_title.toLowerCase().includes(sectionKeyword.toLowerCase())
    );
  };

  // Build Visual Nodes according to type
  const renderVisualContent = () => {
    switch (visualType) {
      // 1. CLASSIFICATION DECISION TREE
      case 'classification': {
        const sec3aCit = findCitation('3(a)') || findCitation('First Schedule') || citations[0];
        const rule158Cit = findCitation('158B') || citations[1] || citations[0];
        const isClassical = combined.includes('classical') || combined.includes('shastriya');
        const isProprietary = combined.includes('proprietary') || combined.includes('anubhuta') || combined.includes('modified');
        const isPhyto = combined.includes('phyto') || combined.includes('122e');

        return (
          <div className="space-y-4">
            <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 text-xs">
              
              {/* Step 1: Formulation Basis */}
              <div className="p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex-1 space-y-1">
                <span className="text-[10px] font-black uppercase text-slate-400 block tracking-wider">01 Inception</span>
                <p className="font-extrabold text-slate-900 font-display">Product Formulation</p>
                <span className="inline-block text-[11px] text-slate-600">Herbal / Botanical Base</span>
              </div>

              <div className="hidden md:flex text-slate-300"><ArrowRight className="w-4 h-4" /></div>
              <div className="flex md:hidden text-slate-300 justify-center"><ArrowDown className="w-4 h-4" /></div>

              {/* Step 2: Treatise / Statutory Gate */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 shadow-xs flex-1 space-y-1.5">
                <span className="text-[10px] font-black uppercase text-slate-400 block tracking-wider">02 Statutory Gate</span>
                <p className="font-bold text-slate-900">First Schedule Text Basis</p>
                {sec3aCit && (
                  <button
                    onClick={() => onOpenCitation && onOpenCitation(sec3aCit)}
                    className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-100/70 hover:bg-emerald-200 text-emerald-900 font-mono text-[10px] font-bold transition-colors"
                  >
                    <BookOpen className="w-3 h-3" />
                    <span>{sec3aCit.section}</span>
                  </button>
                )}
              </div>

              <div className="hidden md:flex text-slate-300"><ArrowRight className="w-4 h-4" /></div>
              <div className="flex md:hidden text-slate-300 justify-center"><ArrowDown className="w-4 h-4" /></div>

              {/* Step 3: Statutory Outcome */}
              <div className={`p-3.5 rounded-2xl border shadow-xs flex-1 space-y-1.5 ${
                isClassical
                  ? 'bg-emerald-50/80 border-emerald-300 text-emerald-950'
                  : isProprietary
                  ? 'bg-amber-50/80 border-amber-300 text-amber-950'
                  : 'bg-blue-50/80 border-blue-300 text-blue-950'
              }`}>
                <span className="text-[10px] font-black uppercase tracking-wider block opacity-70">03 Classification</span>
                <p className="font-extrabold font-display">
                  {isClassical ? 'Classical ASU (Shastriya)' : isProprietary ? 'Proprietary ASU (Rule 158B)' : isPhyto ? 'Phytopharmaceutical Drug' : 'Ayush Category Evaluated'}
                </p>
                {rule158Cit && (
                  <button
                    onClick={() => onOpenCitation && onOpenCitation(rule158Cit)}
                    className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-white/80 hover:bg-white text-slate-800 font-mono text-[10px] font-bold border border-slate-200/80 shadow-2xs transition-colors"
                  >
                    <span>Licensing Rule</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </button>
                )}
              </div>

            </div>
          </div>
        );
      }

      // 2. IP STRATEGY PATHWAY
      case 'ip_strategy': {
        const sec3pCit = findCitation('3(p)') || citations[0];
        const sec3eCit = findCitation('3(e)') || citations[1] || citations[0];
        const tmCit = findCitation('Trade Marks') || findCitation('9') || citations[0];

        return (
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              
              {/* Branch 1: Patent (Sec 3p/3e) */}
              <div className="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-2 flex flex-col justify-between">
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase bg-amber-200/80 text-amber-900">
                      Patent Route
                    </span>
                    <span className="text-[10px] font-bold text-amber-800">Conditional</span>
                  </div>
                  <h4 className="font-extrabold text-slate-900 font-display">Sec 3(p) TK Exclusion Bar</h4>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    Classical formulas barred. Novel synergistic polyherbals require non-obvious bioactivity data under Section 3(e).
                  </p>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {sec3pCit && (
                    <button
                      onClick={() => onOpenCitation && onOpenCitation(sec3pCit)}
                      className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-white text-amber-950 font-mono text-[10px] font-bold border border-amber-300/80 shadow-2xs hover:bg-amber-100 transition-colors w-fit"
                    >
                      <Scale className="w-2.5 h-2.5 text-amber-700" />
                      <span>{sec3pCit.section}</span>
                    </button>
                  )}
                  {sec3eCit && (
                    <button
                      onClick={() => onOpenCitation && onOpenCitation(sec3eCit)}
                      className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-white text-amber-950 font-mono text-[10px] font-bold border border-amber-300/80 shadow-2xs hover:bg-amber-100 transition-colors w-fit"
                    >
                      <Scale className="w-2.5 h-2.5 text-amber-700" />
                      <span>{sec3eCit.section}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Branch 2: Trademark */}
              <div className="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-2 flex flex-col justify-between">
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase bg-emerald-200/80 text-emerald-900">
                      Brand IP
                    </span>
                    <span className="text-[10px] font-bold text-emerald-800">High Protection</span>
                  </div>
                  <h4 className="font-extrabold text-slate-900 font-display">Trademark Registration</h4>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    Register proprietary coined brand mark under Nice Class 5 (Pharma) & Class 30 (Aahara). Avoid generic Sanskrit terms.
                  </p>
                </div>
                {tmCit && (
                  <button
                    onClick={() => onOpenCitation && onOpenCitation(tmCit)}
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-white text-emerald-950 font-mono text-[10px] font-bold border border-emerald-300/80 shadow-2xs hover:bg-emerald-100 transition-colors w-fit"
                  >
                    <ShieldCheck className="w-3 h-3 text-emerald-700" />
                    <span>Inspect {tmCit.section || 'TM Act'}</span>
                  </button>
                )}
              </div>

              {/* Branch 3: Trade Secret */}
              <div className="p-3.5 rounded-2xl bg-blue-50/70 border border-blue-200 space-y-2 flex flex-col justify-between">
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase bg-blue-200/80 text-blue-900">
                      Process IP
                    </span>
                    <span className="text-[10px] font-bold text-blue-800">Proprietary</span>
                  </div>
                  <h4 className="font-extrabold text-slate-900 font-display">Trade Secret & Know-How</h4>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    Protect unpatented extraction parameters, temperature curves, and solvent ratios via confidentiality agreements.
                  </p>
                </div>
                <span className="text-[10px] font-bold text-blue-800 font-mono">
                  Common Law & NDAs
                </span>
              </div>

            </div>
          </div>
        );
      }

      // 3. ABS & BIODIVERSITY FLOW
      case 'abs_flow': {
        const bdaCit = findCitation('Biological Diversity') || findCitation('Section 7') || findCitation('Section 3') || citations[0];
        const isDomestic = combined.includes('domestic') || combined.includes('indian entity') || !combined.includes('foreign');

        return (
          <div className="space-y-3">
            <div className="p-4 rounded-2xl bg-teal-50/60 border border-teal-200/80 space-y-3">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-2 border-b border-teal-200/60 pb-2.5">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded-lg bg-teal-600 text-white"><Leaf className="w-3.5 h-3.5" /></div>
                  <span className="font-extrabold text-xs text-slate-900 font-display">Biological Diversity Act (BDA 2023) Pathway</span>
                </div>
                {bdaCit && (
                  <button
                    onClick={() => onOpenCitation && onOpenCitation(bdaCit)}
                    className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-white text-teal-900 font-mono text-[10px] font-bold border border-teal-200 hover:bg-teal-100 transition-colors"
                  >
                    <span>{bdaCit.section}</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {/* Domestic Route */}
                <div className={`p-3 rounded-xl border ${isDomestic ? 'bg-white border-teal-300 shadow-xs' : 'bg-slate-50 border-slate-200 opacity-60'}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-extrabold text-teal-950">Domestic Indian Entity</span>
                    <span className="text-[9px] font-black px-1.5 py-0.5 rounded bg-teal-100 text-teal-900">SBB Route</span>
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    Submit <strong>SBB Form A Prior Intimation</strong> to the State Biodiversity Board before commercial manufacture. Local AYUSH vaidyas exempted under BDA 2023.
                  </p>
                </div>

                {/* Foreign / Export Route */}
                <div className={`p-3 rounded-xl border ${!isDomestic ? 'bg-white border-teal-300 shadow-xs' : 'bg-slate-50 border-slate-200'}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-extrabold text-slate-900">Foreign / Export / IPR Filing</span>
                    <span className="text-[9px] font-black px-1.5 py-0.5 rounded bg-amber-100 text-amber-900">NBA Route</span>
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    Mandatory <strong>NBA Form I</strong> (Access) or <strong>NBA Form III</strong> (Prior Approval before patent grant under Section 6) to National Biodiversity Authority.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );
      }

      // 4. INTERNATIONAL EXPORT REGIMES
      case 'international': {
        const usCit = findCitation('DSHEA') || findCitation('US') || citations[0];
        const euCit = findCitation('Directive') || findCitation('EU') || citations[1] || citations[0];

        return (
          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* India Export Clearance */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-1.5">
                <span className="text-[10px] font-black uppercase text-slate-400 block tracking-wider">01 Origin Clearance</span>
                <h4 className="font-extrabold text-slate-900 font-display">🇮🇳 India Export Posture</h4>
                <p className="text-[11px] text-slate-600 leading-snug">
                  Requires NBA export clearance and Section 39 Foreign Filing License (FFL) if patenting abroad before India grant.
                </p>
              </div>

              {/* US FDA */}
              <div className="p-3.5 rounded-2xl bg-indigo-50/70 border border-indigo-200 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase text-indigo-700 block tracking-wider">02 US Market</span>
                  {usCit && (
                    <button
                      onClick={() => onOpenCitation && onOpenCitation(usCit)}
                      className="text-[9px] font-mono font-bold text-indigo-900 bg-indigo-100 px-1.5 py-0.5 rounded hover:bg-indigo-200"
                    >
                      {usCit.section}
                    </button>
                  )}
                </div>
                <h4 className="font-extrabold text-slate-900 font-display">🇺🇸 US FDA DSHEA</h4>
                <p className="text-[11px] text-slate-600 leading-snug">
                  Dietary supplement pathway. If modified herb, mandatory 75-Day New Dietary Ingredient (NDI) premarket safety notice.
                </p>
              </div>

              {/* EU EMA */}
              <div className="p-3.5 rounded-2xl bg-blue-50/70 border border-blue-200 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase text-blue-700 block tracking-wider">03 European Union</span>
                  {euCit && (
                    <button
                      onClick={() => onOpenCitation && onOpenCitation(euCit)}
                      className="text-[9px] font-mono font-bold text-blue-900 bg-blue-100 px-1.5 py-0.5 rounded hover:bg-blue-200"
                    >
                      {euCit.section}
                    </button>
                  )}
                </div>
                <h4 className="font-extrabold text-slate-900 font-display">🇪🇺 EU Directive 2004/24/EC</h4>
                <p className="text-[11px] text-slate-600 leading-snug">
                  Traditional Herbal Medicinal Products (THMPD) requires proving 30 years of safe traditional use (min 15 in EU).
                </p>
              </div>
            </div>
          </div>
        );
      }

      // 5. SAFE ABSTENTION / INSUFFICIENT EVIDENCE
      case 'abstention': {
        return (
          <div className="p-4 rounded-2xl bg-amber-50/80 border border-amber-300 space-y-2 text-xs">
            <div className="flex items-center space-x-2 text-amber-950 font-bold">
              <AlertTriangle className="w-4 h-4 text-amber-700" />
              <span>Requires Statutory Verification · Insufficient Product Grounds</span>
            </div>
            <p className="text-[11px] text-amber-900 leading-relaxed">
              {answerData?.abstention_reason || 'The available formulation parameters do not provide sufficient statutory evidence to make a definitive legal determination without risk of misinformation.'}
            </p>
            <div className="pt-1 text-[10px] font-mono text-amber-800 font-bold">
              Action: Provide complete ingredient composition, classical text references, or extraction parameters.
            </div>
          </div>
        );
      }

      // 6. DEFAULT EVIDENCE RELATIONSHIP CHAIN
      default: {
        return (
          <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-3 text-xs">
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-2">
              <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">Statutory Grounding Chain</span>
              <span className="text-[10px] font-mono font-bold text-ayush-forest bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                {citations.length} Verified Sources
              </span>
            </div>

            <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2">
              <div className="p-3 bg-white rounded-xl border border-slate-200 text-center flex-1 space-y-0.5">
                <span className="text-[9px] font-bold uppercase text-slate-400">Inception</span>
                <p className="font-bold text-slate-900 text-[11px]">Innovator Inquiry</p>
              </div>

              <div className="hidden md:flex text-slate-300"><ArrowRight className="w-3.5 h-3.5" /></div>

              <div className="p-3 bg-white rounded-xl border border-slate-200 text-center flex-1 space-y-0.5">
                <span className="text-[9px] font-bold uppercase text-slate-400">Retrieval</span>
                <p className="font-bold text-slate-900 text-[11px]">Gazette Corpus</p>
              </div>

              <div className="hidden md:flex text-slate-300"><ArrowRight className="w-3.5 h-3.5" /></div>

              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-center flex-1 space-y-0.5">
                <span className="text-[9px] font-bold uppercase text-emerald-800">Provision</span>
                <p className="font-bold text-emerald-950 text-[11px]">{citations[0]?.section || 'Verified Statute'}</p>
              </div>

              <div className="hidden md:flex text-slate-300"><ArrowRight className="w-3.5 h-3.5" /></div>

              <div className="p-3 bg-white rounded-xl border border-slate-200 text-center flex-1 space-y-0.5">
                <span className="text-[9px] font-bold uppercase text-slate-400">Determination</span>
                <p className="font-bold text-slate-900 text-[11px]">Grounding Opinion</p>
              </div>
            </div>
          </div>
        );
      }
    }
  };

  return (
    <div className={`rounded-2xl bg-white border border-slate-200/90 shadow-subtle overflow-hidden select-text my-4 animate-fadeIn ${className}`}>
      
      {/* Visual Header */}
      <div className="px-4 py-3 bg-slate-50/90 border-b border-slate-200/80 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-ayush-forest animate-pulse" />
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-800 font-display">
            Statutory Decision Map · {visualType.replace('_', ' ').toUpperCase()}
          </span>
        </div>

        <div className="flex items-center space-x-2 text-[10px] font-bold text-slate-400">
          <span>Data-Driven Visual</span>
          {!compact && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 hover:bg-slate-200/60 rounded text-slate-600 transition-colors"
              title={isExpanded ? 'Collapse diagram' : 'Expand diagram'}
            >
              {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>

      {/* Visual Content Body */}
      <div className={`p-4 transition-all duration-300 ${isExpanded ? 'p-6 bg-slate-50/30' : ''}`}>
        {renderVisualContent()}
      </div>

      {/* Visual Footer Provenance */}
      <div className="px-4 py-2 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
        <span>Grounded on {jurisdiction === 'IN' ? 'Government of India Gazette Notifications' : 'International Treaty Directives'}</span>
        <span className="font-mono">Ayuरक्षा Decision Graph</span>
      </div>

    </div>
  );
};
