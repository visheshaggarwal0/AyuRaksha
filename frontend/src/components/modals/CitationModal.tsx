import React from 'react';
import { Citation } from '../../types';
import { EvidenceInspector } from '../evidence/EvidenceInspector';

interface CitationModalProps {
  citation: Citation | null;
  allCitations?: Citation[];
  onSelectCitation?: (c: Citation) => void;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({
  citation,
  allCitations = [],
  onSelectCitation,
  onClose
}) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-lg w-full max-h-[90vh] shadow-modal border border-slate-200 overflow-hidden transform transition-all flex flex-col min-h-0">
        <EvidenceInspector
          citation={citation}
          allCitations={allCitations.length > 0 ? allCitations : [citation]}
          onSelectCitation={onSelectCitation}
          onClose={onClose}
        />
      </div>
    </div>
  );
};
