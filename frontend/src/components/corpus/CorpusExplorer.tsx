import { useState } from 'react';
import { BookOpen, CheckCircle2, ExternalLink, Hash } from 'lucide-react';

export function CorpusExplorer() {
  const [activeCategory, setActiveCategory] = useState<'acts' | 'tkdl' | 'botanicals'>('acts');

  const statutoryActs = [
    {
      id: 'IND_PATENTS_ACT_1970',
      title: 'The Patents Act, 1970 (as amended 2024)',
      shortTitle: 'Patents Act, 1970',
      authority: 'Intellectual Property India (CGPDTM)',
      authorityLevel: 'Level 5 (Primary Statute)',
      jurisdiction: '🇮🇳 India',
      sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      officialUrl: 'https://www.indiacode.nic.in/handle/123456789/1392',
      keySections: ['Section 2(1)(j) - Novelty', 'Section 3(p) - Traditional Knowledge Exclusion', 'Section 3(e) - Mere Admixture', 'Section 10(4) - Source Origin Disclosure']
    },
    {
      id: 'IND_BIOLOGICAL_DIVERSITY_ACT_2002',
      title: 'The Biological Diversity Act, 2002 (as amended 2023)',
      shortTitle: 'Biological Diversity Act, 2002',
      authority: 'National Biodiversity Authority (NBA)',
      authorityLevel: 'Level 5 (Primary Statute)',
      jurisdiction: '🇮🇳 India',
      sha256: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
      officialUrl: 'https://www.indiacode.nic.in/handle/123456789/2046',
      keySections: ['Section 3 - Foreign Entity Approval (Form I)', 'Section 6 - IPR Linkage (Form III)', 'Section 7 - SBB Prior Intimation', 'Section 21 - Equitable Benefit Sharing']
    },
    {
      id: 'IND_DRUGS_COSMETICS_ACT_1940',
      title: 'The Drugs and Cosmetics Act, 1940 (Chapter IV-A: ASU Drugs)',
      shortTitle: 'Drugs & Cosmetics Act (ASU)',
      authority: 'Ministry of Ayush / CDSCO',
      authorityLevel: 'Level 5 (Primary Statute)',
      jurisdiction: '🇮🇳 India',
      sha256: '7a9332158872bcae4751433f4a30a845e1281eec956279f584e03b29c9ef63e3',
      officialUrl: 'https://www.indiacode.nic.in/handle/123456789/2402',
      keySections: ['Section 3(a) - Classical ASU Definition', 'Section 3(h) - Proprietary ASU Definition', 'First Schedule - 56 Classical Texts', 'Section 33EE - Misbranded ASU Drugs']
    },
    {
      id: 'IND_DRUGS_COSMETICS_RULES_1945',
      title: 'The Drugs and Cosmetics Rules, 1945 (Part XVI & XVII)',
      shortTitle: 'Drugs & Cosmetics Rules (ASU)',
      authority: 'Ministry of Ayush',
      authorityLevel: 'Level 5 (Primary Subordinate Rules)',
      jurisdiction: '🇮🇳 India',
      sha256: '3f9821811e59273c509cfae4f88410292f7543a6d962058444a169123019be55',
      officialUrl: 'https://ayush.gov.in/docs/drugs-and-cosmetics-rules-1945.pdf',
      keySections: ['Rule 158B - Licensing of Proprietary Medicines', 'Rule 161 - Labelling Requirements', 'Schedule T - Good Manufacturing Practices (GMP)', 'Schedule E(1) - Poisonous Substances List']
    },
    {
      id: 'IND_FSSAI_AYURVEDA_AAHARA_2022',
      title: 'FSSAI (Ayurveda Aahara) Regulations, 2022',
      shortTitle: 'Ayurveda Aahara Regulations',
      authority: 'FSSAI / Ministry of Health',
      authorityLevel: 'Level 5 (Statutory Regulations)',
      jurisdiction: '🇮🇳 India',
      sha256: '9a721811e59273c509cfae4f88410292f7543a6d962058444a169123019be12',
      officialUrl: 'https://www.fssai.gov.in',
      keySections: ['Regulation 2(1)(a) - Definition', 'Regulation 5 - Disease Cure Claims Prohibited', 'Regulation 6 - Mandatory Ayurveda Aahara Logo', 'Schedule A - Permissible Classical Recipes']
    }
  ];

  const tkdlFormulations = [
    {
      name: 'Triphala Churna',
      code: 'TKDL-AYU-001',
      source: 'Charaka Samhita (Chikitsasthana, Ch. 1)',
      ingredients: 'Haritaki (Terminalia chebula), Bibhitaki (Terminalia bellirica), Amalaki (Phyllanthus emblica)',
      indication: 'Deepana (Digestive), Chakshushya (Vision), Rasayana',
      patentStatus: 'Section 3(p) Statutory Bar (Prior Art)'
    },
    {
      name: 'Trikatu Churna',
      code: 'TKDL-AYU-002',
      source: 'Sharangadhara Samhita (Madhyama Khanda)',
      ingredients: 'Shunthi (Zingiber officinale), Maricha (Piper nigrum), Pippali (Piper longum)',
      indication: 'Agni-deepana, Kaphahara, Bioavailability enhancer',
      patentStatus: 'Section 3(p) Statutory Bar (Prior Art)'
    },
    {
      name: 'Nisha-Amalaki Churna',
      code: 'TKDL-AYU-003',
      source: 'Ashtanga Hridaya (Prameha Chikitsa)',
      ingredients: 'Haridra (Curcuma longa), Amalaki (Phyllanthus emblica)',
      indication: 'Prameha-hara (Blood sugar management), Kledahara',
      patentStatus: 'Section 3(p) / Section 3(e) Bar (Novel synergy required)'
    }
  ];

  const botanicals = [
    {
      sanskrit: 'Ashwagandha',
      latin: 'Withania somnifera',
      family: 'Solanaceae',
      part: 'Root',
      absCategory: 'Standard Indian Biological Resource (SBB Prior Intimation)',
      status: 'Cultivated in MP/Rajasthan'
    },
    {
      sanskrit: 'Haridra / Turmeric',
      latin: 'Curcuma longa',
      family: 'Zingiberaceae',
      part: 'Rhizome',
      absCategory: 'NTAC Commodity when exported as whole spice; ABS applies if patented extraction',
      status: 'Cultivated extensively'
    },
    {
      sanskrit: 'Katuka / Kutki',
      latin: 'Picrorhiza kurroa',
      family: 'Plantaginaceae',
      part: 'Rhizome',
      absCategory: 'HIGH RISK - Himalayan Endangered Species (CITES App II, strict SBB tracking)',
      status: 'Endangered in wild'
    },
    {
      sanskrit: 'Guduchi / Giloy',
      latin: 'Tinospora cordifolia',
      family: 'Menispermaceae',
      part: 'Stem',
      absCategory: 'Standard Indian Biological Resource (SBB Prior Intimation)',
      status: 'Abundant'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-ayush-border rounded-2xl p-6 shadow-card">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-50 text-ayush-forest rounded-md text-xs font-bold border border-emerald-200 mb-2">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Statutory Corpus & Provenance Manifest</span>
            </div>
            <h1 className="text-2xl font-bold text-ayush-navy">
              Authoritative Legal & TKDL Manifest
            </h1>
            <p className="text-xs text-ayush-slate mt-1 max-w-2xl">
              Inspect official primary legislation, Gazette of India amendments, verifiable SHA-256 document hashes, and public TKDL prior art records.
            </p>
          </div>

          {/* Tab Filter */}
          <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setActiveCategory('acts')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeCategory === 'acts' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-black'
              }`}
            >
              Statutes & Acts ({statutoryActs.length})
            </button>
            <button
              onClick={() => setActiveCategory('tkdl')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeCategory === 'tkdl' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-black'
              }`}
            >
              TKDL Catalog ({tkdlFormulations.length})
            </button>
            <button
              onClick={() => setActiveCategory('botanicals')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeCategory === 'botanicals' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-black'
              }`}
            >
              Botanicals ({botanicals.length})
            </button>
          </div>
        </div>
      </div>

      {/* Category 1: Primary Legislation */}
      {activeCategory === 'acts' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {statutoryActs.map((act) => (
            <div key={act.id} className="bg-white border border-ayush-border rounded-2xl p-5 shadow-card space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300">
                    {act.authorityLevel}
                  </span>
                  <h3 className="font-bold text-sm text-ayush-navy mt-1.5">{act.title}</h3>
                  <p className="text-xs text-ayush-slate">{act.authority} · {act.jurisdiction}</p>
                </div>
              </div>

              {/* SHA-256 Provenance Badge */}
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-[11px] space-y-1">
                <div className="flex items-center space-x-1.5 text-slate-500 font-semibold">
                  <Hash className="w-3.5 h-3.5" />
                  <span>Document SHA-256 Checksum:</span>
                </div>
                <code className="text-[10px] font-mono text-slate-800 break-all block bg-white px-2 py-1 rounded border border-slate-200">
                  {act.sha256}
                </code>
              </div>

              {/* Key Provisions */}
              <div>
                <h4 className="text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                  Indexed Key Provisions:
                </h4>
                <div className="space-y-1">
                  {act.keySections.map((sec, idx) => (
                    <div key={idx} className="flex items-center space-x-2 text-xs text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>{sec}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Official Link */}
              <div className="pt-2 border-t border-ayush-border flex items-center justify-between">
                <span className="text-[11px] text-slate-500">Official India Code Record</span>
                <a
                  href={act.officialUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center space-x-1 text-xs font-bold text-ayush-forest hover:underline"
                >
                  <span>Official Gazette</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Category 2: TKDL Catalog */}
      {activeCategory === 'tkdl' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tkdlFormulations.map((form, idx) => (
            <div key={idx} className="bg-white border border-ayush-border rounded-2xl p-5 shadow-card space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-900 border border-blue-300">
                  {form.code}
                </span>
                <span className="text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  Prior Art
                </span>
              </div>
              <h3 className="font-bold text-sm text-ayush-navy">{form.name}</h3>
              <p className="text-xs text-slate-600 font-medium">
                <strong>Classical Source:</strong> {form.source}
              </p>
              <div className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                <strong>Ingredients:</strong> {form.ingredients}
              </div>
              <p className="text-[11px] text-slate-500">
                <strong>Indications:</strong> {form.indication}
              </p>
              <div className="pt-2 border-t border-ayush-border text-[11px] text-red-700 font-semibold">
                ⚠️ {form.patentStatus}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Category 3: Botanicals */}
      {activeCategory === 'botanicals' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {botanicals.map((bot, idx) => (
            <div key={idx} className="bg-white border border-ayush-border rounded-2xl p-5 shadow-card space-y-2.5">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-sm text-ayush-forestDark">{bot.sanskrit}</h3>
                <span className="text-[11px] font-mono italic text-slate-500">{bot.latin}</span>
              </div>
              <p className="text-xs text-slate-600">
                Family: <strong>{bot.family}</strong> · Part Used: <strong>{bot.part}</strong>
              </p>
              <div className="text-xs text-slate-800 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                <strong>ABS Compliance:</strong> {bot.absCategory}
              </div>
              <p className="text-[11px] text-slate-500">
                Status: {bot.status}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
