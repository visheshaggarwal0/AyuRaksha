import httpx, re
r = httpx.get('https://www.legislative.gov.in/acts', timeout=15, headers={'User-Agent':'Mozilla/5.0'})
links = re.findall(r'(href|src)=["\']([^"\'>]*(?:pdf|act|Acts)[^"\'>]*)["\']', r.text, re.I)
print('found', len(links))
for k,v in links[:30]:
    print(v)
# also look for api json endpoints
api_links = re.findall(r'["\'](/api[^"\']*)["\']', r.text)
print('API endpoints:', api_links[:20])
