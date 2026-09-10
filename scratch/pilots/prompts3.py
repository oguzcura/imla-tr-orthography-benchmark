# -*- coding: utf-8 -*-
"""prompts3.py — Imla FULL STUDY unprimed prompt battery.

UNPRIMED DESIGN (the priming effect is the headline):
  * ZERO caret glyphs anywhere in prompts (asserted: no a\u0302/i\u0302/u\u0302 chars).
  * ZERO bare spellings of any caret-target word (asserted via word-boundary regex
    over the full target lexicon).
  * Target words are elicited ONLY by circumlocution / collocation context so that
    any caret the model emits is fully autonomous (no in-prompt spelling cue).

Registers: chat, social, forum (informal); news, essay (formal).
Battery size: n_total >= 200, formal arm >= 24 (v2's 24 texts was too thin; here the
formal arm is 36 PROMPTS x 6 models = 216 formal texts).
"""
import re

# ---------------------------------------------------------------------------
# Target lexicon (caret forms = GTS-registered headwords; bare = the drop form).
# Words whose canonical spelling carries a caret (GTS overrides kılavuz where
# they conflict; rulings in imla_checker3.RULINGS / imla_full.md).
# ---------------------------------------------------------------------------

# Tier A: only the caret spelling is a GTS headword -> bare is ALWAYS wrong.
TIER_A_BARE = ["kağıt", "rüzgar", "ruzgar", "hükümet", "hukumet", "sanatkar",
               "katip", "kainat", "kabe", "halen"]

# Tier B: nispet-ek attribute adjectives, caret is the attribute-headword form
# (GTS-registered); bare is wrong ONLY in attribute (adjective) position.
NISPET_BARE = ["milli", "resmi", "dini", "tarihi", "ilmi", "askeri",
               "fikri", "hissi", "zihni"]

# Tier C: minimal pairs -- bare is wrong ONLY in the caret sense (collocation/
# STAT-gated). 13 pairs incl. halen (GTS registers only hâlen -> unconditional).
PAIR_BARE = ["kar", "hal", "hala", "adet", "aşık", "alem", "mani", "dahi",
             "yar", "hakim", "şura", "rahim", "halen"]
PAIR_CARET = ["kâr", "hâl", "hâlâ", "âdet", "âşık", "âlem", "mâni", "dâhi",
              "yâr", "hâkim", "şûra", "rahîm", "hâlen"]

# Inflected trigger forms (hal/hala/aşık/hakim families) -- bare surface forms
# that are only ever correct in the non-caret sense and signal the caret word.
INFLECTED_BARE = ["halim", "halin", "hali", "haline", "halinde", "halinden",
                  "halam", "halası", "halamın", "halama", "halamdan",
                  "aşık", "aşığı", "aşığım", "aşıksın", "aşıkım",
                  "aşık oldu", "aşık ol", "aşık olmak", "aşık olma",
                  "hakimi", "hakimin", "hakimlik", "hakimler"]

CARET_SURFACES = (["kâğıt", "rüzgâr", "hükûmet", "sanatkâr", "kâtip", "kâinat",
                   "Kâbe", "kâbe"]
                  + NISPET_BARE  # bare spellings in attr position -> flag
                  + [c for c in PAIR_CARET if c != "kâbe"])

# Word-boundary regex over ALL bare target spellings (prompt hygiene check).
_BARE_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(w) for w in
                         set(TIER_A_BARE + NISPET_BARE + PAIR_BARE)) + r")\b",
    re.IGNORECASE)
_CARET_GLYPH = re.compile(r"[âîû]")

def find_primers(text):
    """Return (glyph_hits, word_hits) for one prompt text."""
    return (_CARET_GLYPH.findall(text), sorted(set(_BARE_PATTERN.findall(text))))

def assert_unprimed():
    """Hard gate: every prompt must be glyph-free and bare-spelling-free."""
    bad = []
    for genre, pid, text in PROMPTS:
        g, w = find_primers(text)
        if g or w:
            bad.append((genre, pid, g, w))
    if bad:
        raise SystemExit("UNPRIMED VIOLATIONS:\n" +
                         "\n".join(f"{a} {b}: glyphs={c} words={d}" for a, b, c, d in bad))
    print(f"[assert_unprimed] OK: {len(PROMPTS)} prompts, 0 caret glyphs, 0 bare target spellings")

# ---------------------------------------------------------------------------
# Informal arm: chat (60) | social (60) | forum (60)   -- n_informal = 180
# ---------------------------------------------------------------------------
_CHAT = []
_SOC = []
_FOR = []
# Formal arm: news (18) | essay (18)                    -- n_formal = 36
_NEWS = []
_ESS = []

