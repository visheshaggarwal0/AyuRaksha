import os
import json
import hashlib
import httpx
import asyncio
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MANIFEST_PATH = BASE_DIR / "data" / "corpus" / "manifests" / "source_manifest_50.json"
RAW_BASE_DIR = BASE_DIR / "data" / "corpus" / "raw"

# Direct official fallback URLs / download mirrors for core legislation
OFFICIAL_DIRECT_DOWNLOADS = {
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

def calculate_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

async def download_file(client: httpx.AsyncClient, url: str, target_path: Path) -> bool:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        print(f"[*] Downloading: {url} -> {target_path.name}")
        resp = await client.get(url, headers=headers, follow_redirects=True, timeout=45.0)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(target_path, "wb") as f:
                f.write(resp.content)
            print(f"[+] Downloaded ({len(resp.content) // 1024} KB): {target_path.name}")
            return True
        else:
            print(f"[-] Failed HTTP {resp.status_code} for {url}")
            return False
    except Exception as e:
        print(f"[!] Error downloading {url}: {e}")
        return False

async def run_raw_source_ingestion():
    if not MANIFEST_PATH.exists():
        print(f"[!] Manifest not found at {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    sources = manifest_data.get("sources", [])
    print(f"[*] Starting Raw Source Layer download for {len(sources)} sources...")

    # Official-source retrieval must validate TLS certificates before accepting content.
    async with httpx.AsyncClient() as client:
        downloaded_count = 0
        for src in sources:
            doc_id = src.get("document_id")
            local_rel = src.get("local_path")
            target_path = BASE_DIR / "data" / "corpus" / local_rel

            # Pick direct download URL if available, else manifest URL
            download_url = OFFICIAL_DIRECT_DOWNLOADS.get(doc_id, src.get("source", {}).get("url"))

            # Download if not already on disk
            if not target_path.exists() and download_url:
                success = await download_file(client, download_url, target_path)
                if success:
                    downloaded_count += 1
                await asyncio.sleep(0.5)

            # If file exists on disk, compute exact SHA-256 and byte size
            if target_path.exists():
                file_hash = calculate_sha256(target_path)
                file_size = target_path.stat().st_size
                src["source"]["sha256"] = file_hash
                src["source"]["file_size_bytes"] = file_size
                print(f"[✓] Verified {doc_id} -> SHA256: {file_hash[:16]}... ({file_size // 1024} KB)")

    # Save updated manifest with real hashes
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] Manifest updated with SHA-256 hashes for Layer 1. Downloaded {downloaded_count} new files.")

if __name__ == "__main__":
    asyncio.run(run_raw_source_ingestion())
