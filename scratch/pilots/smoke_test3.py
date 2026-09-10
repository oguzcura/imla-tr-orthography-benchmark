# -*- coding: utf-8 -*-
"""smoke_test3.py — P/R validation for imla_checker3 (R11 caret gate).

22 positives + 20 negatives, hand-built from the full-study elicitation targets
(14 BATTERY words each with its ruling gate) + 9 nispet-ek POS cases + traps.
Reports precision/recall; prints any mismatch for inspection.

Positives: bare spelling in a flagged context (per RULINGS13 gate).
Negatives: correct-caret forms, possessive readings, safe readings, and gates
that intentionally do NOT fire (conjunction dahi, mountain yar, womb rahim,
plural maniler, name Şura, number adet, weather kar, market hal/garden hala,
possessive nispet-ek with verb head, postposition boyunca, flat adjective bütün).
"""
import sys
sys.path.insert(0, r"C:\Users\oguzc\ai-team\research\scratch\pilots")
from imla_checker3 import check_text3, rule_caret3, RULINGS13

P = [
    ("kar/net",   "Şirketin net karı beklentiyi aştı."),
    ("milli",     "Milli takım maçını izledik."),
    ("resmi",     "Resmi evrak için dilekçe gerekli."),
    ("dini",      "Dini bayramlarda büyüklerimizi ziyaret ederiz."),
    ("tarihi",    "Tarihi eserler müzeye taşındı."),
    ("ilmi",      "Dergide ilmi tartışmalar sürüyor."),
    ("askeri",    "Oğlum askeri okulu kazandı."),
    ("fikri",     "Yazarın fikri mülkiyet hakları korunmalı."),
    ("hissi",     "Mektubun hissi yaklaşımı beni etkiledi."),
    ("zihni",     "Sınav sonrası zihni yorgunluk yaşadım."),
    ("adet",      "Bu köyde düğün adeti oldu."),
    ("aşık",      "Sana aşık oldum."),
    ("alem",      "Haberi tüm alem duyurdu."),
    ("mani",      "Trafik bize mani oldu."),
    ("dahi",      "Bu çocuk gerçek bir dahi."),
    ("yar",       "Sevdiğim yar uğruna türküler söylüyorum."),
    ("hakim",     "Hakim kararı temyiz edildi."),
    ("şura",      "Şura kararı dün açıklandı."),
    ("rahim",     "Allah rahim ve esirgeyendir."),
    ("halen",     "Halen görevde misin?"),
    ("hala",      "Otobüs hala gelmedi."),
    ("hal+hâl",   "Amcamın hali iyi."),
]

N = [
    ("caret-doğru", "Kâr marjı geçen yıla göre daraldı."),
    ("kar/hava",    "Gece kar yağdı, her yer bembeyaz oldu."),
    ("adet/sayı",   "Üç adet kitap aldım."),
    ("hala/iyelik", "Halam bize gelecek."),
    ("hal/pazar",   "Manavdaki sebze haline uğradım."),
    ("resmi/çizdi", "O resmi çizdi."),
    ("dini/bütün",  "Dini bütün bir insandır."),
    ("tarihi/boyunca", "Şehrin tarihi boyunca birçok deprem oldu."),
    ("dahi/bağlaç", "Bunu dahi yapmadı."),
    ("yar/uçurum",  "Yar uçurumun kenarıdır."),
    ("mani/çokluk", "Maniler söylerdi."),
    ("rahim/döl",   "Rahim dokusu ameliyatla alındı."),
    ("şura/ad",     "Şura adında bir kedi var."),
    ("hakim/bilge", "Hoca hakim bir bilgeydi."),
    ("hala/kızı",   "Hala kızı düğüne gelecek."),
    ("hal/pazar2",  "Hal ticaretinin merkezi İstanbul'dur."),
    ("askeri/terhis", "Askeri terhis ettiler."),
    ("caret-doğru2", "Hâlen bu şehirde yaşıyor."),
    ("fikri/iyelik", "Bu fikri çok beğendim."),
    ("zihni/iyelik", "Zihni her an meşguldü."),
]

def flags(text):
    return rule_caret3(text)

tp = fp = 0
print("== POSITIVES (expect >=1 flag each) ==")
for label, s in P:
    f = flags(s)
    ok = len(f) > 0
    tp += ok
    print(f"  {'PASS' if ok else 'FAIL'} {label:15s} flags={len(f)} :: {[x['span'] for x in f]}")
print("== NEGATIVES (expect 0 flags each) ==")
for label, s in N:
    f = flags(s)
    ok = len(f) == 0
    fp += (not ok)
    print(f"  {'PASS' if ok else 'FAIL'} {label:15s} flags={len(f)} :: {[x['span'] for x in f]}")
nP, nN = len(P), len(N)
print(f"\nprecision = {tp}/{tp+fp} = {tp/(tp+fp):.2f}   recall(over P) = {tp}/{nP} = {tp/nP:.2f}")
print(f"RULINGS13 rows: {len(RULINGS13)}")