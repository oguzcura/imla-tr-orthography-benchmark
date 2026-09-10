# -*- coding: utf-8 -*-
"""imla_checker3.py — mechanical TDK orthography-fidelity checker, v3 (Imla full study).

Extends imla_checker2.py (R1..R13) with two v3 upgrades, both motivated by the
full-study (unprimed) corpus:

A) NISPET-EK ATTRIBUTE WORDS: 6 -> 9 (GTS live re-verification 2026-09-04,
   gts_verify3.py): added fikri->fikrî, hissi->hissî, zihni->zihnî (all three are
   registered GTS caret headwords). Rejected candidates (GTS registers ONLY the
   bare form -> caret-free in modern practice): hukuki, idari, siyasi, adli,
   iktisadi, vicdani, akli, şahsi, kanuni, keyfi, ahlaki. Ruling: follow GTS.

   Disambiguation is now POS-BASED (rule_caret3 -> _next_pos) instead of v2's
   fixed FOLLOW_EXCEPT verb list:
     - NOUN  head (or noun + nominal suffix)  -> ATTRIBUTE position  -> FLAG
       ('resmi evrak', 'milli takım', 'fikri mülkiyet hakları')
     - VERB  head (verb stem + tense/person, or inflected in VERB_FORMS)
                                             -> POSSESSIVE  reading -> no flag
       ('resmi çizdi', 'tarihi öğrendik', 'askeri sevdim')
     - POSTPOSITION / flat adjective / UNKNOWN -> conservative NO FLAG
       ('dini bütün', 'tarihi boyunca', 'bu fikri çok beğendim' — 'fikri' = fikir+i)
   Unknown->no-flag is a documented precision-first default (v2 defaulted to FLAG).
   Known FP risk (documented): dative/instrumental bridging ('resmi duvara astı');
   not observed in the full-study corpus.

B) MINIMAL PAIRS: 12 -> 13 with a documented kılavuz-vs-GTS ruling per word
   (RULINGS13). 13th pair = halen/hâlen (GTS registers ONLY 'hâlen'; adopted as
   unconditional STAT gate — quasi Mode-A). Per-word rulings cite TDK Yazım
   Kılavuzu 2012 Düzeltme İşareti section + live GTS headword evidence
   (gts_verify3.py output, 2026-09-04). hala/hâlâ gate extended (STAT next-token:
   temporal adverbs/verbs; 'hala' = aunt only under possessive inflection or in
   kinship collocation 'hala kızı').
   Kâzım tension (kılavuz lists Kâzım, GTS headword only 'kazım'): ruled NOT FLAGGED
   (GTS wins) — documented, excluded from the battery.

P/R validation: smoke_test3.py (22P + 20N, see imla_full.md §checker).
"""
from __future__ import annotations
import re
from typing import Dict, List
from imla_checker2 import (check_text2, rule_informal_lexicon, rule_chat_punct,
                           R11_A, R11_PROPER, R11_ATTR, R11_ATTR_EXCEPT,
                           R11_PROFIT_COLL, R11_HAL_MARKET_EXC, R11_HAL_STATE,
                           R11_HALA_FOLLOW, R11_ADET_PRE, R11_ADET_POST,
                           R11_ASIK_POST, R11_ALEM_POST, R11_MANI_POST,
                           R11_DAHI_COLL, R11_YAR_POST, R11_HAKIM_EXEMPT,
                           R11_SURA_COLL, R11_RAHIM_COLL,
                           _R11_BARE, _R11_BARE_TOKENS, _R11_HAL_INFLECTED,
                           _R11_WEATHER, _words_around, _tokens_with_spans,
                           _next_word, _prev_word, _tok, tr_lower)

# =====================================================================
# A) 9 nispet-ek attribute words (GTS live-verified caret headwords)
# =====================================================================
R11_ATTR3 = dict(R11_ATTR)
R11_ATTR3.update({
    "fikri":  ("fikrî",  "GTS: 'fikrî' düşünsel; 'fikri' = fikir+i iyelik okunuşu mümkün"),
    "hissi":  ("hissî",  "GTS: 'hissî' duygusal; 'hissi' = his+i iyelik okunuşu mümkün"),
    "zihni":  ("zihnî",  "GTS: 'zihnî' zihinsel; 'zihni' = zihin+i iyelik okunuşu mümkün"),
})

