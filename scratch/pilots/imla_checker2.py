# -*- coding: utf-8 -*-
"""imla_checker2.py — mechanical TDK orthography-fidelity checker, v2 (Imla pilot 2).

Extends imla_checker.py (R1..R10) with:

R11 CARET     Düzeltme işareti (^) — lexicon built from LIVE GTS (sozluk.gov.tr)
              verification on 2026-09-04 (gts_caret_validate2.py / gts_anlam_pass.py).
              Three flag modes:
                - MODE_A   bare spelling is NOT a GTS headword -> flag always
                - MODE_ATTR bare spelling flagged in attribute position
                           (bare + following lowercase token), possessive readings
                           excluded via FOLLOW_EXCEPT verb/particle set
                - MODE_COLL bare spelling flagged only in disambiguating
                           collocation (minimal pairs: kar/kâr, hal/hâl, hala/hâlâ,
                           adet/âdet, aşık/âşık, alem/âlem, mani/mâni, dahi/dâhi,
                           yar/yâr, şura/şûra, hakim/hâkim, rahim/rahîm)
              TDK rule page: https://tdk.gov.tr/icerik/yazim-kurallari/duzeltme-isareti/
              Per-word GTS evidence: gts_caret_results.json (this folder)
R12 INFORMAL  Chat/social contractions & shorthands with NO GTS entry
              (verified live 2026-09-04; GTS returns "Sonuç bulunamadı").
              Correct forms per GTS/TDK: yapıcam->yapacağım, heralde->herhalde,
              çünki->çünkü, saol->sağ ol, baya->bayağı, tmm->tamam, slm->selam,
              nbr->ne haber, ...
R13 CHATPUNCT Nonstandard punctuation runs typical of informal chat:
              repeated !/? ([!?]{2,} incl. mixed runs), double dot "..",
              ellipsis of nonstandard length (2 or 4+ dots; "..." is the mark).
              TDK page: https://tdk.gov.tr/icerik/yazim-kurallari/noktalama-isaretleri-aciklamalar/
"""
from __future__ import annotations
import re
from typing import Dict, List
from imla_checker import check_text, _tok, tr_lower  # reuse base engine

# ================================================================ R11 caret lexicon
# Each entry: surface_form -> (correct_form, mode, note)
# GTS evidence recorded in gts_caret_results.json; bare spelling MAY be a registered
# GTS headword for MODE_ATTR/MODE_COLL words (that is exactly why the gate exists).
R11_A = {
    "kağıt":   ("kâğıt",   "GTS: sadece 'kâğıt' madde başı; 'kağıt' girişi yok"),
    "rüzgar":  ("rüzgâr",  "GTS: sadece 'rüzgâr'"),
    "ruzgar":  ("rüzgâr",  "GTS: 'ruzgar' girişi yok"),
    "hükümet": ("hükûmet", "GTS: sadece 'hükûmet'"),
    "hukumet": ("hükûmet", "GTS: 'hukumet' girişi yok"),
    "sanatkar":("sanatkâr","GTS: sadece 'sanatkâr'"),
    "katip":   ("kâtip",   "GTS: sadece 'kâtip'"),
    "kainat":  ("kâinat",  "GTS: sadece 'kâinat'"),
    "halen":   ("hâlen",   "GTS: sadece 'hâlen' (şimdiye kadar)"),
}
R11_PROPER = {"kabe": ("Kâbe", "GTS: sadece 'Kâbe'")}  # case-insensitive

# MODE_ATTR — bare forms whose possessive reading (stem + iyelik eki) is legitimate
R11_ATTR = {
    "milli":  ("millî",  "GTS: 'millî' milletle ilgili; 'milli' = mil içeren (nadir)"),
    "resmi":  ("resmî",  "GTS: 'resmî' kuruluş; 'resmi' = resim+i iyelik okunuşu mümkün"),
    "dini":   ("dinî",   "GTS: 'dinî' bilgiler; 'dini' = din+i iyelik okunuşu mümkün"),
    "tarihi": ("tarihî", "GTS: 'tarihî' eser; 'tarihi' = tarih+i iyelik okunuşu yaygın"),
    "ilmi":   ("ilmî",   "GTS: 'ilmî' tartışmalar; 'ilmi' = ilim+i iyelik okunuşu mümkün"),
    "askeri": ("askerî", "GTS: 'askerî' okul; 'askeri' = asker+i iyelik okunuşu mümkün"),
}
# FOLLOW_EXCEPT: tokens after the bare form that signal the POSSESSIVE reading
R11_ATTR_EXCEPT = {
    "bütün", "boyunca", "gibi", "var", "yok", "değil", "belli", "sür", "sürdü",
    "sürüyor", "sürer", "devam", "etti", "eder", "anlattı", "anlatıyor", "yazdı",
    "yazıyor", "okudu", "okuyor", "biliyor", "bilinmiyor", "merak", "araştır",
    "araştırdı", "çizdi", "çiziyor", "çizil", "öğrendi", "öğreniyor", "konuştu",
    "konuşuyor", "sordu", "soruyor", "düşün", "edildi", "ediliyor", "gördü",
    "görüyor", "söyledi", "söylüyor", "kaldı", "kalmış", "gel", "gitti", "gidiyor",
}

