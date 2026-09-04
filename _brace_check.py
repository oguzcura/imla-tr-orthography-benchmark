import re
lines = open('paper.tex', encoding='utf-8').read().splitlines()
depth = 0
for i, l in enumerate(lines, 1):
    l2 = re.sub(r'(?<!\\)%.*$', '', l)
    no, nc = l2.count('{'), l2.count('}')
    depth += no - nc
    if no != nc:
        print(f'{i:4d} open={no} close={nc} depth={depth} {l[:100]}')