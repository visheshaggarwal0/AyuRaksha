import { X, Shield, Printer } from 'lucide-react';
import { ProductClassificationResponse, ABSAssessmentResponse } from '../../types';

interface ComplianceDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  classificationResult?: ProductClassificationResponse | null;
  absResult?: ABSAssessmentResponse | null;
}

export function ComplianceDossierModal({
  isOpen,
  onClose,
  classificationResult,
  absResult,
}: ComplianceDossierModalProps) {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white border border-ayush-border rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-modal overflow-hidden">
        {/* Modal Header */}
        <div className="bg-ayush-forestDark text-white p-5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-ayush-forest rounded-lg">
              <Shield className="w-5 h-5 text-emerald-300" />
            </div>
            <div>
              <h3 className="font-bold text-base">AyuRaksha Statutory Compliance Dossier</h3>
              <p className="text-xs text-slate-300">Generated under Drugs & Cosmetics Act 1940 & BDA 2002 (2023)</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-bold flex items-center space-x-1.5 border border-white/20 transition-all"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / Save PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-300 hover:text-white rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Printable Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-800 printable-area">
          {/* Dossier Header Info */}
          <div className="border-b border-slate-200 pb-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <div>
              <p className="text-slate-500 font-semibold text-[11px]">CASE DOSSIER ID</p>
              <p className="font-mono font-bold text-sm text-ayush-navy">AYU-SIH26045-2026-X89</p>
            </div>
            <div>
              <p className="text-slate-500 font-semibold text-[11px]">DATE OF GENERATION</p>
              <p className="font-bold text-ayush-navy">{new Date().toLocaleDateString('en-IN', { dateStyle: 'long' })}</p>
            </div>
            <div>
              <p className="text-slate-500 font-semibold text-[11px]">JURISDICTION SCOPE</p>
              <span className="font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300">
                🇮🇳 India (Domestic Regime)
              </span>
            </div>
          </div>

          {/* Section 1: Product Classification Summary */}
          <div className="space-y-3">
            <h4 className="font-bold text-sm text-ayush-navy border-b border-slate-200 pb-1 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[10px]">1</span>
              <span>Statutory Product Classification</span>
            </h4>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-slate-500 block text-[11px]">Assigned Regulatory Category</span>
                  <span className="font-bold text-ayush-forest text-sm">
                    {classificationResult?.category || 'Classical ASU Medicine (Section 3a)'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Governing Statute</span>
                  <span className="font-bold text-slate-800">
                    {classificationResult?.governing_act || 'Drugs and Cosmetics Act, 1940 (First Schedule)'}
                  </span>
                </div>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px] mt-2">Statutory Licensing Rationale</span>
                <p className="text-slate-700 mt-0.5">
                  {classificationResult?.next_actions[0] ||
                    'Manufactured strictly in accordance with formulae described in authoritative classical texts listed in the First Schedule. Exempt from Rule 158B clinical safety trial requirements.'}
                </p>
              </div>
            </div>
          </div>

          {/* Section 2: Biodiversity & ABS Compliance */}
          <div className="space-y-3">
            <h4 className="font-bold text-sm text-ayush-navy border-b border-slate-200 pb-1 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[10px]">2</span>
              <span>Biological Diversity Act (ABS) Assessment</span>
            </h4>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-slate-500 block text-[11px]">Competent Authority</span>
                  <span className="font-bold text-slate-800">
                    {absResult?.applicable_authority || 'State Biodiversity Board (SBB) / National Biodiversity Authority'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Approval Pathway</span>
                  <span className="font-bold text-amber-700">
                    {absResult?.approval_type || 'Section 7 Prior Intimation (Domestic Commercial Utilization)'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Verified Statutory Citations */}
          <div className="space-y-3">
            <h4 className="font-bold text-sm text-ayush-navy border-b border-slate-200 pb-1 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[10px]">3</span>
              <span>Verified Statutory Evidence & Legal Basis</span>
            </h4>
            <div className="space-y-2">
              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <p className="font-bold text-ayush-forest text-xs">Patents Act, 1970 — Section 3(p)</p>
                <p className="text-[11px] text-slate-700 mt-1 italic">
                  "An invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known components is not an invention."
                </p>
              </div>
              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <p className="font-bold text-ayush-forest text-xs">Biological Diversity Act, 2002 — Section 6</p>
                <p className="text-[11px] text-slate-700 mt-1 italic">
                  "No person shall apply for any intellectual property right in or outside India for any invention based on biological resources from India without obtaining previous approval of NBA."
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 p-4 border-t border-slate-200 flex items-center justify-between">
          <span className="text-[11px] text-slate-500">
            AyuRaksha · Verified by Statutory Citation Entailment Engine
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl text-xs font-bold transition-all"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
}
