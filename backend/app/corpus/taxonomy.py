import csv
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("AyuRaksha.Taxonomy")

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

            # Map keys in lowercase
            if sans:
                self._botanical_lookup[sans.lower()] = entry
            if sci:
                self._botanical_lookup[sci.lower()] = entry
            if common:
                for sub in common.split(","):
                    sub_clean = sub.strip().lower()
                    if len(sub_clean) >= 3:
                        self._botanical_lookup[sub_clean] = entry

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
            if len(term) < 4:
                continue
            # Regex boundary match
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                eid = record.get("entity_id") or record.get("botanical_name") or term
                if eid not in seen_ids:
                    seen_ids.add(eid)
                    matched.append({
                        "matched_term": term,
                        "botanical_name": record.get("scientific_name") or record.get("botanical_name", ""),
                        "sanskrit_name": record.get("sanskrit_name", ""),
                        "common_name": record.get("common_name", ""),
                        "details": record
                    })
        return matched

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