# ---- POS lexicons (rule-based Turkish light POS, documented) ----
# INF_VERBS: stems of common Turkish verbs (for tense/person stripping).
VERB_LEMMA = {
    "yap", "et", "çiz", "boya", "sat", "al", "ver", "at", "as", "yaz", "oku",
    "anlat", "söyle", "konuş", "sor", "cevapla", "anla", "bil", "öğren", "öğret",
    "düşün", "inan", "gör", "izle", "seyret", "sev", "beğen", "çalış", "dinlen",
    "uyu", "kalk", "gel", "git", "dön", "kal", "dur", "bekle", "koş", "yürü",
    "bin", "in", "taşı", "götür", "getir", "bırak", "topla", "dağıt", "aç",
    "kapat", "kır", "sil", "temizle", "yıka", "giy", "ara", "bul", "tut", "koy",
    "çek", "it", "sür", "sürdür", "yönet", "yürüt", "düzenle", "hazırla", "planla",
    "onayla", "imzala", "ilet", "gönder", "bildir", "uyar", "hatırlat", "unut",
    "an", "anımsa", "sallan", "devril", "uçur", "es", "estir", "yağ", "çık",
    "düş", "yat", "yetiş", "yetiştir", "bit", "bitir", "başla", "devam", "sürdü",
    "açıkla", "belirt", "duyur", "bildir", "teslim", "öde", "kazan", "kaybet",
    "borçlan", "yatır", "büyüt", "küçül", "hesapla", "harcama", "harca", "kur",
    "kapat", "işlet", "pazarla", "ihraç", "ithal", "üret", "satın", "fiyatla",
    "zam", "indir", "artır", "azalt", "yüksel", "düşür", "karşıla", "önle",
    "engelle", "zorla", "zorlan", "inşa", "tamir", "onar", "bak", "kaldır",
    "kullan", "artır", "yükselt", "düşür", "yolla", "gönder", "teslim",
}
# NOUN_HEADS: common noun heads of nispet-ek attribute phrases (+ plural/case variants
# handled by suffix stripping). These are the direct object of the ATTR test.
NOUN_HEADS = {
    "evrak", "takım", "bayram", "eser", "okul", "mülkiyet", "hak", "yaklaşım",
    "yorgunluk", "tartışma", "kurum", "kuruluş", "daire", "belge", "işlem",
    "yazışma", "yazı", "geçit", "nikah", "tören", "kutlama", "marş", "bayrak",
    "güvenlik", "savunma", "birlik", "eğitim", "öğrenci", "memur", "görevli",
    "makam", "karar", "süreç", "anlaşma", "sözleşme", "düzenleme", "uygulama",
    "politika", "kültür", "gelenek", "değer", "müze", "sergi", "bina", "yapı",
    "anıt", "kalıntı", "çalışma", "araştırma", "proje", "kongre", "akademi",
    "üniversite", "kütüphane", "arşiv", "metin", "yayın", "dergi", "gazete",
    "basın", "ordu", "kışla", "doktrin", "tatbikat", "sınır", "bölge", "ülke",
    "millet", "toplum", "kimlik", "beraberlik", "lig", "federasyon", "spor",
    "müsabaka", "yarışma", "maç", "olimpiyat", "şampiyona", "kadro", "antrenör",
    "teknik", "tesis", "kamp", "kurultay", "meclis", "encümen", "komite",
    "konsey", "heyet", "idare", "yönetim", "bakanlık", "bürokrasi", "protokol",
    "hukuk", "mahkeme", "dava", "savcı", "adalet", "ceza", "hüküm", "yargı",
    "örf", "töre", "ibadet", "inanç", "duygu", "sezgi", "vicdan", "ahlak",
    "ilahi", "ezan", "cami", "bayram", "dua", "mezhep", "tarikat", "cemiyet",
    "kurum", "kongre", "oturum", "celse", "soru", "mektup", "el yazısı", "mürekkep",
    "defter", "dosya", "klasör", "zarf", "pul", "mühür", "kaşe", "imza", "para",
    "harç", "vergi", "resim", "çizim", "fotoğraf", "an", "dönem", "çağ", "devir",
    "kitap", "roman", "öykü", "şiir", "türkü", "şarkı", "ilahi", "eğlence",
    "ziyafet", "yemek", "sofra", "davet", "misafir", "konuk", "hediye", "armağan",
    "sembol", "marka", "şirket", "işletme", "ticaret", "piyasa", "borsa",
}
# POSTPOS: postpositions / particles / complement heads -> POSSESSIVE complement
# reading ('tarihi boyunca', 'resmi gibi', 'ilmi için'...).
POSTPOS = {
    "boyunca", "gibi", "için", "ile", "kadar", "dek", "değin", "tarafından",
    "sayesinde", "yüzünden", "sırasında", "öncesinde", "sonrasında", "üzerinde",
    "altında", "dışında", "içinde", "hakkında", "dolayı", "göre", "rağmen",
    "karşı", "karşın", "başta", "itibaren", "beri", "sonra", "önce", "ötürü",
    "yanında", "arasında", "arasından", "doğru", "üzere", "diye", "bütün",
    "tam", "hep", "hiç", "çok", "pek", "az", "biraz", "daha", "en", "da", "de",
    "mı", "mi", "mu", "mü", "ki", "ya", "ise",
}
# VERB_FORMS: inflected verbs observed in pilot corpora (fast path before stripping).
VERB_FORMS = {
    "yaptı", "yapıyor", "yapıldı", "yapılmış", "etti", "ediyor", "edildi",
    "çizdi", "çiziyor", "çizilmiş", "boyadı", "sattı", "satıyor", "aldı",
    "alıyor", "verdi", "veriyor", "attı", "astı", "yazdı", "yazıyor", "okudu",
    "okuyor", "anlattı", "anlatıyor", "söyledi", "söylüyor", "konuştu",
    "konuşuyor", "sordu", "soruyor", "anladı", "biliyor", "bilmiyor", "öğrendi",
    "öğreniyor", "düşündü", "düşünüyor", "gördü", "görüyor", "izledi", "sevdi",
    "seviyor", "beğendi", "çalışıyor", "kaldı", "kalmış", "duruyor", "bekliyor",
    "geldi", "gelmedi", "geliyor", "gitti", "gitmedi", "gidiyor", "döndü",
    "tuttu", "açtı", "açıldı", "geçti", "aştı", "buldu", "bulundu", "oldu",
    "oluyor", "olmuş", "olmamış", "yörün", "hissetti", "duydu", "duyurdu",
    "yayınlandı", "yayımladı", "imzaladı", "imzalandı", "açıkladı", "belirtti",
    "devretti", "teslim", "değiştirdi", "değişti", "sürüyor", "sürdü", "başladı",
    "bitirdi", "bitti", "yetişti", "getirdi", "götürdü",
}

