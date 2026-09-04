import React from 'react';
import {
  Compass,
  Scale,
  Leaf,
  FileCheck,
  ArrowRight,
  ShieldCheck,
  BookOpen,
  MessageSquare
} from 'lucide-react';
import { ActiveCaseState } from '../../types';

interface LandingPageProps {
  activeCase?: ActiveCaseState | null;
  onStartAssessment: () => void;
  onOpenCopilot: (initialPrompt?: string) => void;
  onNavigateView: (view: 'classification' | 'ip_matrix' | 'abs_wizard' | 'international' | 'corpus' | 'knowledge_graph') => void;
  onOpenDossier: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  activeCase,
  onStartAssessment,
  onOpenCopilot,
  onNavigateView,
  onOpenDossier
}) => {
  const capabilities = [
    {
      id: 'classification',
      icon: Compass,
      step: '01',
      title: 'Product Classification',
      subtitle: 'Drugs & Cosmetics Act, 1940 & Rules',
      description: 'Determine statutory category: Classical Shastriya, Proprietary ASU Drug (Rule 158B), Phytopharmaceutical (GSR 918E), Ayurveda Aahara, or Cosmetic.',
      badge: 'Statutory Pathway',
      color: 'bg-emerald-50 text-emerald-900 border-emerald-200',
      action: () => onNavigateView('classification')
    },
    {
      id: 'ip_strategy',
      icon: Scale,
      step: '02',
      title: 'IP Strategy & Protection',
      subtitle: 'Patents Act 1970 & Trade Marks Act 1999',
      description: 'Assess Section 3(p) Traditional Knowledge bars, Section 3(e) synergistic efficacy requirements, proprietary Trademarks, and Trade Secrets.',
      badge: 'Multi-Modal IP',
      color: 'bg-amber-50 text-amber-900 border-amber-200',
      action: () => onNavigateView('ip_matrix')
    },
    {
      id: 'abs',
      icon: Leaf,
      step: '03',
      title: 'ABS & Biodiversity Compliance',
      subtitle: 'Biological Diversity Act (BDA 2023)',
      description: 'Determine State Biodiversity Board (SBB Form A) Prior Intimation for domestic manufacturers vs National Biodiversity Authority (NBA Form I/III) approval.',
      badge: 'SBB vs NBA Routing',
      color: 'bg-teal-50 text-teal-900 border-teal-200',
      action: () => onNavigateView('abs_wizard')
    },
    {
      id: 'chat',
      icon: MessageSquare,
      step: '04',
      title: 'Evidence-Grounded Questions',
      subtitle: 'Official Gazette & API Monograph Corpus',
      description: 'Ask regulatory questions with verifiable citations, support entailment scores, and contextual Evidence Inspector grounding.',
      badge: 'Verified Decision Support',
      color: 'bg-blue-50 text-blue-900 border-blue-200',
      action: () => onOpenCopilot()
    },
    {
      id: 'dossier',
      icon: FileCheck,
      step: '05',
      title: 'Active Compliance Dossier',
      subtitle: 'Audit-Ready Executive Case File',
      description: 'Synthesize product classification, botanical taxonomy, statutory roadmaps, and verifiable gazette citations into an exportable case dossier.',
      badge: 'Case Synthesis',
      color: 'bg-purple-50 text-purple-900 border-purple-200',
      action: onOpenDossier
    }
  ];

  const workflowStages = [
    { num: '01', title: 'Product Profile', desc: 'Formulation, dosage form, treatise basis' },
    { num: '02', title: 'Classification', desc: 'Shastriya, Proprietary, or Phyto categorization' },
    { num: '03', title: 'IP & ABS Audit', desc: 'Sec 3(p) TK bar, TM protection, SBB/NBA rules' },
    { num: '04', title: 'Evidence Grounding', desc: 'Official Gazette provisions & support scores' },
    { num: '05', title: 'Dossier Assembly', desc: 'Statutory filing timeline & fee blueprint' }
  ];

  const hasActiveCase = activeCase && activeCase.productRequest?.name;

  return (
    <div className="space-y-12 pb-16 animate-fadeIn select-text">

      {/* 1. HERO SECTION */}
      <section className="relative pt-6 pb-4">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          
          {/* Institutional Badge */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-emerald-50 text-ayush-forest border border-emerald-200 text-xs font-bold tracking-wide shadow-xs">
            <ShieldCheck className="w-4 h-4 text-ayush-forest" />
            <span>Ministry of Ayush · SIH 26045 IP-SAKTI Sahayak</span>
          </div>

          {/* Primary Headline & Secondary Line */}
          <div className="space-y-3">
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-slate-900 font-display tracking-tight leading-[1.15]">
              Protecting Ayurveda with evidence.
            </h1>
            <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
              An evidence-grounded decision-support system for Ayurveda IP, regulatory classification, and biological-resource compliance.
            </p>
          </div>

          {/* Primary & Secondary Call to Actions */}
          <div className="flex flex-wrap items-center justify-center gap-3.5 pt-2">
            <button
              onClick={onStartAssessment}
              className="px-6 py-3 bg-ayush-forest hover:bg-ayush-forestDark active:scale-[0.99] text-white text-sm font-bold rounded-2xl flex items-center space-x-2 transition-all shadow-md hover:shadow-lg"
            >
              <span>Start an Assessment</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => onOpenCopilot()}
              className="px-6 py-3 bg-white hover:bg-slate-50 active:scale-[0.99] text-slate-800 text-sm font-bold rounded-2xl border border-slate-200/90 flex items-center space-x-2 transition-all shadow-xs"
            >
              <MessageSquare className="w-4 h-4 text-slate-500" />
              <span>Ask Ayuरक्षा</span>
            </button>
          </div>

          {/* Restrained Visual Composition: Central Mark & Connected Capability Nodes */}
          <div className="pt-6 pb-2 max-w-2xl mx-auto">
            <div className="p-5 rounded-3xl bg-slate-50/80 border border-slate-200/80 shadow-xs relative overflow-hidden">
              <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 text-xs font-bold">
                <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 shadow-xs flex items-center space-x-1.5">
                  <Compass className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Classification</span>
                </span>
                <span className="text-slate-300">•</span>
                <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 shadow-xs flex items-center space-x-1.5">
                  <Scale className="w-3.5 h-3.5 text-amber-600" />
                  <span>IP Strategy</span>
                </span>
                <span className="text-slate-300">•</span>
                <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 shadow-xs flex items-center space-x-1.5">
                  <Leaf className="w-3.5 h-3.5 text-teal-600" />
                  <span>ABS Compliance</span>
                </span>
                <span className="text-slate-300">•</span>
                <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 shadow-xs flex items-center space-x-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                  <span>Gazette Evidence</span>
                </span>
                <span className="text-slate-300">•</span>
                <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 shadow-xs flex items-center space-x-1.5">
                  <FileCheck className="w-3.5 h-3.5 text-purple-600" />
                  <span>Dossier Assembly</span>
                </span>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* 2. ACTIVE CASE CONTINUITY PANEL (If an active case exists) */}
      {hasActiveCase && (
        <section className="max-w-5xl mx-auto">
          <div className="p-5 rounded-2xl bg-emerald-50/60 border border-emerald-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-ayush-forest text-white">
                  Active Assessment Case
                </span>
                <span className="font-mono text-xs font-bold text-slate-700">
                  {activeCase.caseId}
                </span>
              </div>
              <h3 className="font-extrabold text-base text-slate-900 font-display">
                {activeCase.productRequest?.name}
              </h3>
              <p className="text-xs text-slate-600">
                Status: <span className="font-bold text-ayush-forest">{activeCase.status}</span> · Intended Use: {activeCase.productRequest?.intended_use || 'Therapeutic'}
              </p>
            </div>

            <div className="flex items-center space-x-2 shrink-0">
              <button
                onClick={onStartAssessment}
                className="px-4 py-2 bg-ayush-forest hover:bg-ayush-forestDark text-white text-xs font-bold rounded-xl transition-all shadow-xs flex items-center space-x-1.5"
              >
                <span>Continue Assessment</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={onOpenDossier}
                className="px-3.5 py-2 bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition-colors"
              >
                View Dossier
              </button>
            </div>
          </div>
        </section>
      )}

      {/* 3. TRUST STRIP */}
      <section className="max-w-5xl mx-auto border-y border-slate-200/80 py-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="space-y-0.5">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Evidence-Grounded</span>
            <span className="text-xs font-bold text-slate-800">Authoritative Source Retrieval</span>
          </div>
          <div className="space-y-0.5">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Traceable</span>
            <span className="text-xs font-bold text-slate-800">Citation → Source Evidence</span>
          </div>
          <div className="space-y-0.5">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Verifiable</span>
            <span className="text-xs font-bold text-slate-800">Answer Support Checking</span>
          </div>
          <div className="space-y-0.5">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Jurisdiction-Aware</span>
            <span className="text-xs font-bold text-slate-800">India 🇮🇳 & International 🌍</span>
          </div>
        </div>
      </section>

      {/* 4. PRODUCT CAPABILITY CARDS */}
      <section className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 font-display">
              What Ayuरक्षा Helps You Assess
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
              Integrated statutory intelligence modules for Ayurvedic innovators and enterprises.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {capabilities.map((cap) => {
            const Icon = cap.icon;
            return (
              <div
                key={cap.id}
                onClick={cap.action}
                className="p-5 rounded-2xl bg-white border border-slate-200/90 hover:border-ayush-forest/60 hover:shadow-subtle transition-all cursor-pointer flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="w-8 h-8 rounded-xl bg-slate-100 group-hover:bg-emerald-50 text-slate-700 group-hover:text-ayush-forest flex items-center justify-center transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[10px] font-mono font-bold text-slate-400">
                      {cap.step}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <h3 className="font-extrabold text-sm text-slate-900 group-hover:text-ayush-forest transition-colors font-display">
                      {cap.title}
                    </h3>
                    <p className="text-[11px] font-semibold text-slate-400">
                      {cap.subtitle}
                    </p>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">
                    {cap.description}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-ayush-forest group-hover:translate-x-0.5 transition-transform">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">{cap.badge}</span>
                  <div className="flex items-center space-x-1">
                    <span>Open Module</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 5. 5-STAGE WORKFLOW EXPLANATION */}
      <section className="max-w-5xl mx-auto space-y-5 pt-4">
        <div className="text-center space-y-1">
          <h2 className="text-lg sm:text-xl font-extrabold text-slate-900 font-display">
            The Evidence-Grounded Assessment Workflow
          </h2>
          <p className="text-xs text-slate-500">
            From initial product formulation to exportable statutory compliance dossier.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
          {workflowStages.map((stg) => (
            <div
              key={stg.num}
              className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2 text-center"
            >
              <span className="w-6 h-6 rounded-full bg-ayush-forest text-white font-black text-xs flex items-center justify-center mx-auto shadow-xs">
                {stg.num}
              </span>
              <h4 className="font-bold text-xs text-slate-900 font-display">
                {stg.title}
              </h4>
              <p className="text-[11px] text-slate-500 leading-snug">
                {stg.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* 6. STATUTORY DISCLAIMER */}
      <section className="max-w-5xl mx-auto">
        <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-center text-xs text-slate-500 font-medium">
          Ayuरक्षा is an evidence-grounded regulatory and IP decision-support system developed for SIH 26045. It provides statutory intelligence based on official gazette provisions and does not constitute formal legal counsel.
        </div>
      </section>

    </div>
  );
};
