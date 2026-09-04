import React, { useState, useEffect } from 'react';
import {
  Compass,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  BookOpen,
  ExternalLink,
  Scale,
  Layers,
  Leaf,
  FileCheck,
  ShieldCheck,
  Sparkles,
  FileText,
  ChevronDown,
  ChevronUp,
  Network
} from 'lucide-react';
import { api } from '../../services/api';
import {
  ProductClassificationRequest,
  ProductClassificationResponse,
  Citation,
  ActiveCaseState,
  Jurisdiction
} from '../../types';

interface ProductJourneyWizardProps {
  activeCase?: ActiveCaseState | null;
  jurisdiction?: Jurisdiction;
  onOpenCitation: (c: Citation) => void;
  onNavigateView?: (view: 'ip_matrix' | 'abs_wizard' | 'international' | 'chat' | 'knowledge_graph' | 'corpus') => void;
  onOpenDossier?: () => void;
  onClassificationComplete?: (req: ProductClassificationRequest, res: ProductClassificationResponse) => void;
  onAskCopilot?: (query: string) => void;
}

export const ProductJourneyWizard: React.FC<ProductJourneyWizardProps> = ({
  activeCase,
  jurisdiction = 'IN',
  onOpenCitation,
  onNavigateView,
  onOpenDossier,
  onClassificationComplete,
  onAskCopilot
}) => {
  // 1. Initialize form from activeCase (or InnovationProfile if user already completed it)
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 6;
  const [showDecisionFactors, setShowDecisionFactors] = useState(true);

  const [formData, setFormData] = useState<ProductClassificationRequest>(() => {
    if (activeCase?.productRequest) {
      return { ...activeCase.productRequest };
    }
    if (activeCase?.innovationProfile) {
      return {
        name: activeCase.innovationProfile.productName || 'Ashwagandha Synergistic Extract',
        in_classical_text: activeCase.innovationProfile.isTraditionalKnowledge === 'YES',
        is_formulation_modified: activeCase.innovationProfile.isTraditionalKnowledge !== 'YES',
        has_novel_excipients: false,
        is_purified_standardized_fraction: false,
        intended_use: 'therapeutic',
        disease_treatment_claims: true,
        has_biological_resources: true,
        target_market: jurisdiction
      };
    }
    return {
      name: 'Ashwagandha Synergistic Polyherbal Extract',
      in_classical_text: true,
      is_formulation_modified: true,
      has_novel_excipients: false,
      is_purified_standardized_fraction: false,
      intended_use: 'therapeutic',
      disease_treatment_claims: true,
      has_biological_resources: true,
      target_market: jurisdiction
    };
  });

  // Additional rich wizard state
  const [dosageForm, setDosageForm] = useState('Capsule / Vati');
  const [classicalTreatise, setClassicalTreatise] = useState('Charaka Samhita (Chikitsa Sthana)');
  const [classicalFormulationName, setClassicalFormulationName] = useState('Ashwagandhadya Ghrita / Churna variant');
  const [technicalModificationDetail, setTechnicalModificationDetail] = useState('Altered hydro-alcoholic extraction temperature with standardized 5% withanolides');
  const [biologicalSourcingOrigin, setBiologicalSourcingOrigin] = useState('Cultivated and wild-harvested in Madhya Pradesh & Rajasthan, India');
  const [isPreFilled, setIsPreFilled] = useState(false);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProductClassificationResponse | null>(() => activeCase?.classificationResult || null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (activeCase?.innovationProfile && !activeCase.classificationResult) {
      setIsPreFilled(true);
    }
  }, [activeCase]);

  // Handle statutory submission to backend classifier
  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await api.evaluateClassification(formData);
      setResult(res);
      if (onClassificationComplete) {
        onClassificationComplete(formData, res);
      }
    } catch (err: any) {
      console.error('Classification error', err);
      setErrorMessage(err.response?.data?.detail || 'Failed to evaluate product classification. Please verify connection and retry.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setErrorMessage(null);
    setCurrentStep(1);
  };

  // Step definitions
  const stepTitles = [
    { num: 1, title: 'Product Identity & Form', subtitle: 'Name, dosage form & core purpose' },
    { num: 2, title: 'Ayurvedic Treatise Basis', subtitle: 'First Schedule classical text grounding' },
    { num: 3, title: 'Formulation Status', subtitle: 'Classical recipe vs. Modified proprietary' },
    { num: 4, title: 'Ingredients & Sourcing', subtitle: 'Biological resources & origin' },
    { num: 5, title: 'Technical Difference', subtitle: 'Extraction, processing & standardization' },
    { num: 6, title: 'Claims & Market Intent', subtitle: 'Therapeutic vs. food/cosmetic claims' }
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fadeIn select-text">
      
      {/* 1. HEADER BANNER */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-card space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-ayush-forest rounded-full text-xs font-bold border border-emerald-200">
            <Compass className="w-3.5 h-3.5" />
            <span>Statutory ASU Classification Navigator · Module 1</span>
          </div>
          <div className="flex items-center space-x-2 text-[11px] font-mono font-bold">
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
              Case: {activeCase?.caseId || 'AYR-2026-INIT'}
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300">
              Jurisdiction: {formData.target_market === 'IN' ? '🇮🇳 India' : '🌍 International'}
            </span>
          </div>
        </div>

        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-display tracking-tight">
          Ayurvedic Product Regulatory Classification
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-3xl">
          Determine the precise statutory regulatory drug licensing category under the Drugs & Cosmetics Act 1940 (First Schedule & Rule 158B), FSSAI Ayurveda Aahara Regulations 2022, CDSCO Phytopharmaceutical criteria, and Section 3(p) Traditional Knowledge patent exclusions.
        </p>

        {/* Progress Stepper Bar */}
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 pt-4 mt-4 border-t border-slate-100 text-center">
          {stepTitles.map((s) => (
            <div
              key={s.num}
              onClick={() => {
                if (!result) setCurrentStep(s.num);
              }}
              className={`flex flex-col items-center cursor-pointer group ${result ? 'pointer-events-none' : ''}`}
            >
              <span
                className={`w-6 h-6 rounded-full text-[10px] font-black flex items-center justify-center mb-1 transition-all ${
                  result
                    ? 'bg-ayush-forest text-white'
                    : s.num === currentStep
                    ? 'bg-ayush-forest text-white ring-2 ring-emerald-300 shadow-subtle'
                    : s.num < currentStep
                    ? 'bg-emerald-100 text-emerald-900 font-bold'
                    : 'bg-slate-100 text-slate-400 group-hover:bg-slate-200'
                }`}
              >
                {result || s.num < currentStep ? '✓' : s.num}
              </span>
              <span className={`text-[10px] font-bold truncate max-w-full ${s.num === currentStep ? 'text-slate-900' : 'text-slate-400'}`}>
                {s.title.split(' ')[0]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Pre-fill Notification Banner if loaded from Active Innovation Profile */}
      {isPreFilled && !result && (
        <div className="p-3.5 rounded-2xl bg-emerald-50/80 border border-emerald-200 text-xs text-emerald-900 flex items-center justify-between shadow-subtle animate-fadeIn">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-ayush-forest shrink-0" />
            <span className="font-medium">
              Information pre-filled from your <strong>Active Innovation Discovery Profile</strong> (<em>{formData.name}</em>). You can review or adjust any parameter below.
            </span>
          </div>
          <button
            onClick={() => setIsPreFilled(false)}
            className="text-[10px] font-bold text-emerald-700 hover:underline shrink-0 ml-3"
          >
            Dismiss
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between shadow-subtle">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="font-bold ml-4 text-rose-700">✕</button>
        </div>
      )}

      {!result ? (
        /* ========================================================= */
        /* PROGRESSIVE 6-STAGE QUESTIONNAIRE WITH LIVE PROFILE PANEL */
        /* ========================================================= */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          {/* LEFT 2 COLUMNS: ADAPTIVE STEP-BY-STEP FORM */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-card space-y-6">
              
              {/* STEP 1: PRODUCT IDENTITY & DOSAGE FORM */}
              {currentStep === 1 && (
                <div className="space-y-4 animate-fadeIn">
                  <div className="space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                      Stage 01 of 06 · Product Identity
                    </span>
                    <h3 className="text-lg font-extrabold text-slate-900 font-display">
                      What is the Trade Name and Delivery Form of your product?
                    </h3>
                    <p className="text-xs text-slate-500">
                      Product nomenclature and dosage form establish initial classification criteria under the Ayurvedic Pharmacopoeia of India (API).
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                        Product / Formulation Trade Name
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="e.g. Ashwagandha Synergistic Extract / AyurGlyco Vati"
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest text-xs sm:text-sm font-medium bg-slate-50/50"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                        Physical Dosage Form / Presentation
                      </label>
                      <select
                        value={dosageForm}
                        onChange={(e) => setDosageForm(e.target.value)}
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 text-xs font-medium bg-slate-50/50"
                      >
                        <option value="Capsule / Vati (Tablet)">Capsule / Vati (Solid Oral Tablet)</option>
                        <option value="Churna (Powder / Kwatha)">Churna / Kwatha (Crude or Standardized Powder)</option>
                        <option value="Asava / Arishta (Hydro-alcoholic Ferment)">Asava / Arishta (Classical Bio-Fermented Liquid)</option>
                        <option value="Taila / Ghrita (Medicated Oil/Ghee)">Taila / Ghrita (Lipid Base Formulation)</option>
                        <option value="Standardized Botanical Extract / Nano-emulsion">Standardized Botanical Extract / Nano-emulsion</option>
                        <option value="Topical Lepa / Cream / Serum">Topical Lepa / Cosmetic Cream / Serum</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 2: CLASSICAL AYURVEDIC TREATISE BASIS */}
              {currentStep === 2 && (
                <div className="space-y-4 animate-fadeIn">
                  <div className="space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                      Stage 02 of 06 · Ayurvedic Basis
                    </span>
                    <h3 className="text-lg font-extrabold text-slate-900 font-display">
                      Is the formulation derived from a classical Ayurvedic text in the First Schedule?
                    </h3>
                    <p className="text-xs text-slate-500">
                      Under Section 3(a) of the Drugs & Cosmetics Act 1940, classical formulations must appear in 54 specified authoritative books.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, in_classical_text: true })}
                      className={`p-4 rounded-xl border text-left flex flex-col justify-between transition-all ${
                        formData.in_classical_text
                          ? 'bg-emerald-50/80 border-ayush-forest ring-1 ring-ayush-forest shadow-subtle'
                          : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                          <span>📖 Yes — Classical Treatise Basis</span>
                        </span>
                        <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${formData.in_classical_text ? 'border-ayush-forest bg-ayush-forest' : 'border-slate-300'}`}>
                          {formData.in_classical_text && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        Described in First Schedule texts (e.g. Charaka Samhita, Sushruta Samhita, Sharangadhara Samhita, API).
                      </p>
                    </button>

                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, in_classical_text: false })}
                      className={`p-4 rounded-xl border text-left flex flex-col justify-between transition-all ${
                        !formData.in_classical_text
                          ? 'bg-emerald-50/80 border-ayush-forest ring-1 ring-ayush-forest shadow-subtle'
                          : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold text-xs text-slate-900 flex items-center space-x-1.5">
                          <span>🧪 No / Non-Classical Formulation</span>
                        </span>
                        <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${!formData.in_classical_text ? 'border-ayush-forest bg-ayush-forest' : 'border-slate-300'}`}>
                          {!formData.in_classical_text && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        Proprietary polyherbal combination or modern experimental formulation not in classical treatises.
                      </p>
                    </button>
                  </div>

                  {/* Adaptive: If Classical Text Basis == YES */}
                  {formData.in_classical_text && (
                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3 pt-3">
                      <div>
                        <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                          Authoritative Classical Treatise (First Schedule)
                        </label>
                        <select
                          value={classicalTreatise}
                          onChange={(e) => setClassicalTreatise(e.target.value)}
                          className="w-full px-4 py-2 rounded-xl border border-slate-300 text-xs font-medium bg-white"
                        >
                          <option value="Charaka Samhita (Chikitsa Sthana)">Charaka Samhita (First Schedule)</option>
                          <option value="Sushruta Samhita (Uttara Tantra)">Sushruta Samhita (First Schedule)</option>
                          <option value="Ashtanga Hridaya (Vagbhata)">Ashtanga Hridaya (First Schedule)</option>
                          <option value="Sharangadhara Samhita (Madhyama Khanda)">Sharangadhara Samhita (First Schedule)</option>
                          <option value="Bhavaprakasha Nighantu">Bhavaprakasha Nighantu (First Schedule)</option>
                          <option value="Sahasrayogam">Sahasrayogam (First Schedule)</option>
                          <option value="Ayurvedic Pharmacopoeia of India (API)">Ayurvedic Pharmacopoeia of India (API Monograph)</option>
                          <option value="Bhaishajya Ratnavali">Bhaishajya Ratnavali (First Schedule)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                          Original Classical Formulation / Yoga Name
                        </label>
                        <input
                          type="text"
                          value={classicalFormulationName}
                          onChange={(e) => setClassicalFormulationName(e.target.value)}
                          placeholder="e.g. Ashwagandhadya Ghrita, Triphala Churna, Chyawanprash"
                          className="w-full px-4 py-2 rounded-xl border border-slate-300 text-xs font-medium bg-white"
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* STEP 3: FORMULATION STATUS & MODIFICATION */}
              {currentStep === 3 && (
                <div className="space-y-4 animate-fadeIn">
                  <div className="space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                      Stage 03 of 06 · Formulation Status
                    </span>
                    <h3 className="text-lg font-extrabold text-slate-900 font-display">
                      Are the botanical ratios, ingredients, or excipients altered from the classical recipe?
                    </h3>
                    <p className="text-xs text-slate-500">
                      Unchanged formulations qualify as Classical ASU (Rule 158B exempt). Modified formulations become Proprietary ASU (Rule 158B).
                    </p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, is_formulation_modified: false, has_novel_excipients: false })}
                      className={`p-4 rounded-xl border text-left flex flex-col justify-between transition-all ${
                        !formData.is_formulation_modified && !formData.has_novel_excipients
                          ? 'bg-emerald-50/80 border-ayush-forest ring-1 ring-ayush-forest shadow-subtle'
                          : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold text-xs text-slate-900">
                          📜 Unchanged Classical Formulation
                        </span>
                        <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${!formData.is_formulation_modified ? 'border-ayush-forest bg-ayush-forest' : 'border-slate-300'}`}>
                          {!formData.is_formulation_modified && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        Manufactured strictly adhering to classical text ingredient ratios, methods, and traditional excipients.
                      </p>
                    </button>

                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, is_formulation_modified: true })}
                      className={`p-4 rounded-xl border text-left flex flex-col justify-between transition-all ${
                        formData.is_formulation_modified
                          ? 'bg-emerald-50/80 border-ayush-forest ring-1 ring-ayush-forest shadow-subtle'
                          : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold text-xs text-slate-900">
                          ⚙️ Modified / Proprietary (Anubhuta)
                        </span>
                        <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${formData.is_formulation_modified ? 'border-ayush-forest bg-ayush-forest' : 'border-slate-300'}`}>
                          {formData.is_formulation_modified && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        Altered botanical proportions, enriched fractions, or new combination requiring Rule 158B safety proof.
                      </p>
                    </button>
                  </div>

                  {/* Excipient & Delivery System Toggle */}
                  <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-800">
                        Modern Excipients / Nano-carrier Delivery System?
                      </span>
                      <div className="flex items-center space-x-3 text-xs font-semibold">
                        <label className="flex items-center space-x-1.5 cursor-pointer">
                          <input
                            type="radio"
                            name="excipients"
                            checked={formData.has_novel_excipients}
                            onChange={() => setFormData({ ...formData, has_novel_excipients: true })}
                            className="text-ayush-forest focus:ring-ayush-forest"
                          />
                          <span>Yes</span>
                        </label>
                        <label className="flex items-center space-x-1.5 cursor-pointer">
                          <input
                            type="radio"
                            name="excipients"
                            checked={!formData.has_novel_excipients}
                            onChange={() => setFormData({ ...formData, has_novel_excipients: false })}
                            className="text-ayush-forest focus:ring-ayush-forest"
                          />
                          <span>No (Traditional)</span>
                        </label>
                      </div>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Liposomal delivery, cyclodextrin complexes, or synthetic polymers require excipient safety assessment under Rule 158B.
                    </p>
                  </div>
                </div>
              )}

              {/* STEP 4: INGREDIENTS & BIOLOGICAL SOURCING */}
              {currentStep === 4 && (
                <div className="space-y-4 animate-fadeIn">
                  <div className="space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                      Stage 04 of 06 · Biological Resource Sourcing
                    </span>
                    <h3 className="text-lg font-extrabold text-slate-900 font-display">
                      Biological Resources & Sourcing Provenance
                    </h3>
                    <p className="text-xs text-slate-500">
                      Under the Biological Diversity Act 2023, accessing Indian biological resources for commercial manufacture requires Prior Intimation to the State Biodiversity Board (SBB).
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-800">
                          Contains Indian Biological Resources (Plants/Microorganisms)?
                        </span>
                        <div className="flex items-center space-x-3 text-xs font-semibold">
                          <label className="flex items-center space-x-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="bioresources"
                              checked={formData.has_biological_resources}
                              onChange={() => setFormData({ ...formData, has_biological_resources: true })}
                              className="text-ayush-forest focus:ring-ayush-forest"
                            />
                            <span>Yes</span>
                          </label>
                          <label className="flex items-center space-x-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="bioresources"
                              checked={!formData.has_biological_resources}
                              onChange={() => setFormData({ ...formData, has_biological_resources: false })}
                              className="text-ayush-forest focus:ring-ayush-forest"
                            />
                            <span>No</span>
                          </label>
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-500">
                        Herbal roots, stems, leaves, extracts, or resins sourced from India.
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                        Geographical Sourcing Origin / State
                      </label>
                      <input
                        type="text"
                        value={biologicalSourcingOrigin}
                        onChange={(e) => setBiologicalSourcingOrigin(e.target.value)}
                        placeholder="e.g. Sourced from cultivators in Madhya Pradesh / Western Ghats"
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-medium bg-slate-50/50"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 5: INNOVATION, PROCESSING & STANDARDIZATION */}
              {currentStep === 5 && (
                <div className="space-y-4 animate-fadeIn">
                  <div className="space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                      Stage 05 of 06 · Technical Innovation & Phytopharmaceutical Check
                    </span>
                    <h3 className="text-lg font-extrabold text-slate-900 font-display">
                      Did you introduce any novel extraction, standardized fraction, or processing parameter?
                    </h3>
                    <p className="text-xs text-slate-500">
                      Standardized fractions with $\ge 4$ analytical markers are evaluated under CDSCO Phytopharmaceutical Drug Rules (GSR 918(E)) rather than State AYUSH.
                    </p>
                  </div>

                  <div className="space-y-3">
                    {/* Phytopharmaceutical Criteria Toggle */}
                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center justify-between">
                        <label className="text-xs font-bold text-slate-900 flex items-center space-x-1.5">
                          <Layers className="w-4 h-4 text-ayush-forest" />
                          <span>Purified Standardized Fraction ($\ge 4$ Bioactive Markers)?</span>
                        </label>
                        <div className="flex items-center space-x-3 text-xs font-semibold">
                          <label className="flex items-center space-x-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="phytopharm"
                              checked={formData.is_purified_standardized_fraction}
                              onChange={() => setFormData({ ...formData, is_purified_standardized_fraction: true })}
                              className="text-ayush-forest focus:ring-ayush-forest"
                            />
                            <span>Yes (CDSCO GSR 918E)</span>
                          </label>
                          <label className="flex items-center space-x-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="phytopharm"
                              checked={!formData.is_purified_standardized_fraction}
                              onChange={() => setFormData({ ...formData, is_purified_standardized_fraction: false })}
                              className="text-ayush-forest focus:ring-ayush-forest"
                            />
                            <span>No</span>
                          </label>
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        Phytopharmaceuticals require full IND clinical trials (Phase I-III) under CDSCO/DCGI rather than State Ayush Licensing Authorities.
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                        Technical Difference / Extraction Parameter
                      </label>
                      <input
                        type="text"
                        value={technicalModificationDetail}
                        onChange={(e) => setTechnicalModificationDetail(e.target.value)}
                        placeholder="e.g. Hydro-alcoholic extraction at 45°C yielding 2x higher withanolide content"
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-medium bg-slate-50/50"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 6: INTENDED REGULATORY CLAIMS & JURISDICTION */}
              {currentStep === 6 && (
                <div className="space-y-4 animate-fadeIn">
                  <div className="space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                      Stage 06 of 06 · Regulatory Claims & Target Market
                    </span>
                    <h3 className="text-lg font-extrabold text-slate-900 font-display">
                      What therapeutic or commercial claims are intended for the product?
                    </h3>
                    <p className="text-xs text-slate-500">
                      Disease treatment claims trigger the Drugs & Cosmetics Act 1940. Wellness and food claims trigger FSSAI Ayurveda Aahara 2022 Regulations.
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                        Intended Regulatory Category
                      </label>
                      <select
                        value={formData.intended_use}
                        onChange={(e) => setFormData({ ...formData, intended_use: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-medium bg-slate-50/50"
                      >
                        <option value="therapeutic">Therapeutic Medicine (ASU Drug for Disease Diagnosis/Treatment)</option>
                        <option value="supplement">Ayurveda Aahara / Dietary Supplement (Food Safety Act / FSSAI)</option>
                        <option value="cosmetic">Saundarya Prasadana / Ayurvedic Cosmetic (Topical Beautification)</option>
                      </select>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-800">
                          Disease Treatment / Prevention Claims on Label?
                        </span>
                        <div className="flex items-center space-x-3 text-xs font-semibold">
                          <label className="flex items-center space-x-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="claims"
                              checked={formData.disease_treatment_claims}
                              onChange={() => setFormData({ ...formData, disease_treatment_claims: true })}
                              className="text-ayush-forest focus:ring-ayush-forest"
                            />
                            <span>Yes (Medicinal Claims)</span>
                          </label>
                          <label className="flex items-center space-x-1.5 cursor-pointer">
                            <input
                              type="radio"
                              name="claims"
                              checked={!formData.disease_treatment_claims}
                              onChange={() => setFormData({ ...formData, disease_treatment_claims: false })}
                              className="text-ayush-forest focus:ring-ayush-forest"
                            />
                            <span>No (Wellness / Food)</span>
                          </label>
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-500">
                        Under FSSAI Ayurveda Aahara regulations, products marketed as food supplements cannot make disease prevention or cure claims.
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-800 mb-1 uppercase tracking-wider">
                        Target Commercial Market
                      </label>
                      <div className="flex space-x-3 text-xs font-semibold">
                        <label className="flex items-center space-x-1.5 cursor-pointer">
                          <input
                            type="radio"
                            name="market"
                            checked={formData.target_market === 'IN'}
                            onChange={() => setFormData({ ...formData, target_market: 'IN' })}
                            className="text-ayush-forest focus:ring-ayush-forest"
                          />
                          <span>🇮🇳 Domestic India</span>
                        </label>
                        <label className="flex items-center space-x-1.5 cursor-pointer">
                          <input
                            type="radio"
                            name="market"
                            checked={formData.target_market === 'INT'}
                            onChange={() => setFormData({ ...formData, target_market: 'INT' })}
                            className="text-ayush-forest focus:ring-ayush-forest"
                          />
                          <span>🌍 International Export (USA / EU)</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* WIZARD NAVIGATION BUTTONS */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-100 text-xs font-bold">
                <button
                  type="button"
                  onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                  disabled={currentStep === 1}
                  className="px-3.5 py-2 rounded-xl text-slate-600 hover:text-slate-900 disabled:opacity-30 flex items-center space-x-1 transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>

                {currentStep < totalSteps ? (
                  <button
                    type="button"
                    onClick={() => setCurrentStep(currentStep + 1)}
                    className="px-5 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white rounded-xl flex items-center space-x-1.5 transition-all shadow-subtle"
                  >
                    <span>Next Stage</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => handleSubmit()}
                    disabled={loading || !formData.name.trim()}
                    className="px-6 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark disabled:bg-slate-300 text-white font-extrabold rounded-xl shadow-subtle flex items-center space-x-2 transition-all"
                  >
                    <span>{loading ? 'Evaluating Statutory Statutes...' : 'Generate Statutory Classification'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>

            </div>
          </div>

          {/* RIGHT 1 COLUMN: LIVE "CURRENT PRODUCT PROFILE" SUMMARY PANEL */}
          <div className="space-y-4">
            <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 bg-emerald-50 text-ayush-forest rounded-lg">
                    <FileText className="w-4 h-4" />
                  </div>
                  <h4 className="font-extrabold text-xs text-slate-900 uppercase tracking-wider">
                    Current Product Profile
                  </h4>
                </div>
                <span className="px-2 py-0.5 rounded text-[9px] font-black bg-emerald-100 text-emerald-900 font-mono">
                  LIVE
                </span>
              </div>

              <div className="space-y-2.5 text-[11px]">
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Product Name</span>
                  <p className="font-bold text-slate-900">{formData.name || 'Unnamed Formulation'}</p>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Dosage Form</span>
                  <p className="font-semibold text-slate-800">{dosageForm}</p>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Ayurvedic Treatise Basis</span>
                  <p className="font-semibold text-slate-800">
                    {formData.in_classical_text ? `📖 ${classicalTreatise}` : '🧪 Non-Classical Proprietary'}
                  </p>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Formulation Status</span>
                  <p className="font-semibold text-slate-800">
                    {formData.is_formulation_modified ? 'Modified Composition (Anubhuta)' : 'Exact Classical Recipe'}
                  </p>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Intended Regulatory Use</span>
                  <p className="font-bold text-emerald-900 capitalize">
                    {formData.intended_use} {formData.disease_treatment_claims ? '(Disease Treatment)' : '(General Wellness)'}
                  </p>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Target Jurisdiction</span>
                  <p className="font-semibold text-slate-800">
                    {formData.target_market === 'IN' ? '🇮🇳 India Domestic' : '🌍 International Export'}
                  </p>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 text-[10px] text-slate-500 flex items-center space-x-1.5 font-medium">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>Deterministic statutory evaluation under D&C Act 1940.</span>
              </div>
            </div>
          </div>

        </div>
      ) : (
        /* ========================================================= */
        /* COMPREHENSIVE DECISION-SUPPORT RESULTS DASHBOARD          */
        /* ========================================================= */
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-white rounded-3xl p-6 sm:p-9 border border-slate-200 shadow-card space-y-7">
            
            {/* 1. TOP RESULT HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-5">
              <div className="space-y-1.5">
                <div className="flex items-center space-x-2">
                  <span className={`text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-1 rounded-md border ${
                    result.category.includes('CLASSICAL')
                      ? 'bg-amber-50 text-amber-900 border-amber-300'
                      : result.category.includes('PROPRIETARY')
                      ? 'bg-emerald-50 text-emerald-900 border-emerald-300'
                      : result.category.includes('PHYTOPHARMACEUTICAL')
                      ? 'bg-blue-50 text-blue-900 border-blue-300'
                      : 'bg-purple-50 text-purple-900 border-purple-300'
                  }`}>
                    {result.category.includes('CLASSICAL')
                      ? '🟡 Classical Shastriya Medicine'
                      : result.category.includes('PROPRIETARY')
                      ? '🟢 Proprietary Ayurvedic Medicine (Rule 158B)'
                      : result.category.includes('PHYTOPHARMACEUTICAL')
                      ? '🔵 Phytopharmaceutical Drug (CDSCO)'
                      : '🟣 Ayurveda Aahara Food Supplement'}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400">
                    Preliminary Decision Verified
                  </span>
                </div>
                <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 font-display">
                  {result.category}
                </h3>
                <p className="text-xs text-slate-500 font-medium">
                  Product: <strong className="text-slate-800">{result.product_name}</strong> · Governed by <strong className="text-slate-800">{result.governing_act}</strong>
                </p>
              </div>

              <button
                onClick={handleReset}
                className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors self-start sm:self-auto shadow-subtle"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Re-Evaluate Formulation</span>
              </button>
            </div>

            {/* 2. STATUTORY ASSESSMENT RELIABILITY & EVIDENCE STATUS (FEATURE 1F) */}
            <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-950 flex items-center space-x-1.5 uppercase tracking-wider">
                  <ShieldCheck className="w-4 h-4 text-emerald-700" />
                  <span>Statutory Determination Reliability & Verification Basis</span>
                </span>
                <span className="text-xs font-mono font-extrabold text-emerald-900 bg-white px-2.5 py-0.5 rounded-lg border border-emerald-300 shadow-xs">
                  SUPPORTED · HIGH FIDELITY
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-[11px] text-emerald-950 pt-1 font-medium">
                <div className="flex items-center space-x-1.5 bg-white/70 p-2 rounded-lg border border-emerald-200/60">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase bg-emerald-100 text-emerald-800">Supported</span>
                  <span className="truncate">Form: {dosageForm}</span>
                </div>
                <div className="flex items-center space-x-1.5 bg-white/70 p-2 rounded-lg border border-emerald-200/60">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase bg-emerald-100 text-emerald-800">Supported</span>
                  <span className="truncate">Treatise: {formData.in_classical_text ? 'First Schedule' : 'Non-Classical'}</span>
                </div>
                <div className="flex items-center space-x-1.5 bg-white/70 p-2 rounded-lg border border-emerald-200/60">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase bg-emerald-100 text-emerald-800">Detected</span>
                  <span className="truncate">Statute: {result.governing_act.split('(')[0]}</span>
                </div>
                <div className="flex items-center space-x-1.5 bg-white/70 p-2 rounded-lg border border-emerald-200/60">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase bg-emerald-100 text-emerald-800">Detected</span>
                  <span className="truncate">Claims: {formData.disease_treatment_claims ? 'Medicinal' : 'Wellness'}</span>
                </div>
                <div className="flex items-center space-x-1.5 bg-white/70 p-2 rounded-lg border border-emerald-200/60">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase bg-emerald-100 text-emerald-800">Detected</span>
                  <span className="truncate">ABS Trigger: {result.abs_required ? 'SBB Intimation' : 'Exempted'}</span>
                </div>
                <div className="flex items-center space-x-1.5 bg-white/70 p-2 rounded-lg border border-emerald-200/60">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase bg-emerald-100 text-emerald-800">Verified</span>
                  <span className="truncate">Market: {formData.target_market === 'IN' ? 'India 🇮🇳' : 'Export 🌍'}</span>
                </div>
              </div>
            </div>

            {/* 3. "WHY DID WE REACH THIS?" EXPANDABLE DECISION FACTORS (FEATURE 2) */}
            <div className="space-y-3 rounded-2xl border border-slate-200 p-5 bg-slate-50/60">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 bg-emerald-100 text-ayush-forest rounded-lg">
                    <Compass className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
                      Why Did We Reach This Conclusion?
                    </h4>
                    <span className="text-[10px] text-slate-500 font-medium">
                      Structured decision factors grounded in authentic assessment inputs
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setShowDecisionFactors(!showDecisionFactors)}
                  className="inline-flex items-center space-x-1 text-xs font-bold text-ayush-forest hover:text-ayush-forestDark"
                >
                  <span>{showDecisionFactors ? 'Hide Decision Factors' : 'Show Decision Factors'}</span>
                  {showDecisionFactors ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
              </div>

              {showDecisionFactors && (
                <div className="space-y-2.5 pt-2 animate-fadeIn">
                  {/* Factor 1: Product Characteristics */}
                  <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold">
                      <span className="text-slate-800 flex items-center space-x-1.5">
                        <span className="w-4 h-4 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-[9px] font-mono">1</span>
                        <span>Product Characteristics</span>
                      </span>
                      <span className="text-slate-400 font-mono text-[10px]">Input Identity</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium pl-5">
                      Product <em>"{formData.name}"</em> presented in dosage form <strong>{dosageForm}</strong> with commercial target market <strong>{formData.target_market === 'IN' ? 'Domestic India' : 'International Export'}</strong>.
                    </p>
                  </div>

                  {/* Factor 2: Formulation Characteristics */}
                  <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold">
                      <span className="text-slate-800 flex items-center space-x-1.5">
                        <span className="w-4 h-4 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-[9px] font-mono">2</span>
                        <span>Formulation Characteristics</span>
                      </span>
                      <span className="text-slate-400 font-mono text-[10px]">Compositional Status</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium pl-5">
                      {formData.in_classical_text
                        ? `Grounding established in First Schedule classical treatise (${classicalTreatise}) for "${classicalFormulationName}". `
                        : 'Formulation is non-classical or proprietary polyherbal combination. '}
                      {formData.is_formulation_modified
                        ? 'Botanical proportions or extraction methods are altered from traditional recipes (Anubhuta). '
                        : 'Composition adheres strictly to unmodified classical treatise proportions. '}
                      {formData.has_novel_excipients
                        ? 'Novel delivery excipients or synthetic adjuvants are introduced.'
                        : 'Manufactured using traditional classical excipients.'}
                    </p>
                  </div>

                  {/* Factor 3: Traditional Knowledge & Prior Art Signal */}
                  <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold">
                      <span className="text-slate-800 flex items-center space-x-1.5">
                        <span className="w-4 h-4 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-[9px] font-mono">3</span>
                        <span>Traditional Knowledge / Prior Art Signal</span>
                      </span>
                      <span className="text-slate-400 font-mono text-[10px]">Section 3(p) / Prior Art</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium pl-5">
                      {formData.in_classical_text && !formData.is_formulation_modified
                        ? 'Formulation is documented verbatim in classical Ayurvedic texts; excluded from product patent monopolies under Section 3(p) of the Patents Act 1970 as traditional knowledge.'
                        : 'Formulation involves modified extraction or proprietary combination; to overcome Section 3(p) and Section 3(e) prior art bars, demonstrably non-obvious synergistic efficacy surpassing individual herbs is required.'}
                    </p>
                  </div>

                  {/* Factor 4: Relevant Regulatory Trigger */}
                  <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold">
                      <span className="text-slate-800 flex items-center space-x-1.5">
                        <span className="w-4 h-4 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-[9px] font-mono">4</span>
                        <span>Relevant Regulatory Trigger</span>
                      </span>
                      <span className="text-slate-400 font-mono text-[10px]">Statute Trigger</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium pl-5">
                      {formData.disease_treatment_claims
                        ? `Disease diagnosis/treatment claims trigger therapeutic regulation under Chapter IV-A of the Drugs & Cosmetics Act, 1940${formData.is_purified_standardized_fraction ? ' and CDSCO Phytopharmaceutical Drug Rules (GSR 918(E))' : ' and Rule 158B licensing'}.`
                        : 'Wellness/dietary supplement use without disease cure claims triggers FSSAI (Ayurveda Aahara) Regulations 2022.'}
                    </p>
                  </div>

                  {/* Factor 5: Applicable IP & ABS Considerations */}
                  <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold">
                      <span className="text-slate-800 flex items-center space-x-1.5">
                        <span className="w-4 h-4 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-[9px] font-mono">5</span>
                        <span>Applicable IP & ABS Considerations</span>
                      </span>
                      <span className="text-slate-400 font-mono text-[10px]">IP & Compliance</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium pl-5">
                      Patent standing: <strong>{result.patentability}</strong>. Distinctive brand name is protectable under Trade Marks Act 1999 (Nice Class 5). Sourcing Indian herbs triggers Biological Diversity Act (BDA 2023) Prior Intimation to the State Biodiversity Board (SBB).
                    </p>
                  </div>

                  {/* Factor 6: Final Preliminary Assessment */}
                  <div className="p-3 bg-emerald-50/70 rounded-xl border border-emerald-200 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold text-emerald-950">
                      <span className="flex items-center space-x-1.5">
                        <span className="w-4 h-4 rounded-full bg-ayush-forest text-white flex items-center justify-center text-[9px] font-mono">6</span>
                        <span>Final Preliminary Determination</span>
                      </span>
                      <span className="text-emerald-800 font-mono text-[10px]">Summary</span>
                    </div>
                    <p className="text-xs text-emerald-950 leading-relaxed font-semibold pl-5">
                      Classified as <strong>{result.category}</strong> under <strong>{result.governing_act}</strong> administered by <strong>{result.regulatory_authority}</strong>.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* 4. CORE REGULATORY ASSESSMENT & LICENSING (FEATURE 1B) */}
            <div className="space-y-3">
              <h4 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
                Regulatory Assessment & Manufacturing Standards
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-slate-400 font-bold block text-[10px] uppercase">Regulatory Authority</span>
                  <span className="font-bold text-slate-900 text-xs">{result.regulatory_authority}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-slate-400 font-bold block text-[10px] uppercase">Governing Statute</span>
                  <span className="font-bold text-slate-900 text-xs">{result.governing_act}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-slate-400 font-bold block text-[10px] uppercase">Manufacturing Standard</span>
                  <span className="font-bold text-slate-900 text-xs">Schedule T GMP Certification</span>
                </div>
              </div>
            </div>

            {/* 5. DOWNSTREAM IP STRATEGY STANDING (FEATURE 1C & FEATURE 5) */}
            <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2 text-amber-900 font-bold text-xs uppercase tracking-wider">
                  <Scale className="w-4 h-4 text-amber-700" />
                  <span>Intellectual Property Strategy Standing</span>
                </div>
                <span className={`text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-md border ${
                  result.patentability.includes('BARRED')
                    ? 'bg-rose-100 text-rose-900 border-rose-300'
                    : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                }`}>
                  {result.patentability.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-xs text-amber-950 leading-relaxed font-medium">
                {result.patent_rationale}
              </p>
              
              {/* Multi-modal IP Routes preview */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 text-[11px]">
                <div className="p-2.5 bg-white rounded-lg border border-amber-200 space-y-0.5">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Patent Pathway</span>
                  <span className="font-semibold text-slate-800">
                    {result.patentability.includes('BARRED') ? 'Barred under Sec 3(p)' : 'Requires Synergy Data (Sec 3(e))'}
                  </span>
                </div>
                <div className="p-2.5 bg-white rounded-lg border border-amber-200 space-y-0.5">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Brand Protection</span>
                  <span className="font-semibold text-slate-800">Trademark Form TM-A (Class 5)</span>
                </div>
                <div className="p-2.5 bg-white rounded-lg border border-amber-200 space-y-0.5">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block">Process Know-How</span>
                  <span className="font-semibold text-slate-800">Trade Secret NDA / SOP Control</span>
                </div>
              </div>

              {onNavigateView && (
                <div className="pt-2 border-t border-amber-200/60 flex justify-end">
                  <button
                    onClick={() => onNavigateView('ip_matrix')}
                    className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-amber-700 hover:bg-amber-800 text-white rounded-xl text-xs font-bold transition-all shadow-subtle"
                  >
                    <span>Explore Full IP Opportunity Matrix</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>

            {/* 6. BIOLOGICAL RESOURCE & ABS COMPLIANCE (FEATURE 1E & FEATURE 6) */}
            <div className="p-4 rounded-2xl bg-teal-50/70 border border-teal-200 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-teal-950 flex items-center space-x-1.5 uppercase text-[10px] tracking-wider">
                  <Leaf className="w-4 h-4 text-teal-700" />
                  <span>Access & Benefit Sharing (ABS) Standing · BDA 2023</span>
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-white text-teal-900 border border-teal-300">
                  {result.abs_required ? 'SBB PRIOR INTIMATION MANDATORY' : 'EXEMPTED'}
                </span>
              </div>
              <p className="text-teal-950 text-xs leading-relaxed font-medium">
                {result.abs_required
                  ? `Accessing Indian biological resources for commercial manufacture of "${result.product_name}" requires mandatory Prior Intimation to the State Biodiversity Board (SBB Form A) under Section 7 of the Biological Diversity Act, 2002 (as amended 2023). Sourcing origin: ${biologicalSourcingOrigin}.`
                  : 'Biological resources not detected or exempted under current formulation parameters.'}
              </p>
              {onNavigateView && (
                <div className="pt-1 flex justify-end">
                  <button
                    onClick={() => onNavigateView('abs_wizard')}
                    className="inline-flex items-center space-x-1 font-bold text-teal-800 hover:text-teal-950 text-xs"
                  >
                    <span>Open ABS Compliance Navigator</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>

            {/* 7. WHAT COULD ALTER THIS DETERMINATION? */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                What Could Alter This Statutory Determination?
              </span>
              <ul className="space-y-1 text-slate-700 list-disc list-inside leading-relaxed font-medium">
                {result.category.includes('CLASSICAL') ? (
                  <>
                    <li>If you alter the ingredient ratios or add modern excipients, the formulation transitions into a <strong>Proprietary Ayurvedic Medicine</strong> under Rule 158B.</li>
                    <li>If marketed strictly as a wellness food without therapeutic disease claims, it may qualify under <strong>FSSAI Ayurveda Aahara</strong>.</li>
                  </>
                ) : result.category.includes('PROPRIETARY') ? (
                  <>
                    <li>If you isolate a standardized fraction with $\ge 4$ marker compounds, the regulatory pathway shifts from State Ayush to <strong>CDSCO Phytopharmaceutical Drug</strong>.</li>
                    <li>If the formulation is proven strictly identical to a First Schedule text, it reverts to <strong>Classical Shastriya</strong> with safety trial exemptions.</li>
                  </>
                ) : (
                  <>
                    <li>If you introduce therapeutic disease treatment claims, the product is reclassified as an <strong>ASU Therapeutic Drug</strong> under the Drugs & Cosmetics Act.</li>
                  </>
                )}
              </ul>
            </div>

            {/* 8. GROUNDING STATUTORY CITATIONS (FEATURE 3 - WITH VIEW EVIDENCE DRAWER TRIGGER) */}
            {result.citations && result.citations.length > 0 && (
              <div className="space-y-3 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <BookOpen className="w-4 h-4 text-ayush-forest" />
                    <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                      Grounding Statutory Authority Citations ({result.citations.length})
                    </h4>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">
                    Click any source to inspect verbatim gazette quote
                  </span>
                </div>
                <div className="flex flex-wrap gap-2.5">
                  {result.citations.map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => onOpenCitation(c)}
                      className="inline-flex items-center space-x-2 px-3 py-2 bg-slate-50 hover:bg-emerald-50 text-slate-800 rounded-xl text-xs font-semibold border border-slate-200 transition-colors shadow-subtle group"
                    >
                      <BookOpen className="w-3.5 h-3.5 text-ayush-forest" />
                      <span>{c.section} ({c.source_title})</span>
                      <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-1.5 py-0.5 rounded">View Evidence</span>
                      <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-ayush-forest" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* 9. WHAT SHOULD I DO NEXT? — CONNECTED ACTION CENTER (FEATURE 9) */}
            <div className="space-y-3 pt-4 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-ayush-forest" />
                  <h4 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
                    What Should I Do Next? · Action Center
                  </h4>
                </div>
                {onOpenDossier && (
                  <button
                    onClick={onOpenDossier}
                    className="inline-flex items-center space-x-1.5 px-3 py-1 bg-ayush-forest text-white rounded-lg text-xs font-bold transition-all shadow-subtle"
                  >
                    <FileCheck className="w-3.5 h-3.5" />
                    <span>View Active Case Dossier</span>
                  </button>
                )}
              </div>

              {/* Action Buttons Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-1">
                {/* 1. Explore Evidence */}
                {result.citations && result.citations.length > 0 && (
                  <button
                    onClick={() => onOpenCitation(result.citations[0])}
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-ayush-forest bg-white hover:bg-emerald-50/50 text-left transition-all shadow-subtle flex items-center justify-between group"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="p-2 bg-emerald-50 text-ayush-forest rounded-lg group-hover:bg-ayush-forest group-hover:text-white transition-colors">
                        <BookOpen className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block font-bold text-xs text-slate-900">Explore Grounding Evidence</span>
                        <span className="text-[10px] text-slate-500">Inspect official Gazette text</span>
                      </div>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-ayush-forest" />
                  </button>
                )}

                {/* 2. View Knowledge Connections */}
                {onNavigateView && (
                  <button
                    onClick={() => onNavigateView('knowledge_graph')}
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-indigo-400 bg-white hover:bg-indigo-50/50 text-left transition-all shadow-subtle flex items-center justify-between group"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="p-2 bg-indigo-50 text-indigo-700 rounded-lg group-hover:bg-indigo-700 group-hover:text-white transition-colors">
                        <Network className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block font-bold text-xs text-slate-900">Knowledge Connections</span>
                        <span className="text-[10px] text-slate-500">Explore relational graph</span>
                      </div>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-700" />
                  </button>
                )}

                {/* 3. Review IP Strategy */}
                {onNavigateView && (
                  <button
                    onClick={() => onNavigateView('ip_matrix')}
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-amber-400 bg-white hover:bg-amber-50/50 text-left transition-all shadow-subtle flex items-center justify-between group"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="p-2 bg-amber-50 text-amber-800 rounded-lg group-hover:bg-amber-800 group-hover:text-white transition-colors">
                        <Scale className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block font-bold text-xs text-slate-900">Review IP Strategy</span>
                        <span className="text-[10px] text-slate-500">Patent, TM, & Trade Secret</span>
                      </div>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-amber-800" />
                  </button>
                )}

                {/* 4. Open ABS Navigator */}
                {onNavigateView && (
                  <button
                    onClick={() => onNavigateView('abs_wizard')}
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-teal-400 bg-white hover:bg-teal-50/50 text-left transition-all shadow-subtle flex items-center justify-between group"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="p-2 bg-teal-50 text-teal-800 rounded-lg group-hover:bg-teal-800 group-hover:text-white transition-colors">
                        <Leaf className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block font-bold text-xs text-slate-900">Open ABS Navigator</span>
                        <span className="text-[10px] text-slate-500">SBB Prior Intimation (BDA 2023)</span>
                      </div>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-teal-800" />
                  </button>
                )}

                {/* 5. Ask AyuRaksha Copilot */}
                <button
                  onClick={() => {
                    const query = `Explain the regulatory classification and patentability reasons for ${result.product_name} under ${result.governing_act}.`;
                    if (onAskCopilot) {
                      onAskCopilot(query);
                    } else if (onNavigateView) {
                      onNavigateView('chat');
                    }
                  }}
                  className="p-3.5 rounded-xl border border-slate-200 hover:border-slate-800 bg-white hover:bg-slate-50 text-left transition-all shadow-subtle flex items-center justify-between group"
                >
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 bg-slate-100 text-slate-800 rounded-lg group-hover:bg-slate-900 group-hover:text-white transition-colors">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="block font-bold text-xs text-slate-900">Ask AyuRaksha</span>
                      <span className="text-[10px] text-slate-500">Inquire with active product context</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-900" />
                </button>

                {/* 6. Save to Active Case Dossier */}
                {onOpenDossier && (
                  <button
                    onClick={onOpenDossier}
                    className="p-3.5 rounded-xl border border-slate-200 hover:border-ayush-forest bg-white hover:bg-emerald-50/50 text-left transition-all shadow-subtle flex items-center justify-between group"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="p-2 bg-emerald-50 text-ayush-forest rounded-lg group-hover:bg-ayush-forest group-hover:text-white transition-colors">
                        <FileCheck className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="block font-bold text-xs text-slate-900">Active Case Dossier</span>
                        <span className="text-[10px] text-slate-500">Export statutory compliance file</span>
                      </div>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-ayush-forest" />
                  </button>
                )}
              </div>
            </div>

            {/* 10. FOOTER BUTTONS */}
            <div className="pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
              <button
                onClick={handleReset}
                className="px-4 py-2 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-bold flex items-center space-x-1.5 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Adjust Parameters</span>
              </button>

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => {
                    const query = `What are the next statutory compliance and IP filing steps for ${result.product_name}?`;
                    if (onAskCopilot) {
                      onAskCopilot(query);
                    } else if (onNavigateView) {
                      onNavigateView('chat');
                    }
                  }}
                  className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition-all shadow-subtle flex items-center space-x-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
                  <span>Ask AyuRaksha About Next Steps</span>
                </button>
                {onOpenDossier && (
                  <button
                    onClick={onOpenDossier}
                    className="px-5 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white font-extrabold rounded-xl text-xs transition-all shadow-subtle flex items-center space-x-1.5"
                  >
                    <FileCheck className="w-3.5 h-3.5" />
                    <span>View Compliance Dossier</span>
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