# ---------------- CHAT (WhatsApp / messenger, 60) ----------------
C = [
 ("kâr", "Bir WhatsApp yazışması yaz. Sen küçük bir bakkal işletiyorsun, ablan yaklaşan yıl sonunu ve dükkanın elde ettiği gelir fazlasını soruyor. Sen ona işlerin nasıl gittiğini anlat. 60-100 kelime, günlük samimi dil."),
 ("kâr", "WhatsApp yazışması yaz. İki ortak yıl sonunda işlerin iyi gittiğini, elde ettikleri gelir fazlasının beklentiyi aştığını konuşuyor. Bir sonraki yıl için plan yapıyorlar. 60-100 kelime, samimi üslup."),
 ("kâr", "Bir WhatsApp yazışması yaz. Manav sahibi bir arkadaşın bu sezon çok iyi satış yaptığını, elinde kalan net gelirle dükkanını büyütmeyi düşündüğünü söylüyor. Sen ona fikrini söyle. 60-100 kelime."),
 ("kâr", "WhatsApp yazışması yaz. Bir arkadaşın borsada yaptığı işlemden iyi bir getiri elde ettiğini anlatıyor, sen de onu kutluyorsun ve küçük bir uyarı yapıyorsun. 60-100 kelime, günlük dil."),
 ("kâr", "WhatsApp yazışması yaz. Sen bir lokanta işletiyorsun, muhasebeci yıl sonu hesabını çıkarınca elde edilen gelir fazlasının geçen yıla göre arttığını görüyorsun. Bunu aile grubunda anlat. 60-100 kelime."),
 ("hâlâ", "WhatsApp yazışması yaz. Arkadaşın sana otobüsün gelip gelmediğini soruyor; saatlerdir bekliyorsun ve otobüs bir türlü görünmüyor. Sinirli ama esprili bir dille cevap yaz. 60-100 kelime."),
 ("hâlâ", "WhatsApp yazışması yaz. Kuzenin ödevini teslim edip etmediğini soruyor. Sen ödevi akşam bitirdin ama telefonda konuştuğun hocan sonucu şu ana kadar bildirmedi. Durumu anlat. 60-100 kelime."),
 ("hâlâ", "WhatsApp yazışması yaz. Annen sana yemeği yiyip yemediğini soruyor; sen işten yeni çıktın, evde yemek pişmedi ve dışarıdan söylemeyi düşünüyorsun. Cevap yaz. 60-100 kelime, samimi dil."),
 ("hâlâ", "WhatsApp yazışması yaz. Arkadaşın iki saattir görüşmediğinizi söylüyor, sen de kargo kuryesinin gün boyu gelmediğini ve paketi beklediğini anlatıyorsun. 60-100 kelime."),
  ("hâlâ", "WhatsApp yazışması yaz. Arkadaşın aradığın kiracıyı bulup bulamadığını soruyor. Görüştüğün adaylar vardı ama evi tutan olmadı, boşluk sürüyor. Durumu içtenlikle anlat. 60-100 kelime."),
 ("hâl", "WhatsApp yazışması yaz. Uzun zamandır görüşmediğin bir dostuna durumunun nasıl olduğunu, sağlığının iyi olup olmadığını soran bir mesaj yazıyorsun. Misafirliğe de çağır. 60-100 kelime, sıcak üslup."),
 ("hâl", "WhatsApp yazışması yaz. Bir arkadaşın deprem bölgesindeki akrabasından haber bekliyor; tanıdığın bir esnafa durumlarının ne olduğunu soruyorsun. Kaygılı ama ölçülü bir dil. 60-100 kelime."),
 ("hâl", "WhatsApp yazışması yaz. Hasta olan amcanı aradın, sesi iyi gelmiyor. Ona bugününü nasıl geçirdiğini, durumunun ne durumda olduğunu soruyorsun, ilaçlarını hatırlatıyorsun. 60-100 kelime."),
 ("hâl", "WhatsApp yazışması yaz. Eski öğretmenin merhaba dedi; sen ona emeklilik günlerinin nasıl geçtiğini, durumunun iyi olup olmadığını soruyorsun. Saygılı, samimi bir mesaj. 60-100 kelime."),
 ("hâl", "WhatsApp yazışması yaz. Kardeşin iş görüşmesine girdi, sen sonucu bekliyorsun. Soruyorsun: ne oldu, durumu nasıl, aldığı haber ne? Heyecanını belli et. 60-100 kelime."),
 ("kâğıt", "WhatsApp yazışması yaz. Ofiste yazıcı için kullanılan malzeme bitti, sen de amirine mesaj atıp ne yapacağını soruyorsun pratik bir çözüm öneriyorsun. 60-100 kelime."),
 ("kâğıt", "WhatsApp yazışması yaz. İki arkadaş sınav öncesi not çıkarmak için malzeme paylaşımı yapıyor; birinin aklına yazıcıda çıktı almak geliyor ama malzeme az. Ne yapacaklarını konuş. 60-100 kelime."),
 ("kâğıt", "WhatsApp yazışması yaz. Bir arkadaşın evrak ofisine uğradı, belgeleri basmak için gereken malzeme kalmamış, bu yüzden imzası gecikmiş. Durumu sana dert yanarak anlat. 60-100 kelime."),
 ("rüzgâr", "WhatsApp yazışması yaz. Piknik planı yaptınız, arkadaşın hava tahminine bakıyor: kuvvetli hava akımı uyarısı var, çadır devrilir mi diye endişeleniyor. Planı konuşun. 60-100 kelime."),
 ("rüzgâr", "WhatsApp yazışması yaz. Balkondaki saksıların geceki kuvvetli hava akımında devrildiğini, sabah dağıldığını arkadaşına anlat. Komik bir dille yaz. 60-100 kelime."),
 ("şûra", "WhatsApp yazışması yaz. Mahallede güvenlik konularını görüşmek üzere bir danışma kurulu toplantısı yapılacak; sen muhtara kimlerin katılacağını soruyorsun. 60-100 kelime."),
 ("kâr", "WhatsApp yazışması yaz. İki esnaf dost komşu dükkanların yıl sonu kazançlarını konuşuyor; biri geçen yıla göre daha iyi getiri elde ettiğini söylüyor, diğeri ona takılıyor. 60-100 kelime."),
 ("âdet", "WhatsApp yazışması yaz. Yeni evlenen arkadaşın kendi memleketindeki düğün geleneklerini soruyor; sen kendi yörendeki geleneksel uygulamaları anlatıyorsun. 60-100 kelime, samimi."),
 ("âdet", "WhatsApp yazışması yaz. Kardeşin bayramda büyüklerin elini öpme geleneğinin unutulup unutulmadığını soruyor; sen bu geleneğin sizin evde sürdüğünü anlatıyorsun. 60-100 kelime."),
 ("âdet", "WhatsApp yazışması yaz. İki arkadaş yeni yılda ev ziyaretlerinin, kapı kapı dolaşmanın eski bir gelenek olup olmadığını tartışıyor. Birbirinize örnekler verin. 60-100 kelime."),
 ("âdet", "WhatsApp yazışması yaz. Bir arkadaşın işe yeni başladı, ilk gün uyulması gereken yazılı olmayan kuralları sana soruyor. Sen de deneyimlerini anlatıyorsun. 60-100 kelime."),
 ("âşık", "WhatsApp yazışması yaz. Bir arkadaşın yeni tanıştığı birine gönlünü kaptırdığını itiraf ediyor; sen ona takılıp akıl veriyorsun. 60-100 kelime, günlük samimi dil."),
 ("âşık", "WhatsApp yazışması yaz. Arkadaşın çocukluktan beri tanıdığı kişiye duyduğu karşılıksız sevgiyi anlatıyor; sen onu dinleyip cesaretlendiriyorsun. 60-100 kelime."),
 ("millî", "WhatsApp yazışması yaz. Maç günü arkadaşınla yazışıyorsun: ülkenin ulusal futbol takımının akşamki karşılaşmasını, hangi kanalda yayınlanacağını konuşuyorsun. 60-100 kelime."),
 ("millî", "WhatsApp yazışması yaz. Okulun 29 Ekim kutlamasındaki gösteri için kostüm hazırlığı yapıyorsunuz; ulusal bayram provasının saatini konuşuyorsun. 60-100 kelime."),
 ("resmî", "WhatsApp yazışması yaz. Pasaport işlemleri için devlet dairesinin istediği belgeleri hazırlıyorsun; hangi evrakların gerektiğini arkadaşına soruyorsun. 60-100 kelime."),
 ("dinî", "WhatsApp yazışması yaz. İki arkadaş yaklaşan bayramda hangi günlerde ibadete ağırlık vereceklerini, bayram namazı saatini konuşuyor. 60-100 kelime."),
 ("âdet", "WhatsApp yazışması yaz. Kına gecesinde yapılan geleneksel uygulamaları, yakılan türküleri ve takılan kırmızı kuşağı anlatan bir yazışma yaz. 60-100 kelime."),
 ("resmî", "WhatsApp yazışması yaz. Sen bir öğretmensin, veli okulda öğrencisi için nüfus kaydı ve dilekçe gibi devlet işlemlerinin nasıl yürüdüğünü soruyor; yönlendiriyorsun. 60-100 kelime."),
 ("tarihî", "WhatsApp yazışması yaz. Gezi planı yapıyorsunuz; arkadaşın eski dönemlerden kalma yapıları, kervansarayları görmek istiyor, sen de program öneriyorsun. 60-100 kelime."),
 ("hâkim", "WhatsApp yazışması yaz. Bir arkadaşın mahkemesi vardı; davanın sonucunu, yargıcın verdiği kararı sana anlatıyor. Sen de teselli ediyorsun. 60-100 kelime."),
 ("hâkim", "WhatsApp yazışması yaz. Komşunun kiracısıyla davası var; sen de o davaya bakan yargıcın tanındığını, tarafsız biri olduğunu anlatıyorsun. 60-100 kelime."),
 ("hâlâ", "WhatsApp yazışması yaz. Arkadaşın seni kahveye çağırdı ama sen işten çıkamadın, gün boyu mesai uzadı, toplantılar bitmedi. Özür dileyip yeniden söz ver. 60-100 kelime."),
 ("kâğıt", "WhatsApp yazışması yaz. Okulun duyuru panosuna asmak için bildiri bastıracaksın; kırtasiyeciden fiyat alıyorsun, baskı malzemesinin kaç sayfa tutacağını hesaplıyorsun. 60-100 kelime."),
 ("hükûmet", "WhatsApp yazışması yaz. İki arkadaş yeni yılda devlet yönetiminin açıkladığı ekonomik önlemleri, zamları ve destek paketlerini konuşuyor. 60-100 kelime, günlük dil."),
 ("hükûmet", "WhatsApp yazışması yaz. Aile grubunda bakanlar kurulunun duyurduğu yeni düzenlemeleri, enerji yardımını ve maaş artışını tartışıyorsunuz. 60-100 kelime."),
 ("tarihî", "WhatsApp yazışması yaz. Arkadaşın ilçendeki eski dönemden kalma köprü ve hanların restore edildiğini duymuş; sen de gördüklerini anlatıyorsun. 60-100 kelime."),
 ("sanatkâr", "WhatsApp yazışması yaz. Bir arkadaşın el emeğiyle çalışan bakır ustası birini tanıyor; ondan sürahi yaptırmak istiyor, fiyat ve süre soruyorsun. 60-100 kelime."),
 ("millî", "WhatsApp yazışması yaz. İki arkadaş ulusal bayramda okunacak marşın provasını, öğrencilerin giyeceği kıyafetleri konuşuyor. 60-100 kelime."),
 ("âdet", "WhatsApp yazışması yaz. Aile büyüğünün doğum günlerinde, özel günlerde uygulanan geleneksel selamlaşma ve hediye kurallarını iki kuzen birbirine anlatıyor. 60-100 kelime."),
 ("kâr", "WhatsApp yazışması yaz. Çiftçi bir arkadaşın bu yıl hasat iyi olduğu için elinde kalan net gelirin arttığını söylüyor; sen de ona traktör almasını öneriyorsun. 60-100 kelime."),
 ("âşık", "WhatsApp yazışması yaz. İki genç arkadaş birinin okuldaki birine duyduğu sevgiyi, onu görünce dilinin tutulmasını konuşuyor. 60-100 kelime, şakacı dil."),
 ("hâkim", "WhatsApp yazışması yaz. Bir arkadaşın stajını adliyede yapıyor; duruşmalara giren yargıcın ciddiyetini, karar anındaki soğukkanlılığını anlatıyor. 60-100 kelime."),
 ("millî", "WhatsApp yazışması yaz. Spor salonundaki ulusal takım kampına seçilen arkadaşını kutluyorsun; antrenman programını, hocanın beklentisini konuşuyorsun. 60-100 kelime."),
 ("resmî", "WhatsApp yazışması yaz. Belediyeden devlete ait bir evrak istiyorsun; hangi birime gitmen gerektiğini, yanında neler götüreceğini arkadaşına soruyorsun. 60-100 kelime."),
 ("rüzgâr", "WhatsApp yazışması yaz. Tekne turu planlıyorsunuz; arkadaşın denizdeki kuvvetli hava akımı yüzünden seferlerin iptal olup olmadığını soruyor. 60-100 kelime."),
 ("zihnî", "WhatsApp yazışması yaz. Sınava hazırlanan arkadaşın kafa yormaktan çok yorulduğunu, konsantre olamadığını anlatıyor; sen de mola vermesini öneriyorsun. 60-100 kelime."),
 ("hissî", "WhatsApp yazışması yaz. İki arkadaş bir filmin sonunda ağladıklarını, duygu yüklü bir sahnenin onları etkilediğini birbirine anlatıyor. 60-100 kelime."),
 ("âdet", "WhatsApp yazışması yaz. Şehir dışına taşınan arkadaşın yeni yerinde karşılama geleneğini soruyor: kapı kapı gezilir mi, komşuya ilk kim gider? Bilgini paylaş. 60-100 kelime."),
 ("hâlâ", "WhatsApp yazışması yaz. Kardeşin elektronik eşya siparişini bekliyor; kargo firması iki gündür teslimat yapmadı, sen de müşteri hizmetlerine yazıyorsun. Yazışmayı kur. 60-100 kelime."),
 ("hâl", "WhatsApp yazışması yaz. Memleketinde sel oldu, dayını arayıp evin, bahçenin durumunu soruyorsun; o da sakinleştirici bir cevap veriyor. 60-100 kelime."),
 ("hâl", "WhatsApp yazışması yaz. Yeni taşındığın evde internet kurulamadı; komşundan kendi bağlantısının durumunu soruyorsun, yardım istiyorsun. 60-100 kelime."),
 ("âdet", "WhatsApp yazışması yaz. Bayram sabahı aile büyüklerini ziyaret geleneğini iki kardeş planlıyor; kimin evine önce gidileceğini konuşuyorlar. 60-100 kelime."),
 ("kâr", "WhatsApp yazışması yaz. Taksi şoförü bir arkadaşın bayramda yolcu fazlalığından iyi getiri elde ettiğini anlatıyor; sen de ona aracın bakımını hatırlatıyorsun. 60-100 kelime."),
 ("Kâbe", "WhatsApp yazışması yaz. Umreye giden teyzen Mekke'deki kutsal yapıyı ziyaret ettiğini, tavaf ettiğini anlatıyor; sen de ona dua etmesini söylüyorsun. 60-100 kelime."),
]
_CHAT = [(i, t) for i, (_, t) in enumerate(C, 1)]
assert len(_CHAT) == 60, len(_CHAT)

