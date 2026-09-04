import { useState } from 'react';
import { 
  Globe, CheckCircle2, ExternalLink, BookOpen, 
  ArrowRight, ArrowLeftRight, Info
} from 'lucide-react';
import { Citation, Jurisdiction } from '../../types';

interface InternationalViewProps {
  onOpenCitation?: (c: Citation) => void;
  onAskCopilot?: (query: string) => void;
}

export function InternationalView({ onOpenCitation, onAskCopilot }: InternationalViewProps) {
  const [selectedRegime, setSelectedRegime] = useState<Jurisdiction>('CROSS_BORDER');

  const indiaRequirements = [
    {
      title: 'Drugs & Cosmetics Act, 1940 (Chapter IV-A)',
      authority: 'State Licensing Authority (AYUSH)',
      summary: 'Classical formulations strictly licensed under Section 3(a); proprietary polyherbals require Rule 158B safety proofs. No clinical trials needed for classical texts in First Schedule.',
      keyRule: 'Rule 158B / Schedule T GMP'
    },
    {
      title: 'The Patents Act, 1970 — Section 3(p) & 3(e)',
      authority: 'CGPDTM (Indian Patent Office)',
      summary: 'Traditional Ayurvedic knowledge and mere aggregations of known properties are non-patentable. Requires demonstrable synergistic clinical/bioactivity proof.',
      keyRule: 'Section 3(p) TK Exclusion'
    },
    {
      title: 'Biological Diversity Act, 2002 (as amended 2023)',
      authority: 'State Biodiversity Board (SBB) / NBA',
      summary: 'Domestic manufacturers sourcing Indian herbs require Prior Intimation to SBB (Form A). Local vaidyas are exempted under BDA 2023 amendments.',
      keyRule: 'Section 7 (SBB Intimation)'
    },
    {
      title: 'FSSAI (Ayurveda Aahara) Regulations, 2022',
      authority: 'FSSAI & Ministry of Ayush',
      summary: 'Permits traditional food recipes prepared according to classical texts. Disease treatment or cure claims are strictly barred.',
      keyRule: 'Ayurveda Aahara Logo Mandatory'
    }
  ];

  const internationalRequirements = [
    {
      jurisdiction: '🇺🇸 United States (US FDA)',
      title: 'DSHEA 1994 & 21 CFR Part 111 (Dietary Supplements)',
      authority: 'US Food & Drug Administration (FDA)',
      summary: 'Ayurvedic formulations enter predominantly as Dietary Supplements. Requires 75-Day New Dietary Ingredient (NDI) notification if botanical was not marketed in the US before Oct 15, 1994.',
      keyRule: '75-Day NDI Notice & DS cGMP'
    },
    {
      jurisdiction: '🇪🇺 European Union (EU EMA)',
      title: 'Directive 2004/24/EC (Traditional Herbal Medicinal Products - THMPD)',
      authority: 'European Medicines Agency (EMA / HMPC)',
      summary: 'Simplified registration requires proof of 30 years of traditional medicinal use, including at least 15 years within the European Union. Strict bans on heavy metals and aristolochic acid.',
      keyRule: '30-Yr Traditional Proof (15 in EU)'
    },
    {
      jurisdiction: '🌐 Multilateral (WIPO)',
      title: 'WIPO GRATK Treaty, 2024',
      authority: 'World Intellectual Property Organization',
      summary: 'Mandatory patent applicant disclosure of the country of origin and associated traditional knowledge in all patent applications worldwide based on genetic resources.',
      keyRule: 'Article 3 Mandatory Origin Disclosure'
    },
    {
      jurisdiction: '🇦🇪 UAE & Gulf (MOHAP)',
      title: 'Complementary & Alternative Medicine (CAM) Guidelines',
      authority: 'Ministry of Health & Prevention (MOHAP)',
      summary: 'Registration as Herbal Medicine requiring Certificate of Free Sale from Ministry of Ayush India, Pharmacopoeial monograph compliance, and heavy metal testing.',
      keyRule: 'Certificate of Free Sale (CoFS)'
    }
  ];

  const crossBorderChecklist = [
    { item: 'Mandatory NBA Prior Approval (Form I / Form III)', desc: 'Required under Section 3 & 6 of BDA 2002 before exporting biological materials or applying for foreign patents based on Indian herbs.' },
    { item: 'Heavy Metal Limits Verification', desc: 'Must meet international limits: Lead < 10.0 ppm, Arsenic < 3.0 ppm, Mercury < 1.0 ppm, Cadmium < 0.3 ppm (AOAC / ICP-MS certified).' },
    { item: 'Pesticide & Microbial Residues Audit', desc: 'Absence of banned organochlorines, aflatoxins (B1 < 2ppb, Total < 4ppb), and pathogenic microbes (E. coli, Salmonella).' },
    { item: 'Zero Aristolochic Acid & Pyrrolizidine Alkaloids', desc: 'Strict ban in EU/US due to nephrotoxicity and carcinogenic risks; requires LC-MS/MS batch testing certificate.' }
  ];

  const sampleCitation: Citation = {
    source_id: 'INT_WIPO_GRATK_TREATY_2024',
    source_title: 'WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (2024)',
    section: 'Article 3.1 & 3.2',
    jurisdiction: 'INT',
    support_score: 0.98,
    verbatim_quote: 'Where the claimed invention in a patent application is based on genetic resources, each Contracting Party shall require applicants to disclose the country of origin, or if unknown, the source of the genetic resources.'
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-card space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-indigo-50 text-indigo-900 rounded-full text-xs font-bold border border-indigo-200 mb-2">
              <Globe className="w-3.5 h-3.5" />
              <span>Module 5 · Multi-Jurisdiction Regulatory Navigator</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-display tracking-tight">
              International Regimes & Cross-Border Pathway
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
              Understand the sharp statutory distinction between Indian domestic regulations (ASU / BDA 2023) and destination export regimes (US FDA DSHEA, EU THMPD, and WIPO GRATK Treaty 2024).
            </p>
          </div>

          {/* Regime Switcher Pills */}
          <div className="flex items-center bg-slate-100 p-1.5 rounded-2xl border border-slate-200 shrink-0">
            <button
              onClick={() => setSelectedRegime('IN')}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
                selectedRegime === 'IN' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span>🇮🇳 India Domestic</span>
            </button>
            <button
              onClick={() => setSelectedRegime('CROSS_BORDER')}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
                selectedRegime === 'CROSS_BORDER' ? 'bg-ayush-forest text-white shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <ArrowLeftRight className="w-3.5 h-3.5" />
              <span>Cross-Border Split</span>
            </button>
            <button
              onClick={() => setSelectedRegime('INT')}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
                selectedRegime === 'INT' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span>🌍 International</span>
            </button>
          </div>
        </div>

        {/* Regulatory Guidance Note */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center space-x-2.5 text-xs text-slate-700">
          <Info className="w-4 h-4 text-indigo-700 shrink-0" />
          <span>
            <strong>Statutory Rule:</strong> Indian AYUSH drug licenses are not automatically recognized abroad as pharmaceuticals. Products exported to the US or EU typically require re-categorization as <em>Dietary Supplements (DSHEA)</em> or <em>Traditional Herbal Medicinal Products (THMPD)</em>.
          </span>
        </div>
      </div>

      {/* VIEW 1: CROSS-BORDER SPLIT VIEW (DEFAULT) */}
      {selectedRegime === 'CROSS_BORDER' && (
        <div className="space-y-6">
          {/* Side-by-Side 2-Column Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Left: Indian Domestic Framework */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-card space-y-4">
              <div className="flex items-center space-x-2.5 border-b border-slate-100 pb-3">
                <span className="text-xl">🇮🇳</span>
                <div>
                  <h2 className="font-extrabold text-base text-slate-900 font-display">
                    India Domestic Regime
                  </h2>
                  <p className="text-[11px] text-slate-500 font-medium">AYUSH SLA · Patents Act Sec 3(p) · BDA 2023</p>
                </div>
              </div>

              <div className="space-y-3">
                {indiaRequirements.map((req, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-xs text-slate-900">{req.title}</h4>
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-700">
                        {req.keyRule}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium">
                      {req.summary}
                    </p>
                    <div className="text-[10px] font-semibold text-slate-400 pt-0.5">
                      Administered by: {req.authority}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Target Export Regimes */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-card space-y-4">
              <div className="flex items-center space-x-2.5 border-b border-slate-100 pb-3">
                <span className="text-xl">🌍</span>
                <div>
                  <h2 className="font-extrabold text-base text-slate-900 font-display">
                    Destination Export Regimes
                  </h2>
                  <p className="text-[11px] text-slate-500 font-medium">US FDA DSHEA · EU Directive 2004/24/EC · WIPO</p>
                </div>
              </div>

              <div className="space-y-3">
                {internationalRequirements.map((req, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-xs text-slate-900">{req.jurisdiction}</h4>
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white border border-slate-200 text-indigo-700">
                        {req.keyRule}
                      </span>
                    </div>
                    <h5 className="font-semibold text-xs text-slate-800">{req.title}</h5>
                    <p className="text-xs text-slate-600 leading-relaxed font-medium">
                      {req.summary}
                    </p>
                    <div className="text-[10px] font-semibold text-slate-400 pt-0.5">
                      Authority: {req.authority}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Cross-Border Bridge Checklist */}
          <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-indigo-950 text-white rounded-3xl p-7 shadow-card space-y-4">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-base font-display">
                  Mandatory Cross-Border Export Compliance Checklist
                </h3>
                <p className="text-xs text-slate-300">
                  Essential statutory filings and analytical certificates required before shipping Ayurvedic formulations abroad.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              {crossBorderChecklist.map((item, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
                  <h4 className="font-bold text-xs text-emerald-300 flex items-center space-x-1.5">
                    <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-300 flex items-center justify-center text-[10px] shrink-0 font-mono">
                      {idx + 1}
                    </span>
                    <span>{item.item}</span>
                  </h4>
                  <p className="text-[11px] text-slate-300 leading-relaxed pl-5 font-medium">
                    {item.desc}
                  </p>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs">
              <button
                onClick={() => onOpenCitation && onOpenCitation(sampleCitation)}
                className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-emerald-300 text-xs font-bold transition-all border border-white/10"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Inspect WIPO GRATK Treaty 2024 Provisions</span>
                <ExternalLink className="w-3 h-3" />
              </button>

              {onAskCopilot && (
                <button
                  onClick={() => onAskCopilot('Explain the key export requirements and heavy metal testing standards for exporting Ayurvedic formulations to the US and EU.')}
                  className="inline-flex items-center space-x-1.5 text-xs font-bold text-slate-200 hover:text-white underline underline-offset-4"
                >
                  <span>Ask Copilot about Export Standards</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: INDIA ONLY VIEW */}
      {selectedRegime === 'IN' && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-card space-y-5">
          <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
            <span className="text-2xl">🇮🇳</span>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 font-display">
                Indian Domestic Ayurvedic Regulatory Regime
              </h2>
              <p className="text-xs text-slate-500 font-medium">Governed by Ministry of Ayush, CDSCO, IP India, and National Biodiversity Authority</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {indiaRequirements.map((req, idx) => (
              <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-slate-50/70 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300">
                    {req.keyRule}
                  </span>
                  <span className="text-[10px] text-slate-400 font-bold uppercase">{req.authority}</span>
                </div>
                <h3 className="font-bold text-sm text-slate-900">{req.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-medium">{req.summary}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* VIEW 3: INTERNATIONAL ONLY VIEW */}
      {selectedRegime === 'INT' && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-card space-y-5">
          <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
            <span className="text-2xl">🌍</span>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 font-display">
                International Destination Frameworks
              </h2>
              <p className="text-xs text-slate-500 font-medium">US FDA DSHEA, EU THMPD 2004/24/EC, WIPO GRATK Treaty, and Gulf MOHAP</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {internationalRequirements.map((req, idx) => (
              <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-slate-50/70 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-900 border border-indigo-300">
                    {req.keyRule}
                  </span>
                  <span className="text-[10px] text-slate-400 font-bold uppercase">{req.jurisdiction}</span>
                </div>
                <h3 className="font-bold text-sm text-slate-900">{req.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-medium">{req.summary}</p>
                <div className="text-[10px] text-slate-400 font-medium">Authority: {req.authority}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
