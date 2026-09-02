import csv
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("AyuRaksha.Taxonomy")

# ---------------------------------------------------------------------------
# Curated botanical enrichment: common English / vernacular aliases for
# high-value Ayurvedic medicinal plants. Sourced from authoritative references
# (Ministry of Ayush E-Charak, National Medicinal Plants Board, WHO/API):
#   * https://echarak.ayush.gov.in/knowledge_resources  (Medicinal Plants List)
#   * https://www.nmpb.nic.in/medicinal_list
#   * Ayurvedic Pharmacopoeia of India (single botanical drugs)
# The base plants.csv (TKDL) stores canonical Sanskrit/scientific names; many
# queries refer to these species by common English names (e.g. "ashwagandha",
# "giloy", "amla") that are not present as lookup keys. This alias map bridges
# that gap so text resolution, entity extraction, and dossier generation can
# map colloquial names to their scientific binomial.
# ---------------------------------------------------------------------------
BOTANICAL_ALIASES = {
    "Withania somnifera": [
        "ashwagandha", "ashvagandha", "winter cherry", "wintercherry",
        "indian ginseng", "asgandh", "aswagandha",
    ],
    "Azadirachta indica": [
        "neem", "nimba", "indian lilac", "margosa tree", "nim tree",
    ],
    "Ocimum sanctum": [
        "tulsi", "tulasi", "tulshi", "holy basil", "sacred basil", "krishna tulsi",
    ],
    "Ocimum tenuiflorum": [
        "tulsi", "tulasi", "holy basil", "sacred basil",
    ],
    "Tinospora cordifolia": [
        "giloy", "guduchi", "giloya", "amrita", "heart-leaved moonseed",
    ],
    "Phyllanthus emblica": [
        "amla", "amalaki", "indian gooseberry", "emblic myrobalan",
    ],
    "Emblica officinalis": [
        "amla", "amalaki", "indian gooseberry", "emblic myrobalan",
    ],
    "Bacopa monnieri": [
        "brahmi", "water hyssop", "indian pennywort",
    ],
    "Centella asiatica": [
        "brahmi", "gotu kola", "indian pennywort", "mandukaparni",
    ],
    "Asparagus racemosus": [
        "shatavari", "shatamuli", "hundred roots", "shatawari",
    ],
    "Saraca asoca": [
        "ashoka", "sita ashoka",
    ],
    "Terminalia bellirica": [
        "bibhitaki", "beleric", "baheda",
    ],
    "Terminalia chebula": [
        "haritaki", "harada", "chebulic myrobalan",
    ],
    "Terminalia arjuna": [
        "arjuna", "arjun tree",
    ],
    "Curcuma longa": [
        "turmeric", "haldi", "haridra",
    ],
    "Zingiber officinale": [
        "ginger", "adrak", "shunti", "shunthi",
    ],
    "Piper longum": [
        "pippali", "long pepper", "pipali",
    ],
    "Piper nigrum": [
        "black pepper", "maricha", "marich",
    ],
    "Glycyrrhiza glabra": [
        "licorice", "liquorice", "yashtimadhu", "mulethi",
    ],
    "Commiphora wightii": [
        "guggul", "guggulu", "indian bdellium",
    ],
    "Asparagus adscendens": [
        "safed musli", "shweta musli",
    ],
    "Mucuna pruriens": [
        "kapikachhu", "cowhage", "velvet bean", "kaunch",
    ],
    "Sida cordifolia": [
        "bala", "country mallow",
    ],
    "Boerhavia diffusa": [
        "punarnava", "spreading hogweed",
    ],
    "Tribulus terrestris": [
        "gokshura", "puncture vine", "land caltrops",
    ],
    "Tectona grandis": [
        "teak", "sagwan",
    ],
    "Santalum album": [
        "sandalwood", "chandana", "chandan",
    ],
    "Pterocarpus santalinus": [
        "red sandalwood", "rakta chandana", "raktachandan",
    ],
    "Aquilaria malaccensis": [
        "agarwood", "eaglewood", "agar", "aloewood", "agaru",
    ],
    "Picrorhiza kurroa": [
        "kutki", "katuki", "picrorhiza", "himalayan kutki",
    ],
    "Berberis aristata": [
        "daruharidra", "indian barberry", "tree turmeric",
    ],
    "Aegle marmelos": [
        "bael", "bilva", "bel fruit", "bengal quince",
    ],
    "Elettaria cardamomum": [
        "cardamom", "elaichi", "ela",
    ],
    "Myristica fragrans": [
        "nutmeg", "jaiphal", "jati",
    ],
    "Cinnamomum verum": [
        "cinnamon", "dalchini", "tvak",
    ],
    "Foeniculum vulgare": [
        "fennel", "saunf", "mishreya",
    ],
    "Coriandrum sativum": [
        "coriander", "dhaniya", "dhanyaka",
    ],
    "Allium sativum": [
        "garlic", "lasuna", "lassan",
    ],
    "Vitis vinifera": [
        "grapes", "draksha", "drakh",
    ],
    "Punica granatum": [
        "pomegranate", "dadima", "anar",
    ],
    "Sesamum indicum": [
        "sesame", "til", "tila",
    ],
    "Anacyclus pyrethrum": [
        "akarkara", "pellitory",
    ],
    "Withania coagulans": [
        "paneer dodi", "indian rennet",
    ],
    "Hemidesmus indicus": [
        "anantmool", "sarsaparilla", "anantamula",
    ],
    "Nigella sativa": [
        "black cumin", "kalonji", "black seed", "upakunchika",
    ],
}

