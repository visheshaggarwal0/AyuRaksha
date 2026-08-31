import httpx, re, json
r = httpx.get('https://www.legislative.gov.in/acts', timeout=15, headers={'User-Agent':'Mozilla/5.0'})
m = re.search(r'__NEXT_DATA__[^=]*=({.*?});', r.text, re.S)
if m:
    data = json.loads(m.group(1))
    print(json.dumps(data, indent=2)[:2000])
else:
    print('not found')
