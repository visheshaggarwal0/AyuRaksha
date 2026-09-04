import React, { useState } from 'react';
import {
  Sparkles,
  Compass,
  ArrowRight,
  ArrowLeft,
  Edit2,
  FileText,
  ShieldCheck,
  Scale,
  RotateCcw,
  BookOpen,
  X,
  Check
} from 'lucide-react';
import { InnovationProfile, Jurisdiction } from '../../types';

interface InnovationDiscoveryWorkflowProps {
  initialProductName?: string;
  jurisdiction: Jurisdiction;
  onComplete: (profile: InnovationProfile) => void;
  onNavigateView?: (view: 'classification' | 'ip_matrix' | 'abs_wizard' | 'chat') => void;
  onAskCopilot?: (query: string) => void;
}

export const InnovationDiscoveryWorkflow: React.FC<InnovationDiscoveryWorkflowProps> = ({
  initialProductName = '',
  jurisdiction,
  onComplete,
  onNavigateView,
  onAskCopilot
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 8;

  const [profile, setProfile] = useState<InnovationProfile>({
    productName: initialProductName || 'Modified Polyherbal Extract',
    baseline: 'Classical Ayurvedic formulation (First Schedule text)',
    differenceType: 'Extraction & Processing Parameter',
    userStatedDifference: 'Subcritical hydro-alcoholic extraction at lower temperature',
    technicalFeature: 'Standardized active biomarker fraction with altered solvent ratio',
    technicalEffect: 'Improved stability and 2.5x higher bioavailability in-vitro',
    evidenceTypes: ['Experimental analytical HPLC chromatogram', 'Comparative stability assay'],
    evidenceDetails: 'Tested over 6 months showing negligible biomarker degradation',
    isTraditionalKnowledge: 'PARTIALLY',
    classicalSourceText: 'Sahasrayogam / Charaka Samhita reference',
    commercialIntent: 'Sell in India and explore US FDA dietary supplement export',
    targetJurisdiction: jurisdiction
  });

  const [freeText, setFreeText] = useState('');
  const [isEditing, setIsEditing] = useState<keyof InnovationProfile | null>(null);
  const [editValue, setEditValue] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  // Stage Definitions
  const stages = [
    {
      step: 1,
      name: 'Product Definition',
      title: 'What formulation, extract, or composition did you develop?',
      whyWeAsk: 'Establishing the core identity and ingredients defines the statutory boundaries under the Drugs & Cosmetics Act 1940 and First Schedule texts.',
      options: [
        'Modified Polyherbal Formulation (e.g. Ashwagandha + Guduchi)',
        'Standardized Botanical Extract / Enriched Fraction',
        'Novel Dosage Form (Nano-emulsion, Tablet, Transdermal)',
        'Classical Ayurvedic Medicine with Modern Excipients'
      ],
      field: 'productName' as keyof InnovationProfile
    },
    {
      step: 2,
      name: 'Baseline Reference',
      title: 'What known formulation, classical text, or prior process is this based on?',
      whyWeAsk: 'Under Section 3(p) of the Patents Act, 1970, an innovation must be evaluated against known classical Ayurvedic knowledge (TKDL / 54 authoritative texts).',
      options: [
        'Classical Ayurvedic formulation from 1st Schedule text',
        'Existing commercial Ayurvedic product',
        'Known conventional extraction method',
        'Completely non-classical novel synthetic-herbal combination',
        'Traditional tribal / folklore remedy'
      ],
      field: 'baseline' as keyof InnovationProfile
    },
    {
      step: 3,
      name: 'Technical Difference',
      title: 'What specific difference did you introduce compared with the baseline?',
      whyWeAsk: 'To overcome Section 3(p) and Section 3(e) exclusions, the law requires demonstrating an inventive technical modification rather than a mere aggregation of known herbs.',
      options: [
        'Altered extraction solvent, temperature, or pressure',
        'Specific synergistic ingredient ratio (e.g. 3:1:0.5)',
        'Purification / standardization of key phytochemical biomarkers',
        'Addition of a novel bioavailability enhancer / lipid carrier',
        'Elimination of a toxic / unstable classical ingredient'
      ],
      field: 'userStatedDifference' as keyof InnovationProfile
    },
    {
      step: 4,
      name: 'Technical Feature',
      title: 'Which technical feature or processing parameter was altered?',
      whyWeAsk: 'Patent claims require clear, structured technical features that are reproducible and non-obvious to a person skilled in the art.',
      options: [
        'Standardized biomarker concentration (>5% withanolides / curcuminoids)',
        'Controlled particle size reduction (Micronization / Nano-suspension)',
        'Multi-stage aqueous-ethanolic extraction sequence',
        'Targeted pH-stabilized aqueous formulation'
      ],
      field: 'technicalFeature' as keyof InnovationProfile
    },
    {
      step: 5,
      name: 'Reported Technical Effect',
      title: 'What measurable improvement or effect resulted from this change?',
      whyWeAsk: 'Under Indian Patent Office Guidelines (2012), patenting herbal formulations requires proving a non-obvious, measurable technical effect (synergism, enhanced stability, or reduced dose).',
      options: [
        'Measurable increase in bioavailability / absorption (e.g. 2x to 3x)',
        'Enhanced room-temperature shelf-life (>24 months without degradation)',
        'Demonstrated synergistic efficacy index (Combination Index < 0.8)',
        'Significant reduction in required therapeutic dosage / side-effects',
        'Higher extraction yield of active phytochemical markers'
      ],
      field: 'technicalEffect' as keyof InnovationProfile
    },
    {
      step: 6,
      name: 'Validation Evidence',
      title: 'What experimental validation or analytical evidence currently exists?',
      whyWeAsk: 'Claims of synergism or inventive step must be substantiated by empirical comparative data to satisfy patent examiners and licensing authorities.',
      options: [
        'Analytical fingerprint data (HPLC / HPTLC / LC-MS chromatograms)',
        'Comparative stability testing data (Accelerated / Real-time)',
        'In-vitro / In-vivo comparative efficacy assays',
        'Pilot clinical trial / human observational data',
        'No empirical comparative data generated yet (Concept Stage)'
      ],
      field: 'evidenceDetails' as keyof InnovationProfile
    },
    {
      step: 7,
      name: 'Traditional Knowledge Scope',
      title: 'Is the therapeutic indication or herb combination described in classical texts?',
      whyWeAsk: 'If the exact disease indication is already documented in classical texts for that herb, patentability is barred under Section 3(p), though licensing as Classical ASU is expedited.',
      options: [
        'Yes — Directly cited in First Schedule texts for the same indication',
        'Partially — Uses classical herbs but for a modern indication or new delivery',
        'No — Entirely new indication not described in any traditional treatises',
        'Unsure — Classical text prior-art verification required'
      ],
      field: 'classicalSourceText' as keyof InnovationProfile
    },
    {
      step: 8,
      name: 'Commercial Intent & Jurisdiction',
      title: 'What is your intended commercial and regulatory deployment pathway?',
      whyWeAsk: 'Commercial intent dictates whether State Ayush licensing (Rule 158B), Biological Diversity Act (BDA 2023) ABS approvals, or US FDA / EU export frameworks apply.',
      options: [
        'Commercial manufacturing and sale in India (Domestic Ayush License)',
        'Export to USA / EU (US FDA DSHEA / EU THMPD Compliance)',
        'Patent filing first, then technology licensing to pharmaceutical MSMEs',
        'Academic / R&D validation before commercialization'
      ],
      field: 'commercialIntent' as keyof InnovationProfile
    }
  ];

  const currentStageData = stages[currentStep - 1];

  const handleSelectOption = (opt: string) => {
    const field = currentStageData.field;
    setProfile((prev) => ({
      ...prev,
      [field]: opt
    }));
    setFreeText('');
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      finishWorkflow({ ...profile, [field]: opt });
    }
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!freeText.trim()) return;
    const field = currentStageData.field;
    const updated = {
      ...profile,
      [field]: freeText.trim()
    };
    setProfile(updated);
    setFreeText('');
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      finishWorkflow(updated);
    }
  };

  const finishWorkflow = (finalProfile: InnovationProfile) => {
    const completed = {
      ...finalProfile,
      completedAt: new Date().toISOString()
    };
    setProfile(completed);
    setIsComplete(true);
    onComplete(completed);
  };

  const startEditField = (field: keyof InnovationProfile) => {
    setIsEditing(field);
    const val = profile[field];
    setEditValue(typeof val === 'string' ? val : '');
  };

  const handleSaveEdit = () => {
    if (!isEditing) return;
    setProfile((prev) => ({
      ...prev,
      [isEditing]: editValue
    }));
    setIsEditing(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn select-text">
      
      {/* 1. HEADER BANNER */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-card space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-ayush-forest rounded-full text-xs font-bold border border-emerald-200">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Interactive Innovation Discovery Facilitator · Step {currentStep} of {totalSteps}</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-display tracking-tight">
          Ayurvedic Innovation & Technical Baseline Assessment
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-3xl">
          Progressively articulate what is technically distinct about your Ayurvedic formulation or process before statutory patentability and regulatory licensing evaluations.
        </p>

        {/* Multi-step Progress Bar */}
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5 pt-4 mt-4 border-t border-slate-100 text-center">
          {stages.map((s) => (
            <div
              key={s.step}
              onClick={() => setCurrentStep(s.step)}
              className="flex flex-col items-center cursor-pointer group"
            >
              <span
                className={`w-6 h-6 rounded-full text-[10px] font-black flex items-center justify-center mb-1 transition-all ${
                  s.step === currentStep
                    ? 'bg-ayush-forest text-white ring-2 ring-emerald-300 shadow-subtle'
                    : s.step < currentStep
                    ? 'bg-emerald-100 text-emerald-900 font-bold'
                    : 'bg-slate-100 text-slate-400 group-hover:bg-slate-200'
                }`}
              >
                {s.step < currentStep ? '✓' : s.step}
              </span>
              <span className={`text-[10px] font-bold truncate max-w-full ${s.step === currentStep ? 'text-slate-900' : 'text-slate-400'}`}>
                {s.name.split(' ')[0]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {!isComplete ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          {/* 2. QUESTION & OPTION INTERFACE (LEFT 2 COLUMNS) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-card space-y-5">
              
              {/* Question Heading */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                  Stage {currentStageData.step} · {currentStageData.name}
                </span>
                <h3 className="text-base sm:text-lg font-extrabold text-slate-900 font-display">
                  {currentStageData.title}
                </h3>
              </div>

              {/* Curated Interactive Options */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold text-slate-500 block uppercase tracking-wider">
                  Select Applicable Baseline:
                </span>
                <div className="grid grid-cols-1 gap-2">
                  {currentStageData.options.map((opt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSelectOption(opt)}
                      className="p-3.5 rounded-xl border border-slate-200 hover:border-ayush-forest bg-white hover:bg-emerald-50/60 text-xs font-semibold text-slate-800 transition-all text-left flex items-center justify-between group shadow-subtle"
                    >
                      <span>{opt}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-ayush-forest shrink-0 ml-2" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Free-Text Entry */}
              <form onSubmit={handleCustomSubmit} className="pt-3 border-t border-slate-100 space-y-2">
                <span className="text-[11px] font-bold text-slate-500 block uppercase tracking-wider">
                  Or Describe in Your Own Words:
                </span>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={freeText}
                    onChange={(e) => setFreeText(e.target.value)}
                    placeholder="Enter specific formulation details, parameters, or data..."
                    className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest"
                  />
                  <button
                    type="submit"
                    disabled={!freeText.trim()}
                    className="px-4 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark disabled:bg-slate-200 text-white font-bold rounded-xl text-xs transition-all shadow-subtle shrink-0"
                  >
                    Confirm
                  </button>
                </div>
              </form>

              {/* "Why We Ask This" Box */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <div className="flex items-center space-x-1.5 text-ayush-forest">
                  <BookOpen className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-black uppercase tracking-wider">Why We Ask This</span>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed font-medium">
                  {currentStageData.whyWeAsk}
                </p>
              </div>

              {/* Navigation Back / Next */}
              <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs font-bold">
                <button
                  onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                  disabled={currentStep === 1}
                  className="px-3 py-2 rounded-xl text-slate-600 hover:text-slate-900 disabled:opacity-30 flex items-center space-x-1 transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <button
                  onClick={() => {
                    if (currentStep < totalSteps) {
                      setCurrentStep(currentStep + 1);
                    } else {
                      finishWorkflow(profile);
                    }
                  }}
                  className="px-4 py-2 rounded-xl bg-ayush-forest hover:bg-ayush-forestDark text-white flex items-center space-x-1.5 transition-all shadow-subtle"
                >
                  <span>{currentStep === totalSteps ? 'Compile Innovation Profile' : 'Next Question'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

            </div>
          </div>

          {/* 3. LIVE INNOVATION PROFILE SUMMARY PANEL (RIGHT 1 COLUMN) */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-card space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 bg-emerald-50 text-ayush-forest rounded-lg">
                    <FileText className="w-4 h-4" />
                  </div>
                  <h4 className="font-extrabold text-xs text-slate-900 uppercase tracking-wider">
                    Live Innovation Profile
                  </h4>
                </div>
                <span className="px-2 py-0.5 rounded text-[9px] font-black bg-emerald-100 text-emerald-900 font-mono">
                  ACTIVE CASE
                </span>
              </div>

              <div className="space-y-3 text-[11px]">
                
                {/* Field 1: Product */}
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase">
                    <span>Product Name</span>
                    <button
                      onClick={() => startEditField('productName')}
                      className="text-ayush-forest hover:underline flex items-center space-x-0.5"
                    >
                      <Edit2 className="w-2.5 h-2.5" />
                      <span>Edit</span>
                    </button>
                  </div>
                  <p className="font-bold text-slate-900">{profile.productName}</p>
                </div>

                {/* Field 2: Baseline */}
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase">
                    <span>Baseline Reference</span>
                    <button
                      onClick={() => startEditField('baseline')}
                      className="text-ayush-forest hover:underline flex items-center space-x-0.5"
                    >
                      <Edit2 className="w-2.5 h-2.5" />
                      <span>Edit</span>
                    </button>
                  </div>
                  <p className="font-semibold text-slate-800">{profile.baseline}</p>
                </div>

                {/* Field 3: Difference */}
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase">
                    <span>User-Stated Difference</span>
                    <button
                      onClick={() => startEditField('userStatedDifference')}
                      className="text-ayush-forest hover:underline flex items-center space-x-0.5"
                    >
                      <Edit2 className="w-2.5 h-2.5" />
                      <span>Edit</span>
                    </button>
                  </div>
                  <p className="font-semibold text-slate-800">{profile.userStatedDifference}</p>
                </div>

                {/* Field 4: Technical Feature */}
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase">
                    <span>Technical Feature</span>
                    <button
                      onClick={() => startEditField('technicalFeature')}
                      className="text-ayush-forest hover:underline flex items-center space-x-0.5"
                    >
                      <Edit2 className="w-2.5 h-2.5" />
                      <span>Edit</span>
                    </button>
                  </div>
                  <p className="font-semibold text-slate-800">{profile.technicalFeature}</p>
                </div>

                {/* Field 5: Technical Effect */}
                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase">
                    <span>Reported Technical Effect</span>
                    <button
                      onClick={() => startEditField('technicalEffect')}
                      className="text-ayush-forest hover:underline flex items-center space-x-0.5"
                    >
                      <Edit2 className="w-2.5 h-2.5" />
                      <span>Edit</span>
                    </button>
                  </div>
                  <p className="font-semibold text-emerald-900">{profile.technicalEffect}</p>
                </div>

              </div>

              <div className="pt-2 border-t border-slate-100 text-[10px] text-slate-500 flex items-center space-x-1 font-medium">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>Distinguishing user claims from statutory prior art.</span>
              </div>
            </div>
          </div>

        </div>
      ) : (
        /* 4. FINAL STRUCTURED INNOVATION PROFILE SUMMARY VIEW */
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-card space-y-6 animate-fadeIn">
          
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4">
            <div>
              <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                Structured Profile Compiled
              </span>
              <h3 className="text-xl font-extrabold text-slate-900 font-display">
                Innovation & IP Readiness Profile · {profile.productName}
              </h3>
            </div>
            <button
              onClick={() => setIsComplete(false)}
              className="px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold flex items-center space-x-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Modify Details</span>
            </button>
          </div>

          {/* User-Stated vs System Evaluation Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* User-Stated Profile */}
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-slate-200 text-slate-800">
                User-Stated Technical Profile
              </span>
              <div className="space-y-2.5 text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Baseline Comparison</span>
                  <p className="font-bold text-slate-800">{profile.baseline}</p>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">User-Reported Difference</span>
                  <p className="font-semibold text-slate-800">{profile.userStatedDifference}</p>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Technical Feature</span>
                  <p className="font-semibold text-slate-800">{profile.technicalFeature}</p>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Reported Technical Effect</span>
                  <p className="font-bold text-emerald-800">{profile.technicalEffect}</p>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Available Evidence</span>
                  <p className="text-slate-700">{profile.evidenceDetails}</p>
                </div>
              </div>
            </div>

            {/* Potential IP & Statutory Posture */}
            <div className="p-5 rounded-2xl bg-emerald-950 text-white space-y-3">
              <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-emerald-800 text-emerald-200 border border-emerald-700">
                Potential IP & Regulatory Alignment
              </span>
              <div className="space-y-2.5 text-xs text-emerald-100">
                <div>
                  <span className="text-emerald-400 block text-[10px] uppercase font-bold">Patent (Section 3(p) Screening)</span>
                  <p className="font-semibold text-white">
                    {profile.isTraditionalKnowledge === 'YES'
                      ? 'Barred as pure classical formulation unless independent synergistic novelty is proven.'
                      : 'Potentially eligible for composition/process patent if comparative stability/synergism is substantiated.'}
                  </p>
                </div>
                <div>
                  <span className="text-emerald-400 block text-[10px] uppercase font-bold">Regulatory Drug Licensing</span>
                  <p className="text-slate-200">
                    Qualifies for Proprietary Ayurvedic Medicine under Rule 158B of Drugs & Cosmetics Rules, 1945.
                  </p>
                </div>
                <div>
                  <span className="text-emerald-400 block text-[10px] uppercase font-bold">Biological Diversity & ABS</span>
                  <p className="text-slate-200">
                    Sourcing Indian biological resources requires prior intimation to State Biodiversity Board (SBB).
                  </p>
                </div>
                <div>
                  <span className="text-emerald-400 block text-[10px] uppercase font-bold">Trade Secret Potential</span>
                  <p className="text-slate-200">
                    Proprietary extraction temperature and solvent ratios can be maintained as protected trade secrets.
                  </p>
                </div>
              </div>
            </div>

          </div>

          {/* Action Pathways */}
          <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {onNavigateView && (
                <>
                  <button
                    onClick={() => onNavigateView('classification')}
                    className="px-4 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white font-bold rounded-xl text-xs transition-all shadow-subtle flex items-center space-x-1.5"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    <span>Evaluate Regulatory Classification (Module 1)</span>
                  </button>
                  <button
                    onClick={() => onNavigateView('ip_matrix')}
                    className="px-4 py-2.5 bg-white hover:bg-emerald-50 text-slate-800 border border-slate-200 font-bold rounded-xl text-xs transition-all shadow-subtle flex items-center space-x-1.5"
                  >
                    <Scale className="w-3.5 h-3.5 text-ayush-forest" />
                    <span>View IP Opportunity Matrix</span>
                  </button>
                </>
              )}
            </div>

            {onAskCopilot && (
              <button
                onClick={() =>
                  onAskCopilot(
                    `Can I patent my innovation "${profile.productName}" which features "${profile.userStatedDifference}" achieving "${profile.technicalEffect}"?`
                  )
                }
                className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition-all shadow-subtle flex items-center space-x-1.5"
              >
                <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
                <span>Ask Ayuरक्षा Specific Patent Analysis</span>
              </button>
            )}
          </div>

        </div>
      )}

      {/* 5. INLINE FIELD EDIT DIALOG */}
      {isEditing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-md w-full p-5 border border-slate-200 shadow-modal space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h4 className="font-extrabold text-sm text-slate-900 font-display">
                Edit Innovation Profile Field
              </h4>
              <button onClick={() => setIsEditing(null)} className="p-1 text-slate-400 hover:text-slate-800 rounded-lg">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                {String(isEditing)}
              </span>
              <textarea
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                rows={3}
                className="w-full p-3 rounded-xl border border-slate-200 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest"
              />
            </div>
            <div className="flex items-center justify-end space-x-2 pt-2">
              <button
                onClick={() => setIsEditing(null)}
                className="px-3 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 rounded-xl bg-ayush-forest hover:bg-ayush-forestDark text-white text-xs font-bold flex items-center space-x-1 shadow-subtle"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Save Correction</span>
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
