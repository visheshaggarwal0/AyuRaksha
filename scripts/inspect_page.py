import httpx, re
r = httpx.get('https://www.legislative.gov.in/acts', timeout=15, headers={'User-Agent':'Mozilla/5.0'})
# Look for __NEXT_DATA__
m = re.search(r'__NEXT_DATA__[^=]*=({.*?});', r.text, re.S)
if m:
    print('NEXT DATA found, len:', len(m.group(1)))
    print(m.group(1)[:1000])
else:
    print('no NEXT DATA')
    # Look for any json
    js = re.findall(r'window\.__[^=]*=', r.text)
    print('window vars:', js[:5])
    # Look for page data
    m2 = re.search(r'"props":\{.*?\}', r.text, re.S)
    if m2: print('props:', m2.group(0)[:500])