# ---------------- SOCIAL (posts + comments, 60) ----------------
S = [
 ("rüzgâr", "Sosyal medyada paylaşılmış gibi bir gönderi yaz: gece çıkan kuvvetli hava akımı elektrikleri kesti, sabah mahalle karanlıkta kaldı. Altına iki yorum ekle. 60-100 kelime."),
 ("rüzgâr", "Sosyal medya gönderisi yaz: sahil kasabasında fırtına şemsiyeleri uçurdu, plajdaki kafeler zarar gördü. Gönderi + iki yorum. 60-100 kelime."),
 ("rüzgâr", "Sosyal medyada paylaş: dağ bisikleti turunda sert hava akımına yakalandın, yokuşta zorlandın, yine de eğlendin. İki yorum ekle. 60-100 kelime."),
 ("hâlâ", "Sosyal medyada paylaş: iki haftadır randevu almak için hastaneyi aradın, telefonlar meşgul, bir türlü ulaşamıyorsun. Altına yorumlar ekle. 60-100 kelime."),
 ("hâlâ", "Sosyal medya gönderisi: elektrikli bisikletin şarjı çabuk bitiyor, servise gönderdin, aradan üç hafta geçti, haber yok. İki yorum ekle. 60-100 kelime."),
 ("hâlâ", "Sosyal medya gönderisi: yağmurlu günde çamaşırlar kurumadı, balkonda asılı duruyor, günlerdir aynı manzara. İki yorum ekle. 60-100 kelime."),
 ("kâr", "Sosyal medyada paylaş: evde yaptığın reçelleri satıyorsun, bu ay elde ettiğin gelir fazlası giderlerini karşıladı. Gönderi + iki yorum. 60-100 kelime."),
 ("kâr", "Sosyal medya gönderisi: küçük esnafın yıl sonu kazancı üzerine bir tespit yaz; zincir mağazalarla rekabeti anlat. İki yorum ekle. 60-100 kelime."),
 ("kâr", "Sosyal medyada paylaş: bahçenden topladığın sebzeleri pazarda sattın, elde ettiğin net gelirle fidan aldın. İki yorum ekle. 60-100 kelime."),
 ("millî", "Sosyal medya gönderisi: ülkenin ulusal futbol takımının galibiyetini kutlayan bir yazı yaz, stadın atmosferini anlat. İki yorum ekle. 60-100 kelime."),
 ("millî", "Sosyal medyada paylaş: ulusal bayram kutlamalarında okulda yapılan töreni, süslenen caddeleri anlat. İki yorum ekle. 60-100 kelime."),
 ("millî", "Sosyal medya gönderisi: ulusal takımın genç bir oyuncusunun başarısı üzerine bir değerlendirme yaz. İki yorum ekle. 60-100 kelime."),
 ("resmî", "Sosyal medyada paylaş: devlet dairesinde evrak işinin ne kadar uzadığını, sıra beklemenin zorluğunu mizahi bir dille anlat. İki yorum ekle. 60-100 kelime."),
 ("resmî", "Sosyal medya gönderisi: tapu işlemleri için devlete ait belgeleri tamamladın, nihayet randevu aldın; süreci anlat. İki yorum ekle. 60-100 kelime."),
 ("resmî", "Sosyal medya gönderisi: düğün için nikah işlemlerini anlat; devlet dairesinde beklediğin saatleri, evrak silsilesini yaz. İki yorum ekle. 60-100 kelime."),
 ("âdet", "Sosyal medyada paylaş: köyünüzdeki kına gecesi geleneğini, damadın kına yakma anını anlat. İki yorum ekle. 60-100 kelime."),
 ("âdet", "Sosyal medya gönderisi: yörenizdeki geleneksel bayramlaşma usulünü anlat; çocukların şeker toplama gezintisini yaz. İki yorum ekle. 60-100 kelime."),
 ("âdet", "Sosyal medya gönderisi: yılbaşında kapı kapı dolaşan davulcuların geleneğini hatırlat. İki yorum ekle. 60-100 kelime."),
 ("tarihî", "Sosyal medyada paylaş: geçtiğimiz yaz gezdiğin eski dönemden kalma bir kaleyi ve surları anlat; fotoğraf çektiğin noktaları yaz. İki yorum ekle. 60-100 kelime."),
 ("tarihî", "Sosyal medya gönderisi: ilçendeki antik tiyatronun restorasyonuna dikkat çek. İki yorum ekle. 60-100 kelime."),
 ("tarihî", "Sosyal medya gönderisi: eski bir hamamın kütüphaneye çevrilmesi haberini yorumla. İki yorum ekle. 60-100 kelime."),
 ("sanatkâr", "Sosyal medyada paylaş: çarşıda el emeğiyle çalışan bir bakır ustasını ziyaret ettin; tezgahını, sabrını anlat. İki yorum ekle. 60-100 kelime."),
 ("sanatkâr", "Sosyal medya gönderisi: halı dokuyan bir ustanın atölyesindeki günü anlat; düğümlerin inceliğini yaz. İki yorum ekle. 60-100 kelime."),
 ("dâhi", "Sosyal medyada paylaş: yarışmada her soruyu bilen, olağanüstü zekasıyla dikkat çeken çocuğu anlat. İki yorum ekle. 60-100 kelime."),
 ("dâhi", "Sosyal medya gönderisi: tarihe mal olmuş, olağanüstü yetenekli bir bilim insanının çocukluğunu anlatan bir yazı yaz. İki yorum ekle. 60-100 kelime."),
 ("dâhi", "Sosyal medya gönderisi: bir müzisyenin doğaçlama yeteneğini öven bir paylaşım yaz; konserdeki anı anlat. İki yorum ekle. 60-100 kelime."),
 ("hükûmet", "Sosyal medyada paylaş: devlet yönetiminin açıkladığı gençlere yönelik destek programını değerlendir. İki yorum ekle. 60-100 kelime."),
 ("hükûmet", "Sosyal medya gönderisi: bakanlar kurulunun aldığı eğitim kararlarını tartışan bir yazı yaz. İki yorum ekle. 60-100 kelime."),
 ("âşık", "Sosyal medya gönderisi: şehirlerarası otobüste tanıştığı birine gönlünü kaptırdığını anlatan komik bir paylaşım yaz. İki yorum ekle. 60-100 kelime."),
 ("âşık", "Sosyal medya gönderisi: komşunun köpeğine duyduğun saf sevgiyi itiraf et; her sabah pencereden izlediğini yaz. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medyada paylaş: kedin sabaha karşı kapıda miyavlayıp seni uyandırdı, uykusuzluğunu mizahi anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: yağmurda durmadan yürüyen sporcu olarak ıslandığını, ama keyfinin yerinde olduğunu yaz. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: sabah kahvesini döküp işe koşan birinin gününü anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: pazar sabahı kurulan semt pazarının kalabalığını, esnafın bağırışlarını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: mahalle bakkalındaki kediye her akşam mama bıraktığını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: komşunun davul zurna eşliğinde oğlunu askere uğurlamasını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: el yapımı kurabiyelerin fotoğrafını paylaşıp tarifini özetle. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: kütüphanede bulduğun eski bir dergiyi, içindeki yazıları anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: gece yarısı duyduğun komşu tartışmasını mizahi bir dille anlat (kimse zarar görmedi). İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: sabah koşusunda karşılaştığın martıların peşinden koşan köpeği anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: garda beklerken tanık olduğun vedalaşma sahnesini anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: evde yaptığın deneme yanılma yemek macerasını anlat; sonucun iyi olduğunu yaz. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: otobüste telefonu çalan ama açamayan amcayı anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: kitapçıda vitrine bakarken tanıdığın eski bir hocana rastladığını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: iş yerindeki kahve makinesinin sürekli bozulmasını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: apartman bahçesindeki kiraz ağacının ilk meyvesini topladığını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: minibüste şoförün radyodaki türküye eşlik etmesini anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: kargo kuryesine kapıda su ikram etme alışkanlığını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: mahalledeki fırının sabah kokusuyla uyanmayı anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: okul çıkışında çocukların top peşinde koşmasını anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: elinde simit, martılarla atışan birini anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: teleferikte sıkışıp kalanları anlatan bir gönderi yaz. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya gönderisi: gece yarısı marketten aldığın dondurmayı anlat. İki yorum ekle. 60-100 kelime."),
 ("hikâye", "Sosyal medya paylaşımı: balkonunda saksıya fesleğen dikme maceranı anlat. İki yorum ekle. 60-100 kelime."),
 ("rüzgâr", "Sosyal medya gönderisi: çatıdaki uydu antenini kuvvetli hava akımı uçurdu; komşunun çatıya çıkıp alamayışını mizahi anlat. İki yorum ekle. 60-100 kelime."),
 ("kâğıt", "Sosyal medya paylaşımı: eski bir mektubu, üzerindeki el yazısını, mürekkebin solmuşluğunu anlat; mektup saklama alışkanlığını yaz. İki yorum ekle. 60-100 kelime."),
 ("tarihî", "Sosyal medya gönderisi: şehirdeki eski dönemden kalma evlerin cumbalarını, demir parmaklıklarını anlatan bir paylaşım yaz. İki yorum ekle. 60-100 kelime."),
 ("hükûmet", "Sosyal medya paylaşımı: devlet yönetiminin ilan ettiği bayram tatili günlerini, yolcu yoğunluğunu yorumla. İki yorum ekle. 60-100 kelime."),
 ("adet", "Sosyal medya gönderisi: ailenizde kahve fincanı ikramının bir gelenek olarak nasıl sürdüğünü anlat; fincanın yanında su ikramını yaz. İki yorum ekle. 60-100 kelime."),
 ("hâlâ", "Sosyal medya paylaşımı: yeni yıl kararlarının şubat ayında nasıl unutulduğunu, spor salonu üyeliğinin kullanılmayışını esprili anlat. İki yorum ekle. 60-100 kelime."),
]
_SOC = [(i, t) for i, (_, t) in enumerate(S, 1)]
assert len(_SOC) == 60, len(_SOC)

