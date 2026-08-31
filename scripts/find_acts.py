import httpx, re
r = httpx.get('https://www.legislative.gov.in/indian-acts', timeout=15, headers={'User-Agent':'Mozilla/5.0'})
print('status:', r.status_code, 'len:', len(r.text))
links = re.findall(r'href="([^"]*(?:pdf|act)[^"]*)"', r.text, re.I)
print('pdf/act links:', links[:20])
all_links = re.findall(r'href="([^"]*)"', r.text)
print('all links count:', len(all_links))
for l in all_links[:30]:
    print(' ', l)
