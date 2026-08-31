import json
import pathlib
import sys

def main():
    root = pathlib.Path(__file__).resolve().parents[1]
    manifest_path = root / 'data' / 'corpus' / 'manifests' / 'source_manifest_extracted.json'
    
    if not manifest_path.exists():
        manifest_path = root / 'data' / 'corpus' / 'manifests' / 'source_manifest_expanded_150.json'
        
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_links = []
    for src in data.get('sources', []):
        doc_id = src.get('document_id')
        title = src.get('title')
        url = src.get('source', {}).get('url', '')
        if url and not url.startswith('http://example.com'):
            all_links.append((doc_id, title, url))

    md = '# AyuRaksha Manual Download Links (Golden Corpus)\n\n'
    md += 'The automated downloader could not bypass the government CDNs and firewalls. Every single "PDF" it downloaded was actually an HTML block page disguised as a PDF. We must build the Golden Corpus manually.\n\n'
    
    md += '> [!IMPORTANT]\n'
    md += '> **How to build the corpus:**\n'
    md += '> 1. Click each link below to download the actual PDF in your browser.\n'
    md += '> 2. Save it to `data/corpus/raw_downloads/`.\n'
    md += '> 3. **CRITICAL:** Name the file exactly as its Document ID (e.g., `IND_PATENTS_ACT_1970.pdf`).\n\n'

    md += '| Document ID | Title | Download URL |\n'
    md += '|---|---|---|\n'
    for doc_id, title, url in all_links:
        md += f'| `{doc_id}` | {title} | [Download Link]({url}) |\n'

    out_path = pathlib.Path(r'C:\Users\aggar\.gemini\antigravity-ide\brain\f35eea18-39f8-49be-a1c7-cb0c72522388\manual_download_links.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(md)
        
    print(f"Artifact created at {out_path} with {len(all_links)} links.")

if __name__ == "__main__":
    main()