# ---------- POS classifier ----------
_VERB_PLUR = ("lar", "ler")
_VERB_PERS = ("dım", "dın", "dı", "dık", "dınız", "dılar",
              "dim", "din", "di", "dik", "diniz", "diler",
              "dum", "dun", "du", "duk", "dunuz", "dular",
              "tım", "tın", "tı", "tık", "tınız", "tılar",
              "tim", "tin", "ti", "tik", "tiniz", "tiler",
              "tum", "tun", "tu", "tuk", "tunuz", "tular",
              "yorum", "yorsun", "yor", "yoruz", "yorsunuz", "yorlar",
              "mışım", "mışsın", "mış", "mışız", "mışsınız", "mışlar",
              "mişim", "mişsin", "miş", "mişiz", "mişsiniz", "mişler",
              "muşum", "muşsun", "muş", "muşuz", "muşsunuz", "muşlar",
              "müşüm", "müşsün", "müş", "müşüz", "müşsünüz", "müşler",
              "acağım", "acaksın", "acak", "acağız", "acaksınız", "acaklar",
              "eceğim", "eceksin", "ecek", "eceğiz", "eceksiniz", "ecekler")
_VERB_TENSE = ("yor", "dı", "di", "du", "dü", "tı", "ti", "tu", "tü",
               "mış", "miş", "muş", "müş", "acak", "ecek")
