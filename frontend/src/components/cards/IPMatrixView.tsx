import { useState } from 'react';
import { 
  Scale, ShieldCheck, AlertTriangle, Info, ExternalLink, BookOpen, 
  Sparkles, Layers, Sprout, LayoutGrid, ListFilter
} from 'lucide-react';
import { Citation, ActiveCaseState } from '../../types';

interface IPMatrixViewProps {
  activeCase?: ActiveCaseState | null;
  onOpenCitation?: (c: Citation) => void;
  onAskCopilot?: (query: string) => void;
}

export function IPMatrixView({ activeCase, onOpenCitation, onAskCopilot }: IPMatrixViewProps) {
  const [selectedRoute, setSelectedRoute] = useState<string>('patent');
  const [viewMode, setViewMode] = useState<'matrix' | 'pathway'>('matrix');

  const ipRoutes = [
    {
      id: 'patent',
      title: 'Patent Protection',
      category: 'Invention & Formulation',
      assetType: 'Novel extraction process, synergistic polyherbal ratio, or standardized fraction',
      status: 'CONDITIONAL',
      statusLabel: 'Requires Novelty & Synergistic Assessment',
      statusColor: 'bg-amber-50 text-amber-900 border-amber-300',
      badgeDot: 'bg-amber-500',
      icon: Scale,
      statute: 'The Patents Act, 1970 (as amended 2024)',
      sections: ['Section 3(p)', 'Section 3(e)', 'Section 10(4)', 'Rule 131 (Form 27)'],
      whatIsIt: 'Potential 20-year monopoly over novel, non-obvious Ayurvedic extraction processes, purified fractions, or synergistic polyherbals.',
      whyRationale: 'Pure classical recipes described in First Schedule treatises are strictly barred under Section 3(p) as traditional knowledge. Modified extracts or synergistic formulations require non-obvious clinical/bioactivity proof (Sec 3(e)) and biological source origin disclosure (Sec 10(4)).',
      filingRequirements: [
        'Form 1: Application for Grant of Patent in India',
        'Form 2: Complete Specification with Biological Source Origin Disclosure under Section 10(4)',
        'Form 18A: Expedited Examination for AYUSH Startups & MSMEs (Patents Rules 2024)',
        'NBA Form III: Mandatory Prior Approval from National Biodiversity Authority before patent grant (BDA Sec 6)'
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
      title: 'Trademark & Brand Identity',
      category: 'Brand & Commercial Identity',
      assetType: 'Distinctive brand name, trade name, logo, coined trademark prefix',
      status: 'AVAILABLE',
      statusLabel: 'Available / Highly Recommended',
      statusColor: 'bg-emerald-50 text-emerald-900 border-emerald-300',
      badgeDot: 'bg-emerald-500',
      icon: ShieldCheck,
      statute: 'The Trade Marks Act, 1999',
      sections: ['Section 9(1)(b)', 'Nice Class 5 (Medicines)', 'Nice Class 30 (Foods)', 'Nice Class 3 (Cosmetics)'],
      whatIsIt: 'Commercial brand monopoly over distinctive coined brand names, logos, and packaging styles (renewable every 10 years indefinitely).',
      whyRationale: 'Distinctive proprietary brand names can be registered. Generic Sanskrit plant names (e.g. "Ashwagandha", "Triphala") cannot be registered due to Section 9 descriptiveness bars.',
      filingRequirements: [
        'Form TM-A: Application for Registration of Trademark with Trademark Registry',
        'Multi-Class Filing: Nice Class 5 (ASU Medicines), Class 3 (Cosmetics), and Class 30 (Ayurveda Aahara)',
        'Distinctiveness Audit: Ensure mark contains non-descriptive arbitrary or coined prefix'
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
      id: 'design',
      title: 'Industrial Design & Packaging',
      category: 'Ergonomic & Visual Packaging',
      assetType: 'Unique bottle shape, blister geometry, applicator dispenser design',
      status: 'AVAILABLE',
      statusLabel: 'Available for Novel Packaging Geometry',
      statusColor: 'bg-indigo-50 text-indigo-900 border-indigo-300',
      badgeDot: 'bg-indigo-500',
      icon: Layers,
      statute: 'The Designs Act, 2000 & Designs Rules 2001',
      sections: ['Section 4 (Novelty)', 'Section 5 (Application)', 'Locarno Class 09 (Packaging)'],
      whatIsIt: '10-year exclusive monopoly (extendable to 15 years) over novel visual container contours, bottle geometry, and packaging aesthetics.',
      whyRationale: 'Protects ornamental features of innovative Ayurvedic medicine delivery dispensers or bottle shapes against commercial imitation.',
      filingRequirements: [
        'Form 1: Application for Registration of Design (Designs Office, Kolkata)',
        'Locarno Classification: Class 09 (Packages and containers for the transport or handling of goods)',
        'Six-angle orthogonal drawing views proving geometric novelty prior to market release'
      ],
      citationSample: {
        source_id: 'IND_DESIGNS_ACT_2000',
        source_title: 'The Designs Act, 2000',
        section: 'Section 4',
        jurisdiction: 'IN' as const,
        support_score: 0.90,
        verbatim_quote: 'A design which is not new or original, or has been disclosed to the public anywhere in India or in any other country prior to the filing date shall not be registered.'
      }
    },
    {
      id: 'trade_secret',
      title: 'Trade Secret & Manufacturing Know-How',
      category: 'Process & Extraction Confidentiality',
      assetType: 'Unpublished extraction curves, Bhavana soaking duration, temperature profiles, SOPs',
      status: 'AVAILABLE',
      statusLabel: 'Available via Contractual Controls',
      statusColor: 'bg-emerald-50 text-emerald-900 border-emerald-300',
      badgeDot: 'bg-emerald-500',
      icon: ShieldCheck,
      statute: 'Indian Contract Act, 1872 & Common Law',
      sections: ['Section 27', 'Bilateral Non-Disclosure Agreements'],
      whatIsIt: 'Unpublished proprietary extraction curves, Bhavana cycles, temperature profiles, and formulation ratios kept confidential indefinitely.',
      whyRationale: 'Where Section 3(p) bars public patent monopolies on herbal combinations, trade secrets protect precise processing know-how without public disclosure.',
      filingRequirements: [
        'Bilateral Non-Disclosure Agreements (NDAs) for employees, R&D staff, and CMOs',
        'Physical and digital access security protocols at GMP manufacturing facilities',
        'Standard Operating Procedure (SOP) confidentiality controls and IP assignment covenants'
      ],
      citationSample: {
        source_id: 'TRADE_SECRET_COMMON_LAW',
        source_title: 'Confidential Information & Trade Secrets Doctrine',
        section: 'Section 27 Contract Act',
        jurisdiction: 'IN' as const,
        support_score: 0.85,
        verbatim_quote: 'Trade secrets and proprietary manufacturing techniques are legally enforceable through strict contractual covenants and non-disclosure obligations.'
      }
    },
    {
      id: 'abs',
      title: 'Access & Benefit Sharing (ABS Linkage)',
      category: 'Biodiversity & Heritage Compliance',
      assetType: 'Biological herb sourcing provenance, community knowledge, IPR linkage approval',
      status: 'MANDATORY',
      statusLabel: 'Mandatory Statutory Compliance',
      statusColor: 'bg-rose-50 text-rose-900 border-rose-300',
      badgeDot: 'bg-rose-500',
      icon: AlertTriangle,
      statute: 'The Biological Diversity Act, 2002 (as amended 2023)',
      sections: ['Section 7 (SBB)', 'Section 3 (NBA)', 'Section 6 (IPR Linkage)'],
      whatIsIt: 'Statutory compliance obligation for accessing and commercially utilizing Indian herbs and biological resources.',
      whyRationale: 'Commercial manufacturers must give Prior Intimation to the State Biodiversity Board (SBB Form A). Foreign entities and export applicants must obtain NBA Prior Approval (Form I / Form III). Local AYUSH vaidyas are exempted under BDA 2023.',
      filingRequirements: [
        'SBB Prior Intimation (Form A): For domestic Indian manufacturers sourcing wild biological material',
        'NBA Form I: For foreign entities accessing Indian bio-resources for research or commercialization',
        'NBA Form III: Mandatory approval before patent grant based on Indian biological resources'
      ],
      citationSample: {
        source_id: 'IND_BIOLOGICAL_DIVERSITY_ACT_2002',
        source_title: 'Biological Diversity Act, 2002 (as amended 2023)',
        section: 'Section 6',
        jurisdiction: 'IN' as const,
        support_score: 1.0,
        verbatim_quote: 'No person shall apply for any intellectual property right in or outside India for any invention based on biological resources from India without prior approval of NBA.'
      }
    },
    {
      id: 'gi',
      title: 'Geographical Indication (GI)',
      category: 'Regional Terroir & Community IP',
      assetType: 'Regional landrace botanicals (Kashmiri Saffron, Alleppey Green Cardamom, Malabar Pepper)',
      status: 'COMMUNITY',
      statusLabel: 'Community / Regional Terroir Right',
      statusColor: 'bg-blue-50 text-blue-900 border-blue-300',
      badgeDot: 'bg-blue-500',
      icon: Info,
      statute: 'Geographical Indications of Goods Act, 1999',
      sections: ['Section 2(1)(e)', 'Section 17 (Authorized User)'],
      whatIsIt: 'Collective regional IP right protecting botanicals whose quality is attributable to regional agro-climatic terroir.',
      whyRationale: 'Individual commercial entities cannot monopolize a GI directly, but can register as an "Authorized User" under Section 17 to legally sell certified GI produce.',
      filingRequirements: [
        'Form GI-1: Filed by Producer Associations or Community Collectives',
        'Form GI-3: Application for Registration as an Authorized User of registered GI',
        'Traceability Audit: Certificate of origin proving harvest within the demarcated GI geography'
      ],
      citationSample: {
        source_id: 'IND_GEOGRAPHICAL_INDICATIONS_ACT_1999',
        source_title: 'Geographical Indications of Goods Act, 1999',
        section: 'Section 2(1)(e)',
        jurisdiction: 'IN' as const,
        support_score: 0.90,
        verbatim_quote: 'An indication which identifies goods as originating in a territory where a given quality or reputation is essentially attributable to its geographical origin.'
      }
    },
    {
      id: 'ppvfr',
      title: 'Plant Variety Protection (PPV&FR)',
      category: 'Novel Cultivar & Plant Breeding',
      assetType: 'Distinct, Uniform, Stable (DUS) cultivated medicinal plant varieties',
      status: 'CONDITIONAL',
      statusLabel: 'Review Required for Bred Cultivars',
      statusColor: 'bg-teal-50 text-teal-900 border-teal-300',
      badgeDot: 'bg-teal-500',
      icon: Sprout,
      statute: 'Protection of Plant Varieties and Farmers Rights Act, 2001',
      sections: ['Section 15 (DUS Criteria)', 'Section 24 (Registration)'],
      whatIsIt: '15-to-18-year breeder monopoly over novel, distinct, uniform, and stable cultivated medicinal plant varieties.',
      whyRationale: 'Wild medicinal plants cannot be registered, but novel agronomic cultivars bred for higher withanolide/curcuminoid yield qualify for plant breeder rights.',
      filingRequirements: [
        'Form 1: Application for Registration of Plant Variety with PPV&FR Authority, New Delhi',
        'DUS Field Testing: Conduct 2-year Distinctiveness, Uniformity, and Stability field trials',
        'Complete genealogical breeding history and deposition of reference seeds at National Gene Bank'
      ],
      citationSample: {
        source_id: 'IND_PPVFR_ACT_2001',
        source_title: 'Protection of Plant Varieties and Farmers Rights Act, 2001',
        section: 'Section 15',
        jurisdiction: 'IN' as const,
        support_score: 0.88,
        verbatim_quote: 'A new variety shall be registered if it conforms to the criteria of novelty, distinctiveness, uniformity and stability.'
      }
    }
  ];

  const currentRoute = ipRoutes.find((r) => r.id === selectedRoute) || ipRoutes[0];

  return (
    <div className="space-y-6 animate-fadeIn select-text">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="space-y-1.5">
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-ayush-forest rounded-full text-xs font-bold border border-emerald-200">
              <Scale className="w-3.5 h-3.5" />
              <span>Module 2 · Multi-Modal IP Decision Matrix</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-display tracking-tight">
              Ayurvedic Intellectual Property Opportunity Matrix
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 max-w-3xl leading-relaxed">
              Systematic decision matrix across Patents, Trademarks, Industrial Designs, Trade Secrets, ABS Linkages, Geographical Indications, and Plant Variety Rights. Understand legal boundaries under Section 3(p) and identify valid commercial protection pathways.
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-bold shrink-0">
            <button
              onClick={() => setViewMode('matrix')}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center space-x-1.5 ${
                viewMode === 'matrix' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span>Decision Matrix</span>
            </button>
            <button
              onClick={() => setViewMode('pathway')}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center space-x-1.5 ${
                viewMode === 'pathway' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <ListFilter className="w-3.5 h-3.5" />
              <span>Detailed Pathway</span>
            </button>
          </div>
        </div>

        {activeCase?.productRequest?.name && (
          <div className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-200 text-xs flex items-center justify-between">
            <span className="text-emerald-950 font-medium">
              Evaluating IP options for Active Case: <strong>{activeCase.productRequest.name}</strong> ({activeCase.caseId})
            </span>
            <span className="text-[10px] font-mono font-bold text-emerald-800 bg-white px-2 py-0.5 rounded border border-emerald-200">
              {activeCase.status}
            </span>
          </div>
        )}
      </div>

      {/* VIEW 1: STRUCTURED DECISION MATRIX TABLE */}
      {viewMode === 'matrix' && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-card space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-base font-extrabold text-slate-900 font-display">
                Protection Route Decision Matrix
              </h3>
              <p className="text-xs text-slate-500">
                Comparative analysis of asset types, potential protection routes, statutory grounds, and evidence actions.
              </p>
            </div>
            <span className="text-[10px] font-mono text-slate-400 font-bold">
              {ipRoutes.length} IP Dimensions
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/70 text-slate-600 text-[10px] uppercase font-black tracking-wider">
                  <th className="p-3.5 rounded-l-xl">Asset / Feature</th>
                  <th className="p-3.5">Possible Route</th>
                  <th className="p-3.5">Statutory Ground / Reason</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 rounded-r-xl text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {ipRoutes.map((route) => (
                  <tr key={route.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="p-3.5 align-top">
                      <div className="space-y-0.5">
                        <span className="font-bold text-slate-900 block">{route.title}</span>
                        <span className="text-[11px] text-slate-500 line-clamp-2">{route.assetType}</span>
                      </div>
                    </td>
                    <td className="p-3.5 align-top">
                      <span className="font-semibold text-slate-800 block">{route.category}</span>
                      <span className="text-[10px] font-mono text-slate-400">{route.statute.split('(')[0]}</span>
                    </td>
                    <td className="p-3.5 align-top max-w-xs">
                      <p className="text-[11px] text-slate-600 leading-relaxed line-clamp-2">
                        {route.whyRationale}
                      </p>
                    </td>
                    <td className="p-3.5 align-top whitespace-nowrap">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border inline-block ${route.statusColor}`}>
                        {route.statusLabel}
                      </span>
                    </td>
                    <td className="p-3.5 align-top text-right whitespace-nowrap">
                      <div className="flex items-center justify-end space-x-1.5">
                        <button
                          onClick={() => onOpenCitation && onOpenCitation(route.citationSample)}
                          className="px-2.5 py-1 bg-slate-100 hover:bg-emerald-50 text-ayush-forest rounded-lg text-xs font-bold border border-slate-200 transition-colors"
                          title="Inspect Statutory Grounding Evidence"
                        >
                          Evidence
                        </button>
                        <button
                          onClick={() => {
                            setSelectedRoute(route.id);
                            setViewMode('pathway');
                          }}
                          className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition-all shadow-subtle"
                        >
                          Details
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* VIEW 2: DETAILED 2-COLUMN PATHWAY VIEW */}
      {viewMode === 'pathway' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          
          {/* Left Column: Route Selector List */}
          <div className="lg:col-span-5 space-y-2.5">
            {ipRoutes.map((route) => {
              const isSelected = selectedRoute === route.id;
              return (
                <button
                  key={route.id}
                  onClick={() => setSelectedRoute(route.id)}
                  className={`w-full p-4 rounded-2xl border text-left transition-all flex items-center justify-between ${
                    isSelected
                      ? 'bg-emerald-50/80 border-ayush-forest shadow-card ring-1 ring-ayush-forest'
                      : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50 shadow-subtle'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-2.5 rounded-xl ${isSelected ? 'bg-ayush-forest text-white' : 'bg-slate-100 text-slate-700'}`}>
                      <route.icon className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-bold text-xs sm:text-sm text-slate-900">{route.title}</h3>
                      <p className="text-[11px] text-slate-500 font-medium">{route.category}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1.5">
                    <span className={`w-2 h-2 rounded-full ${route.badgeDot}`} />
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${route.statusColor}`}>
                      {route.status}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Right Column: Detailed 5-Point Strategy Breakdown */}
          <div className="lg:col-span-7 bg-white border border-slate-200 rounded-3xl p-6 sm:p-7 shadow-card space-y-6">
            
            {/* Header & Status */}
            <div className="border-b border-slate-100 pb-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className={`text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-md border ${currentRoute.statusColor}`}>
                  {currentRoute.statusLabel}
                </span>
                <span className="text-xs font-mono text-slate-400">
                  Statute: {currentRoute.statute.split('(')[0]}
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-slate-900 font-display">
                {currentRoute.title} Strategic Pathway
              </h2>
            </div>

            {/* 1. Scope of Protection */}
            <div className="space-y-1.5">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                1. Scope of Protection & Eligible Assets
              </h4>
              <p className="text-xs text-slate-800 leading-relaxed font-medium">
                {currentRoute.whatIsIt}
              </p>
            </div>

            {/* 2. Statutory Rationale & Why */}
            <div className="space-y-1.5">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                2. Statutory Ground & Legal Rationale
              </h4>
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed font-medium">
                {currentRoute.whyRationale}
              </div>
            </div>

            {/* 3. Mandatory Filing Roadmap */}
            <div className="space-y-2">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                3. Recommended Filing Forms & Actions
              </h4>
              <div className="space-y-1.5">
                {currentRoute.filingRequirements.map((req, idx) => (
                  <div key={idx} className="flex items-start space-x-2.5 text-xs text-slate-800 bg-white p-2.5 rounded-lg border border-slate-200/80 shadow-subtle">
                    <div className="w-4 h-4 rounded-full bg-emerald-100 text-ayush-forest flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5 font-mono">
                      {idx + 1}
                    </div>
                    <span className="font-medium">{req}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 4. Actions: Evidence Trigger & Copilot Query */}
            <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
              <button
                onClick={() => onOpenCitation && onOpenCitation(currentRoute.citationSample)}
                className="inline-flex items-center space-x-1.5 px-3 py-2 bg-slate-50 hover:bg-emerald-50 text-ayush-forest rounded-xl text-xs font-bold border border-slate-200 transition-colors shadow-subtle"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Inspect Statutory Evidence ({currentRoute.citationSample.section})</span>
                <ExternalLink className="w-3 h-3 text-slate-400" />
              </button>

              {onAskCopilot && (
                <button
                  onClick={() => onAskCopilot(`How can I pursue ${currentRoute.title} for an Ayurvedic product under ${currentRoute.statute}? What are the key statutory hurdles?`)}
                  className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-ayush-forest hover:bg-ayush-forestDark text-white rounded-xl text-xs font-bold transition-all shadow-subtle"
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-200" />
                  <span>Ask Copilot About This Route</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