# MODE_COLL — minimal pairs; bare flagged only under disambiguating context
R11_PROFIT_COLL = {
    "net", "brüt", "elde", "sağla", "sağladı", "dağıt", "dağıttı", "marj",
    "pay", "zarar", "getiri", "kazanç", "gelir", "gider", "ticaret", "ticari",
    "işletme", "şirket", "satış", "yıllık", "vergi", "faiz", "yatırım", "sermaye",
    "borsa", "hisse", "ortak", "hissedar", "müşteri", "fiyat", "piyasa", "esnaf",
    "tüccar", "dükkân", "dükkan", "mağaza", "üretim", "ihracat", "ithalat",
    "muhasebe", "bilanço", "para", "lira", "dolar", "euro", "milyon", "milyar",
    "ekonomi", "ekonomik", "kazanıldı", "kazandı", "kazanır", "kazanmak",
    "kazanacağız", "kazançlı", "işyeri", "işveren", "maaş", "ücret", "kârlı",
    "kârlılık", "özsermaye",
}
R11_HAL_MARKET_EXC = {"sebze", "meyve", "balık", "çiçek", "manav", "kuruyemiş",
                      "aktar", "sergi", "bitkisel", "toptan", "perakende"}
R11_HAL_STATE = {"ne", "şu", "bu", "öyle", "böyle", "içinde", "dışında", "durum",
                 "son", "eski", "bugünkü", "gerçek", "doğal", "iyi", "kötü",
                 "yorgun", "mutlu", "üzgün", "nasıl", "zor", "güzel", "anda",
                 "anım", "canlı", "ruh", "psikolojik", "yorgunluk", "halsiz", "perisan",
                 "perişan", "berbat", "harika", "süper", "fena", "beter"}
R11_HALA_FOLLOW = {"değil", "mı", "mi", "mu", "mü", "ben", "sen", "biz", "siz",
                   "o", "bu", "şu", "aynı", "burada", "orada", "hiç", "her",
                   "ne", "kim", "kimse", "biri", "bir", "hâlâ", "acaba", "yanlız",
                   "yalnız", "bekliyor"}
R11_ADET_PRE = {"eski", "töre", "örf", "gelenek", "yöresel", "ananevi", "dini",
                "dinî", "millî", "milli", "halk"}
R11_ADET_POST = {"oldu", "olmuş", "olur", "olmaz", "edinmiş", "edindi", "haline",
                 "gereği", "yıllardır", "devam", "sürdü", "sürüyor", "sürer",
                 "kaldı", "yaşatılıyor", "hala", "hâlâ", "gerçekleşti", "bozuldu"}
R11_ASIK_POST = {"oldu", "olmuş", "olur", "oluyor", "oldum", "olduğu", "olduğum",
                 "olan", "olma", "olacağım", "oldun", "olduk"}
R11_ALEM_POST = {"duyur", "duyurdu", "oldu", "olsun", "karıştı", "karışır",
                 "döndü", "döner", "alemlerin", "sahibi", "içinde", "çalkalan"}
R11_MANI_POST = {"ol", "oldu", "olur", "olmuş", "olmaz", "olmasın", "olmayan",
                 "olmak", "oluyor", "olamaz", "olamadım", "olamadı", "olamadık"}
R11_DAHI_COLL = {"deha", "zekâ", "zeka", "zeki", "bilim", "büyük", "gerçek",
                 "matematik", "fizik", "sanat", "edebiyat", "yetenek", "tarih",
                 "müzik", "satranç", "dâhi", "dahiler", "çocuk"}
R11_YAR_POST = {"olur", "olsun", "olmayan", "gibi", "ile", "için", "uğruna",
                "sevgili"}
R11_HAKIM_EXEMPT = {"bilge", "hikmet", "filozof", "alim", "âlim", "bilgin",
                    "hakimane", "hikmetli"}
