import React from 'react';
import { CheckCircle2, ChevronRight } from 'lucide-react';
import { Citation } from '../../types';

interface StatutoryMarkdownRendererProps {
  content: string;
  citations?: Citation[];
  activeCitation?: Citation | null;
  onCitationClick?: (citation: Citation) => void;
}

export const StatutoryMarkdownRenderer: React.FC<StatutoryMarkdownRendererProps> = ({
  content,
  citations = [],
  activeCitation = null,
  onCitationClick
}) => {
  if (!content) return null;

  // Render text with bold, italic, and interactive citation pills
  const renderInline = (text: string): React.ReactNode[] => {
    // Regex matches [N] or [N(X)] citation tags, **bold**, and *italic*
    const tokenRegex = /(\[\d+(?:\([A-Za-z0-9]+\))?\])|(\*\*[^*]+\*\*)|(\*[^*]+\*)/g;
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = tokenRegex.exec(text)) !== null) {
      // Preceding normal text
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }

      const [, citationMatch, boldMatch, italicMatch] = match;

      if (citationMatch) {
        // Parse citation index, e.g. "[2]" -> 2, "[1(I)]" -> 1
        const numMatch = citationMatch.match(/\d+/);
        const citIdx = numMatch ? parseInt(numMatch[0], 10) - 1 : -1;
        const matchingCitation = citations[citIdx] || (citations.length > 0 ? citations[0] : null);
        const isCurrentlyActive = matchingCitation && activeCitation &&
          (matchingCitation.source_id === activeCitation.source_id && matchingCitation.section === activeCitation.section);

        parts.push(
          <button
            key={`cit-${match.index}`}
            type="button"
            onClick={() => {
              if (matchingCitation && onCitationClick) {
                onCitationClick(matchingCitation);
              }
            }}
            className={`inline-flex items-center px-1.5 py-0.2 mx-1 text-[11px] font-mono font-bold rounded transition-all align-baseline cursor-pointer ${
              isCurrentlyActive
                ? 'bg-ayush-forest text-white shadow-sm ring-2 ring-emerald-400 scale-105'
                : 'text-emerald-800 bg-emerald-50 hover:bg-emerald-100 active:bg-emerald-200 border border-emerald-200'
            }`}
            title={matchingCitation ? `View Statutory Source: ${matchingCitation.source_title} (${matchingCitation.section})` : 'Statutory Reference'}
          >
            {citationMatch}
          </button>
        );
      } else if (boldMatch) {
        const inner = boldMatch.slice(2, -2);
        parts.push(
          <strong key={`b-${match.index}`} className="font-semibold text-slate-900">
            {inner}
          </strong>
        );
      } else if (italicMatch) {
        const inner = italicMatch.slice(1, -1);
        parts.push(
          <em key={`i-${match.index}`} className="italic text-slate-700">
            {inner}
          </em>
        );
      }

      lastIndex = tokenRegex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts;
  };

  // Parse lines into structured blocks with rich visual hierarchy
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];

  const flushList = (key: number) => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`ul-${key}`} className="space-y-2 my-2.5 pl-1 list-none">
          {currentList}
        </ul>
      );
      currentList = [];
    }
  };

  lines.forEach((rawLine, idx) => {
    const line = rawLine.trim();

    if (!line) {
      flushList(idx);
      return;
    }

    // 1. Primary Section Headings (### 1. Classical ASU Drug Classification or ### Heading)
    if (line.startsWith('### ')) {
      flushList(idx);
      const rawHeading = line.replace('### ', '').trim();
      const numPrefix = rawHeading.match(/^(\d+)\.\s*(.*)/);

      if (numPrefix) {
        const num = numPrefix[1];
        const title = numPrefix[2];
        elements.push(
          <div key={`h3-${idx}`} className="mt-7 mb-3 pt-3 border-t border-slate-100 first:mt-1 first:pt-0 first:border-0">
            <div className="flex items-center space-x-2.5">
              <span className="w-6 h-6 rounded-lg bg-emerald-800 text-white font-mono text-xs font-bold flex items-center justify-center shadow-xs">
                {num}
              </span>
              <h3 className="text-[15px] font-bold text-slate-900 tracking-tight">
                {renderInline(title)}
              </h3>
            </div>
          </div>
        );
      } else {
        elements.push(
          <div key={`h3-${idx}`} className="mt-6 mb-2.5 pt-2 border-t border-slate-100 first:mt-1 first:pt-0 first:border-0">
            <h3 className="text-[15px] font-bold text-slate-900 tracking-tight">
              {renderInline(rawHeading)}
            </h3>
          </div>
        );
      }
      return;
    }

    // 2. Heading 2: ## ...
    if (line.startsWith('## ')) {
      flushList(idx);
      elements.push(
        <h2 key={`h2-${idx}`} className="text-base font-extrabold text-slate-900 mt-6 mb-3 pb-1 border-b border-slate-100">
          {renderInline(line.replace('## ', ''))}
        </h2>
      );
      return;
    }

    // 3. Subheading / Group Divider (* **Key Criteria:** or **Key Characteristics:**)
    const isSubheader = line.match(/^(\*|-)?\s*\*\*([^*]+):\*\*\s*$/);
    if (isSubheader) {
      flushList(idx);
      const subheadTitle = isSubheader[2];
      elements.push(
        <div key={`sub-${idx}`} className="mt-4 mb-2 flex items-center space-x-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 font-mono">
            {subheadTitle}
          </span>
          <div className="h-px bg-slate-200/80 flex-1" />
        </div>
      );
      return;
    }

    // 4. Regulatory Callout Box (* **Implication:** ... or * **Takeaway:** ...)
    const isCallout = line.match(/^(\*|-)?\s*\*\*(Implication|Takeaway|Conclusion|Warning|Caution|Requirement):\*\*\s*(.+)$/i);
    if (isCallout) {
      flushList(idx);
      const calloutType = isCallout[2];
      const calloutBody = isCallout[3];
      elements.push(
        <div key={`callout-${idx}`} className="my-3 p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200/90 text-slate-800 text-[13.5px] leading-relaxed flex items-start space-x-2.5 shadow-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
          <div className="flex-1">
            <strong className="text-emerald-950 font-bold">{calloutType}: </strong>
            <span>{renderInline(calloutBody)}</span>
          </div>
        </div>
      );
      return;
    }

    // 5. Structured Definition / Field Tier (* **For ASU medicines with...:** Studies required...)
    const isField = line.match(/^(\*|-)\s+\*\*([^*]+):\*\*\s*(.+)$/);
    if (isField) {
      const fieldLabel = isField[2];
      const fieldValue = isField[3];
      currentList.push(
        <li key={`field-${idx}`} className="flex items-start space-x-2 text-slate-700 text-[14px] leading-relaxed my-1.5 pl-1">
          <ChevronRight className="w-3.5 h-3.5 text-emerald-700 shrink-0 mt-1" />
          <div className="flex-1">
            <span className="font-semibold text-slate-900">{fieldLabel}: </span>
            <span>{renderInline(fieldValue)}</span>
          </div>
        </li>
      );
      return;
    }

    // 6. Standard Nested List Item (* The formulation... or - The formulation...)
    if (line.startsWith('* ') || line.startsWith('- ')) {
      const itemText = line.substring(2);
      currentList.push(
        <li key={`li-${idx}`} className="flex items-start space-x-2.5 text-slate-700 text-[14px] leading-relaxed my-1.5 pl-1">
          <span className="w-1.5 h-1.5 rounded-full bg-slate-400 mt-2 shrink-0" />
          <div className="flex-1">{renderInline(itemText)}</div>
        </li>
      );
      return;
    }

    // 7. Numbered List Item (1. ... or 2. ...)
    const numMatch = line.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      flushList(idx);
      elements.push(
        <div key={`num-${idx}`} className="flex items-start space-x-2 text-slate-700 text-[14px] leading-relaxed my-1.5">
          <span className="text-emerald-800 font-bold shrink-0">{numMatch[1]}.</span>
          <div className="flex-1">{renderInline(numMatch[2])}</div>
        </div>
      );
      return;
    }

    // 8. Regular paragraph
    flushList(idx);
    elements.push(
      <p key={`p-${idx}`} className="text-slate-700 text-[14px] leading-relaxed my-2">
        {renderInline(line)}
      </p>
    );
  });

  flushList(lines.length);

  return <div className="space-y-1">{elements}</div>;
};

export default StatutoryMarkdownRenderer;
