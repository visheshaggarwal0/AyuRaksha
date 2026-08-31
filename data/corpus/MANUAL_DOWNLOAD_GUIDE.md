# AyuRaksha Corpus — Manual Download Guide (Layer 1)

India Code (`indiacode.nic.in`) and IP India (`ipindia.gov.in`, `ipindiaservices.gov.in`) **block headless clients** with WAF (403) — this is expected and correct. For a legally defensible corpus you want a *human-verified* download anyway (Gemini point 4).

## Auto-fetched (verified, sha256 in manifest) — 9 clean PDFs
- `raw/international/cbd_nagoya/cbd_text.pdf` (4.5 MB) — CBD
- `raw/international/cbd_nagoya/nagoya_protocol.pdf` (502 KB) — Nagoya
- `raw/international/wipo/trips_agreement.pdf` (197 KB) — WTO TRIPS
- `raw/international/wipo/wipo_gratk_2024.html` (187 KB) — WIPO GRATK 2024
- `raw/international/export_regimes/us_fda_dshea.html` (91 KB) — FDA DSHEA
- `raw/india/ayush/fssai_labelling_2020.pdf` (1 MB) — FSSAI Labelling 2020
- `raw/india/ayush/fssai_ayurveda_aahara_2022.pdf` (3 KB placeholder — retry via browser, FSSAI WAF is intermittent)
- `raw/international/export_regimes/eu_thmpd_2004_24.html` / `eu_food_supplements_2002.html` (2 KB each — EUR-Lex returned minimal due to JS; open in browser to get full directive)
- `raw/india/ayush/ayush_portal.html` (12 KB)

## Placeholders created (need browser drop)
All `raw/india/legislation/*.pdf` and `raw/india/ip/*.html` placeholders are tiny text files (200-300 bytes) containing the error + retry URL. Replace by **browser Save As**:

1. Open the URL from `data/corpus/manifests/source_manifest_50.json: source.url` in a normal browser
2. Save PDF/HTML to the exact `local_path` shown
3. Re-run: `python scripts/download_corpus.py` — it will compute `sha256` and update `retrieved_at` without re-downloading if file >1 KB and sha already present

### Priority manual batch (15 core statutes for decision engines)
- Patents Act 1970 — https://www.indiacode.nic.in/handle/123456789/1362
- BDA 2002 — https://www.indiacode.nic.in/handle/123456789/2047
- BDA Amendment 2023 — https://www.indiacode.nic.in/handle/123456789/17046
- D&C Act 1940 — https://www.indiacode.nic.in/handle/123456789/2152
- Trade Marks Act 1999 — https://www.indiacode.nic.in/handle/123456789/1991
- GI Act 1999 — https://www.indiacode.nic.in/handle/123456789/1988
- Designs Act 2000 — https://www.indiacode.nic.in/handle/123456789/1910
- Copyright Act 1957 — https://www.indiacode.nic.in/handle/123456789/1367
- DMR Act 1954 — https://www.indiacode.nic.in/handle/123456789/2156
- FSS Act 2006 — https://www.indiacode.nic.in/handle/123456789/2066
- Patents Manual 2025 — https://ipindia.gov.in/writereaddata/Portal/Images/pdf/Manual_for_Patent_Office_Practice_and_Procedure.pdf
- TM Rules 2017 — https://ipindia.gov.in/writereaddata/Portal/Images/pdf/TM-Rules-2017.pdf
- Cosmetics Rules 2020 — https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Cosmetics/Cosmetics_Rules_2020.pdf
- First Schedule — https://www.ayush.gov.in/docs/Firsy-schedule-ayurved.pdf
- ABS Regulations 2014 — https://nbaindia.org/uploaded/pdf/ABS_Regulations_2014.pdf (auto fetched but HTML wrapper — use browser save)

### TKDL
`raw/india/ayush/tkdl_overview.html` is intentionally a **policy-only placeholder** — TKDL database is **access-controlled**. Do not scrape. Use the representative open catalog at `data/corpus/ayurveda_tk_and_taxonomy/tkdl_representative_formulations.json` for RAG.

## Next layer
Once ~30-40 raw files are human-verified, run:
```
python scripts/extract_corpus.py  # PDF -> text/tables (planned)
python scripts/chunk_and_embed.py # provision -> chunks (pgvector)
```
See `data/corpus/raw/README.md` for 4-layer flow.