R11_SURA_COLL = {"danışma", "kurul", "yüksek", "askerî", "askeri", "millî",
                 "milli", "güvenlik", "karar", "üye", "başkan", "toplantı",
                 "seçim", "devlet"}
R11_RAHIM_COLL = {"allah", "tanrı", "esirgeyen", "merhamet", "koruyan",
                  "bağışlayan", "rahmet", "yaradan", "yüce"}

_R11_BARE = re.compile(r"\b(kağıt|rüzgar|ruzgar|hükümet|hukumet|sanatkar|katip|kainat|halen|kabe|milli|resmi|dini|tarihi|ilmi|askeri|kar|hal|hala|adet|aşık|alem|mani|dahi|yar|hakim|şura|rahim)\b", re.IGNORECASE)
_R11_BARE_TOKENS = re.compile(r"kağıt|rüzgar|ruzgar|hükümet|hukumet|sanatkar|katip|kainat|halen|kabe|milli|resmi|dini|tarihi|ilmi|askeri|kar|hal|hala|adet|aşık|alem|mani|dahi|yar|hakim|şura|rahim")
_R11_HAL_INFLECTED = re.compile(r"\bhal(im|in|i|ine|inden|ini|imiz|iniz|leri|de|den|iyle)\b", re.IGNORECASE)
_R11_WEATHER = {"hava", "soğuk", "kış", "tipi", "yağış", "yağdı", "yağıyor", "yağacak",
                "meteoroloji", "derece", "don", "buz", "fırtına", "eridi", "eriyor",
                "kartopu", "kardan", "kayak", "çığ", "sis", "bulut"}

def _words_around(tokens, i, w=2):
    """Return set of lowercase words within window w of token index i."""
    out = set()
    for j in range(max(0, i - w), min(len(tokens), i + w + 1)):
        if j != i:
            out.add(tr_lower(tokens[j]))
    return out