# ---------------- FORUM (60) ----------------
F = [
 ("kâr", "Bir yatırım forumuna mesaj yaz: küçük işletmelerin yıl sonu kazançlarını nasıl hesaplayacağını, gelir fazlasının vergisini sor. 60-100 kelime."),
 ("kâr", "Foruma yaz: bakkal işletmecisi kardeşine tavsiye iste; rakiplere karşı marjın nasıl korunacağını, maliyet hesabını tartış. 60-100 kelime."),
 ("kâr", "Bir esnaf forumuna mesaj: pazarda kazancın düştüğünü, giderlerin arttığını anlat; çözüm iste. 60-100 kelime."),
 ("kâr", "Foruma yaz: çiftçilikte bu sezon iyi hasat, yüksek getiri hikayeleri paylaşın; hangi ürünün kazandırdığını sor. 60-100 kelime."),
 ("kâr", "Bir girişimcilik forumuna mesaj: ilk yılınızda zarar ettiniz, ikinci yıl kara geçmek için ne yapmalısınız? Deneyim paylaşımı. 60-100 kelime."),
 ("kâr", "Foruma yaz: el yapımı ürün satanlar, fuarlarda elde ettiğiniz gelir fazlasını ve stand kirasını paylaşın. 60-100 kelime."),
 ("kar", "Bir hava durumu sohbet forumuna yaz: şehirde gece beklenen yoğun yağış uyarısını, yolların kapanma ihtimalini tartışın. 60-100 kelime."),
 ("koşullu", "Foruma yaz: memleketinde ilk kez yoğun yağış oldu, okullar tatil edildi; deneyimini anlat. 60-100 kelime."),
 ("hâlâ", "Foruma yaz: aldığınız elektronik ürün iki haftadır elinize ulaşmadı; satıcıyla yazışmalarınızı, garanti sürecini anlat. 60-100 kelime."),
 ("hâlâ", "Bir sağlık forumuna mesaj: randevu sisteminde günlerdir sıra bekliyorsun, telefonlar meşgul; çözüm önerisi iste. 60-100 kelime."),
 ("hâlâ", "Foruma yaz: internet bağlantın kesik, servis ekibi günlerdir gelmedi; kurumsal müşteri hizmetleriyle yaşadıklarını anlat. 60-100 kelime."),
 ("hâlâ", "Bir kitap forumuna mesaj: beklediğin yeni baskı romanın raflara gelmesini aylardır iple çekiyorsun; yayınevine nasıl ulaşılır? 60-100 kelime."),
 ("hâlâ", "Foruma yaz: dil kursuna kaydoldun, sınıf bir türlü açılmıyor; kayıt paranın durumunu sor. 60-100 kelime."),
 ("adet", "Bir gelenek forumuna mesaj: düğünlerde para takma adedini tartış; herkes kendi yöresinden örnek versin. 60-100 kelime."),
 ("adet", "Foruma yaz: bayramda büyükleri ziyaret alışkanlığı gençlerde kayboluyor mu? Fikirlerinizi yazın. 60-100 kelime."),
 ("adet", "Bir iş forumuna mesaj: toplantılarda dakikliğin, kıyafet seçiminin kurumsal kültürle ilgisi üzerine görüş sor. 60-100 kelime."),
 ("tarihî", "Bir gezi forumuna mesaj: gezdiğiniz eski dönemden kalma kervansarayları, hanları önerin; hangisi restore edilmiş? 60-100 kelime."),
 ("tarihî", "Foruma yaz: şehrindeki antik kalıntıların korunması için ne yapılabilir? Belediye duyarsız, tepkini yaz. 60-100 kelime."),
 ("tarihî", "Bir tarih forumuna mesaj: eski bir caminin avlusundaki mezar taşlarının kitabelerini okumak istiyorsun; yardım iste. 60-100 kelime."),
 ("tarihî", "Foruma yaz: müzelerdeki eski döneme ait eşyaların sergilenme koşullarını eleştir. 60-100 kelime."),
 ("millî", "Bir spor forumuna mesaj: ulusal takımın kadro seçimini tartış; genç oyunculara şans verilmeli mi? 60-100 kelime."),
 ("millî", "Foruma yaz: ulusal bayram törenlerinde okulların katılımını, provaların yoğunluğunu konuşun. 60-100 kelime."),
 ("millî", "Bir spor forumuna mesaj: ulusal marş öncesi tribünlerdeki coşkuyu anlat; unutulmaz bir maç anın. 60-100 kelime."),
 ("millî", "Foruma yaz: ülkenin ulusal takımının yurt dışındaki kamp koşullarını eleştir. 60-100 kelime."),
 ("resmî", "Bir hukuk forumuna mesaj: devlet dairesinden evrak almak için kaç gün beklenir? Yaşadığın süreci anlat. 60-100 kelime."),
 ("resmî", "Foruma yaz: okul diplomanın tasdik işlemi için devlete ait belgelerin fotokopisi gerekti; evrak listesini sor. 60-100 kelime."),
 ("resmî", "Bir memur forumuna mesaj: kurum içi yazışmaların, devlete ait evrakların dijital ortama taşınmasını tartışın. 60-100 kelime."),
 ("resmî", "Foruma yaz: işyeri ruhsatı almak için devlet kurumlarında geçen süreyi ve istenen belgeleri paylaşın. 60-100 kelime."),
 ("fikrî", "Bir teknoloji forumuna mesaj: yazılım patentlerinin, telif haklarının küçük geliştiricileri nasıl etkilediğini tartış. 60-100 kelime."),
 ("fikrî", "Foruma yaz: telif hakları ihlali davalarında düşünce ürünlerinin korunmasını tartış; örnek ver. 60-100 kelime."),
 ("fikrî", "Bir tasarım forumuna mesaj: tasarımcıların eserlerinin izinsiz kullanımına karşı ne yapmalı? Deneyim paylaş. 60-100 kelime."),
 ("katip", "Bir memuriyet forumuna mesaj: adliyedeki tutanakların yazılması işinin ne kadar yoğun olduğunu anlat; mesai saatlerini sor. 60-100 kelime."),
 ("katip", "Foruma yaz: devlet dairesinde yazışma görevlisi olarak işe başlayacaklara tavsiye ver. 60-100 kelime."),
 ("ilmi", "Bir akademik forumda paylaş: bilimsel dergilerde hakemlik sürecinin yavaşlığından yakın; deneyimini anlat. 60-100 kelime."),
 ("ilmi", "Foruma yaz: üniversitelerdeki bilimsel çalışmaların şehir hayatına etkisini tartış; bir araştırma merkezi örneği ver. 60-100 kelime."),
 ("ilmi", "Bir eğitim forumuna mesaj: fen lisesinde bilimsel araştırma projelerine katılımı teşvik etmek için öneri iste. 60-100 kelime."),
 ("askerî", "Foruma yaz: savunma sanayisindeki yerli üretim hamlesini, orduya ait yeni araçların testini tartış. 60-100 kelime."),
 ("askerî", "Bir güvenlik forumuna mesaj: ordu okullarının eğitim müfredatını tartış; hangi dersler ağırlıklı? 60-100 kelime."),
 ("zihnî", "Bir eğitim forumuna mesaj: sınav döneminde kafa yormaktan kaynaklanan yorgunluğu, odaklanma tekniklerini konuşun. 60-100 kelime."),
 ("zihnî", "Foruma yaz: satranç turnuvası öncesi zihinsel hazırlığı, konsantrasyon antrenmanlarını tartış. 60-100 kelime."),
 ("hükûmet", "Bir ekonomi forumuna mesaj: bakanlar kurulunun açıkladığı kredi paketini yorumla; kimler yararlanabilir? 60-100 kelime."),
 ("hükûmet", "Foruma yaz: devlet yönetiminin konut projelerini, taksit koşullarını tartışın. 60-100 kelime."),
 ("hükûmet", "Bir çiftçi forumuna mesaj: devlet yönetiminin tarım desteklerinin yetersiz olduğunu anlat; öneri iste. 60-100 kelime."),
 ("dâhi", "Foruma yaz: satrançta yaşıtlarını geçen olağanüstü yetenekli bir çocuğu tartışın; eğitimi nasıl olmalı? 60-100 kelime."),
 ("dâhi", "Bir bilgisayar forumuna mesaj: çok erken yaşta kod yazmaya başlayan, olağanüstü zekalı genç yazılımcıları konuşun. 60-100 kelime."),
 ("mani", "Bir edebiyat forumuna mesaj: halk edebiyatındaki kısa dörtlük türünün ezgilerle nasıl söylendiğini sor; bildiğin örnekleri ver. 60-100 kelime."),
 ("mani", "Foruma yaz: düğünlerde söylenen kısa dörtlüklerin sözlerinin yeni nesle aktarılmasını tartış. 60-100 kelime."),
 ("alem", "Bir felsefe forumuna mesaj: evrenin sonsuzluğu, insanın bu büyüklük karşısındaki yeri üzerine düşüncelerini yaz. 60-100 kelime."),
 ("alem", "Foruma yaz: gece gökyüzüne bakıp evrenin ihtişamını düşündüğün bir anı anlat; merak ettiğin soruları yaz. 60-100 kelime."),
 ("şura", "Bir güvenlik forumuna mesaj: ülkenin güvenlik konularını görüşen üst danışma kurulunun kararlarını değerlendir. 60-100 kelime."),
 ("hâlâ", "Foruma yaz: yeni çıkan oyunun sunucusuna giriş sorunlarını anlat; teknik destek cevap vermiyor. 60-100 kelime."),
 ("kâğıt", "Bir kitap forumuna mesaj: e-kitap mı basılı kitap mı? Basılı kitabın dokusunu, sayfa çevirme zevkini savun. 60-100 kelime."),
 ("kâğıt", "Foruma yaz: matbaacılıkta kullanılan malzemenin kalitesinin baskıya etkisini tartış; deneyim sor. 60-100 kelime."),
 ("kâğıt", "Bir ofis forumuna mesaj: arşivlemede dijital ortam mı basılı çıktı mı? Evrak yönetimi önerileri iste. 60-100 kelime."),
 ("rüzgâr", "Bir denizcilik forumuna mesaj: koyda kuvvetli hava akımı varken demir atmak güvenli mi? Tecrübelilerden görüş iste. 60-100 kelime."),
 ("rüzgâr", "Foruma yaz: yelkenliyle geçtiğin bir fırtına anını anlat; rotanı nasıl değiştirdin? 60-100 kelime."),
 ("hâl", "Bir emlak forumuna mesaj: kiracının evi terk etmesi durumunda eşyaların ve anahtarın durumuyla nasıl ilgilenilir? Sor. 60-100 kelime."),
 ("hâl", "Foruma yaz: deprem sonrası binanızın güçlendirme sürecinin durumunu sor; müteahhit ne diyor? 60-100 kelime."),
 ("hâl", "Bir sağlık forumuna mesaj: yakınınızın tedavi sürecinin durumunu, doktor kontrolünü anlat; benzer deneyim iste. 60-100 kelime."),
 ("ironik", "Foruma yaz: kışın soğukta otobüs durağında beklerken gördüğün komik bir anı anlat. 60-100 kelime."),
]
_FOR = [(i, t) for i, (_, t) in enumerate(F, 1)]
assert len(_FOR) == 60, len(_FOR)

