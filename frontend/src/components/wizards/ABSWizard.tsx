import React, { useState, useEffect } from 'react';
import { 
  Leaf, CheckCircle2, ArrowRight, RotateCcw, BookOpen, 
  ExternalLink, Globe, Building2, Sparkles, Network, Scale, FolderCheck
} from 'lucide-react';
import { api } from '../../services/api';
import { ABSAssessmentRequest, ABSAssessmentResponse, Citation, ActiveCaseState } from '../../types';

interface ABSWizardProps {
  activeCase?: ActiveCaseState | null;
  onOpenCitation: (c: Citation) => void;
  onABSComplete?: (req: ABSAssessmentRequest, res: ABSAssessmentResponse) => void;
  onNavigateView?: (view: string) => void;
  onAskCopilot?: (query: string) => void;
  onOpenDossier?: () => void;
}

export const ABSWizard: React.FC<ABSWizardProps> = ({ 
  activeCase, 
  onOpenCitation, 
  onABSComplete,
  onNavigateView,
  onAskCopilot,
  onOpenDossier
}) => {
  const [formData, setFormData] = useState<ABSAssessmentRequest>({
    biological_resource: 'Himalayan Kutki (Picrorhiza kurroa)',
    origin_country: 'India',
    sourced_from_state: 'Himachal Pradesh',
    is_commercial_utilization: true,
    is_traditional_knowledge_associated: true,
    is_indian_entity: true,
    is_export_intended: false,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ABSAssessmentResponse | null>(activeCase?.absResult || null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Auto-populate from active case if available
  useEffect(() => {
    if (activeCase?.productRequest?.name) {
      setFormData(prev => ({
        ...prev,
        biological_resource: activeCase.productRequest?.name || prev.biological_resource,
      }));
    }
    if (activeCase?.absResult) {
      setResult(activeCase.absResult);
    }
  }, [activeCase]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await api.evaluateABS(formData);
      setResult(res);
      if (onABSComplete) {
        onABSComplete(formData, res);
      }
    } catch (err: any) {
      console.error('ABS evaluation error', err);
      setErrorMessage(err.response?.data?.detail || 'Failed to evaluate ABS compliance. Please check connection and retry.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn select-text">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-card space-y-4">
        <div className="space-y-1.5">
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-ayush-forest rounded-full text-xs font-bold border border-emerald-200">
            <Leaf className="w-3.5 h-3.5" />
            <span>Module 3 · Biological Diversity Act 2023 Navigator</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-display tracking-tight">
            Access & Benefit Sharing (ABS) Compliance Navigator
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 max-w-3xl leading-relaxed">
            Determine statutory compliance obligations under the Biological Diversity Act, 2002 (as amended 2023). Identify whether your enterprise requires <strong>State Biodiversity Board (SBB) Prior Intimation</strong> under Section 7 or <strong>National Biodiversity Authority (NBA Chennai) Prior Approval</strong> under Section 3 & 19.
          </p>
        </div>

        {/* Active Case Context Pill */}
        {activeCase?.productRequest && (
          <div className="p-3 bg-emerald-50/60 rounded-2xl border border-emerald-200 text-xs flex items-center justify-between">
            <span className="text-emerald-950 font-medium">
              Active Case: <strong>{activeCase.productRequest.name}</strong> ({activeCase.caseId})
            </span>
            <span className="text-[10px] font-mono font-bold text-emerald-800 bg-white px-2 py-0.5 rounded border border-emerald-200">
              Formulation Herb Sourcing
            </span>
          </div>
        )}

        {/* Visual Authority Flowchart */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-2 text-center">
          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs">
            <span className="font-bold text-slate-900 block mb-0.5">1. Sourcing</span>
            <span className="text-[11px] text-slate-500">Indian Biological Herbs</span>
          </div>
          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs">
            <span className="font-bold text-slate-900 block mb-0.5">2. Entity Status</span>
            <span className="text-[11px] text-slate-500">Domestic vs Foreign Shareholding</span>
          </div>
          <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs">
            <span className="font-bold text-emerald-950 block mb-0.5">3. Authority Pathway</span>
            <span className="text-[11px] text-emerald-700 font-medium">SBB Form A vs NBA Form I/III</span>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between shadow-subtle">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="font-bold ml-4 text-rose-700">✕</button>
        </div>
      )}

      {!result ? (
        /* Questionnaire Form */
        <form onSubmit={handleSubmit} className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-card space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Biological Herb Name */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1.5 uppercase tracking-wider">
                1. Biological Resource / Botanical Herb Name
              </label>
              <input
                type="text"
                required
                value={formData.biological_resource}
                onChange={(e) => setFormData({ ...formData, biological_resource: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest text-sm font-medium bg-slate-50/50"
                placeholder="e.g. Ashwagandha, Himalayan Kutki, Guggulu"
              />
            </div>

            {/* Sourced State */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1.5 uppercase tracking-wider">
                2. Indian State of Harvesting / Sourcing
              </label>
              <input
                type="text"
                required
                value={formData.sourced_from_state}
                onChange={(e) => setFormData({ ...formData, sourced_from_state: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest text-sm font-medium bg-slate-50/50"
                placeholder="e.g. Himachal Pradesh, Kerala, Madhya Pradesh"
              />
            </div>
          </div>

          {/* Entity Incorporation Status (Card-Based Radios) */}
          <div className="space-y-3">
            <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider">
              3. Entity Incorporation & Ownership Structure
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, is_indian_entity: true })}
                className={`p-4 rounded-2xl border text-left flex flex-col justify-between transition-all ${
                  formData.is_indian_entity
                    ? 'bg-emerald-50/70 border-emerald-500 ring-1 ring-emerald-500 shadow-subtle'
                    : 'bg-slate-50/50 border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                    <Building2 className="w-3.5 h-3.5 text-ayush-forest" />
                    <span>100% Indian Domestic Enterprise</span>
                  </span>
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${formData.is_indian_entity ? 'border-ayush-forest bg-ayush-forest' : 'border-slate-300'}`}>
                    {formData.is_indian_entity && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </div>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Indian citizen or company incorporated in India with zero foreign equity/control (Routes to State Biodiversity Board under Section 7).
                </p>
              </button>

              <button
                type="button"
                onClick={() => setFormData({ ...formData, is_indian_entity: false })}
                className={`p-4 rounded-2xl border text-left flex flex-col justify-between transition-all ${
                  !formData.is_indian_entity
                    ? 'bg-emerald-50/70 border-emerald-500 ring-1 ring-emerald-500 shadow-subtle'
                    : 'bg-slate-50/50 border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                    <Globe className="w-3.5 h-3.5 text-amber-600" />
                    <span>Foreign Entity / NRI / Foreign Equity</span>
                  </span>
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${!formData.is_indian_entity ? 'border-ayush-forest bg-ayush-forest' : 'border-slate-300'}`}>
                    {!formData.is_indian_entity && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </div>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Foreign citizen, NRI, or Indian company with foreign shareholding (Requires mandatory NBA Chennai Prior Approval under Section 3).
                </p>
              </button>
            </div>
          </div>

          {/* Utilization & Export Intent */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
              <label className="block text-xs font-bold text-slate-800">
                4. Purpose of Utilization
              </label>
              <div className="flex space-x-4 pt-1 text-xs font-medium">
                <label className="flex items-center space-x-1.5 cursor-pointer">
                  <input
                    type="radio"
                    name="commercial"
                    checked={formData.is_commercial_utilization}
                    onChange={() => setFormData({ ...formData, is_commercial_utilization: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Commercial Extraction & Sale</span>
                </label>
                <label className="flex items-center space-x-1.5 cursor-pointer">
                  <input
                    type="radio"
                    name="commercial"
                    checked={!formData.is_commercial_utilization}
                    onChange={() => setFormData({ ...formData, is_commercial_utilization: false })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Pure Academic Research</span>
                </label>
              </div>
            </div>

            <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2">
              <label className="block text-xs font-bold text-slate-800">
                5. Export of Biological Material / Formulation
              </label>
              <div className="flex space-x-4 pt-1 text-xs font-medium">
                <label className="flex items-center space-x-1.5 cursor-pointer">
                  <input
                    type="radio"
                    name="export"
                    checked={formData.is_export_intended}
                    onChange={() => setFormData({ ...formData, is_export_intended: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Yes (Export to Global Markets)</span>
                </label>
                <label className="flex items-center space-x-1.5 cursor-pointer">
                  <input
                    type="radio"
                    name="export"
                    checked={!formData.is_export_intended}
                    onChange={() => setFormData({ ...formData, is_export_intended: false })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>No (Domestic India Only)</span>
                </label>
              </div>
            </div>
          </div>

          {/* Form Submit */}
          <div className="pt-4 border-t border-slate-200 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-ayush-forest hover:bg-ayush-forestDark text-white font-bold rounded-xl text-xs sm:text-sm shadow-subtle flex items-center space-x-2 transition-all"
            >
              <span>{loading ? 'Evaluating BDA 2023 Provisions...' : 'Evaluate ABS Statutory Obligations'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      ) : (
        /* ========================================================= */
        /* RESULTS VIEW — AUTHORITY ROUTING & MANDATORY ACTIONS      */
        /* ========================================================= */
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-card space-y-6">
            
            {/* Top Status Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-5">
              <div>
                <div className="flex items-center space-x-2">
                  <span className={`text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-md border ${
                    result.risk_level.includes('HIGH')
                      ? 'bg-rose-100 text-rose-900 border-rose-300'
                      : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                  }`}>
                    {result.risk_level.includes('HIGH') ? '🔴 High Statutory Compliance' : '🟢 Domestic Compliance Pathway'}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400">
                    BDA 2023 Assessment Complete
                  </span>
                </div>
                <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 font-display mt-2">
                  {result.approval_type}
                </h3>
              </div>

              <button
                onClick={handleReset}
                className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors self-start sm:self-auto shadow-subtle"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Re-Evaluate Herb</span>
              </button>
            </div>

            {/* 2-Column Authority & Fee Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-slate-500 font-bold block uppercase text-[10px] tracking-wider">
                  Designated Statutory Authority
                </span>
                <span className="font-bold text-slate-900 text-sm">{result.applicable_authority}</span>
                <p className="text-[11px] text-slate-500 mt-1">
                  {result.applicable_authority.includes('State') 
                    ? 'State Biodiversity Board handles prior intimation from Indian entities.' 
                    : 'National Biodiversity Authority (Chennai) has exclusive jurisdiction over foreign entities and export authorizations.'}
                </p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-slate-500 font-bold block uppercase text-[10px] tracking-wider">
                  Equitable Benefit Sharing (EBS) Fee
                </span>
                <span className="font-bold text-slate-900 text-sm">
                  {result.benefit_sharing_applicable ? '0.1%–0.5% Annual Turnover or 3%–5% Purchase Price' : 'Exempted for Registered AYUSH Practitioners'}
                </span>
                <p className="text-[11px] text-slate-500 mt-1">
                  Under BDA Amendment 2023, codified benefit sharing schedules govern commercial bio-resource extraction.
                </p>
              </div>
            </div>

            {/* Mandatory Compliance Roadmap */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Mandatory Statutory Checklist:
              </h4>
              <div className="space-y-2">
                {result.mandatory_next_steps.map((step, idx) => (
                  <div key={idx} className="flex items-start space-x-2.5 text-xs text-slate-800 bg-slate-50/60 p-3.5 rounded-xl border border-slate-200/80">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span className="font-medium leading-relaxed">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Statutory Citations */}
            {result.statutory_citations && result.statutory_citations.length > 0 && (
              <div className="space-y-3 pt-2 border-t border-slate-100">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Authoritative Statutory Grounding:
                </h4>
                <div className="flex flex-wrap gap-2.5">
                  {result.statutory_citations.map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => onOpenCitation(c)}
                      className="inline-flex items-center space-x-2 px-3 py-2 bg-slate-50 hover:bg-emerald-50 text-slate-800 rounded-xl text-xs font-semibold border border-slate-200 transition-colors shadow-subtle group"
                    >
                      <BookOpen className="w-3.5 h-3.5 text-ayush-forest" />
                      <span>{c.section} ({c.source_title})</span>
                      <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-ayush-forest" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* ACTION CENTER */}
            <div className="pt-4 border-t border-slate-100 space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Next Recommended Actions:
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {onAskCopilot && (
                  <button
                    onClick={() => onAskCopilot(`How do I prepare the compliance application for ${result.approval_type} under the Biological Diversity Act 2023? What documents are required for ${formData.biological_resource}?`)}
                    className="p-3.5 bg-ayush-forest hover:bg-ayush-forestDark text-white rounded-2xl text-xs font-bold transition-all shadow-subtle flex items-center justify-center space-x-2"
                  >
                    <Sparkles className="w-4 h-4 text-emerald-200" />
                    <span>Ask AyuRaksha Copilot</span>
                  </button>
                )}

                {onNavigateView && (
                  <>
                    <button
                      onClick={() => onNavigateView('ip_matrix')}
                      className="p-3.5 bg-white hover:bg-slate-50 text-slate-800 rounded-2xl text-xs font-bold transition-all border border-slate-200 shadow-subtle flex items-center justify-center space-x-2"
                    >
                      <Scale className="w-4 h-4 text-ayush-forest" />
                      <span>Review IP Strategy Matrix</span>
                    </button>

                    <button
                      onClick={() => onNavigateView('knowledge_graph')}
                      className="p-3.5 bg-white hover:bg-slate-50 text-slate-800 rounded-2xl text-xs font-bold transition-all border border-slate-200 shadow-subtle flex items-center justify-center space-x-2"
                    >
                      <Network className="w-4 h-4 text-ayush-forest" />
                      <span>Explore Knowledge Graph</span>
                    </button>
                  </>
                )}

                {onOpenDossier && (
                  <button
                    onClick={onOpenDossier}
                    className="p-3.5 bg-slate-900 hover:bg-slate-800 text-white rounded-2xl text-xs font-bold transition-all shadow-subtle flex items-center justify-center space-x-2"
                  >
                    <FolderCheck className="w-4 h-4 text-emerald-300" />
                    <span>Active Case Dossier</span>
                  </button>
                )}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};

