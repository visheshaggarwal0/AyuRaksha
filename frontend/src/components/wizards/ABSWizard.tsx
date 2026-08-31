import React, { useState } from 'react';
import { Leaf, CheckCircle2, ArrowRight, RotateCcw, BookOpen, ExternalLink } from 'lucide-react';
import { api } from '../../services/api';
import { ABSAssessmentRequest, ABSAssessmentResponse, Citation } from '../../types';

interface ABSWizardProps {
  onOpenCitation: (c: Citation) => void;
}

export const ABSWizard: React.FC<ABSWizardProps> = ({ onOpenCitation }) => {
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
  const [result, setResult] = useState<ABSAssessmentResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.evaluateABS(formData);
      setResult(res);
    } catch (err) {
      console.error('ABS evaluation error', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-ayush-border shadow-card">
        <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-50 text-ayush-forest rounded-md text-xs font-bold border border-emerald-200 mb-2">
          <Leaf className="w-3.5 h-3.5" />
          <span>Module 3 · Biological Diversity Act 2023 Navigator</span>
        </div>
        <h2 className="text-2xl font-bold text-ayush-navy">Access & Benefit Sharing (ABS) Compliance</h2>
        <p className="text-xs text-ayush-slate mt-1">
          Determine statutory obligations under the Biological Diversity Act, 2002 (as amended 2023) for State Biodiversity Board (SBB) Prior Intimation or National Biodiversity Authority (NBA) approval.
        </p>
      </div>

      {!result ? (
        /* Questionnaire Form */
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl p-6 sm:p-8 border border-ayush-border shadow-card space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Biological Resource */}
            <div>
              <label className="block text-xs font-bold text-ayush-navy mb-1.5 uppercase tracking-wider">
                1. Biological Resource / Herb Name
              </label>
              <input
                type="text"
                required
                value={formData.biological_resource}
                onChange={(e) => setFormData({ ...formData, biological_resource: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest text-xs sm:text-sm font-medium"
                placeholder="e.g. Ashwagandha, Himalayan Kutki"
              />
            </div>

            {/* Sourced From State */}
            <div>
              <label className="block text-xs font-bold text-ayush-navy mb-1.5 uppercase tracking-wider">
                2. Indian State of Origin / Sourcing
              </label>
              <input
                type="text"
                required
                value={formData.sourced_from_state}
                onChange={(e) => setFormData({ ...formData, sourced_from_state: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest text-xs sm:text-sm font-medium"
                placeholder="e.g. Himachal Pradesh, Kerala, MP"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-1">
            {/* Entity Nationality */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2">
              <label className="block text-xs font-bold text-ayush-navy">
                3. Company / Entity Incorporation
              </label>
              <p className="text-[11px] text-ayush-slate">Does the entity have any foreign shareholding or NRI directors?</p>
              <div className="flex space-x-4 pt-1">
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="entity_type"
                    checked={formData.is_indian_entity}
                    onChange={() => setFormData({ ...formData, is_indian_entity: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>100% Indian Entity</span>
                </label>
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="entity_type"
                    checked={!formData.is_indian_entity}
                    onChange={() => setFormData({ ...formData, is_indian_entity: false })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Foreign / NRI Entity</span>
                </label>
              </div>
            </div>

            {/* Commercial Purpose */}
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-2">
              <label className="block text-xs font-bold text-ayush-navy">
                4. Commercial Utilization
              </label>
              <p className="text-[11px] text-ayush-slate">Is the biological resource being used for commercial sales?</p>
              <div className="flex space-x-4 pt-1">
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
                  <input
                    type="radio"
                    name="commercial"
                    checked={formData.is_commercial_utilization}
                    onChange={() => setFormData({ ...formData, is_commercial_utilization: true })}
                    className="text-ayush-forest focus:ring-ayush-forest"
                  />
                  <span>Commercial Sale</span>
                </label>
                <label className="flex items-center space-x-2 text-xs font-medium cursor-pointer">
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
          </div>

          <div className="pt-4 border-t border-slate-200 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white font-bold rounded-xl text-xs sm:text-sm shadow-subtle flex items-center space-x-2 transition-all"
            >
              <span>{loading ? 'Evaluating ABS Obligations...' : 'Run ABS Assessment'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      ) : (
        /* Results View */
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-ayush-border shadow-card space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
              <div>
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded border ${
                  result.risk_level.includes('HIGH') ? 'bg-red-100 text-red-900 border-red-300' : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                }`}>
                  ABS Risk: {result.risk_level}
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-ayush-navy mt-2">
                  {result.approval_type}
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
                <span className="text-slate-500 font-semibold block mb-1">Competent Authority</span>
                <span className="font-bold text-slate-900">{result.applicable_authority}</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-slate-500 font-semibold block mb-1">Benefit Sharing Estimation</span>
                <span className="font-bold text-slate-900">{result.benefit_sharing_applicable ? 'Applicable' : 'Not triggered'}</span>
              </div>
            </div>

            {/* Compliance Steps */}
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Mandatory Compliance Roadmap:
              </h4>
              <div className="space-y-2">
                {result.mandatory_next_steps.map((step, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-xs text-slate-800">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Verified Citations */}
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Statutory Citations:
              </h4>
              <div className="flex flex-wrap gap-2">
                {result.statutory_citations.map((c, idx) => (
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