class TKDLTaxonomyEngine:
    """
    In-memory indexing and resolution engine for TKDL and Ayurvedic corpus CSVs:
    - ayurveda_books.csv (121 Classical First Schedule Texts)
    - plants.csv (335 Botanical Species & Vernaculars)
    - minerals.csv (34 Rasashastra Minerals)
    - diseases.csv (155 Ayurvedic & Modern Disease Terms)
    - drug_properties.csv (Karmas, Rasas, Viryas)
    - glossary.csv (422 Clinical & Statutory Terms with Definitions)
    - entities.csv (688 Unified Named Entities)
    """

    def __init__(self, csv_dir: Optional[Path] = None):
        self.csv_dir = csv_dir or Path(__file__).resolve().parents[3] / "data" / "corpus" / "csv files"
        self._plants: List[Dict[str, Any]] = []
        self._books: List[Dict[str, Any]] = []
        self._minerals: List[Dict[str, Any]] = []
        self._diseases: List[Dict[str, Any]] = []
        self._glossary: List[Dict[str, Any]] = []
        self._entities: List[Dict[str, Any]] = []
        self._botanical_lookup: Dict[str, Dict[str, Any]] = {}
        self._loaded = False
        self.load_corpus()

    def _read_csv(self, filename: str) -> List[Dict[str, str]]:
        file_path = self.csv_dir / filename
        if not file_path.exists():
            logger.warning(f"CSV file not found: {file_path}")
            return []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                return [dict(row) for row in reader]
        except Exception as e:
            logger.error(f"Failed to read CSV {filename}: {e}")
            return []

    def load_corpus(self):
        if self._loaded:
            return

        self._books = self._read_csv("ayurveda_books.csv")
        self._plants = self._read_csv("plants.csv")
        self._minerals = self._read_csv("minerals.csv")
        self._diseases = self._read_csv("diseases.csv")
        self._glossary = self._read_csv("glossary.csv")
        self._entities = self._read_csv("entities.csv")

        # Build fast botanical lookup
        for plant in self._plants:
            sci = plant.get("scientific_name", "").strip()
            sans = plant.get("sanskrit_name", "").strip()
            common = plant.get("common_name", "").strip()

            entry = {
                "entity_id": plant.get("entity_id", ""),
                "scientific_name": sci,
                "sanskrit_name": sans,
                "common_name": common,
                "unani_name": plant.get("unani_name", ""),
                "siddha_name": plant.get("siddha_name", "")
            }

            # Map keys in lowercase (allow 3+ char vernaculars like "neem"/"til").
            # Scientific names are kept whole (a "/" indicates an ambiguous multi-taxon
            # conversion string and must not split into spurious single-genus keys).
            def _key_values(value: str):
                if not value:
                    return []
                if value == sci:
                    return [value.strip().lower()]
                return [sub.strip().lower() for sub in re.split(r"[,/&]+", value) if len(sub.strip()) >= 3]

            for value in (sci, sans, common):
                for sub in _key_values(value or ""):
                    if len(sub) >= 3:
                        self._botanical_lookup.setdefault(sub, entry)

        # Apply curated alias map so common English names resolve to canonical species
        for sci_name, aliases in BOTANICAL_ALIASES.items():
            canonical = self._botanical_lookup.get(sci_name.lower())
            if canonical is None:
                # Prefer an explicit binomial match (skip combined / alternative taxon strings)
                sci_lower = sci_name.lower()
                genus = sci_lower.split(" ")[0]
                candidates = [
                    entry for entry in self._botanical_lookup.values()
                    if entry.get("scientific_name")
                    and entry["scientific_name"].lower().startswith(genus)
                ]
                candidates.sort(key=lambda e: (
                    1 if "/" in e["scientific_name"] else 0,  # prefer single-taxon rows
                    0 if sci_lower in e["scientific_name"].lower() else 1,
                ))
                canonical = candidates[0] if candidates else None
            if canonical is None:
                canonical = {
                    "entity_id": "ENRICH",
                    "scientific_name": sci_name,
                    "sanskrit_name": "",
                    "common_name": aliases[0].title() if aliases else sci_name,
                    "unani_name": "",
                    "siddha_name": ""
                }
            for alias in aliases:
                alias = alias.strip().lower()
                if len(alias) >= 3:
                    self._botanical_lookup.setdefault(alias, canonical)

        # Also map unified entities
        for ent in self._entities:
            b_name = ent.get("botanical_name", "").strip()
            s_name = ent.get("sanskrit_name", "").strip()
            c_name = ent.get("common_name", "").strip()
            h_name = ent.get("hindi_name", "").strip()
            entry = {
                "entity_id": ent.get("entity_id", ""),
                "entity_type": ent.get("entity_type", "plant"),
                "canonical_name": ent.get("canonical_name", ""),
                "botanical_name": b_name,
                "sanskrit_name": s_name,
                "common_name": c_name,
                "hindi_name": h_name
            }
            if s_name:
                self._botanical_lookup.setdefault(s_name.lower(), entry)
            if b_name:
                self._botanical_lookup.setdefault(b_name.lower(), entry)
            if h_name:
                self._botanical_lookup.setdefault(h_name.lower(), entry)

        self._loaded = True
        logger.info(f"Loaded TKDL taxonomy: {len(self._plants)} plants, {len(self._books)} classical books, {len(self._glossary)} glossary terms, {len(self._entities)} entities.")

    def resolve_botanicals_in_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans a text for plant/botanical references and returns matched botanical records.
        """
        text_lower = text.lower()
        matched = []
        seen_ids = set()

        # Check known lookup terms
        for term, record in self._botanical_lookup.items():
            if len(term) < 3:
                continue
            # Regex boundary match
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                eid = record.get("entity_id") or record.get("botanical_name") or term
                if eid not in seen_ids:
                    seen_ids.add(eid)
                    sci = record.get("scientific_name") or record.get("botanical_name", "")
                    matched.append({
                        "matched_term": term,
                        "scientific_name": sci,
                        "botanical_name": sci,
                        "sanskrit_name": record.get("sanskrit_name", ""),
                        "common_name": record.get("common_name", ""),
                        "unani_name": record.get("unani_name", ""),
                        "siddha_name": record.get("siddha_name", ""),
                        "details": record
                    })
        return matched

    def resolve_plant(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Resolves a plant by common, Sanskrit, Unani, or scientific name and returns
        a normalized botanical record, or ``None`` if it cannot be identified.
        Used by the compliance dossier generator to enrich ingredient provenance.
        """
        if not name:
            return None
        key = name.strip().lower()
        record = self._botanical_lookup.get(key)
        if record is None:
            # Fall back to a partial match on the scientific binomial (first genus word)
            matches = self.search_plants(name, limit=1)
            if matches:
                first = matches[0]
                return {
                    "scientific_name": first.get("scientific_name", ""),
                    "sanskrit_name": first.get("sanskrit_name", ""),
                    "common_name": first.get("common_name", ""),
                    "unani_name": first.get("unani_name", ""),
                    "siddha_name": first.get("siddha_name", ""),
                    "matched_term": key
                }
            return None
        return {
            "scientific_name": record.get("scientific_name") or record.get("botanical_name", ""),
            "sanskrit_name": record.get("sanskrit_name", ""),
            "common_name": record.get("common_name", ""),
            "unani_name": record.get("unani_name", ""),
            "siddha_name": record.get("siddha_name", ""),
            "matched_term": key
        }

    def is_classical_text(self, text_name: str) -> bool:
        """
        Checks if a given book/text title is registered in the First Schedule / TKDL catalogue.
        """
        t_clean = text_name.lower().strip()
        for book in self._books:
            title = book.get("title", "").lower()
            if t_clean in title or title in t_clean:
                return True
        return False

    def search_books(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        if not query.strip():
            return self._books[:limit]
        q = query.lower()
        res = [
            b for b in self._books
            if q in b.get("title", "").lower() or q in b.get("author", "").lower() or q in b.get("description", "").lower()
        ]
        return res[:limit]

    def search_plants(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        if not query.strip():
            return self._plants[:limit]
        q = query.lower()
        res = [
            p for p in self._plants
            if q in p.get("scientific_name", "").lower()
            or q in p.get("sanskrit_name", "").lower()
            or q in p.get("common_name", "").lower()
            or q in p.get("unani_name", "").lower()
            or q in p.get("siddha_name", "").lower()
        ]
        return res[:limit]

    def search_glossary(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        if not query.strip():
            return self._glossary[:limit]
        q = query.lower()
        res = [
            g for g in self._glossary
            if q in g.get("term", "").lower()
            or q in g.get("category", "").lower()
            or q in g.get("definition", "").lower()
        ]
        return res[:limit]

    def search_entities(self, query: str = "", entity_type: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        res = self._entities
        if entity_type:
            res = [e for e in res if e.get("entity_type", "").lower() == entity_type.lower()]
        if query.strip():
            q = query.lower()
            res = [
                e for e in res
                if q in e.get("canonical_name", "").lower()
                or q in e.get("botanical_name", "").lower()
                or q in e.get("sanskrit_name", "").lower()
                or q in e.get("common_name", "").lower()
                or q in e.get("synonyms", "").lower()
            ]
        return res[:limit]

    def get_corpus_statistics(self) -> Dict[str, int]:
        return {
            "classical_books_count": len(self._books),
            "plants_count": len(self._plants),
            "minerals_count": len(self._minerals),
            "diseases_count": len(self._diseases),
            "glossary_terms_count": len(self._glossary),
            "unified_entities_count": len(self._entities)
        }

# Global singleton instance
taxonomy_engine = TKDLTaxonomyEngine()
