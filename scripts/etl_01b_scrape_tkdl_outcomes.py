import httpx
import pathlib
import urllib.parse
from bs4 import BeautifulSoup
import time
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "corpus" / "raw_downloads"
RAW_DIR.mkdir(parents=True, exist_ok=True)

URLS = [
    "https://tkdl.res.in/tkdl/langdefault/common/Outcome.asp?PatentOffice=USPTO",
    "https://tkdl.res.in/tkdl/langdefault/common/Outcome.asp?PatentOffice=EPO",
    "https://tkdl.res.in/tkdl/langdefault/common/outcomemain.asp?GL=Eng"
]

HOME_URL = "https://tkdl.res.in/tkdl/langdefault/common/Home.asp"

import ssl

def run_scraper():
    print("Starting TKDL Outcome Scraper...")
    
    # TKDL uses extremely outdated SSL/TLS. Modern Python drops the connection.
    # We must explicitly downgrade the security level to allow legacy ciphers.
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.options |= ssl.OP_LEGACY_SERVER_CONNECT
    
    try:
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=0')
    except Exception:
        pass # SECLEVEL=0 might not be supported on all OpenSSL versions
        
    with httpx.Client(verify=ssl_context, timeout=30.0) as client:
        print(f"1. Establishing ASP Session via {HOME_URL}...")
        try:
            client.get(HOME_URL)
        except Exception as e:
            print(f"Warning on homepage: {e}")
            
        for page_url in URLS:
            print(f"\n2. Fetching {page_url}...")
            try:
                response = client.get(page_url)
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to fetch {page_url}: {e}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links in the page
            links = soup.find_all('a', href=True)
            doc_links = []
            
            for a in links:
                href = a['href']
                # Filter out obvious navigation links, javascript, etc.
                if href.startswith('javascript:') or href.startswith('#') or 'Logout' in href or 'Home' in href:
                    continue
                
                # We want links that look like actual documents or detailed case pages
                if '.pdf' in href.lower() or '.doc' in href.lower() or 'details' in href.lower() or 'search' in href.lower():
                    full_url = urllib.parse.urljoin(page_url, href)
                    doc_links.append((a.text.strip(), full_url))
            
            print(f"Found {len(doc_links)} potential document links on this page.")
            
            for idx, (text, link) in enumerate(doc_links):
                # We'll limit to a few to prevent overwhelming the server right away
                filename = link.split('/')[-1]
                if '?' in filename:
                    # Clean up query params for the filename
                    filename = re.sub(r'[^a-zA-Z0-9_\.]', '_', filename) + ".pdf"
                    
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
                    
                dest_path = RAW_DIR / filename
                
                if dest_path.exists():
                    print(f"  [{idx+1}/{len(doc_links)}] Already downloaded: {filename}")
                    continue
                    
                print(f"  [{idx+1}/{len(doc_links)}] Downloading {filename}...")
                try:
                    # Small delay to avoid IP ban
                    time.sleep(1.0)
                    doc_resp = client.get(link)
                    doc_resp.raise_for_status()
                    
                    with open(dest_path, "wb") as f:
                        f.write(doc_resp.content)
                except Exception as e:
                    print(f"  Failed to download {link}: {e}")
                    
    print("\nScraping complete. Documents saved to data/corpus/raw_downloads/")

if __name__ == "__main__":
    run_scraper()
