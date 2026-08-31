import httpx
tests = {
    'github_stable': 'https://raw.githubusercontent.com/github/docs/main/README.md',
    'legislative_indianacts': 'https://www.legislative.gov.in/indian-acts',
    'ipindia_tm': 'https://ipindia.gov.in/trade-marks.htm',
    'ipindia_writeread_pdf': 'https://ipindia.gov.in/writereaddata/Portal/Images/pdf/TM-Rules-2017.pdf',
    'indiacode_patents': 'https://www.indiacode.nic.in/handle/123456789/1362',
    'nbaindia': 'https://nbaindia.org/',
    'cdsco_cosmetics': 'https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Cosmetics/Cosmetics_Rules_2020.pdf',
}
for k,u in tests.items():
    try:
        r=httpx.get(u, timeout=12, headers={'User-Agent':'Mozilla/5.0'}, follow_redirects=True)
        print(f'{k}: {r.status_code} {len(r.text)} {str(r.url)[:60]}')
    except Exception as e:
        print(f'{k}: FAIL {type(e).__name__} {str(e)[:60]}')
