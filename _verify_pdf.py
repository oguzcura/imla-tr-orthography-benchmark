import re, sys
try:
    import fitz
except ImportError:
    print("NO_PYMUPDF"); sys.exit(0)
doc = fitz.open('out/paper.pdf')
text = ''.join(p.get_text() for p in doc)
print('pages:', doc.page_count)
print('chars:', len(text))
# unresolved citation markers
q = [m.start() for m in re.finditer(r'[?]', text)]
print('question-mark hits:', len(q))
for i in q[:12]:
    print('  ...', text[max(0,i-45):i+20].replace('\n',' '))
# citation markers like [1] [12]
cites = re.findall(r'\[[\d,\s–-]+\]', text)
print('numeric bracket groups:', len(cites), cites[:20])
# Turkish glyph counts
for g in 'ğğıİşçöüĞİŞÇÖÜâîû':
    c = text.count(g)
    if c: print(f'glyph {g}: {c}')
print('total turkish glyphs:', sum(text.count(g) for g in 'ğğıİşçöüĞİŞÇÖÜâîû'))
# key words sanity
for w in ['17.3', '61.1', '77.6', '80.9', '34.1', 'RULINGS13', '216', 'transparency', 'K\u00e2be', 'k\u00e2\u011f\u0131t']:
    print(w, '->', w in text)