_NOUN_CASE = ("ların", "lerin", "ın", "in", "un", "ün", "a", "e", "da", "de",
              "dan", "den", "ı", "i", "u", "ü", "ları", "leri", "im", "in", "i",
              "ile", "la", "le", "yla", "yle", "ta", "te",
              "ydi", "ydı", "ydu", "ydü", "ydular", "ydiler", "ydum", "ydun",
              "ydik", "ydiniz", "ydim", "dir", "dır", "dur", "dür", "tir", "tır",
              "tür", "tu", "tı", "muş", "miş")


def _stem_verb(tok: str):
    """Iteratively strip plural/person/tense/negation/connective/aorist; return a
    VERB_LEMMA stem or None (rule-based light POS, documented in module docstring)."""
    t = tok
    if t.endswith(("lar", "ler")):
        t = t[:-3]
    for p in _VERB_PERS:
        if t.endswith(p):
            t = t[:-len(p)]
            break
    for s in _VERB_TENSE:
        if t.endswith(s):
            t = t[:-len(s)]
            break
    for n in ("me", "ma", "mı", "mi", "mu", "mü"):
        if t.endswith(n):
            t = t[:-len(n)]
            break
    if t in VERB_LEMMA:
        return t
    for v in ("ı", "i", "u", "ü"):
        if t.endswith(v) and t[:-1] in VERB_LEMMA:
            return t[:-1]
    for a in ("ar", "er", "ır", "ir", "ur", "ür", "r"):
        if len(t) > len(a) and t.endswith(a) and t[:-len(a)] in VERB_LEMMA:
            return t[:-len(a)]
    return None


def _strip_noun_suffixes(tok: str):
    """Strip plural and/or one case/possession/copula suffix; return a root that is
    in NOUN_HEADS, or None. (BFS over 2 suffix layers — e.g. bayram+lar+da — capped;
    the root must be a known noun head: precision-first POS classification.)"""
    cands, seen = [tok], {tok}
    for c in cands:
        for case in sorted(_NOUN_CASE, key=len, reverse=True):
            if c.endswith(case) and len(c) > len(case):
                nxt = c[:-len(case)]
                if nxt not in seen and len(cands) < 40:
                    seen.add(nxt); cands.append(nxt)
        if c.endswith(("lar", "ler")) and len(c) > 3:
            nxt = c[:-3]
            if nxt not in seen and len(cands) < 40:
                seen.add(nxt); cands.append(nxt)
    for c in cands:
        if c in NOUN_HEADS:
            return c
    return None


def _strip_any_root(tok: str):
    """Head-free suffix stripper: plural and/or one case/possession/copula suffix.
    Returns the stripped root even if it is not a known noun head (for collocation
    and exempt-set matching)."""
    cands = [tok]
    if tok.endswith(("lar", "ler")):
        cands.append(tok[:-3])
    for c in list(cands):
        for case in sorted(_NOUN_CASE, key=len, reverse=True):
            if c.endswith(case) and len(c) > len(case):
                cands.append(c[:-len(case)])
            if c.endswith(("lar", "ler")) and len(c) > 3:
                cands.append(c[:-3])
    return min(cands, key=len)


def _root_match(toks, i, w, collset):
    """True if a token (or its stripped nominal root) in the +/-w window is in collset."""
    for j in range(max(0, i - w), min(len(toks), i + w + 1)):
        if j == i:
            continue
        t = toks[j].strip(".,;:!?…()[]{}'\"")
        if t in collset:
            return True
        if _strip_any_root(t) in collset:
            return True
    return False


def _root_match_words(text, start, w, collset):
    """Root-match collocate in +/-w words of raw text at start (for inflected gates)."""
    toks = [tr_lower(t) for t, _, _ in _tokens_with_spans(text)]
    i = None
    for k, (t, s0, e0) in enumerate(_tokens_with_spans(text)):
        if s0 <= start < e0 or start <= s0:
            i = k
        if s0 >= start:
            if i is None:
                i = k
            break
    if i is None:
        return False
    return _root_match(toks, i, w, collset)


def _next_root_in(tok, collset):
    """True if next token or its stripped root is in collset (positional gates)."""
    if not tok:
        return False
    t = tok.rstrip(".,;:!?…()[]{}'\"")
    if t in collset:
        return True
    return _strip_any_root(t) in collset