# ---------------- NEWS (formal, 18) ----------------
N = [
 ("kâr", "Bir haber metni yaz: büyük bir teknoloji şirketi yıl sonu kazançlarını açıkladı, elde ettiği gelir fazlası analist beklentilerini aştı. 90-130 kelime, haber üslubu."),
 ("rüzgâr", "Bir haber metni yaz: Meteoroloji Genel Müdürlüğü kuvvetli hava akımı uyarısı yaptı; yarın yurt genelinde fırtına bekleniyor, ulaşımda aksamalar olabilir. 90-130 kelime."),
 ("hükûmet", "Bir haber metni yaz: bakanlar kurulu yeni yılda geçerli olacak ekonomik önlemleri açıkladı; enerji ve gıdada destek paketi duyuruldu. 90-130 kelime."),
 ("millî", "Bir haber metni yaz: ülkenin ulusal futbol takımı eleme maçında galibiyet aldı; teknik direktör ve kaptan maç sonu açıklamalarda bulundu. 90-130 kelime."),
 ("resmî", "Bir haber metni yaz: e-devlet uygulaması üzerinden devlete ait belgelerin temininde yeni düzenleme yürürlüğe girdi; vatandaşlar süreci daha kısa sürede tamamlayabilecek. 90-130 kelime."),
 ("tarihî", "Bir haber metni yaz: kent merkezindeki 500 yıllık antik yapının restorasyonu tamamlandı; yapı ziyarete açıldı. 90-130 kelime."),
 ("hakim", "Bir haber metni yaz: mahkeme başkanı olarak görev yapan yargıç, uzun süren davanın kararını açıkladı; taraflar salonu terk etti. 90-130 kelime."),
 ("âdet", "Bir haber metni yaz: ilde düzenlenen geleneksel bahar kutlamalarına binlerce kişi katıldı; yöresel oyunlar ve kına gecesi etkinlikleri yapıldı. 90-130 kelime."),
 ("dinî", "Bir haber metni yaz: bayram namazının kılınacağı camilerde hazırlıklar tamamlandı; vatandaşların bayramlaşma ve inanç günlerine yönelik programı açıklandı. 90-130 kelime."),
 ("askerî", "Bir haber metni yaz: ordu birlikleri geniş katılımlı bir tatbikatta görev yaptı; savunma sistemleri test edildi. 90-130 kelime."),
 ("ilmi", "Bir haber metni yaz: üniversitede tamamlanan bilimsel araştırma projesinin sonuçları açıklandı; çalışmanın tarım verimliliğine katkı sağlayacağı belirtildi. 90-130 kelime."),
 ("katip", "Bir haber metni yaz: adliye binasında yazışma görevlileri için yeni çalışma düzeni getirildi; tutanakların dijital ortama aktarımı hızlandırılacak. 90-130 kelime."),
 ("hâlen", "Bir haber metni yaz: sanat galerisinde açılan sergi ziyaretçilerle buluştu; eserler şu anda ve önümüzdeki ay boyunca görülebilecek. 90-130 kelime."),
 ("şura", "Bir haber metni yaz: ülkenin güvenlik konularını görüşen üst danışma kurulu toplandı; toplantıda sınır güvenliği başlığı ele alındı. 90-130 kelime."),
 ("Kâbe", "Bir haber metni yaz: hac mevsimi için Mekke'deki kutsal yapının çevresinde hazırlıklar sürüyor; yetkililer kapasite artışını duyurdu. 90-130 kelime."),
 ("resmî", "Bir haber metni yaz: yeni açılan devlet hastanesinin laboratuvar bölümünde cihazların devreye alındığı bildirildi; hastane tam kapasite hizmet verecek. 90-130 kelime."),
 ("hükûmet", "Bir haber metni yaz: devlet yönetimi, kırsal kalkınma için yeni hibeler açıkladı; başvuruların belediyelere yapılacağı duyuruldu. 90-130 kelime."),
 ("sanatkâr", "Bir haber metni yaz: kaybolmaya yüz tutan el işi meslekler için atölye açıldı; bakır işleme ve ebru kursları ilgi gördü. 90-130 kelime."),
]
_NEWS = [(i, t) for i, (_, t) in enumerate(N, 1)]
assert len(_NEWS) == 18, len(_NEWS)