def _tokens_with_spans(text):
    return [(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", text)]

def _next_word(text, end):
    m = re.search(r"\s*([^\s,.;:!?…()\[\]{}'\"]+)", text[end:])
    return tr_lower(m.group(1)).rstrip(".,;:!?") if m else None

def _prev_word(text, start):
    m = re.search(r"([^\s,.;:!?…()\[\]{}'\"]+)\s*$", text[:start])
    return tr_lower(m.group(1)).lstrip(".,;:!?") if m else None

def rule_caret(text: str):
    out = []
    toks = _tokens_with_spans(text)
    words = [tr_lower(t) for t, _, _ in toks]
    for i, (tok, s0, e0) in enumerate(toks):
        t = tr_lower(tok).strip(".,;:!?…()[]{}'\"")
        if not t or not _R11_BARE_TOKENS.fullmatch(t if len(t) <= 12 else "skip"):
            continue
        # ---- MODE_A: unconditional bare spellings ----
        if t in R11_A:
            right, note = R11_A[t]
            out.append({"span": tok, "msg": f"'{tok}': düzeltme işareti gerekir ('{right}') — {note}"})
            continue
        if t == "kabe":
            out.append({"span": tok, "msg": f"'{tok}': özel ad 'Kâbe' düzeltme işaretiyle yazılır"})
            continue
        # ---- MODE_ATTR: attribute position = bare + following lowercase token ----
        if t in R11_ATTR:
            right, note = R11_ATTR[t]
            nx = _next_word(text, e0)
            if nx and nx not in R11_ATTR_EXCEPT:
                out.append({"span": tok, "msg": f"'{tok}': nispet eki düzeltme işaretiyle yazılır ('{right} {nx}') — {note}"})
            continue
        # ---- MODE_COLL: minimal pairs ----
        if t == "kar":
            nxt = words[i + 1] if i + 1 < len(words) else ""
            weather = not nxt.startswith("yağ") and not (_words_around(words, i, 2) & _R11_WEATHER)
            if weather and (_words_around(words, i, 2) & R11_PROFIT_COLL):
                out.append({"span": tok, "msg": f"'{tok}': kazanç anlamında 'kâr' yazılır (GTS: kâr = alışveriş işlerinin sağladığı para kazancı)"})
            continue
        if t == "hal":
            prev = _prev_word(text, s0)
            if prev not in R11_HAL_MARKET_EXC:
                nx = _next_word(text, e0)
                coll = _words_around(words, i, 1)
                if nx in R11_HAL_STATE or coll & R11_HAL_STATE:
                    out.append({"span": tok, "msg": f"'{tok}': durum anlamında 'hâl' yazılır (GTS: hâl = durum, vaziyet)"})
            continue
        if t == "hala":
            nx = _next_word(text, e0)
            if nx and (nx in R11_HALA_FOLLOW or nx.endswith(("yor", "yordum", "yordur"))):
                out.append({"span": tok, "msg": f"'{tok}': 'henüz' anlamında 'hâlâ' yazılır (GTS: hâlâ = şimdiye kadar; hala = babanın kız kardeşi)"})
            continue
        if t == "adet":
            prev, nx = _prev_word(text, s0), _next_word(text, e0)
            if prev in R11_ADET_PRE or nx in R11_ADET_POST:
                out.append({"span": tok, "msg": f"'{tok}': görenek anlamında 'âdet' yazılır (GTS: âdet = görenek; adet = sayı)"})
            continue
        if t == "aşık":
            nx = _next_word(text, e0)
            if nx in R11_ASIK_POST:
                out.append({"span": tok, "msg": f"'{tok}': tutkun anlamında 'âşık' yazılır (GTS: âşık = vurgun, tutkun; aşık = eklem kemiği)"})
            continue
        if t == "alem":
            nx = _next_word(text, e0)
            if nx in R11_ALEM_POST:
                out.append({"span": tok, "msg": f"'{tok}': dünya/evren anlamında 'âlem' yazılır (GTS: âlem = dünya, evren; alem = bayrak)"})
            continue
        if t == "mani":
            nx = _next_word(text, e0)
            if nx in R11_MANI_POST:
                out.append({"span": tok, "msg": f"'{tok}': engel anlamında 'mâni' yazılır (GTS: mâni = engel; mani = mania)"})
            continue
        if t == "dahi":
            coll = _words_around(words, i, 2)
            if coll & R11_DAHI_COLL:
                out.append({"span": tok, "msg": f"'{tok}': deha anlamında 'dâhi' yazılır (GTS: dâhi; dahi = bağlaç)"})
            continue
        if t == "yar":
            nx = _next_word(text, e0)
            if nx in R11_YAR_POST:
                out.append({"span": tok, "msg": f"'{tok}': sevgili anlamında 'yâr' yazılır"})
            continue
        if t == "hakim":
            coll = _words_around(words, i, 2)
            if not (coll & R11_HAKIM_EXEMPT):
                out.append({"span": tok, "msg": f"'{tok}': yargıç/egemen anlamında 'hâkim' yazılır (GTS: hâkim; 'hakim' = bilge okunuşu için hakîm)"})
            continue
        if t == "şura":
            coll = _words_around(words, i, 2)
            if coll & R11_SURA_COLL:
                out.append({"span": tok, "msg": f"'{tok}': danışma kurulu anlamında 'şûra' yazılır (GTS: şûra = danışma kurulu; şura = şu yer)"})
            continue
        if t == "rahim":
            coll = _words_around(words, i, 2)
            if coll & R11_RAHIM_COLL:
                out.append({"span": tok, "msg": f"'{tok}': koruyan anlamında 'rahîm' yazılır (GTS: rahîm = koruyan, merhamet eden)"})
            continue
    # ---- inflected state-forms of hal (hâl + possession) ----
    for m in _R11_HAL_INFLECTED.finditer(text):
        prev = _prev_word(text, m.start())
        if prev not in R11_HAL_MARKET_EXC:
            out.append({"span": m.group(0),
                        "msg": f"'{m.group(0)}': durum anlamında 'hâl{m.group(0)[3:]}' yazılır (hâl + iyelik; GTS: hâl = durum)"})
    return out

# ================================================================ R12 informal lexicon
# All tokens verified 2026-09-04: GTS returns "Sonuç bulunamadı" (no headword).
R12_FIX = {
    "yapıcam": "yapacağım", "yapıcak": "yapacak", "yapicam": "yapacağım",
    "gidicem": "gideceğim", "gidecem": "gideceğim", "gelicem": "geleceğim",
    "gelecem": "geleceğim", "alıcam": "alacağım", "alıcak": "alacak",
    "bakıcam": "bakacağım", "olucak": "olacak", "olucam": "olacağım",
    "görücem": "göreceğim", "diycem": "diyeceğim", "yazıcam": "yazacağım",
    "anlıcam": "anlayacağım", "çalışıcam": "çalışacağım", "sevicem": "seveceğim",
    "uyucam": "uyuyacağım", "yicem": "yiyeceğim", "dönücem": "döneceğim",
    "gelmicek": "gelmeyecek", "gitmicek": "gitmeyecek", "yapmıcak": "yapmayacak",
    "olmıcak": "olmayacak", "almıcam": "almayacağım", "bilmiyom": "bilmiyorum",
    "geliyom": "geliyorum", "yapıyom": "yapıyorum", "ediyom": "ediyorum",
    "görüyom": "görüyorum", "biliyom": "biliyorum", "gidiyom": "gidiyorum",
    "oluyom": "oluyorum", "napıyom": "ne yapıyorum", "napiyim": "ne yapayım",
    "napim": "ne yapayım", "napcam": "ne yapacağım", "nolcak": "ne olacak",
    "tmm": "tamam", "slm": "selam", "mrb": "merhaba", "nbr": "ne haber",
    "hbr": "haber", "heralde": "herhalde", "çünki": "çünkü", "saol": "sağ ol",
    "güsel": "güzel", "iydi": "iyiydi", "baya": "bayağı", "bi": "bir",
}
_R12_RE = re.compile(r"\b(" + "|".join(sorted(R12_FIX, key=len, reverse=True)) + r")\b")

def rule_informal_lexicon(text: str):
    out = []
    for m in _R12_RE.finditer(text):
        tok = m.group(1)
        if tok == "bi" and text[m.start() - 1:m.start()].isalpha():
            continue  # avoid matching inside words (regex already word-bound; safety)
        out.append({"span": m.group(0), "msg": f"'{tok}': günlük konuşma kısaltması; GTS'de girişi yok, doğrusu '{R12_FIX[tok]}'"})
    return out

# ================================================================ R13 chat punctuation
_R13_BANG = re.compile(r"[!?]{2,}")
_R13_MIXED = re.compile(r"[!?][?!]")
_R13_DOT2 = re.compile(r"(?<!\.)\.\.(?!\.)")
_R13_DOTRUN = re.compile(r"\.{4,}")

def rule_chat_punct(text: str):
    out = []
    for m in _R13_BANG.finditer(text):
        out.append({"span": m.group(0), "msg": f"'{m.group(0)}': ünlem/soru işareti tek kullanılır (chat'te tekrar dizileri standart dışı)"})
    for m in _R13_MIXED.finditer(text):
        out.append({"span": m.group(0), "msg": f"'{m.group(0)}': karışık '!?' dizisi standart dışı"})
    # two-dot ellipsis is sanctioned ONLY after ! or ? (TDK UYARI: "Gök ekini biçer gibi!..")
    for m in _R13_DOT2.finditer(text):
        prev_ch = text[m.start() - 1] if m.start() > 0 else ""
        if prev_ch not in "!?":
            out.append({"span": m.group(0), "msg": "İki nokta ile noktalama yapılmaz; üç nokta '...' kullanılır"})
    for m in _R13_DOTRUN.finditer(text):
        out.append({"span": m.group(0), "msg": f"'{m.group(0)}': üç nokta tam olarak üç noktadan oluşur"})
    return out

# ================================================================ orchestrator
NEW_RULES = {
    "R11_caret": rule_caret,
    "R12_informal_lexicon": rule_informal_lexicon,
    "R13_chat_punct": rule_chat_punct,
}
ALL_RULES = {**{
    "R1_dotless_i": lambda t: check_text(t)["R1_dotless_i"],
    "R2_locative": lambda t: check_text(t)["R2_locative"],
    "R3_bildirme_dir": lambda t: check_text(t)["R3_bildirme_dir"],
    "R4_soru_eki": lambda t: check_text(t)["R4_soru_eki"],
    "R5_apostrophe_proper": lambda t: check_text(t)["R5_apostrophe_proper"],
    "R6_casing": lambda t: check_text(t)["R6_casing"],
    "R7_punct_spacing": lambda t: check_text(t)["R7_punct_spacing"],
    "R8_ki": lambda t: check_text(t)["R8_ki"],
    "R9_numbers": lambda t: check_text(t)["R9_numbers"],
    "R10_apostrophe_misuse": lambda t: check_text(t)["R10_apostrophe_misuse"],
}, **NEW_RULES}

def check_text2(text: str) -> Dict[str, List[dict]]:
    """R1..R13. R1-R10 reuse imla_checker (unchanged behavior)."""
    base = check_text(text)
    base.update({rid: fn(text) for rid, fn in NEW_RULES.items()})
    return base

def summarize2(text: str) -> dict:
    v = check_text2(text)
    return {"violations": v, "total": sum(len(x) for x in v.values())}