def _next_pos(tok: str):
    """Classify the word following a bare nispet-ek candidate.

    Returns 'NOUN' | 'VERB' | 'POSTP' | None (None = unknown -> no flag).
    Order: exact lexicons -> verb morphology (stem in VERB_LEMMA) -> noun
    morphology (root in NOUN_HEADS) -> unknown.
    """
    if not tok:
        return None
    t = tok.rstrip(".,;:!?…()[]{}'\"")
    if t in NOUN_HEADS:
        return "NOUN"
    if t in POSTPOS:
        return "POSTP"
    # noun-head morphology FIRST: attribute+noun is the dominant pattern and the
    # aorist verb fallback would otherwise swallow noun heads like 'eser' (es-er).
    if _strip_noun_suffixes(t):
        return "NOUN"
    if t in VERB_FORMS or t in VERB_LEMMA:
        return "VERB"
    if _stem_verb(t):
        return "VERB"
    return None


def pos_gate(text: str, end: int):
    """POS gate for attribute position (v3)."""
    nx = _next_word(text, end)
    return _next_pos(nx)


# =====================================================================
# B) 13 minimal pairs — documented kılavuz-vs-GTS rulings
# =====================================================================
# gate kinds: COLL = disambiguating collocation window; STAT = next-token
# statistics / distributional gate; UNCOND = unconditional (GTS registers only
# the caret form).
RULINGS13 = [
    {"word": "kar",  "pair": "kar/kâr", "gate": "COLL",
     "kılavuz": "TDK YK 2012, Düzeltme İşareti: 'kâr (kazanç)' örneklemi",
     "gts": "GTS: kâr = alışveriş işlerinin sağladığı para kazancı; kar = atmosferdeki su buharının yoğunlaşması",
     "logic": "flag iff ±2 window ∩ R11_PROFIT_COLL and not weather; bare 'kar' otherwise legitimate (snow/other)"},
    {"word": "hal",  "pair": "hal/hâl", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'hâl (durum)' örneklemi; inflected hâl+iyelik too",
     "gts": "GTS: hâl = durum; hal = çözme/sebze-meyve hali/tahttan indirme",
     "logic": "flag iff STATE collocate (R11_HAL_STATE) in ±1 window and prev not market-exc; market reading (sebze/meyve...) exempt"},
    {"word": "hala", "pair": "hala/hâlâ", "gate": "STAT",
     "kılavuz": "TDK YK 2012: 'hâlâ (henüz)' örneklemi",
     "gts": "GTS: hâlâ = şimdiye kadar, henüz; hala = babanın kız kardeşi",
     "logic": "flag iff next token ∈ R11_HALA_FOLLOW3 (temporal-verb/adverb statistics: gelmedi, bekliyor, yok, mı, ...); aunt reading requires possessive inflection or kinship collocation ('hala kızı')"},
    {"word": "adet", "pair": "adet/âdet", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'âdet (görenek)' örneklemi",
     "gts": "GTS: âdet = görenek; adet = sayı",
     "logic": "flag iff prev ∈ ADET_PRE or next ∈ ADET_POST (gelenek/oldu/...); number sense exempt"},
    {"word": "aşık", "pair": "aşık/âşık", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'âşık (tutkun)' örneklemi",
     "gts": "GTS: âşık = vurgun, tutkun; aşık = eklem kemiği (aşık kemiği)",
     "logic": "flag iff next ∈ ASIK_POST (ol- family: oldum, oldu, olan...)"},
    {"word": "alem", "pair": "alem/âlem", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'âlem (dünya)' örneklemi",
     "gts": "GTS: âlem = dünya, evren; alem = minare/kubbe/bayrak direği tepesi",
     "logic": "flag iff next ∈ ALEM_POST (duyurdu, oldu, olsun, döndü...); finial reading rare in corpus"},
    {"word": "mani", "pair": "mani/mâni", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'mâni (engel)' örneklemi",
     "gts": "GTS: mâni = engel; mani = mania (psik.) / kısa halk şiiri (mâni)",
     "logic": "flag iff next ∈ MANI_POST (ol- family); known limitation: 'mâni' poem-sense collocations (mâni söylemek) not gated -> misses documented"},
    {"word": "dahi", "pair": "dahi/dâhi", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'dâhi (deha sahibi)' örneklemi; 'dahi' bağlaç yazımı korunur",
     "gts": "GTS: dâhi = olağanüstü yetenekli kimse; dahi = bağlaç (da)",
     "logic": "flag iff ±2 window ∩ DAHI_COLL (deha, zekâ, bilim...); bare 'dahi' as conjunction sanctioned"},
    {"word": "yar",  "pair": "yar/yâr", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'yâr (sevgili)' örneklemi",
     "gts": "GTS: yâr = sevgili; yar = uçurum",
     "logic": "flag iff next ∈ YAR_POST (uğruna, olur, olsun, gibi, için, sevgili...); cliff sense exempt"},
    {"word": "hakim", "pair": "hakim/hâkim", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'hâkim (egemen, yargıç)' örneklemi",
     "gts": "GTS: hâkim = egemenliğini yürüten; hakim = bilge (hakîm okunuşu)",
     "logic": "flag unless ±2 window ∩ HAKIM_EXEMPT (bilge, hikmet, filozof...)"},
    {"word": "şura", "pair": "şura/şûra", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'şûra (danışma kurulu)' örneklemi",
     "gts": "GTS: şûra = danışma kurulu; şura = şu yer",
     "logic": "flag iff ±2 window ∩ SURA_COLL (danışma, kurul, güvenlik...)"},
    {"word": "rahim", "pair": "rahim/rahîm", "gate": "COLL",
     "kılavuz": "TDK YK 2012: 'rahîm (koruyan, acıyan — Allah)' örneklemi",
     "gts": "GTS: rahîm = koruyan, acıyan (Tanrı); rahim = döl yatağı",
     "logic": "flag iff ±2 window ∩ RAHIM_COLL (allah, merhamet, esirgeyen...); womb sense exempt"},
    {"word": "halen", "pair": "halen/hâlen", "gate": "STAT",
     "kılavuz": "TDK YK 2012 lists hâlen (şimdiye kadar / şu anda)",
     "gts": "GTS registers ONLY 'hâlen' — bare 'halen' has no headword (hard 'halen' -> hâlen)",
     "logic": "unconditional (quasi Mode-A): bare 'halen' flagged always; temporal-adverb slot"},
]
KAZIM_RULING = ("kazım/Kâzım — kılavuz lists 'Kâzım'; GTS headword is only 'kazım' "
                "(kazmak işi). Ruling: GTS wins -> Kâzım NOT flagged, word excluded "
                "from the battery (documented kılavuz-vs-GTS tension).")

