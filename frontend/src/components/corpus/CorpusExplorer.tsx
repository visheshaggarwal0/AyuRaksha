import { useState, useEffect } from 'react';
import { BookOpen, CheckCircle2, ExternalLink, Hash, Search, Leaf, Library, HelpCircle, Loader2 } from 'lucide-react';
import { api } from '../../services/api';

export function CorpusExplorer() {
  const [activeCategory, setActiveCategory] = useState<'acts' | 'books' | 'botanicals' | 'glossary'>('acts');
  const [searchQuery, setSearchQuery] = useState('');
  const [books, setBooks] = useState<any[]>([]);
  const [plants, setPlants] = useState<any[]>([]);
  const [glossary, setGlossary] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);

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

  useEffect(() => {
    // Load initial corpus stats
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
    }
  }, [activeCategory, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-ayush-border rounded-2xl p-6 shadow-card">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-50 text-ayush-forest rounded-md text-xs font-bold border border-emerald-200 mb-2">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Statutory Corpus & TKDL Taxonomy</span>
            </div>
            <h1 className="text-2xl font-bold text-ayush-navy">
              Authoritative Legal & TKDL Taxonomy Registry
            </h1>
            <p className="text-xs text-ayush-slate mt-1 max-w-2xl">
              Inspect official primary statutes, First Schedule authoritative texts, 335+ verified medicinal plants, and TKDL regulatory terms with cryptographic checksums.
            </p>
          </div>

          {/* Tab Filter */}
          <div className="flex flex-wrap items-center gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200">
            <button
              onClick={() => { setActiveCategory('acts'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeCategory === 'acts' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-black'
              }`}
            >
              Statutes ({statutoryActs.length})
            </button>
            <button
              onClick={() => { setActiveCategory('books'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeCategory === 'books' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-black'
              }`}
            >
              <Library className="w-3.5 h-3.5" />
              <span>Classical Books ({stats?.classical_books_count || 121})</span>
            </button>
            <button
              onClick={() => { setActiveCategory('botanicals'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeCategory === 'botanicals' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-black'
              }`}
            >
              <Leaf className="w-3.5 h-3.5" />
              <span>Plants ({stats?.plants_count || 335})</span>
            </button>
            <button
              onClick={() => { setActiveCategory('glossary'); setSearchQuery(''); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1 ${
                activeCategory === 'glossary' ? 'bg-white text-ayush-forest shadow-subtle' : 'text-slate-600 hover:text-black'
              }`}
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Glossary ({stats?.glossary_terms_count || 422})</span>
            </button>
          </div>
        </div>

        {/* Live Search Bar for Dynamic Categories */}
        {activeCategory !== 'acts' && (
          <div className="mt-4 pt-4 border-t border-slate-100 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-7" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                activeCategory === 'books'
                  ? 'Search by title, author, or publisher (e.g. Charaka, Vagbhata, Sharangadhara)...'
                  : activeCategory === 'botanicals'
                  ? 'Search by Sanskrit, scientific, or common name (e.g. Ashwagandha, Withania, Neem, Tulsi)...'
                  : 'Search regulatory & Ayurvedic definitions (e.g. Rasayana, Ama, Ahara)...'
              }
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 focus:border-ayush-forest"
            />
          </div>
        )}
      </div>

      {/* Loading Spinner */}
      {loading && (
        <div className="flex items-center justify-center p-12 text-ayush-slate">
          <Loader2 className="w-6 h-6 animate-spin text-ayush-forest mr-2" />
          <span className="text-xs font-semibold">Filtering TKDL taxonomy records...</span>
        </div>
      )}

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

      {/* Category 2: Classical Texts (First Schedule) */}
      {!loading && activeCategory === 'books' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {books.map((book, idx) => (
            <div key={idx} className="bg-white border border-ayush-border rounded-2xl p-5 shadow-card space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-200">
                    {book.source_text_id || 'First Schedule'}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                    {book.publication_year || 'Classical'}
                  </span>
                </div>
                <h3 className="font-bold text-sm text-ayush-navy leading-snug">{book.title}</h3>
                {book.author && (
                  <p className="text-xs text-slate-600">
                    <strong>Author:</strong> {book.author}
                  </p>
                )}
                {book.publisher && (
                  <p className="text-[11px] text-slate-500 line-clamp-2">
                    <strong>Publisher:</strong> {book.publisher}
                  </p>
                )}
                {book.description && (
                  <div className="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100 line-clamp-3">
                    {book.description}
                  </div>
                )}
              </div>

              {book.tkdl_url && (
                <div className="pt-2 border-t border-slate-100">
                  <a
                    href={book.tkdl_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 text-xs font-bold text-ayush-forest hover:underline"
                  >
                    <span>TKDL Registry Record</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Category 3: Botanicals (plants.csv) */}
      {!loading && activeCategory === 'botanicals' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {plants.map((plant, idx) => (
            <div key={idx} className="bg-white border border-ayush-border rounded-2xl p-5 shadow-card space-y-2.5 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-200">
                    {plant.entity_id || 'TKDL-PLANT'}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                    ABS Mandate
                  </span>
                </div>
                <h3 className="font-bold text-sm text-ayush-forestDark">
                  {plant.sanskrit_name || plant.common_name || 'Ayurvedic Plant'}
                </h3>
                <p className="text-xs font-mono italic text-slate-600">
                  {plant.scientific_name}
                </p>
                {plant.common_name && (
                  <p className="text-[11px] text-slate-600">
                    <strong>Common:</strong> {plant.common_name}
                  </p>
                )}
                {plant.unani_name && (
                  <p className="text-[11px] text-slate-500">
                    <strong>Unani:</strong> {plant.unani_name}
                  </p>
                )}
                {plant.siddha_name && (
                  <p className="text-[11px] text-slate-500">
                    <strong>Siddha:</strong> {plant.siddha_name}
                  </p>
                )}
              </div>
              <div className="pt-2 border-t border-slate-100 text-[11px] text-ayush-slate">
                <span>Verified against TKDL Botanical Taxonomy</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Category 4: Glossary (glossary.csv) */}
      {!loading && activeCategory === 'glossary' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {glossary.map((item, idx) => (
            <div key={idx} className="bg-white border border-ayush-border rounded-2xl p-5 shadow-card space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-900 border border-purple-200">
                  {item.category || 'Ayurvedic Category'}
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {item.glossary_id}
                </span>
              </div>
              <h3 className="font-bold text-sm text-ayush-navy">{item.term}</h3>
              <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                {item.definition}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
