import { useState } from 'react';
import { Scale, ShieldCheck, AlertTriangle, Info, ExternalLink } from 'lucide-react';
import { Citation } from '../../types';

interface IPMatrixViewProps {
  onOpenCitation?: (c: Citation) => void;
}

export function IPMatrixView({ onOpenCitation }: IPMatrixViewProps) {
  const [selectedRoute, setSelectedRoute] = useState<string | null>('patent');

  const ipRoutes = [
    {
      id: 'patent',
      title: 'Patent Protection',
      status: 'CONDITIONAL',
      statusLabel: 'Conditional / Assessment Required',
      statusColor: 'bg-amber-100 text-amber-900 border-amber-300',
      icon: Scale,
      statute: 'The Patents Act, 1970',
      sections: ['Section 3(p)', 'Section 3(e)', 'Section 10(4)'],
      summary: 'Classical formulations are strictly barred under Section 3(p). Modified extracts or synergistic polyherbals require proof of non-obvious efficacy and NBA Form III approval.',
      filingRequirements: [
        'Form 1 (Application for Grant of Patent)',
        'Form 2 (Complete Specification with Source Origin Disclosure under Sec 10(4))',
        'Form 18A (Expedited Examination for AYUSH Startups under 2024 Rules)',
        'NBA Form III (Prior Approval before grant under Biological Diversity Act Sec 6)'
      ],
      citationSample: {
        source_id: 'IND_PATENTS_ACT_1970',
        source_title: 'The Patents Act, 1970',
        section: 'Section 3(p)',
        jurisdiction: 'IN' as const,
        support_score: 1.0,
        verbatim_quote: 'An invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not an invention.'
      }
    },
    {
      id: 'trademark',
      title: 'Trademark & Brand Protection',
      status: 'APPLICABLE',
      statusLabel: 'Highly Applicable',
      statusColor: 'bg-emerald-100 text-emerald-900 border-emerald-300',
      icon: ShieldCheck,
      statute: 'The Trade Marks Act, 1999',
      sections: ['Section 9(1)(b)', 'Class 5', 'Class 3'],
      summary: 'Distinctive proprietary brand names (e.g. "Liv-52", "Zandu") can be registered under Class 5 (Medicines) or Class 3 (Cosmetics). Generic Sanskrit herb names cannot be monopolized.',
      filingRequirements: [
        'TM-A Application for Trademark Registration',
        'Filing in Nice Class 5 (Pharmaceuticals/ASU) and Class 30 (Foods/Aahara)',
        'Distinctiveness audit to prevent Section 9 refusal for descriptive herb names'
      ],
      citationSample: {
        source_id: 'IND_TRADE_MARKS_ACT_1999',
        source_title: 'The Trade Marks Act, 1999',
        section: 'Section 9(1)(b)',
        jurisdiction: 'IN' as const,
        support_score: 0.95,
        verbatim_quote: 'Trade marks which consist exclusively of marks which may serve in trade to designate the kind, quality, or intended purpose of the goods shall not be registered.'
      }
    },
    {
      id: 'gi',
      title: 'Geographical Indication (GI)',
      status: 'CONDITIONAL',
      statusLabel: 'Community / Regional Applicable',
      statusColor: 'bg-amber-100 text-amber-900 border-amber-300',
      icon: Info,
      statute: 'The Geographical Indications of Goods Act, 1999',
      sections: ['Section 2(1)(e)', 'Section 17'],
      summary: 'Applies to regionally cultivated botanicals with unique terroir qualities (e.g., Alleppey Cardamom, Malabar Pepper, Kashmiri Saffron). Individual companies apply as Authorized Users.',
      filingRequirements: [
        'GI Application Form GI-1 for Community/Producer Organizations',
        'Form GI-3 for Registration as an Authorized User of existing registered GI'
      ],
      citationSample: {
        source_id: 'IND_GEOGRAPHICAL_INDICATIONS_ACT_1999',
        source_title: 'Geographical Indications Act, 1999',
        section: 'Section 2(1)(e)',
        jurisdiction: 'IN' as const,
        support_score: 0.90,
        verbatim_quote: 'An indication which identifies goods as originating in a territory where a given quality or reputation is essentially attributable to its geographical origin.'
      }
    },
    {
      id: 'abs',
      title: 'Access & Benefit Sharing (ABS)',
      status: 'MANDATORY',
      statusLabel: 'Mandatory Compliance Check',
      statusColor: 'bg-red-100 text-red-900 border-red-300',
      icon: AlertTriangle,
      statute: 'The Biological Diversity Act, 2002 (as amended 2023)',
      sections: ['Section 7 (SBB)', 'Section 3 (NBA)', 'Section 6 (IPR)'],
      summary: 'Commercial utilization of Indian herbs requires SBB Prior Intimation for Indian entities or NBA Prior Approval for foreign companies. Local AYUSH vaidyas are exempted under 2023 amendment.',
      filingRequirements: [
        'Form I to NBA (Foreign entities accessing Indian biological resources)',
        'State Biodiversity Board Prior Intimation Form (Domestic commercial manufacturers)',
        'Form III to NBA (Before patent grant involving Indian biological material)'
      ],
      citationSample: {
        source_id: 'IND_BIOLOGICAL_DIVERSITY_ACT_2002',
        source_title: 'Biological Diversity Act, 2002',
        section: 'Section 6',
        jurisdiction: 'IN' as const,
        support_score: 1.0,
        verbatim_quote: 'No person shall apply for any intellectual property right in or outside India for any invention based on biological resources from India without prior approval of NBA.'
      }
    },
    {
      id: 'trade_secret',
      title: 'Trade Secret / Know-How',
      status: 'APPLICABLE',
      statusLabel: 'Highly Applicable',
      statusColor: 'bg-emerald-100 text-emerald-900 border-emerald-300',
      icon: ShieldCheck,
      statute: 'Indian Contract Act, 1872 & Common Law',
      sections: ['Section 27', 'Non-Disclosure Agreements'],
      summary: 'Proprietary Bhavana extraction parameters, precise temperature control curves, and bespoke manufacturing know-how should be protected as confidential trade secrets.',
      filingRequirements: [
        'Robust Employee Non-Disclosure & Non-Compete Agreements (NDAs)',
        'Physical and digital access control in GMP manufacturing plants',
        'Batch manufacturing record (BMR) redactions'
      ],
      citationSample: {
        source_id: 'TRADE_SECRET_COMMON_LAW',
        source_title: 'Confidential Information & Trade Secrets Doctrine',
        section: 'Section 27 Contract Act',
        jurisdiction: 'IN' as const,
        support_score: 0.85,
        verbatim_quote: 'Trade secrets and proprietary manufacturing techniques are legally enforceable through strict contractual covenants and non-disclosure obligations.'
      }
    }
  ];

  const currentRoute = ipRoutes.find((r) => r.id === selectedRoute) || ipRoutes[0];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-ayush-border rounded-2xl p-6 shadow-card">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-50 text-ayush-forest rounded-md text-xs font-bold border border-emerald-200 mb-2">
              <Scale className="w-3.5 h-3.5" />
              <span>Module 2 · IP Opportunity Navigator</span>
            </div>
            <h1 className="text-2xl font-bold text-ayush-navy">
              Ayurvedic IP Opportunity Matrix
            </h1>
            <p className="text-xs text-ayush-slate mt-1 max-w-2xl">
              Evaluate statutory eligibility across Patents, Trademarks, Geographical Indications, Trade Secrets, and Biodiversity (ABS) with verified legal citations.
            </p>
          </div>
        </div>
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Route Selector Cards */}
        <div className="lg:col-span-5 space-y-3">
          {ipRoutes.map((route) => {
            const isSelected = selectedRoute === route.id;
            return (
              <div
                key={route.id}
                onClick={() => setSelectedRoute(route.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-emerald-50/60 border-ayush-forest shadow-card ring-1 ring-ayush-forest'
                    : 'bg-white border-ayush-border hover:border-slate-300 shadow-subtle'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${isSelected ? 'bg-ayush-forest text-white' : 'bg-slate-100 text-slate-700'}`}>
                      <route.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-ayush-navy">{route.title}</h3>
                      <p className="text-[11px] text-ayush-slate">{route.statute}</p>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${route.statusColor}`}>
                    {route.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Detailed Strategy & Filing Breakdown */}
        <div className="lg:col-span-7 bg-white border border-ayush-border rounded-2xl p-6 shadow-card space-y-6">
          <div className="border-b border-ayush-border pb-4 flex items-start justify-between">
            <div>
              <span className={`text-xs font-bold px-2.5 py-1 rounded border ${currentRoute.statusColor}`}>
                {currentRoute.statusLabel}
              </span>
              <h2 className="text-xl font-bold text-ayush-navy mt-2">
                {currentRoute.title} Strategy
              </h2>
              <p className="text-xs text-ayush-slate font-medium mt-0.5">
                Primary Statute: <strong className="text-ayush-navy">{currentRoute.statute}</strong>
              </p>
            </div>
          </div>

          {/* Legal Summary */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Statutory Evaluation & Legal Rationale
            </h4>
            <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              {currentRoute.summary}
            </p>
          </div>

          {/* Filing & Regulatory Requirements */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Mandatory Filing Roadmap & Official Forms
            </h4>
            <div className="space-y-2">
              {currentRoute.filingRequirements.map((req, idx) => (
                <div key={idx} className="flex items-start space-x-2.5 text-xs text-slate-800">
                  <div className="w-4 h-4 rounded-full bg-emerald-100 text-ayush-forest flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                    {idx + 1}
                  </div>
                  <span>{req}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Citation Trigger */}
          <div className="pt-2 border-t border-ayush-border">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Statutory Authority:</span>
              <button
                onClick={() => onOpenCitation && onOpenCitation(currentRoute.citationSample)}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-100 hover:bg-emerald-50 text-ayush-forest rounded-lg text-xs font-bold border border-slate-200 transition-colors"
              >
                <span>View {currentRoute.citationSample.section} Citation</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