# hala STAT gate extension (next-token temporal-verb statistics, v2 + new)
R11_HALA_FOLLOW3 = R11_HALA_FOLLOW | {
    "gelmedi", "gelmiyor", "gelmemiş", "gitmedi", "gitmiyor", "bitmedi",
    "bitmiyor", "olmadı", "olmayan", "bekliyorum", "bekliyorsun", "duruyor",
    "çalışıyor", "yok", "gelemedi", "gelememiş", "gönderilmedi", "dönmedi",
    "uğramadı", "cevaplamadı", "aramadı",
}

# bare-surface regex: v2 31 tokens + 3 new nispet words = 34 tokens
_R11_BARE3 = re.compile(
    r"\b(kağıt|rüzgar|ruzgar|hükümet|hukumet|sanatkar|katip|kainat|halen|kabe|"
    r"milli|resmi|dini|tarihi|ilmi|askeri|fikri|hissi|zihni|"
    r"kar|hal|hala|adet|aşık|alem|mani|dahi|yar|hakim|şura|rahim)\b", re.IGNORECASE)
_R11_BARE_TOKENS3 = re.compile(
    r"kağıt|rüzgar|ruzgar|hükümet|hukumet|sanatkar|katip|kainat|halen|kabe|"
    r"milli|resmi|dini|tarihi|ilmi|askeri|fikri|hissi|zihni|"
    r"kar|hal|hala|adet|aşık|alem|mani|dahi|yar|hakim|şura|rahim")
