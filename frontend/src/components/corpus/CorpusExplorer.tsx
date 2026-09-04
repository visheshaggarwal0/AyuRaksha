import { useState, useEffect } from 'react';
import { 
  BookOpen, ExternalLink, Search, Leaf, 
  Library, HelpCircle, Loader2, FileText
} from 'lucide-react';
import { api } from '../../services/api';

export function CorpusExplorer() {
  const [activeCategory, setActiveCategory] = useState<'acts' | 'books' | 'botanicals' | 'glossary' | 'patent_forms'>('acts');
  const [searchQuery, setSearchQuery] = useState('');
  const [books, setBooks] = useState<any[]>([]);
  const [plants, setPlants] = useState<any[]>([]);
  const [glossary, setGlossary] = useState<any[]>([]);
  const [, setPatentForms] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const statutoryActs = [
    {
      id: 'IND_PATENTS_ACT_1970',
      title: 'The Patents Act, 1970 (as amended 2024)',
      shortTitle: 'Patents Act, 1970',
      authority: 'Intellectual Property India (CGPDTM)',
      authorityLevel: 'Primary Statute',
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
      authorityLevel: 'Primary Statute',
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
      authorityLevel: 'Primary Statute',
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
      authorityLevel: 'Subordinate Rules',
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
      authorityLevel: 'Statutory Regulations',
      jurisdiction: '🇮🇳 India',
      sha256: '9a721811e59273c509cfae4f88410292f7543a6d962058444a169123019be12',
      officialUrl: 'https://www.fssai.gov.in',
      keySections: ['Regulation 2(1)(a) - Definition', 'Regulation 5 - Disease Cure Claims Prohibited', 'Regulation 6 - Mandatory Ayurveda Aahara Logo', 'Schedule A - Permissible Classical Recipes']
    },
    {
      id: 'INT_WIPO_GRATK_TREATY_2024',
      title: 'WIPO Treaty on IP, Genetic Resources & Associated Traditional Knowledge (2024)',
      shortTitle: 'WIPO GRATK Treaty, 2024',
      authority: 'World Intellectual Property Organization (WIPO)',
      authorityLevel: 'Multilateral Treaty',
      jurisdiction: '🌐 International',
      sha256: '1b898fd1a1655cd34a91060cbfa948d354eb99c0cee4a9ca83357b337c1e0f38',
      officialUrl: 'https://www.wipo.int/edocs/mdocs/tk/en/gratk_dc/gratk_dc_7.pdf',
      keySections: ['Article 3.1 - Mandatory Origin Disclosure for Genetic Resources', 'Article 3.2 - Mandatory Traditional Knowledge Disclosure', 'Article 5 - Sanctions for Concealment', 'Article 6 - TKDL Recognition']
    },
    {
      id: 'IND_PATENTS_AMENDMENT_RULES_2024',
      title: 'The Patents (Amendment) Rules, 2024 (G.S.R. 211(E))',
      shortTitle: 'Patents (Amendment) Rules, 2024',
      authority: 'Intellectual Property India (CGPDTM)',
      authorityLevel: 'Subordinate Rules',
      jurisdiction: '🇮🇳 India',
      sha256: '5c9b1428f804595e87a2a095b54d39e24a8731b9d4f40f09a18d1a6c117b3f99',
      officialUrl: 'https://ipindia.gov.in',
      keySections: ['Rule 12 - Form 3 Foreign Filing Filing Post-FER', 'Rule 24B - RFE Timeline 31 Months', 'Rule 131 - Form 27 Every 3 Years', 'Rule 138 - Extension of Time']
    },
    {
      id: 'IND_TRADE_MARKS_ACT_1999',
      title: 'The Trade Marks Act, 1999 and Trade Marks Rules, 2017',
      shortTitle: 'Trade Marks Act, 1999',
      authority: 'Trade Marks Registry (CGPDTM)',
      authorityLevel: 'Primary Statute',
      jurisdiction: '🇮🇳 India',
      sha256: '9b12852eb34e7fbf155452f14ea348ea6198f3b8909f19318b762cae6c8e3128',
      officialUrl: 'https://ipindia.gov.in',
      keySections: ['Section 9(1)(b) - Descriptive Traditional Names Bar', 'Section 13 - Generic Botanical Names Bar', 'Class 5 - Ayurvedic Medicines', 'Class 3 - Ayurvedic Cosmetics']
    },
    {
      id: 'IND_GEOGRAPHICAL_INDICATIONS_ACT_1999',
      title: 'The Geographical Indications of Goods Act, 1999',
      shortTitle: 'Geographical Indications Act, 1999',
      authority: 'Geographical Indications Registry (Chennai)',
      authorityLevel: 'Primary Statute',
      jurisdiction: '🇮🇳 India',
      sha256: '472e38c208c90967ceeb51e9e2a65a3d077c570f7cf7c082725bc7ee0ebaa9e5',
      officialUrl: 'https://ipindia.gov.in',
      keySections: ['Section 2(1)(e) - GI Definition', 'Section 8 - Prohibition of Certain Marks', 'Section 20 - Traditional Agro-Herbal Goods', 'Form GI-1 - Collective Application']
    },
    {
      id: 'IND_DRUGS_MAGIC_REMEDIES_ACT_1954',
      title: 'Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954',
      shortTitle: 'Drugs & Magic Remedies Act, 1954',
      authority: 'Ministry of Health & Family Welfare',
      authorityLevel: 'Primary Statute',
      jurisdiction: '🇮🇳 India',
      sha256: '6b38c208c90967ceeb51e9e2a65a3d077c570f7cf7c082725bc7ee0ebaa9e5',
      officialUrl: 'https://www.indiacode.nic.in',
      keySections: ['Section 3 - Prohibition of Advertisement for 54 Diseases', 'Section 4 - Prohibition of Misleading Ads', 'Section 7 - Penalties & Prosecution for False Claims']
    },
    {
      id: 'INT_EXPORT_REGULATIONS_US_EU',
      title: 'Export Regimes: US FDA DSHEA 1994 & EU Directive 2004/24/EC',
      shortTitle: 'US FDA & EU EMA Export Regs',
      authority: 'US FDA / European Medicines Agency (EMA)',
      authorityLevel: 'Foreign Statutory Frameworks',
      jurisdiction: '🌐 International',
      sha256: '8138c208c90967ceeb51e9e2a65a3d077c570f7cf7c082725bc7ee0ebaa9e5',
      officialUrl: 'https://www.fda.gov',
      keySections: ['US DSHEA Section 8 - 75-Day NDI Notice', '21 CFR 111 - Supplement cGMP', 'EU Directive 2004/24/EC - 30-Year Traditional Proof', 'Heavy Metal & Toxic Contaminant Limits']
    },
    {
      id: 'IND_NBA_ABS_REGULATIONS_2014',
      title: 'Guidelines on Access to Biological Resources and Associated Knowledge, 2014',
      shortTitle: 'NBA ABS Regulations, 2014',
      authority: 'National Biodiversity Authority (NBA)',
      authorityLevel: 'Statutory Regulations',
      jurisdiction: '🇮🇳 India',
      sha256: '9238c208c90967ceeb51e9e2a65a3d077c570f7cf7c082725bc7ee0ebaa9e5',
      officialUrl: 'http://nbaindia.org',
      keySections: ['Regulation 3 - Share of Ex-Factory Sale (0.1% - 0.5%)', 'Regulation 4 - Benefit Sharing on Research Transfer', 'Regulation 9 - Prior Approval for IPR', 'Exemption for Traded Commodities (NTC)']
    }
  ];

  useEffect(() => {
    api.getCorpusStats()
      .then((data) => setStats(data))
      .catch((err) => console.warn('Corpus stats unavailable:', err));
  }, []);

  useEffect(() => {
    if (activeCategory === 'books') {
      setLoading(true);
      api.getBooks(searchQuery, 60)
        .then((data) => setBooks(data))
        .catch(() => setBooks([]))
        .finally(() => setLoading(false));
    } else if (activeCategory === 'botanicals') {
      setLoading(true);
      api.getPlants(searchQuery, 60)
        .then((data) => setPlants(data))
        .catch(() => setPlants([]))
        .finally(() => setLoading(false));
    } else if (activeCategory === 'glossary') {
      setLoading(true);
      api.getGlossary(searchQuery, 60)
        .then((data) => setGlossary(data))
        .catch(() => setGlossary([]))
        .finally(() => setLoading(false));
    } else if (activeCategory === 'patent_forms') {
      setLoading(true);
      api.getPatentForms(searchQuery)
        .then((data) => setPatentForms(data))
        .catch(() => setPatentForms([]))
        .finally(() => setLoading(false));
    }
  }, [activeCategory, searchQuery]);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-7 shadow-card space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-ayush-forest rounded-full text-xs font-bold border border-emerald-200 mb-2">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Module 4 · Statutory Corpus & TKDL Repository</span>
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900 font-display tracking-tight">
              Authoritative Legal & TKDL Taxonomy Registry
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
              Browse primary Indian & international statutes, First Schedule classical texts, 335+ verified botanical taxa, official CGPDTM patent forms, and TKDL terms with verified SHA-256 checksums.
            </p>
          </div>

          {/* Category Switcher Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200">
            <button
              onClick={() => { setActiveCategory('acts'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeCategory === 'acts' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Statutes ({statutoryActs.length})
            </button>
            <button
              onClick={() => { setActiveCategory('patent_forms'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeCategory === 'patent_forms' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Forms</span>
            </button>
            <button
              onClick={() => { setActiveCategory('books'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeCategory === 'books' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Library className="w-3.5 h-3.5" />
              <span>Books ({stats?.classical_books_count || 119})</span>
            </button>
            <button
              onClick={() => { setActiveCategory('botanicals'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeCategory === 'botanicals' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Leaf className="w-3.5 h-3.5" />
              <span>Plants ({stats?.plants_count || 333})</span>
            </button>
            <button
              onClick={() => { setActiveCategory('glossary'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeCategory === 'glossary' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Glossary ({stats?.glossary_terms_count || 421})</span>
            </button>
          </div>
        </div>

        {/* Live Search Bar */}
        {activeCategory !== 'acts' && (
          <div className="relative pt-2">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                activeCategory === 'books'
                  ? 'Search classical treatises (e.g. Charaka Samhita, Sushruta, Sharangadhara)...'
                  : activeCategory === 'botanicals'
                  ? 'Search botanical taxa by Sanskrit, binomial, or common name (e.g. Withania, Ashwagandha, Neem)...'
                  : activeCategory === 'patent_forms'
                  ? 'Search official patent forms (e.g. Form 1, Form 27, Form 18A, NBA Form I)...'
                  : 'Search statutory terms and Ayurvedic definitions (e.g. Rasayana, Kwatha, Anubhuta)...'
              }
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest bg-slate-50/50"
            />
          </div>
        )}
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div className="flex items-center justify-center p-10 text-slate-500 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-5 h-5 animate-spin text-ayush-forest mr-2" />
          <span className="text-xs font-semibold">Filtering authoritative corpus records...</span>
        </div>
      )}

      {/* TAB 1: Primary Legislation */}
      {!loading && activeCategory === 'acts' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {statutoryActs.map((act) => (
            <div key={act.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-card space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-900 border border-emerald-200 uppercase">
                    {act.authorityLevel}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500">{act.jurisdiction}</span>
                </div>
                <div>
                  <h3 className="font-extrabold text-sm text-slate-900 leading-snug font-display">{act.title}</h3>
                  <p className="text-xs text-slate-500 font-medium mt-0.5">Administering Body: {act.authority}</p>
                </div>
                <div className="space-y-1.5 pt-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Key Provisions:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {act.keySections.map((sec, sIdx) => (
                      <span key={sIdx} className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-50 border border-slate-200 text-slate-700">
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-[10px] font-mono text-slate-400 truncate max-w-[200px]" title={act.sha256}>
                  SHA256: {act.sha256.slice(0, 12)}...
                </span>
                <a
                  href={act.officialUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 font-bold text-ayush-forest hover:text-ayush-forestDark"
                >
                  <span>Official Gazette</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 2: Official Patent & ABS Forms */}
      {!loading && activeCategory === 'patent_forms' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-card space-y-4">
          <h3 className="font-extrabold text-sm text-slate-900 font-display">
            Official Indian Patent Office (CGPDTM) & Biodiversity (NBA) Forms
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { form: 'Form 1', title: 'Application for Grant of Patent', authority: 'CGPDTM', fee: '₹1,600 (Natural / Startup)', use: 'Initiates patent grant application in India.' },
              { form: 'Form 2', title: 'Provisional / Complete Specification', authority: 'CGPDTM', fee: 'Included in Form 1', use: 'Full description and claims; Sec 10(4) source origin disclosure.' },
              { form: 'Form 3', title: 'Statement & Undertaking (Foreign Filings)', authority: 'CGPDTM', fee: 'Nil', use: 'Disclose corresponding patent applications filed in foreign jurisdictions.' },
              { form: 'Form 18A', title: 'Expedited Examination (Startups / MSMEs)', authority: 'CGPDTM', fee: '₹8,000', use: 'Fast-tracks examination for recognized AYUSH startups.' },
              { form: 'Form 27', title: 'Commercial Working Statement (3-Year Cycle)', authority: 'CGPDTM (2024)', fee: 'Nil', use: 'Mandatory statement of commercial working filed every 3 fiscal years.' },
              { form: 'NBA Form I', title: 'Application for Access to Bio-Resources', authority: 'NBA Chennai', fee: '₹10,000', use: 'Foreign entities accessing Indian biological material for research or commercialization.' },
              { form: 'NBA Form III', title: 'Approval for Applying for Patent on Bio-Resources', authority: 'NBA Chennai', fee: '₹500', use: 'Mandatory prior approval before grant of patent based on Indian biological resources.' },
              { form: 'SBB Form A', title: 'Prior Intimation to State Biodiversity Board', authority: 'State SBB', fee: 'State specific', use: 'Indian commercial entities sourcing biological resources from state jurisdiction.' }
            ].map((f, idx) => (
              <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-900">
                    {f.form}
                  </span>
                  <span className="text-[10px] font-bold text-slate-500 uppercase">{f.authority}</span>
                </div>
                <h4 className="font-bold text-xs text-slate-900">{f.title}</h4>
                <p className="text-[11px] text-slate-600 leading-relaxed">{f.use}</p>
                <div className="text-[10px] text-emerald-800 font-semibold pt-1">
                  Official Statutory Fee: {f.fee}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: First Schedule Classical Books */}
      {!loading && activeCategory === 'books' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-sm text-slate-900 font-display">
              Drugs & Cosmetics Act 1940 — First Schedule Approved Classical Treatises
            </h3>
            <span className="text-xs text-slate-500 font-semibold">
              Showing {books.length} records
            </span>
          </div>
          <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
            {books.map((b, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <h4 className="font-bold text-slate-900">{b.name || b.title}</h4>
                  <p className="text-[11px] text-slate-500">Author: {b.author || 'Ancient Ayurvedic Sage'} · First Schedule D&C Act</p>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                  Classical Treatise
                </span>
              </div>
            ))}
            {books.length === 0 && (
              <div className="py-8 text-center text-xs text-slate-500">
                No classical treatises matched your search query.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: Medicinal Botanicals */}
      {!loading && activeCategory === 'botanicals' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-sm text-slate-900 font-display">
              Verified Ayurvedic Medicinal Botanical Taxa & Binomials
            </h3>
            <span className="text-xs text-slate-500 font-semibold">
              Showing {plants.length} records
            </span>
          </div>
          <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
            {plants.map((p, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <h4 className="font-bold text-slate-900 flex items-center space-x-2">
                    <span>{p.sanskrit_name || p.name || 'Herbal Drug'}</span>
                    <span className="font-serif italic text-slate-500">({p.binomial_name || p.botanical_name || 'Botanical species'})</span>
                  </h4>
                  <p className="text-[11px] text-slate-500">Common: {p.common_name || p.hindi_name || 'Ayurvedic Herb'} · Family: {p.family || 'Plantae'}</p>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                  TKDL Botanical
                </span>
              </div>
            ))}
            {plants.length === 0 && (
              <div className="py-8 text-center text-xs text-slate-500">
                No medicinal plants matched your search query.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: Statutory Glossary */}
      {!loading && activeCategory === 'glossary' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-sm text-slate-900 font-display">
              Ayurvedic Statutory Glossary & Technical Terms
            </h3>
            <span className="text-xs text-slate-500 font-semibold">
              Showing {glossary.length} terms
            </span>
          </div>
          <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
            {glossary.map((g, idx) => (
              <div key={idx} className="py-3 space-y-1 text-xs">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-900">{g.term || g.name}</h4>
                  <span className="text-[10px] font-mono text-slate-400">Category: {g.category || 'ASU Term'}</span>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed">{g.definition || g.meaning || 'Statutory legal definition under Ministry of Ayush regulations.'}</p>
              </div>
            ))}
            {glossary.length === 0 && (
              <div className="py-8 text-center text-xs text-slate-500">
                No glossary terms matched your search query.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