# ---------------- ESSAY (formal, 18) ----------------
E = [
 ("kâr", "Bir deneme yaz: ticarette elde edilen gelir fazlasının insan ilişkilerini nasıl değiştirdiği üzerine düşüncelerini anlat. 90-130 kelime, ağırbaşlı üslup."),
 ("hâlâ", "Deneme yaz: insanın geçmişten bugüne taşıdığı bekleyişleri, özlemi; bir şeyin bir türlü gelmemesinin ruh üzerindeki etkisini anlat. 90-130 kelime."),
 ("hâl", "Deneme yaz: hasta bir dostu ziyaret etmenin, onun durumunu sormanın insanlık değeri üzerine. 90-130 kelime."),
 ("millî", "Deneme yaz: ulusal bayramların, ortak marşların ve ülke takımının toplumu birleştirici gücü üzerine. 90-130 kelime."),
 ("resmî", "Deneme yaz: devlete ait evrakların, bürokrasinin hayatımızdaki yerini ve sadeleşme ihtiyacını tartış. 90-130 kelime."),
 ("tarihî", "Deneme yaz: eski dönemden kalma yapıların bugünü anlamamıza nasıl yardım ettiğini anlat. 90-130 kelime."),
 ("dinî", "Deneme yaz: inanç günlerinin, bayram sabahlarının ve ibadetin insana kattığı sükuneti anlat. 90-130 kelime."),
 ("ilmi", "Deneme yaz: bilimsel merakın, akademik çalışmanın günlük yaşamı nasıl zenginleştirdiğini anlat. 90-130 kelime."),
 ("âşık", "Deneme yaz: karşılıksız sevginin, birine gönül vermenin edebiyattaki yansımaları üzerine düşün. 90-130 kelime."),
 ("âşık", "Deneme yaz: divan şiirinde sevgiliye duyulan hasretin, aşk acısının dile gelişini anlat. 90-130 kelime."),
 ("mani", "Deneme yaz: halk edebiyatındaki kısa dörtlüklerin, ezgili söyleyişin Anadolu insanının duygu dünyasını nasıl anlattığını yaz. 90-130 kelime."),
 ("alem", "Deneme yaz: yıldızlı bir gecede gökyüzüne bakarken evrenin büyüklüğü karşısında duyulan hayranlığı anlat. 90-130 kelime."),
 ("kainat", "Deneme yaz: bir sabah bahçede kuş sesleriyle uyanmanın, doğanın düzenini fark etmenin verdiği huzuru anlat. 90-130 kelime."),
 ("yâr", "Deneme yaz: uzakta olan bir dostu, arkadaşı hatırlamanın; onun yokluğunda yaşanan özlemin güzelliğini anlat. 90-130 kelime."),
 ("yâr", "Deneme yaz: eski mektupların, dost elinden gelen satırların değerini anlat; mektup bekleyen insanın heyecanını yaz. 90-130 kelime."),
 ("hissî", "Deneme yaz: duyguların, sezgilerin kararlarımızı yönlendirmesi; akıl ile kalbin dengesi üzerine düşün. 90-130 kelime."),
 ("zihnî", "Deneme yaz: kafa yormak, düşünmek insanı nasıl olgunlaştırır; zihinsel emeğin değeri üzerine düşün. 90-130 kelime."),
 ("rahîm", "Deneme yaz: merhametin, bağışlamanın insan ilişkilerindeki iyileştirici gücünü anlat; bir affediş anısından söz et. 90-130 kelime."),
]
_ESS = [(i, t) for i, (_, t) in enumerate(E, 1)]
assert len(_ESS) == 18, len(_ESS)

# ---------------------------------------------------------------------------
def _finalize(items, genre, off):
    return [(genre, f"{genre[0].upper()}{off + i}", t) for i, (pid, t) in enumerate(items)]

CHAT = _finalize(_CHAT, "chat", 0)
SOCIAL = _finalize(_SOC, "social", 0)
FORUM = _finalize(_FOR, "forum", 0)
NEWS = _finalize(_NEWS, "news", 0)
ESS = _finalize(_ESS, "essay", 0)

PROMPTS = CHAT + SOCIAL + FORUM + NEWS + ESS
FORMAL = NEWS + ESS
INFORMAL = CHAT + SOCIAL + FORUM

if __name__ == "__main__":
    assert_unprimed()
    n_info = len(INFORMAL); n_formal = len(FORMAL)
    print(f"total={len(PROMPTS)}  informal={n_info}  formal={n_formal}  (formal>=24: {n_formal>=24}, total>=200: {len(PROMPTS)>=200})")