# inflected possessive forms: kar+kâr (kazanç) and adet+âdet (görenek)
_R11_KAR_INF = re.compile(r"\bkar(ı|ım|ımız|ımızın|ımızı|ın|ını|ına|ından|ınız|"
                          r"ları|ların|larını|larına|larından|larıyla|ıyla|la|dan|da)\b", re.IGNORECASE)
_R11_ADET_INF = re.compile(r"\badet(im|in|i|imiz|iniz|ine|inden|leri|lerin|"
                           r"lerine|leriyle|iyle|e)\b", re.IGNORECASE)


def rule_caret3(text: str):
    """R11 v3: Mode-A + 9-word POS-gated ATTR + 13-pair gated COLL."""
    out = []
    toks = _tokens_with_spans(text)
    words = [tr_lower(t) for t, _, _ in toks]
    for i, (tok, s0, e0) in enumerate(toks):
        t = tr_lower(tok).strip(".,;:!?…()[]{}'\"")
        if not t or not _R11_BARE_TOKENS3.fullmatch(t if len(t) <= 12 else "skip"):
            continue
        # ---- MODE_A: unconditional bare spellings ----
        if t in R11_A:
            right, note = R11_A[t]
            out.append({"span": tok, "msg": f"'{tok}': düzeltme işareti gerekir ('{right}') — {note}"})
            continue
        if t == "kabe":
            out.append({"span": tok, "msg": f"'{tok}': özel ad 'Kâbe' düzeltme işaretiyle yazılır"})
            continue
        # ---- MODE_ATTR (9 nispet words): POS gate (v3) ----
        if t in R11_ATTR3:
            right, note = R11_ATTR3[t]
            p = pos_gate(text, e0)
            if p == "NOUN":
                nx = _next_word(text, e0)
                out.append({"span": tok, "msg": f"'{tok}': nispet eki düzeltme işaretiyle yazılır ('{right} {nx}') — {note}"})
            continue
        # ---- MODE_COLL: 13 minimal pairs ----
        if t == "kar":
            nxt = words[i + 1] if i + 1 < len(words) else ""
            weather = not nxt.startswith("yağ") and not _root_match(words, i, 2, _R11_WEATHER)
            if weather and _root_match(words, i, 2, R11_PROFIT_COLL):
                out.append({"span": tok, "msg": f"'{tok}': kazanç anlamında 'kâr' yazılır (GTS: kâr = alışveriş işlerinin sağladığı para kazancı)"})
            continue
        if t == "hal":
            prev = _prev_word(text, s0)
            if prev not in R11_HAL_MARKET_EXC:
                nx = _next_word(text, e0)
                if _next_root_in(nx, R11_HAL_STATE) or _root_match(words, i, 1, R11_HAL_STATE):
                    out.append({"span": tok, "msg": f"'{tok}': durum anlamında 'hâl' yazılır (GTS: hâl = durum, vaziyet)"})
            continue
        if t == "hala":
            nx = _next_word(text, e0)
            if nx and (nx in R11_HALA_FOLLOW3 or nx.endswith(("yor", "yordum", "yordur"))):
                out.append({"span": tok, "msg": f"'{tok}': 'henüz' anlamında 'hâlâ' yazılır (GTS: hâlâ = şimdiye kadar; hala = babanın kız kardeşi)"})
            continue
        if t == "adet":
            prev, nx = _prev_word(text, s0), _next_word(text, e0)
            if _next_root_in(prev, R11_ADET_PRE) or _next_root_in(nx, R11_ADET_POST):
                out.append({"span": tok, "msg": f"'{tok}': görenek anlamında 'âdet' yazılır (GTS: âdet = görenek; adet = sayı)"})
            continue
        if t == "aşık":
            nx = _next_word(text, e0)
            if _next_root_in(nx, R11_ASIK_POST):
                out.append({"span": tok, "msg": f"'{tok}': tutkun anlamında 'âşık' yazılır (GTS: âşık = vurgun, tutkun; aşık = eklem kemiği)"})
            continue
        if t == "alem":
            nx = _next_word(text, e0)
            if _next_root_in(nx, R11_ALEM_POST):
                out.append({"span": tok, "msg": f"'{tok}': dünya/evren anlamında 'âlem' yazılır (GTS: âlem = dünya, evren; alem = bayrak)"})
            continue
        if t == "mani":
            nx = _next_word(text, e0)
            if _next_root_in(nx, R11_MANI_POST):
                out.append({"span": tok, "msg": f"'{tok}': engel anlamında 'mâni' yazılır (GTS: mâni = engel; mani = mania)"})
            continue
        if t == "dahi":
            if _root_match(words, i, 2, R11_DAHI_COLL):
                out.append({"span": tok, "msg": f"'{tok}': deha anlamında 'dâhi' yazılır (GTS: dâhi; dahi = bağlaç)"})
            continue
        if t == "yar":
            nx = _next_word(text, e0)
            if _next_root_in(nx, R11_YAR_POST):
                out.append({"span": tok, "msg": f"'{tok}': sevgili anlamında 'yâr' yazılır"})
            continue
        if t == "hakim":
            if not _root_match(words, i, 2, R11_HAKIM_EXEMPT):
                out.append({"span": tok, "msg": f"'{tok}': yargıç/egemen anlamında 'hâkim' yazılır (GTS: hâkim; 'hakim' = bilge okunuşu için hakîm)"})
            continue
        if t == "şura":
            if _root_match(words, i, 2, R11_SURA_COLL):
                out.append({"span": tok, "msg": f"'{tok}': danışma kurulu anlamında 'şûra' yazılır (GTS: şûra = danışma kurulu; şura = şu yer)"})
            continue
        if t == "rahim":
            if _root_match(words, i, 2, R11_RAHIM_COLL):
                out.append({"span": tok, "msg": f"'{tok}': koruyan anlamında 'rahîm' yazılır (GTS: rahîm = koruyan, merhamet eden)"})
            continue
        if t == "halen":  # pair #13 — unconditional (GTS registers only hâlen)
            out.append({"span": tok, "msg": f"'{tok}': 'şimdiye kadar/şu anda' anlamında 'hâlen' yazılır (GTS: sadece 'hâlen' madde başı)"})
            continue
    # ---- inflected possessive forms of kar (kâr + iyelik) and adet (âdet + iyelik) ----
    for m in _R11_KAR_INF.finditer(text):
        nxt = _next_word(text, m.end())
        w = not nxt.startswith("yağ") and not _root_match_words(text, m.start(), 2, _R11_WEATHER)
        if w and _root_match_words(text, m.start(), 2, R11_PROFIT_COLL):
            out.append({"span": m.group(0), "msg": f"'{m.group(0)}': kazanç anlamında 'kâr{m.group(0)[3:]}' yazılır (GTS: kâr = alışveriş işlerinin sağladığı para kazancı)"})
    for m in _R11_ADET_INF.finditer(text):
        nx = _next_word(text, m.end())
        if _next_root_in(nx, R11_ADET_POST):
            out.append({"span": m.group(0), "msg": f"'{m.group(0)}': görenek anlamında 'âdet{m.group(0)[4:]}' yazılır (GTS: âdet = görenek; adet = sayı)"})
    # ---- inflected state-forms of hal (hâl + possession) ----
    for m in _R11_HAL_INFLECTED.finditer(text):
        prev = _prev_word(text, m.start())
        if prev not in R11_HAL_MARKET_EXC:
            out.append({"span": m.group(0),
                        "msg": f"'{m.group(0)}': durum anlamında 'hâl{m.group(0)[3:]}' yazılır (hâl + iyelik; GTS: hâl = durum)"})
    return out


def check_text3(text: str) -> Dict[str, List[dict]]:
    """R1..R13 with v3 R11 (POS-gated nispet-ek + 13 gated pairs)."""
    v = check_text2(text)
    v["R11_caret"] = rule_caret3(text)
    return v


def summarize3(text: str) -> dict:
    v = check_text3(text)
    return {"violations": v, "total": sum(len(x) for x in v.values())}


if __name__ == "__main__":
    import sys
    demo = ("Şirketin net karı beklentiyi aştı; milli takım maçını izledik; "
            "resmi evrak için dilekçe gerekli; tarihi eserler müzeye taşındı. "
            "O resmi çizdi; şehrin tarihi boyunca; bu fikri çok beğendim; hala gelmedi; "
            "halen görevde misin?")
    print(summarize3(demo))
    print("RULINGS13:", len(RULINGS13), "rows;", KAZIM_RULING)