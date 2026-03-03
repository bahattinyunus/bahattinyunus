import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('README.md', 'r', encoding='utf-8') as f:
    text = f.read()

urls = re.findall(r'https?://[^\s\"\'\)<>]+', text)
bad_urls = []
for url in set(urls):
    if 'capsule-render' in url or 'typing-svg' in url or 'shields' in url or 'skillicons' in url or 'readme' in url or 'komarev' in url:
        continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
    except Exception as e:
        bad_urls.append((url, str(e)))

print('Found broken:' if bad_urls else 'All checked URLs OK.')
for u, err in bad_urls:
    print(f'{u} -> {err}')
