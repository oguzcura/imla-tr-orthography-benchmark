import re, collections
log = open('build.log', encoding='utf-8', errors='replace').read()
# distinct warning kinds (drop per-line underfull/overfull noise)
kinds = collections.Counter()
samples = {}
for m in re.finditer(r'(?:warning: [^:]+:\d+: )?(?:(Package|LaTeX|Class) [A-Za-z]+ (?:Warning|Error)):? ?([^\n]*)', log):
    key = m.group(0)[:110]
    kinds[key] += 1
    samples.setdefault(key, '')
for k, c in kinds.most_common(40):
    print(c, '|', k.strip())
print('---')
print('Invalid UTF-8 count:', log.count('Invalid UTF-8'))
print('lineno count:', log.count('lineno'))
print('Underfull count:', log.count('Underfull'))
print('Overfull count:', log.count('Overfull'))