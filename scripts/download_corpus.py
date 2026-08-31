"""
AyuRaksha Corpus Downloader — Layer 1 Raw Source Acquisition
- Reads data/corpus/manifests/source_manifest_50.json
- Downloads authoritative primary source PDFs and official Gazette files
- Saves to data/corpus/<local_path>
- Computes SHA-256 hash and updates manifest
"""
import json
import hashlib
import pathlib
import sys
import urllib.request
import ssl
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "corpus" / "manifests" / "source_manifest_50.json"

# High-reliability direct download endpoints from official government portals
OFFICIAL_DIRECT_URLS = {
    "IND_PATENTS_ACT_1970": "https://www.ipindia.gov.in/writereaddata/Portal/IPOAct/1_31_1_patent-act-1970-11march2015.pdf",
    "IND_PATENTS_RULES_2003_2024": "https://www.ipindia.gov.in/writereaddata/Portal/Images/pdf/Patents_Amendment_Rules_2024.pdf",
    "IND_PATENT_MANUAL_2025": "https://www.ipindia.gov.in/writereaddata/Portal/Images/pdf/Manual_for_Patent_Office_Practice_and_Procedure_.pdf",
    "IND_PATENTS_AMEND_2024": "https://www.ipindia.gov.in/writereaddata/Portal/Images/pdf/Patents_Amendment_Rules_2024.pdf",
    "IND_BIOLOGICAL_DIVERSITY_ACT_2002": "https://nbaindia.org/uploaded/act/BDACT_2002.pdf",
    "IND_BIOLOGICAL_DIVERSITY_AMEND_2023": "https://nbaindia.org/uploaded/pdf/Biological_Diversity_Amendment_Act_2023.pdf",
    "IND_BD_RULES_2004": "https://nbaindia.org/uploaded/act/bdrules2004.pdf",
    "IND_ABS_REGULATIONS_2014": "https://nbaindia.org/uploaded/pdf/ABS_Guidance_Regulations_2014.pdf",
    "IND_DRUGS_COSMETICS_ACT_1940_ASU": "https://cdsco.gov.in/opencms/export/sites/CDSCO_Web/Pdf-documents/acts_rules/2016DrugsandCosmeticsAct1940Rules1945.pdf",
    "IND_DRUGS_COSMETICS_RULES_1945_ASU": "https://ayush.gov.in/docs/drugs-and-cosmetics-rules-1945.pdf",
    "IND_FSSAI_AYURVEDA_AAHARA_2022": "https://fssai.gov.in/upload/notifications/2022/05/627a195ca5b2aGazette_Notification_Ayurveda_Aahara_06_05_2022.pdf",
    "IND_DRUGS_MAGIC_REMEDIES_ACT_1954": "https://www.indiacode.nic.in/bitstream/123456789/1393/1/A1954-21.pdf",
    "IND_TRADE_MARKS_ACT_1999": "https://www.ipindia.gov.in/writereaddata/Portal/IPOAct/1_43_1_trade-marks-act.pdf",
    "INT_WIPO_GRATK_TREATY_2024": "https://www.wipo.int/edocs/mdocs/tk/en/gratk_dc/gratk_dc_7.pdf",
    "INT_NAGOYA_PROTOCOL_2010": "https://www.cbd.int/abs/doc/protocol/nagoya-protocol-en.pdf"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def download_one(url: str, dest: pathlib.Path, timeout=45) -> tuple[bool, str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read()
            if len(data) > 500:
                dest.write_bytes(data)
                return True, f"{len(data)} bytes ({len(data)//1024} KB)"
            return False, f"Empty response ({len(data)} bytes)"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def main():
    if not MANIFEST.exists():
        print(f"[!] Manifest not found: {MANIFEST}", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = manifest["sources"]
    total = len(sources)

    print(f"[*] AyuRaksha Raw Layer (Layer 1) Downloader")
    print(f"[*] Processing {total} sources...")
    print("=" * 70)

    downloaded = 0
    existing = 0
    failed = 0

    for idx, src in enumerate(sources, start=1):
        doc_id = src["document_id"]
        local_path = ROOT / "data" / "corpus" / src["local_path"]
        
        # Pick direct government portal endpoint or fallback
        url = OFFICIAL_DIRECT_URLS.get(doc_id, src["source"]["url"])

        # Download if missing
        if not local_path.exists():
            print(f"[{idx:02d}/{total}] Downloading {doc_id} -> {local_path.name}")
            ok, msg = download_one(url, local_path)
            if ok:
                downloaded += 1
                print(f"      [✓] Success: {msg}")
            else:
                failed += 1
                print(f"      [✗] Failed: {msg} ({url})")
        else:
            existing += 1

        # Calculate exact SHA-256 and byte size
        if local_path.exists():
            sha = sha256_file(local_path)
            size = local_path.stat().st_size
            src["source"]["sha256"] = sha
            src["source"]["file_size_bytes"] = size
            src["source"]["retrieved_at"] = datetime.now(timezone.utc).isoformat()

    # Save manifest with exact SHA-256 hashes
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print("=" * 70)
    print(f"[COMPLETED] Layer 1 Raw Sources Updated.")
    print(f" - Downloaded: {downloaded}")
    print(f" - Existing on disk: {existing}")
    print(f" - Failed: {failed}")
    print(f" - Manifest SHA-256 checksums synchronized with disk.")

if __name__ == "__main__":
    main()
