import re
t = open('build.log', encoding='utf-8', errors='replace').read()
idx = t.rfind('note: Running TeX')
seg = t[idx:]
ov = re.findall(r'Overfull \\hbox \(([\d.]+)pt too wide\)"?(.*)', seg)
print('final-pass overfulls:', len(ov))
for pt, ctx in ov[:16]:
    print(f'  {pt}pt :: {ctx.strip()[:90]}')
print('final-pass underfulls:', len(re.findall(r'Underfull \\hbox', seg)))
print('warnings final pass:', len(re.findall(r'[Ww]arning', seg)))
for w in set(re.findall(r'[Pp]ackage (\w+) ([Ww]arning[^\n]*)', seg)):
    print('  pk:', w)