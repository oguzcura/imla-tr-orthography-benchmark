# -*- coding: utf-8 -*-
"""gts_verify3.py — live GTS (sozluk.gov.tr) verification for Imla full study.

1) Nispet-ek attribute candidates: bare vs caret headwords (need 9 total: existing 6
   milli/resmi/dini/tarihi/ilmi/askeri + 3 new GTS-registered caret forms).
2) 13 minimal-pair words: both spellings' headwords + anlam text (for the documented
   kılavuz-vs-GTS ruling table).
3) kılavuz-flagged-but-GTS-bare words (Kâzım, hukukî, siyasî...) — ruling inputs.
"""
import json, time, urllib.request, urllib.parse

def heads(query):
    url = "https://sozluk.gov.tr/gts?" + urllib.parse.urlencode({"ara": query})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (imla-full)"})
    d = json.loads(urllib.request.urlopen(req, timeout=20).read())
    if isinstance(d, dict):
        return [("ERR", d.get("error", ""), "")]
    out = []
    for e in d:
        madde = e.get("madde")
        anlam = ""
        try:
            anlam = e["anlamlarListe"][0]["anlam"][:80].strip()
        except Exception:
            pass
        cesit = e.get("cesit") or ""
        out.append((madde, cesit, anlam))
    return out

def show(q, label=""):
    hs = heads(q)
    print(f"{label or q:<10} -> " + " || ".join(f"{m} [{c}] {a[:55]}" for m, c, a in hs[:4]))
    time.sleep(0.12)
    return hs

print("=" * 70)
print("1) NISPET-EK ATTRIBUTE CANDIDATES (bare | caret)")
print("=" * 70)
nispet = ["milli/millî", "resmi/resmî", "dini/dinî", "tarihi/tarihî", "ilmi/ilmî",
          "askeri/askerî", "hukuki/hukukî", "idari/idarî", "siyasi/siyasî",
          "adli/adlî", "iktisadi/iktisadî", "fikri/fikrî", "hissi/hissî",
          "vicdani/vicdanî", "akli/aklî", "şahsi/şahsî", "zihni/zihnî", "bedeni/bedenî",
          "kanuni/kanunî", "keyfi/keyfî", "ilmi/ilmî", "ahlaki/ahlakî"]
for pair in nispet:
    b, c = pair.split("/")
    hb, hc = show(b, b), show(c, c)

print("=" * 70)
print("2) MINIMAL PAIRS (both spellings; full list)")
print("=" * 70)
pairs = ["kar/kâr", "hal/hâl", "hala/hâlâ", "halen/hâlen", "adet/âdet", "aşık/âşık",
         "alem/âlem", "mani/mâni", "dahi/dâhi", "yar/yâr", "hakim/hâkim",
         "şura/şûra", "rahim/rahîm", "kazım/Kâzım"]
for pair in pairs:
    b, c = pair.split("/")
    show(b, b); show(c, c)

print("=" * 70)
print("3) TIER-A words re-check (bare must have NO caret headword)")
print("=" * 70)
for w in ["kağıt", "kâğıt", "rüzgar", "rüzgâr", "hükümet", "hükûmet", "sanatkar",
          "sanatkâr", "katip", "kâtip", "kainat", "kâinat", "kabe", "Kâbe"]:
    show(w)