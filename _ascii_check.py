import re, sys
for p in ['paper.tex','custom.bib']:
    data = open(p, encoding='utf-8').read()
    hits = [(i+1, l) for i, l in enumerate(data.splitlines()) if re.search(r'[^\x00-\x7F]', l)]
    print(p, 'non-ascii lines:', len(hits))
    for n, l in hits[:12]:
        print(' ', n, repr(l[:90]))