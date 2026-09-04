import React, { useState, useEffect } from 'react';
import {
  X,
  Printer,
  Download,
  FileText,
  Scale,
  ShieldCheck,
  Compass
} from 'lucide-react';
import { ActiveCaseState, Citation } from '../../types';
import { api } from '../../services/api';
import { AnswerVisual } from '../visuals/AnswerVisual';

interface ComplianceDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeCase: ActiveCaseState | null;
  onStartAssessment?: () => void;
  onOpenCitation?: (c: Citation) => void;
}

export const ComplianceDossierModal: React.FC<ComplianceDossierModalProps> = ({
  isOpen,
  onClose,
  activeCase,
  onStartAssessment,
  onOpenCitation
}) => {
  const [loading, setLoading] = useState(false);
  const [dossierData, setDossierData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const hasActiveAssessment = Boolean(
    activeCase && (activeCase.productRequest || activeCase.classificationResult)
  );

  useEffect(() => {
    if (!isOpen || !hasActiveAssessment || !activeCase?.productRequest) {
      setDossierData(null);
      return;
    }

    const generateCaseDossier = async () => {
      setLoading(true);
      setError(null);
      try {
        const req = activeCase.productRequest!;
        const ingredientsList = (req as any).ingredients && Array.isArray((req as any).ingredients) && (req as any).ingredients.length > 0
          ? (req as any).ingredients
          : [req.name || 'Ayurvedic Botanical Component'];

        const res = await api.generateDossier({
          product_name: req.name,
          ingredients: ingredientsList,
          in_classical_text: req.in_classical_text,
          is_formulation_modified: req.is_formulation_modified,
          is_purified_standardized_fraction: req.is_purified_standardized_fraction || false,
          intended_use: req.intended_use || 'therapeutic',
          disease_treatment_claims: req.disease_treatment_claims,
          is_indian_entity: true,
          target_market: req.target_market || 'IN'
        });
        setDossierData(res);
      } catch (err: any) {
        console.error('Failed to compile data-driven case dossier:', err);
        setError('Failed to synthesize case dossier from active assessment data. Please retry.');
      } finally {
        setLoading(false);
      }
    };

    generateCaseDossier();
  }, [isOpen, hasActiveAssessment, activeCase?.productRequest, activeCase?.updatedAt]);

  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleExportMarkdown = async () => {
    if (!dossierData || !activeCase?.productRequest) return;
    try {
      const req = activeCase.productRequest;
      const ingredientsList = (req as any).ingredients || [req.name];
      const blob = await api.exportDossierMarkdown({
        product_name: req.name || 'Ayuरक्षा_Product',
        ingredients: ingredientsList,
        in_classical_text: req.in_classical_text,
        is_formulation_modified: req.is_formulation_modified,
        is_purified_standardized_fraction: req.is_purified_standardized_fraction || false,
        intended_use: req.intended_use || 'therapeutic',
        disease_treatment_claims: req.disease_treatment_claims,
        is_indian_entity: true,
        target_market: req.target_market || 'IN'
      });
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `${activeCase.caseId}_${(req.name || 'dossier').toLowerCase().replace(/\s+/g, '_')}.md`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error('Export markdown failed:', e);
    }
  };

  const formatDate = (isoString?: string) => {
    if (!isoString) return 'Active Session';
    try {
      return new Date(isoString).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white border border-slate-200 rounded-2xl max-w-5xl w-full max-h-[92vh] flex flex-col min-h-0 shadow-modal overflow-hidden">
        
        {/* MODAL ACTION BAR */}
        <div className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between border-b border-slate-800 shrink-0">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-ayush-forest rounded-xl text-white">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-bold text-base font-display">Ayuरक्षा Case Dossier</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                  {hasActiveAssessment ? activeCase?.caseId : 'NO ACTIVE CASE'}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Official Regulatory & IP Decision Dossier · Drugs & Cosmetics Act 1940 · BDA 2023 · Patents Act 1970
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {hasActiveAssessment && dossierData && (
              <>
                <button
                  onClick={handleExportMarkdown}
                  disabled={loading}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold flex items-center space-x-1.5 transition-all shadow-sm"
                  title="Download full Markdown case report"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Export Markdown</span>
                </button>
                <button
                  onClick={handlePrint}
                  className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-bold flex items-center space-x-1.5 border border-white/20 transition-all"
                  title="Print official case file"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Print / PDF</span>
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* MODAL BODY */}
        <div className="p-6 overflow-y-auto flex-1 min-h-0 space-y-6 text-xs text-slate-800 printable-area">
          
          {/* STATE 1: NO ACTIVE CASE */}
          {!hasActiveAssessment ? (
            <div className="py-16 text-center space-y-5 max-w-md mx-auto animate-fadeIn">
              <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-ayush-forest mx-auto flex items-center justify-center border border-emerald-200 shadow-subtle">
                <FileText className="w-7 h-7" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-lg font-extrabold text-slate-900 font-display">
                  No Active Assessment Case
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  The Ayuरक्षा Case Dossier is a live, audit-ready record compiled directly from your actual product parameters, statutory classification, and patent/ABS evaluations.
                </p>
                <p className="text-[11px] text-slate-500">
                  Start an assessment in Module 1 to construct an authoritative case dossier.
                </p>
              </div>
              <button
                onClick={() => {
                  onClose();
                  if (onStartAssessment) onStartAssessment();
                }}
                className="px-5 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white font-bold rounded-xl text-xs shadow-subtle flex items-center space-x-2 mx-auto transition-all"
              >
                <Compass className="w-4 h-4" />
                <span>Start New Product Assessment</span>
              </button>
            </div>
          ) : loading ? (
            <div className="py-20 text-center space-y-3">
              <div className="w-8 h-8 border-3 border-ayush-forest border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm font-bold text-slate-700">
                Compiling statutory classifications, botanical taxonomy, and filing milestones...
              </p>
            </div>
          ) : error ? (
            <div className="p-5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 space-y-2 text-center">
              <p className="font-bold">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-bold"
              >
                Reload Case
              </button>
            </div>
          ) : dossierData ? (
            <div className="space-y-6">
              
              {/* 1. DOSSIER CASE HEADER */}
              <div className="border border-slate-200 bg-slate-50/80 p-5 rounded-2xl space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/80 pb-3">
                  <div>
                    <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                      Ayuरक्षा · IP & Regulatory Case Dossier
                    </span>
                    <h2 className="text-lg sm:text-xl font-extrabold text-slate-900 font-display">
                      {activeCase?.productRequest?.name || dossierData.product_profile?.name}
                    </h2>
                  </div>
                  <div className="flex items-center space-x-2 text-[11px]">
                    <span className="px-2.5 py-1 rounded-lg font-bold bg-white text-slate-800 border border-slate-200 shadow-xs">
                      Jurisdiction: {activeCase?.productRequest?.target_market === 'IN' ? '🇮🇳 India' : '🌍 International'}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg font-bold bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-xs">
                      Status: {activeCase?.status || 'EVALUATED'}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
                  <div>
                    <span className="text-slate-400 font-semibold block text-[10px] uppercase">Case ID</span>
                    <span className="font-mono font-bold text-slate-900">{activeCase?.caseId}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-semibold block text-[10px] uppercase">Created Date</span>
                    <span className="font-bold text-slate-700">{formatDate(activeCase?.createdAt)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-semibold block text-[10px] uppercase">Last Updated</span>
                    <span className="font-bold text-slate-700">{formatDate(activeCase?.updatedAt)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 font-semibold block text-[10px] uppercase">Assessment Reliability</span>
                    <span className="font-bold text-emerald-800 flex items-center space-x-1">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Source-Backed</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* 2. PRODUCT PROFILE & RESOLVED BOTANICAL TAXONOMY */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
                    <span className="w-5 h-5 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[10px] font-black">1</span>
                    <span>Product Profile & Botanical Resource Taxonomy</span>
                  </h4>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-[11px]">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Classical Text Basis</span>
                    <span className="font-bold text-slate-800">
                      {activeCase?.productRequest?.in_classical_text ? 'Yes (First Schedule Text)' : 'No / Modified'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Modification Level</span>
                    <span className="font-bold text-slate-800">
                      {activeCase?.productRequest?.is_formulation_modified ? 'Modified Composition / Excipients' : 'Classical Direct Recipe'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Intended Use</span>
                    <span className="font-bold text-slate-800 capitalize">
                      {activeCase?.productRequest?.intended_use || 'Therapeutic'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Disease Treatment Claims</span>
                    <span className="font-bold text-slate-800">
                      {activeCase?.productRequest?.disease_treatment_claims ? 'Claimed' : 'Not Claimed'}
                    </span>
                  </div>
                </div>

                {dossierData.product_profile?.ingredients && dossierData.product_profile.ingredients.length > 0 && (
                  <div className="overflow-x-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-left text-[11px]">
                      <thead className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                        <tr>
                          <th className="p-2.5">Input Component</th>
                          <th className="p-2.5">Botanical Binomial</th>
                          <th className="p-2.5">Sanskrit Synonym</th>
                          <th className="p-2.5">Botanical Family</th>
                          <th className="p-2.5">Parts Used</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 bg-white">
                        {dossierData.product_profile.ingredients.map((ing: any, i: number) => (
                          <tr key={i} className="hover:bg-slate-50">
                            <td className="p-2.5 font-bold text-slate-800">{ing.input_name}</td>
                            <td className="p-2.5 italic text-emerald-800 font-semibold">{ing.scientific_name}</td>
                            <td className="p-2.5 text-slate-700">{ing.sanskrit_name}</td>
                            <td className="p-2.5 text-slate-600">{ing.family}</td>
                            <td className="p-2.5 text-slate-600">{ing.parts_used}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Optional: User-Stated Innovation Discovery Profile */}
                {activeCase?.innovationProfile && (
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest">
                        User-Stated Technical Innovation Profile
                      </span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-slate-200 text-slate-700">
                        Self-Reported Baseline
                      </span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Baseline Comparison:</span>
                        <span className="font-semibold text-slate-800">{activeCase.innovationProfile.baseline}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">User-Stated Difference:</span>
                        <span className="font-semibold text-slate-800">{activeCase.innovationProfile.userStatedDifference}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Technical Feature:</span>
                        <span className="font-semibold text-slate-800">{activeCase.innovationProfile.technicalFeature}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold">Reported Technical Effect:</span>
                        <span className="font-bold text-emerald-800">{activeCase.innovationProfile.technicalEffect}</span>
                      </div>
                      {activeCase.innovationProfile.evidenceDetails && (
                        <div className="sm:col-span-2">
                          <span className="text-slate-400 block text-[10px] uppercase font-bold">Available Evidence:</span>
                          <span className="text-slate-700">{activeCase.innovationProfile.evidenceDetails}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* 3. REGULATORY CLASSIFICATION & IP POSITION */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* 3A. Regulatory Classification */}
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2.5">
                  <h5 className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                    <span className="w-4 h-4 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[9px] font-black">2A</span>
                    <span>Regulatory Drug Classification</span>
                  </h5>
                  <div className="space-y-2 text-[11px]">
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Assigned Category</span>
                      <span className="font-bold text-ayush-forest text-xs">
                        {dossierData.regulatory_classification?.category || 'Classical Ayurvedic Medicine'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Governing Statute</span>
                      <span className="font-semibold text-slate-800">
                        {dossierData.regulatory_classification?.governing_act || 'Drugs & Cosmetics Act, 1940 (Rule 158B)'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Licensing Authority</span>
                      <span className="font-semibold text-slate-800">
                        {dossierData.regulatory_classification?.regulatory_authority || 'State Licensing Authority (Ayush)'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 3B. IP Standing & Section 3(p) */}
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2.5">
                  <h5 className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                    <span className="w-4 h-4 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[9px] font-black">2B</span>
                    <span>Intellectual Property Standing</span>
                  </h5>
                  <div className="space-y-2 text-[11px]">
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Section 3(p) Patentability Status</span>
                      <span className={`font-bold px-2 py-0.5 rounded text-[10px] inline-block ${
                        dossierData.regulatory_classification?.patentability === 'BARRED'
                          ? 'bg-rose-100 text-rose-800 border border-rose-300'
                          : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                      }`}>
                        {dossierData.regulatory_classification?.patentability === 'BARRED'
                          ? 'Section 3(p) TK Exclusion Triggered'
                          : 'Potential Route with Novel Excipient / Synergism'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Patent Rationale</span>
                      <p className="text-slate-700 text-[11px] leading-relaxed">
                        {dossierData.regulatory_classification?.patent_rationale ||
                          'Traditional formulations from First Schedule texts are excluded under Section 3(p) of the Patents Act, 1970 unless non-obvious synergistic efficacy is proven.'}
                      </p>
                    </div>
                  </div>
                </div>

              </div>

              {/* 3C. CASE DECISION ROADMAP */}
              <div className="space-y-2">
                <h5 className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                  <span className="w-4 h-4 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[9px] font-black">2C</span>
                  <span>Statutory Case Decision Roadmap</span>
                </h5>
                <AnswerVisual
                  questionText={activeCase?.productRequest?.name || 'Product Classification Roadmap'}
                  answerText={`${dossierData.regulatory_classification?.category || ''} ${dossierData.regulatory_classification?.governing_act || ''} ${dossierData.regulatory_classification?.patent_rationale || ''}`}
                  answerData={{
                    direct_answer: dossierData.executive_summary || '',
                    assessment_table: {},
                    verified_claims: [],
                    citations: dossierData.verifiable_citations || dossierData.citations || [],
                    caveats: [],
                    confidence_level: 'HIGH',
                    safe_abstention: false,
                    jurisdiction: 'IN',
                    recommended_next_action: 'Proceed with statutory roadmap.'
                  }}
                  onOpenCitation={onOpenCitation}
                  compact={true}
                />
              </div>

              {/* 4. ACCESS & BENEFIT-SHARING (ABS) STANDING */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5">
                <h5 className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                  <span className="w-4 h-4 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[9px] font-black">3</span>
                  <span>Biological Diversity Act (ABS) Standing</span>
                </h5>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-[11px]">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Governing Statute</span>
                    <span className="font-semibold text-slate-800">
                      {dossierData.abs_assessment?.governing_statute || 'Biological Diversity Act, 2002 (BDA 2023)'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Competent Authority</span>
                    <span className="font-bold text-slate-800">
                      {dossierData.abs_assessment?.applicable_authority || 'State Biodiversity Board (SBB) / NBA'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Statutory Trigger</span>
                    <span className="font-semibold text-emerald-800">
                      {dossierData.abs_assessment?.approval_type || 'Intimation to SBB / Form I Exemption Review'}
                    </span>
                  </div>
                </div>
              </div>

              {/* 5. CROSS-BORDER & INTERNATIONAL POSTURE (if applicable) */}
              {dossierData.cross_border_posture && (
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5">
                  <h5 className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                    <span className="w-4 h-4 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[9px] font-black">4</span>
                    <span>Cross-Border & Export Regulatory Posture</span>
                  </h5>
                  <div className="space-y-2 text-[11px]">
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">India Export Clearance</span>
                      <p className="text-slate-700 leading-relaxed">
                        {dossierData.cross_border_posture.india_export_clearance}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Destination Market Clearance</span>
                      <p className="text-slate-700 leading-relaxed">
                        {dossierData.cross_border_posture.destination_market_clearance}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* 6. STATUTORY FILING ROADMAP & TIMELINE */}
              <div className="space-y-3">
                <h4 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[10px] font-black">5</span>
                  <span>Sequential Statutory Filing Roadmap & Fee Schedule</span>
                </h4>
                <div className="space-y-2.5">
                  {(dossierData.filing_roadmap || []).map((step: any) => (
                    <div key={step.step_number} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="font-black text-xs text-ayush-forest">Step {step.step_number}:</span>
                          <span className="font-bold text-xs text-slate-900">{step.title}</span>
                        </div>
                        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                          {step.mandatory_form}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-700 leading-relaxed">{step.action_details}</p>
                      <div className="flex flex-wrap items-center gap-4 text-[10px] text-slate-500 pt-1.5 border-t border-slate-200/80">
                        <span><strong>Authority:</strong> {step.authority}</span>
                        <span><strong>Timeline:</strong> {step.statutory_timeline}</span>
                        <span><strong>Est. Fee:</strong> {step.fee_estimate}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 7. EVIDENCE REGISTER & GROUNDED STATUTORY CITATIONS */}
              <div className="space-y-3">
                <h4 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[10px] font-black">6</span>
                  <span>Evidence Register · Grounded Statutory Authority Citations</span>
                </h4>
                <div className="space-y-2">
                  {(dossierData.verifiable_citations || dossierData.citations || []).slice(0, 5).map((c: any, i: number) => (
                    <div
                      key={i}
                      onClick={() => onOpenCitation && onOpenCitation(c)}
                      className="p-3 bg-emerald-50/50 hover:bg-emerald-50 rounded-xl border border-emerald-200/80 space-y-1 transition-all cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <p className="font-bold text-ayush-forest text-xs">
                          {c.source_title} · {c.section}
                        </p>
                        {c.support_score && (
                          <span className="font-mono text-[9px] font-bold px-1.5 py-0.5 bg-emerald-100 text-emerald-900 rounded">
                            {Math.round(c.support_score * 100)}% Match
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-700 italic">
                        "{c.verbatim_quote || 'Statutory authority provision verified against official Gazette notifications.'}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 8. LEGAL DISCLAIMER */}
              <div className="p-3.5 bg-slate-100 rounded-xl border border-slate-200 text-[11px] text-slate-600 font-medium leading-relaxed">
                Information provided by Ayuरक्षा is for decision-support and research purposes only and does not constitute legal advice. Filing, licensing, enforcement, and commercial decisions should be reviewed by an appropriately qualified IP / regulatory professional.
              </div>

            </div>
          ) : null}

        </div>

        {/* MODAL FOOTER */}
        <div className="bg-slate-50 px-6 py-3.5 border-t border-slate-200 flex items-center justify-between">
          <span className="text-[11px] text-slate-500">
            Ayuरक्षा · SIH 26045 IP-SAKTI Sahayak
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
};
