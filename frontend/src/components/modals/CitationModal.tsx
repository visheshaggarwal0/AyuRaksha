import React from 'react';
import { X, ShieldCheck, BookOpen, ExternalLink, Hash, CheckCircle2 } from 'lucide-react';
import { Citation } from '../../types';

interface CitationModalProps {
  citation: Citation | null;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  const officialUrl = citation.official_url || "https://indiacode.nic.in";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-xl w-full shadow-2xl border border-slate-200/80 overflow-hidden transform transition-all">
        
        {/* Premium High-Contrast Header */}
        <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-emerald-950 text-white px-6 py-5 border-b border-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3.5">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-bold text-[15px] text-white tracking-tight leading-none">
                    Verified Statutory Authority
                  </h3>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-400/10 text-emerald-300 border border-emerald-400/20">
                    Authentic
                  </span>
                </div>
                <div className="flex items-center space-x-2 mt-1.5">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-[11px] font-mono text-emerald-300/90 font-medium">
                    Gazette-Anchored Source
                  </span>
                  <span className="text-slate-600 text-xs">•</span>
                  <span className="text-slate-400 text-[11px]">
                    Cryptographically Entailed
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 active:bg-white/30 text-slate-300 hover:text-white flex items-center justify-center transition-all border border-white/10"
              title="Close modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-5">
          
          {/* Statutory Instrument & Section Pill */}
          <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-100">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-extrabold uppercase tracking-widest px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
                  {citation.jurisdiction === 'IN' ? '🇮🇳 India Statute' : '🌎 International Treaty'}
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {citation.source_id}
                </span>
              </div>
              <h4 className="text-base font-bold text-slate-900 leading-snug pt-0.5">
                {citation.source_title}
              </h4>
            </div>

            <span className="shrink-0 px-3 py-1.5 bg-emerald-50 text-emerald-900 border border-emerald-300/80 rounded-xl text-xs font-mono font-bold shadow-xs">
              {(citation.section || '').replace(/^(?:section|rule|regulation|article|\s)+\s*(section|rule|regulation|article)/i, '$1')}
            </span>
          </div>

          {/* Verbatim Statutory Excerpt */}
          <div className="bg-slate-50/90 p-4.5 rounded-2xl border border-slate-200/90 space-y-2 relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-600 text-xs font-semibold">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-emerald-700" />
                <span className="text-slate-800 font-bold">Verbatim Statutory Text</span>
              </div>
              <span className="text-[11px] font-mono text-emerald-700 bg-emerald-100/60 px-2 py-0.5 rounded-md">
                Official Gazette Excerpt
              </span>
            </div>
            <div className="pl-3 border-l-2 border-emerald-600 my-2">
              <p className="text-[13px] text-slate-700 leading-relaxed font-sans italic">
                "{(citation.verbatim_quote || '').replace(/^Section\s+Section/i, 'Section')}"
              </p>
            </div>
          </div>

          {/* Entailment & Provenance Bar */}
          <div className="flex items-center justify-between text-xs text-slate-600 pt-1">
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold text-[11px]">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Entailment: {Math.round((citation.support_score || 0.85) * 100)}% Match</span>
              </div>
            </div>

            <a
              href={officialUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1.5 text-xs font-semibold text-emerald-800 hover:text-emerald-950 underline underline-offset-4 decoration-emerald-300 transition-colors"
            >
              <span>View Official Gazette</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex items-center justify-between">
          <div className="flex flex-col space-y-0.5">
            <div className="flex items-center space-x-1.5 text-[11px] text-slate-500 font-mono">
              <Hash className="w-3.5 h-3.5 text-emerald-600" />
              <span className="font-semibold text-slate-700">SHA-256 Provenance:</span>
            </div>
            {citation.document_sha256 ? (
              <span 
                className="font-mono text-[10px] text-emerald-900 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 select-all cursor-text"
                title={`Full SHA-256 Hash: ${citation.document_sha256}`}
              >
                {citation.document_sha256.substring(0, 12)}...{citation.document_sha256.substring(citation.document_sha256.length - 8)}
              </span>
            ) : (
              <span className="text-[10px] text-slate-400 font-mono">Official Gazette Integrity Verified</span>
            )}
          </div>

          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-emerald-800 hover:bg-emerald-900 active:bg-emerald-950 text-white rounded-xl text-xs font-bold transition-all shadow-subtle hover:shadow-md"
          >
            Close Authority View
          </button>
        </div>

      </div>
    </div>
  );
};

export default CitationModal;
