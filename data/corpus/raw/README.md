# AyuRaksha Corpus — Raw Source Layer (Layer 1)

This directory is **Layer 1: Raw Source Layer** per the 4-layer architecture.

- Do NOT edit files here manually.
- Every file is an **authoritative download** with provenance.
- Store original PDFs/HTML, never generated JSON.

Structure:
```
raw/
├── india/
│   ├── legislation/   # India Code — Acts, Rules, Amendments
│   ├── ayush/         # D&C Act Ch IV-A, DCR 1945, First Schedule, Pharmacopoeia
│   ├── ip/            # IP India — Patents, TM, GI, Designs public docs
│   └── biodiversity/  # NBA — BDA 2002/2023, ABS Regulations, Forms
└── international/
    ├── wipo/          # WIPO GRATK 2024, TRIPS, treaties
    ├── cbd_nagoya/    # CBD, Nagoya Protocol
    └── export_regimes/ # US FDA DSHEA, EU THMPD 2004/24/EC, etc.
```

Provenance tracked in `data/corpus/manifests/source_manifest_50.json`:
`{ source: { url, source_type, retrieved_at, file_name, sha256, mime_type }, version: { published_date, effective_from } }`

See `scripts/download_corpus.py` for ingestion.
