import React from 'react';
import {
  Scale,
  ShieldCheck,
  Sparkles,
  ExternalLink,
  CheckCircle2,
  HelpCircle,
  FileText,
  ArrowRight
} from 'lucide-react';
import { Citation, StructuredAnswer, Jurisdiction, ClarificationChip } from '../../types';
import { StatutoryMarkdownRenderer } from '../common/StatutoryMarkdownRenderer';

interface ConversationalAnswerProps {
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

export const ConversationalAnswer: React.FC<ConversationalAnswerProps> = ({
  answerText,
  answerData,
  jurisdiction,
  onOpenCitation,
  onInspectAllEvidence,
  onAskFollowUp
}) => {
  const isGreeting = answerData?.intent_type === 'GREETING' || answerData?.execution_mode === 'CONVERSATIONAL_GREETING';
  const isIntake = answerData?.intent_type === 'CLASSIFICATION_INTAKE' || answerData?.execution_mode === 'CLASSIFICATION_INTAKE';
  const citations = answerData?.citations || [];
  const chips: ClarificationChip[] = answerData?.clarification_chips || [];
  const nextActions = answerData?.assessment_table?.['Next Actions']
    ? (Array.isArray(answerData.assessment_table['Next Actions'])
      ? answerData.assessment_table['Next Actions']
      : [String(answerData.assessment_table['Next Actions'])])
    : (answerData?.recommended_next_action ? [answerData.recommended_next_action] : []);

  // Determine category & status badges if available
  const category = answerData?.statutory_category ||
    (answerData?.assessment_table?.['Category'] as string) ||
    (answerData?.assessment_table?.['Product Category'] as string) ||
    null;

  const patentRisk = answerData?.assessment_table?.['Patentability'] as string ||
    (answerData?.assessment_table?.['Section 3(p) Risk'] as string) ||
    null;

  const absStatus = answerData?.assessment_table?.['ABS Requirement'] as string ||
    (answerData?.assessment_table?.['ABS Duty'] as string) ||
    null;

  return (
    <div className="w-full rounded-2xl bg-white border border-slate-200/90 shadow-sm hover:shadow-md transition-shadow overflow-hidden text-slate-800 animate-fadeIn select-text">
      
      {/* 1. Header Bar: Minimal, Clean */}
      <div className="px-5 py-3 border-b border-slate-100 bg-slate-50/60 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-lg bg-emerald-100/80 text-ayush-forest flex items-center justify-center shrink-0">
            {isGreeting ? <Sparkles className="w-3.5 h-3.5" /> : isIntake ? <HelpCircle className="w-3.5 h-3.5" /> : <Scale className="w-3.5 h-3.5" />}
          </div>
          <span className="text-xs font-bold text-slate-700">
            {isGreeting
              ? 'IP-SAKTI Sahayak · Welcome'
              : isIntake
              ? 'Formulation Intake & Clarification'
              : 'Regulatory & IP Assessment'}
          </span>
        </div>

        {/* Status badges */}
        <div className="flex items-center space-x-2 text-[11px]">
          <span className="px-2 py-0.5 rounded-md font-semibold bg-white text-slate-700 border border-slate-200">
            {jurisdiction === 'IN' ? '🇮🇳 India' : jurisdiction === 'CROSS_BORDER' ? '⚖️ Cross-Border' : '🌍 International'}
          </span>
          {!isGreeting && !isIntake && citations.length > 0 && (
            <span className="px-2 py-0.5 rounded-md font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center space-x-1">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              <span>{citations.length} Grounded {citations.length === 1 ? 'Citation' : 'Citations'}</span>
            </span>
          )}
        </div>
      </div>

      {/* 2. Key 3-Pillar Bar (Only for substantive legal assessments) */}
      {!isGreeting && !isIntake && (category || patentRisk || absStatus) && (
        <div className="px-5 py-2.5 bg-slate-100/50 border-b border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
          {category && (
            <div className="flex items-center space-x-1.5 truncate">
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Category:</span>
              <span className="px-2 py-0.5 rounded font-bold text-[11px] bg-white text-emerald-950 border border-emerald-200 truncate">
                {category}
              </span>
            </div>
          )}
          {patentRisk && (
            <div className="flex items-center space-x-1.5 truncate">
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Patent:</span>
              <span className="px-2 py-0.5 rounded font-bold text-[11px] bg-white text-slate-800 border border-slate-200 truncate">
                {patentRisk}
              </span>
            </div>
          )}
          {absStatus && (
            <div className="flex items-center space-x-1.5 truncate">
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">ABS Duty:</span>
              <span className="px-2 py-0.5 rounded font-bold text-[11px] bg-white text-slate-800 border border-slate-200 truncate">
                {absStatus}
              </span>
            </div>
          )}
        </div>
      )}

      {/* 3. Main Message Prose */}
      <div className="p-5 text-sm sm:text-base leading-relaxed text-slate-800 space-y-4">
        <StatutoryMarkdownRenderer
          content={answerData?.direct_answer || answerText}
          citations={citations}
          onCitationClick={(c: Citation) => onOpenCitation(c, answerData)}
        />

        {/* 4. Interactive Clarification Chips (when provided by backend) */}
        {chips.length > 0 && (
          <div className="pt-3 border-t border-slate-100 space-y-2">
            <span className="text-xs font-bold text-slate-500 block">
              {isIntake ? 'Select an option to clarify your product:' : 'Quick Actions / Guided Categories:'}
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {chips.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => onAskFollowUp && onAskFollowUp(chip.action_payload)}
                  className="p-3 rounded-xl border border-slate-200 hover:border-ayush-forest bg-slate-50/70 hover:bg-emerald-50/50 text-xs font-semibold text-slate-800 transition-all text-left flex items-center justify-between group shadow-2xs cursor-pointer"
                >
                  <span className="truncate group-hover:text-emerald-950">{chip.label}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-ayush-forest shrink-0 ml-1.5 transition-transform group-hover:translate-x-0.5" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 5. Next Steps Checklist (If applicable) */}
        {!isGreeting && !isIntake && nextActions.length > 0 && (
          <div className="pt-2">
            <div className="p-3.5 bg-emerald-50/50 rounded-xl border border-emerald-200/80 space-y-2">
              <div className="flex items-center space-x-1.5 text-emerald-900 font-bold text-xs">
                <CheckCircle2 className="w-4 h-4 text-ayush-forest shrink-0" />
                <span>Recommended Next Steps:</span>
              </div>
              <ul className="space-y-1 text-xs text-slate-700">
                {nextActions.map((action, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <span className="font-bold text-emerald-700 shrink-0">{idx + 1}.</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* 6. Footer Citation Strip (Clickable Pills to open On-Demand Evidence Inspector) */}
      {!isGreeting && !isIntake && citations.length > 0 && (
        <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/50 flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mr-1 flex items-center space-x-1">
              <FileText className="w-3 h-3" />
              <span>Grounded Citations:</span>
            </span>
            {citations.slice(0, 4).map((c, idx) => (
              <button
                key={idx}
                onClick={() => onOpenCitation(c, answerData)}
                className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-slate-700 hover:text-emerald-900 transition-all flex items-center space-x-1 shadow-2xs cursor-pointer"
                title="Click to view verbatim Gazette text in Evidence Inspector"
              >
                <span className="font-mono text-[10px] text-emerald-700 font-bold">[{idx + 1}]</span>
                <span className="truncate max-w-[140px]">{c.section || c.source_title}</span>
                <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
              </button>
            ))}
            {citations.length > 4 && (
              <span className="text-[11px] text-slate-400 font-medium self-center">
                +{citations.length - 4} more
              </span>
            )}
          </div>

          <button
            onClick={() => onInspectAllEvidence(answerData!)}
            className="text-xs font-bold text-ayush-forest hover:text-ayush-forestDark flex items-center space-x-1 transition-colors ml-auto cursor-pointer"
          >
            <span>Open Evidence Inspector</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
