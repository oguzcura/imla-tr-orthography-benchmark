p = 'paper.tex'
s = open(p, encoding='utf-8').read()
repl = [
 (r"kar=ya{\u{g}}{\i}{\c s}", r"kar = ya{\u{g}}{\i}{\c s}"),
 (r"hal=market/{\c c}{\"o}zme", r"hal = market / {\c c}{\"o}zme"),
 (r"adet=say{\i}", r"adet = say{\i}"),
 (r"a{\c s}{\i}k=kemik", r"a{\c s}{\i}k = kemik"),
 (r"alem=tepe s{\"u}s{\"u}", r"alem = tepe s{\"u}s{\"u}"),
 (r"mani=hastal{\i}k", r"mani = hastal{\i}k"),
 (r"dahi=da (ba{\u{g}}la{\c c})", r"dahi = da (ba{\u{g}}la{\c c})"),
 (r"yar=u{\c c}urum", r"yar = u{\c c}urum"),
 (r"hakim=bilge", r"hakim = bilge"),
 (r"h{\^a}kim=egemen/yarg{\i}{\c c}", r"h{\^a}kim = egemen / yarg{\i}{\c c}"),
 (r"{\c s}ura={\c s}u yer", r"{\c s}ura = {\c s}u yer"),
 (r"rahim=d{\"o}l yata{\u{g}}{\i}", r"rahim = d{\"o}l yata{\u{g}}{\i}"),
 (r"m{\^a}ni=engel/{\c s}iir", r"m{\^a}ni = engel / {\c s}iir"),
]
for a, b in repl:
    assert a in s, a
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')