import React from 'react';
import {
  FileCheck,
  Download,
  Printer,
  ShieldCheck,
  Scale,
  Leaf,
  CheckCircle2,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { ActiveCaseState } from '../../types';

interface ActiveDossierViewProps {
  activeCase: ActiveCaseState | null;
  onAskCopilot: (query: string) => void;
}

export const ActiveDossierView: React.FC<ActiveDossierViewProps> = ({
  activeCase,
  onAskCopilot
}) => {
  const req = activeCase?.productRequest;
  const res = activeCase?.classificationResult;
  const abs = activeCase?.absResult;

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    if (!activeCase) return;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(activeCase, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${activeCase.caseId || 'AyuRaksha_Dossier'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  if (!activeCase || (!req && !res)) {
    return (
      <div className="max-w-3xl mx-auto py-16 px-4 text-center space-y-5 animate-fadeIn">
        <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-ayush-forest mx-auto flex items-center justify-center border border-emerald-200 shadow-sm">
          <FileCheck className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-slate-900 font-display">No Active Compliance Dossier Yet</h2>
          <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
            As you chat with the IP-SAKTI Sahayak, your formulation is classified into one of the 6 statutory categories and your complete regulatory roadmap is compiled here in real time.
          </p>
        </div>
        <div className="pt-2">
          <button
            onClick={() => onAskCopilot('Evaluate my Ayurvedic formulation')}
            className="px-5 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white text-xs font-bold rounded-xl shadow-sm transition-all inline-flex items-center space-x-2 cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            <span>Start Formulation Intake in Copilot</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto h-full overflow-y-auto space-y-6 pr-1 pb-8 animate-fadeIn">
      
      {/* 1. Dossier Header */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-[11px] font-bold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-md">
              {activeCase.caseId}
            </span>
            <span className="text-[11px] text-slate-400 font-medium">
              Updated: {new Date(activeCase.updatedAt).toLocaleDateString()}
            </span>
          </div>
          <h1 className="text-xl font-extrabold text-slate-900 font-display">
            {req?.name || 'Ayurvedic Formulation Dossier'}
          </h1>
          <p className="text-xs text-slate-600">
            Formulation & IP Compliance Record for State Licensing Authority (SLA) & Patent Office
          </p>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={handleDownloadJSON}
            className="px-3.5 py-2 rounded-xl border border-slate-200 hover:border-slate-300 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-bold flex items-center space-x-1.5 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>JSON</span>
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-2 rounded-xl bg-ayush-forest hover:bg-ayush-forestDark text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm transition-all cursor-pointer"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Dossier</span>
          </button>
        </div>
      </div>

      {/* 2. Three-Pillar Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* Pillar 1: Drug Regulatory Classification */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-ayush-forest">
            <Scale className="w-4 h-4" />
            <h3 className="text-xs font-black uppercase tracking-wider">1. Regulatory Category</h3>
          </div>
          <div>
            <div className="text-sm font-bold text-slate-900">
              {res?.category || (req?.in_classical_text ? 'Classical Shastriya' : 'Proprietary ASU')}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Governed by: {res?.governing_act || 'Drugs and Cosmetics Act, 1940 (Rule 158B)'}
            </p>
          </div>
          <div className="pt-1 text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            {req?.in_classical_text
              ? 'Manufactured strictly in accordance with First-Schedule classical Ayurvedic text.'
              : 'Requires pilot safety proof and citation of textual ingredients under Rule 158B.'}
          </div>
        </div>

        {/* Pillar 2: Patent & Section 3(p) Status */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-emerald-700">
            <ShieldCheck className="w-4 h-4" />
            <h3 className="text-xs font-black uppercase tracking-wider">2. Patent & Section 3(p)</h3>
          </div>
          <div>
            <div className="text-sm font-bold text-slate-900">
              {res?.patentability || (req?.in_classical_text ? 'Barred under Section 3(p)' : 'Requires Novel Extraction / Synergy')}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Traditional Knowledge Digital Library (TKDL) Check
            </p>
          </div>
          <div className="pt-1 text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            {res?.patent_rationale ||
              (req?.in_classical_text
                ? 'Section 3(p) bars patenting traditional knowledge or aggregation of known properties.'
                : 'Process claims for standardized fractions are patentable if synergistic index is validated.')}
          </div>
        </div>

        {/* Pillar 3: ABS & Biodiversity Act 2023 */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-teal-700">
            <Leaf className="w-4 h-4" />
            <h3 className="text-xs font-black uppercase tracking-wider">3. Biodiversity & ABS</h3>
          </div>
          <div>
            <div className="text-sm font-bold text-slate-900">
              {abs?.trigger_detected !== undefined
                ? (abs.trigger_detected ? 'NBA / SBB Approval Required' : 'Exempt under BDA 2023')
                : 'Domestic AYUSH Exemption Available'}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Biological Diversity (Amendment) Act, 2023
            </p>
          </div>
          <div className="pt-1 text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            Registered Indian AYUSH practitioners and cultivated herbs benefit from Section 7 exemptions under BDA 2023.
          </div>
        </div>
      </div>

      {/* 3. Detailed Regulatory Action Checklist */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-ayush-forest" />
          <span>Filing & Licensing Checklist for State Licensing Authority (SLA)</span>
        </h2>

        <div className="space-y-2.5 text-xs text-slate-700">
          {[
            {
              title: 'Manufacturing License Application (Form 24D / 24E)',
              desc: 'Submit application to State AYUSH Licensing Authority with Good Manufacturing Practices (GMP) Schedule T certification.'
            },
            {
              title: 'Batch Testing & Heavy Metal Analysis',
              desc: 'Standardize against Ayurvedic Pharmacopoeia of India (API) thresholds for Lead, Arsenic, Cadmium, and Mercury.'
            },
            {
              title: 'Section 3(p) Patent & Trademark Protection',
              desc: 'Protect brand identity via Trademark (Class 5 Pharmaceuticals) rather than raw formulation composition claims.'
            },
            {
              title: 'Biological Diversity Sourcing Declarations',
              desc: 'Maintain purchase records confirming botanical resources are sourced from certified cultivators or legitimate mandis.'
            }
          ].map((item, idx) => (
            <div key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-start space-x-3">
              <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                {idx + 1}
              </div>
              <div className="space-y-0.5">
                <div className="font-bold text-slate-900">{item.title}</div>
                <div className="text-slate-600 leading-relaxed">{item.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={() => onAskCopilot(`What specific documents do I need for ${req?.name || 'this product'} SLA licensing?`)}
            className="text-xs font-bold text-ayush-forest hover:text-ayush-forestDark inline-flex items-center space-x-1 cursor-pointer"
          >
            <span>Ask Copilot for specific SLA document checklist</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

    </div>
  );
};
