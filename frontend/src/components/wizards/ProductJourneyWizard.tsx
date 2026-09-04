import React, { useState } from 'react';
import { Compass, ArrowRight, RotateCcw, BookOpen, ExternalLink, Scale } from 'lucide-react';
import { api } from '../../services/api';
import { ProductClassificationRequest, ProductClassificationResponse, Citation } from '../../types';
import { useTranslation } from '../../i18n/LanguageContext';

interface ProductJourneyWizardProps {
  onOpenCitation: (c: Citation) => void;
}

export const ProductJourneyWizard: React.FC<ProductJourneyWizardProps> = ({ onOpenCitation }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<ProductClassificationRequest>({
    name: 'DiabaRakshak Synergistic Extract',
    in_classical_text: true,
    is_formulation_modified: true,
    has_novel_excipients: false,
    is_purified_standardized_fraction: false,
    intended_use: 'therapeutic',
    disease_treatment_claims: true,
    has_biological_resources: true,
    target_market: 'IN',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProductClassificationResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await api.evaluateClassification(formData);
      setResult(res);
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
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-ayush-border shadow-card">
        <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-50 text-ayush-forest rounded-md text-xs font-bold border border-emerald-200 mb-2">
          <Compass className="w-3.5 h-3.5" />
          <span>{t('wizard.module1')}</span>
        </div>
        <h2 className="text-2xl font-bold text-ayush-navy">{t('wizard.title')}</h2>
        <p className="text-xs text-ayush-slate mt-1">
          {t('wizard.subtitle')}
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center justify-between">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="font-bold ml-4">✕</button>
        </div>
      )}

      {!result ? (
        /* Questionnaire Form */
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl p-6 sm:p-8 border border-ayush-border shadow-card space-y-6">
          {/* Product Name */}
          <div>
            <label className="block text-xs font-bold text-ayush-navy mb-1.5 uppercase tracking-wider">
              1. Formulation / Product Name
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest text-xs sm:text-sm font-medium"
              placeholder="e.g. AyurGlyco Anti-Diabetic Polyherbal"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-1">
            {/* Classical Text */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2">
              <label className="block text-xs font-bold text-ayush-navy">
                2. Is formulation in a Classical Text?
              </label>
              <p className="text-[11px] text-ayush-slate">Described in First Schedule books (e.g. Charaka Samhita, Sharangadhara).</p>
              <div className="flex space-x-4 pt-1">
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="classical"
                    checked={formData.in_classical_text}
                    onChange={() => setFormData({ ...formData, in_classical_text: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Yes (Shastriya)</span>
                </label>
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="classical"
                    checked={!formData.in_classical_text}
                    onChange={() => setFormData({ ...formData, in_classical_text: false })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>No (Novel recipe)</span>
                </label>
              </div>
            </div>

            {/* Modified Composition */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2">
              <label className="block text-xs font-bold text-ayush-navy">
                3. Is the Composition or Ratio Modified?
              </label>
              <p className="text-[11px] text-ayush-slate">Altered proportions, novel extracts, or synthetic additives.</p>
              <div className="flex space-x-4 pt-1">
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="modified"
                    checked={formData.is_formulation_modified}
                    onChange={() => setFormData({ ...formData, is_formulation_modified: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Yes (Modified)</span>
                </label>
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="modified"
                    checked={!formData.is_formulation_modified}
                    onChange={() => setFormData({ ...formData, is_formulation_modified: false })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>No (Exact traditional)</span>
                </label>
              </div>
            </div>

            {/* Intended Use */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2">
              <label className="block text-xs font-bold text-ayush-navy">
                4. Primary Product Category
              </label>
              <select
                value={formData.intended_use}
                onChange={(e) => setFormData({ ...formData, intended_use: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs font-medium bg-white"
              >
                <option value="therapeutic">Therapeutic Medicine (AYUSH Drug)</option>
                <option value="supplement">Dietary Supplement (Ayurveda Aahara)</option>
                <option value="cosmetic">Skin/Hair Care (Ayurvedic Cosmetic)</option>
                <option value="food">General Food / Beverage</option>
              </select>
            </div>

            {/* Disease Claims */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2">
              <label className="block text-xs font-bold text-ayush-navy">
                5. Therapeutic Treatment Claims?
              </label>
              <p className="text-[11px] text-ayush-slate">Does the label claim to treat/cure diabetes, hypertension, arthritis?</p>
              <div className="flex space-x-4 pt-1">
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="claims"
                    checked={formData.disease_treatment_claims}
                    onChange={() => setFormData({ ...formData, disease_treatment_claims: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Yes (Therapeutic Claims)</span>
                </label>
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="claims"
                    checked={!formData.disease_treatment_claims}
                    onChange={() => setFormData({ ...formData, disease_treatment_claims: false })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>No (General Wellness)</span>
                </label>
              </div>
            </div>

            {/* Phytopharmaceutical Drug (Standardized Fraction) */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2 md:col-span-2">
              <label className="block text-xs font-bold text-ayush-navy">
                6. Is this a Purified & Standardized Fraction (Phytopharmaceutical)?
              </label>
              <p className="text-[11px] text-ayush-slate">
                Defined under Gazette G.S.R. 918(E) & New Drugs Rules 2019: minimum 4 analytical/bioactive marker compounds with specific extraction protocols, regulated directly by CDSCO (DCGI) rather than State Ayush SLAs.
              </p>
              <div className="flex space-x-4 pt-1">
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="phytopharmaceutical"
                    checked={formData.is_purified_standardized_fraction}
                    onChange={() => setFormData({ ...formData, is_purified_standardized_fraction: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Yes (Standardized Bioactive Fraction / CDSCO Pathway)</span>
                </label>
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="phytopharmaceutical"
                    checked={!formData.is_purified_standardized_fraction}
                    onChange={() => setFormData({ ...formData, is_purified_standardized_fraction: false })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>No (Crude Extract / Classical Whole Herb Formulation)</span>
                </label>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white font-bold rounded-xl text-xs sm:text-sm shadow-subtle flex items-center space-x-2 transition-all"
            >
              <span>{loading ? 'Evaluating Statutes...' : 'Evaluate Classification'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      ) : (
        /* Results View */
        <div className="space-y-6 animate-fadeIn">
          {/* Classification Banner */}
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-ayush-border shadow-card space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-emerald-100 text-emerald-900 border border-emerald-300">
                  Assigned Category
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-ayush-forestDark mt-2">
                  {result.category}
                </h3>
              </div>
              <button
                onClick={handleReset}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors self-start sm:self-auto"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Re-Evaluate</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-slate-500 font-semibold block mb-1">Governing Statute</span>
                <span className="font-bold text-slate-900">{result.governing_act}</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-slate-500 font-semibold block mb-1">Licensing Authority</span>
                <span className="font-bold text-slate-900">{result.regulatory_authority}</span>
              </div>
            </div>

            {/* Patentability Analysis */}
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-2">
              <div className="flex items-center space-x-2 text-amber-900 font-bold text-xs">
                <Scale className="w-4 h-4 text-amber-700" />
                <span>Patents Act Section 3(p) & 3(e) Assessment</span>
              </div>
              <p className="text-xs text-amber-900 leading-relaxed">
                {result.patent_rationale}
              </p>
            </div>

            {/* Verified Citations */}
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Statutory Citations:
              </h4>
              <div className="flex flex-wrap gap-2">
                {result.citations.map((c, idx) => (
                  <button
                    key={idx}
                    onClick={() => onOpenCitation(c)}
                    className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-emerald-50 text-slate-800 rounded-lg text-xs font-semibold border border-slate-200 transition-colors"
                  >
                    <BookOpen className="w-3.5 h-3.5 text-ayush-forest" />
                    <span>{c.section} ({c.source_title})</span>
                    <ExternalLink className="w-3 h-3 text-slate-400" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
