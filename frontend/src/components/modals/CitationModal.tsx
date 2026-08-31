import { X, ShieldCheck, BookOpen, AlertCircle } from 'lucide-react';
import { Citation } from '../../types';

interface CitationModalProps {
  citation: Citation | null;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl max-w-xl w-full shadow-modal border border-ayush-border overflow-hidden">
        {/* Modal Header */}
        <div className="bg-ayush-forestDark text-white p-5 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-emerald-300" />
            <h3 className="font-bold text-base">Verified Statutory Authority</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 transition-colors text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-ayush-border pb-3">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-ayush-forest">
                {citation.jurisdiction === 'IN' ? '🇮🇳 India Law' : '🌎 International Treaty'}
              </span>
              <h4 className="text-base font-bold text-ayush-navy">{citation.source_title}</h4>
            </div>
            <span className="px-2.5 py-1 bg-emerald-100 text-emerald-900 border border-emerald-300 rounded-md text-xs font-bold">
              {citation.section}
            </span>
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <div className="flex items-center space-x-2 text-slate-500 text-xs font-bold mb-2">
              <BookOpen className="w-4 h-4 text-ayush-forest" />
              <span>Verbatim Statutory Text</span>
            </div>
            <p className="text-xs italic text-slate-800 leading-relaxed">
              "{citation.verbatim_quote}"
            </p>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
            <div className="flex items-center space-x-1.5">
              <AlertCircle className="w-4 h-4 text-emerald-700" />
              <span>Entailment Score: <strong>{(citation.support_score * 100).toFixed(0)}% Match</strong></span>
            </div>
            <span className="font-mono text-[10px] bg-slate-100 px-2 py-0.5 rounded text-slate-700 border border-slate-200">
              {citation.source_id}
            </span>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 p-4 border-t border-ayush-border flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-ayush-forest hover:bg-ayush-forestDark text-white rounded-xl text-xs font-bold transition-all shadow-subtle"
          >
            Close Authority View
          </button>
        </div>
      </div>
    </div>
  );
};
